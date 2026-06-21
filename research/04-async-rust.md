# Async Rust — Best Practices & Pitfalls

A practical, opinionated field guide for writing correct async Rust on Tokio, current as of mid-2026 (stable Rust ~1.85+, Edition 2024). Every section pairs the **good practice** with the **mistake to avoid**, a short rationale, and — where useful — a tiny code sketch. Citations map to the Sources list.

Async Rust is a `Future`-polling model: an `async fn` desugars to a state machine that returns `impl Future`, and a runtime (almost always Tokio) drives those futures by repeatedly polling them, only making progress at `.await` points [1][10]. Two consequences flow from this and explain most footguns below: (1) the runtime can only switch tasks *at an `.await`*, so anything between awaits monopolizes the thread; and (2) dropping a future *is* cancellation, and the compiler will not warn you about it [9][3].

## The cardinal rule: never block the executor

**Good:** Treat the async thread as a cooperative scheduler. Aim for no more than ~10–100 microseconds of work between `.await` points [4]. Tokio explicitly will *not* detect blocking and spin up rescue threads for you — that is your job [12][2].

**Mistake:** Calling synchronous/blocking APIs (`std::fs`, `std::net`, `reqwest::blocking`, `std::thread::sleep`, big CPU loops, `Mutex` contention) directly inside an `async fn`. If code "spends a long time without reaching an `.await`", you are *blocking the thread* — starving every other task on that worker, including the ones that would let an `.await` you are waiting on complete [2][4].

**Why it bites:** Tokio's default multi-threaded runtime has a small worker pool (one per core). One blocked worker is a measurable fraction of your throughput gone, and a deadlock if the blocked work depends on another task on the same worker.

## spawn_blocking, block_in_place, and CPU-bound work

**Good — blocking I/O / occasional sync calls:** Wrap them in `tokio::task::spawn_blocking`, which moves the work to a dedicated blocking-thread pool where blocking is allowed [2][13].

```rust
let contents = tokio::task::spawn_blocking(move || std::fs::read_to_string(path)).await??;
```

**Good — heavy CPU work:** `spawn_blocking` is fine for a *few* short CPU tasks, but its pool defaults to a very large cap (512 threads) tuned for I/O, not compute. CPU-bound work runs best with threads ≈ cores, so reach for **rayon** (or a bounded pool) and bridge results back via a channel/`oneshot` [4][13].

**Mistakes to avoid:**
- **Long-lived loops in `spawn_blocking`.** It is meant for short, bounded work. A persistent worker should be a real `std::thread::spawn`; otherwise it permanently consumes a pool slot and queues out other blocking ops [13].
- **Assuming `spawn_blocking` work is cancellable.** It is not. "Tasks spawned using `spawn_blocking` cannot be aborted because they are not async" — `abort()` is a no-op once it starts, and runtime shutdown will *wait* for it (use `shutdown_timeout` to bound that) [13].
- **Reaching for `block_in_place` reflexively.** It blocks the *current* worker while attempting to hand off its other tasks, only works on the multi-thread runtime, and is easy to misuse; prefer `spawn_blocking` unless you specifically need to keep the surrounding task on the same thread [2].

## Cancellation safety: the silent footgun

In async Rust, "dropping a future implies it can never be polled again. This is called *cancellation* and it can occur at any `await` point" [9]. A future is **cancellation-safe** if, when it has not completed, "it must be a no-op to drop that future and recreate it" [3].

**Mistake:** Holding partial state in a future's *local* variables across an `.await` inside a `select!` loop. The classic bug: a line-reader buffers bytes into a local `Vec`, and when another `select!` branch wins, that future — and its buffer — is dropped, silently losing data. `AsyncBufReadExt::read_line`, `read_exact`, `read_to_end`, and `write_all` are explicitly **not** cancel-safe [9][3].

**Good:** Move accumulator state *out of the future and into a struct field* so a cancelled-and-restarted future resumes where it left off [9]. Know the cancel-safe set: `mpsc::Receiver::recv`, `TcpListener::accept`, `AsyncReadExt::read` (single buffer), and `StreamExt::next` are safe; `Mutex::lock` and `Semaphore::acquire` are not (you lose your queue position) [3]. The compiler gives you nothing here — "you need to read API documentation and consider what state your `async fn` holds" [9].

## tokio::select! pitfalls

`select!` polls several futures concurrently and, on the first to complete, **drops all the others** [3][8]. That drop is exactly the cancellation hazard above.

**Mistakes:**
- **Putting a non-cancel-safe operation in a branch.** E.g. `tx.send(x)` — `mpsc::Sender::send` is not cancel-safe and can lose the message. Use `tx.reserve()` to get a permit first (reserving *is* mostly cancel-safe) and only `permit.send()` once a branch is chosen [3][1].
- **Recreating a future every loop iteration** when you wanted to *resume* it. Each iteration builds a fresh future, throwing away progress. Instead pin once and pass `&mut` to keep the same future across iterations (it must be `Unpin`; use `tokio::pin!`) [8][3].

```rust
let sleep = tokio::time::sleep(dur);
tokio::pin!(sleep);
loop {
    tokio::select! {
        _ = &mut sleep => break,        // same future resumed each pass
        msg = rx.recv() => handle(msg),  // recv() is cancel-safe
    }
}
```

- **Racy `if` preconditions.** A `select!` branch guarded by `if cond` evaluates `cond` *before* polling; state can change in between, so a branch you "disabled" may still be the only ready one — leading to missed wakeups or spins [3].

## Send bounds on futures (and why your spawn won't compile)

`tokio::spawn` requires the future to be `Send + 'static` because the work-stealing scheduler may move the task between threads at any `.await` [11].

**Mistake:** Holding a `!Send` value (e.g. `Rc`, `RefCell`, or a `std::sync::MutexGuard`) *across* an `.await`. The whole future becomes `!Send` and `spawn` rejects it with "future cannot be sent between threads safely" [11][6].

**Good:** Confine the `!Send` value to a scope that ends before the next `.await`, so it never lands in the future's persisted state [11]:

```rust
let n = { let r = Rc::new(1); *r };  // Rc dropped here
do_async(n).await;                    // future stays Send
```

If you genuinely need `!Send` tasks, run them on a `current_thread` runtime / `LocalSet` with `spawn_local`.

## async traits: status and the Send-bound problem

**What's stable:** Since Rust 1.75, `async fn` in traits and return-position `impl Trait` in traits (AFIT / RPITIT) work natively — `async fn` is "just sugar" for `-> impl Future` [1][5]. Niko Matsakis calls AFIT "the foundation of basically *everything*" for async [5].

**The catch — the "Send bound problem":** you still cannot, in the trait definition, require that the *returned* future be `Send`, which is exactly what you need to `spawn` it on a multithreaded runtime. This is "the inability to require that an `async fn` returns a `Send` future" [7][5].

**Good (today's pragmatic answer):**
- For traits you intend to spawn on Tokio, use **`#[trait_variant::make(MyTrait: Send)]`** to auto-generate a `Send` variant alongside the base trait [1].
- For *public* APIs, the official guidance is still cautious: "it's best to avoid \[native async fn in trait\] for now unless you can anticipate all the bounds your users might want" — the mature `async-trait` crate (which boxes futures) remains a reasonable choice when you need `dyn` dispatch or guaranteed `Send` [1].

**Mistakes:** Exposing a native `async fn` in a public trait and discovering downstream users can't add the `Send` bound they need; or expecting `dyn MyAsyncTrait` to work — AFIT/RPITIT traits are **not object-safe** [1][5]. The longer-term fix, *return-type notation* (RTN), lets callers write bounds like `where T: Trait<method(..): Send>`; it is progressing but not the stable default yet [7].

**Adjacent 2024/2025 wins:** async closures (`async || {}` with `AsyncFn`/`AsyncFnMut`/`AsyncFnOnce`) stabilized in Rust 1.85 / Edition 2024, removing a long-standing combinator gap [16]. Async `Drop` and runtime-generic code remain open problems [5].

## Structured concurrency: scope your tasks

The async-book's default advice is blunt: "You should probably use `spawn` and `JoinHandle`s unless you have a good reason not to" — spawning is "usually less error-prone, more general, and performance is more predictable" than hand-rolled `join!`/`select!` [10]. But spawning is *unstructured*: a bare `tokio::spawn` returns a `JoinHandle` that, **when dropped, detaches the task** — it keeps running, orphaned, with its result lost [11].

**Mistake — fire-and-forget leaks:** `tokio::spawn(async { ... });` with the handle dropped. The task outlives its logical parent, can hold resources open, and won't be cancelled on error. This is the "future leak" structured concurrency exists to prevent.

**Good — `JoinSet`:** Group related tasks in a `tokio::task::JoinSet`. You can `join_next()` to collect results, and crucially "when the `JoinSet` is dropped, all tasks in the `JoinSet` are immediately aborted" — tasks cannot outlive their scope [14].

```rust
let mut set = tokio::task::JoinSet::new();
for job in jobs { set.spawn(run(job)); }
while let Some(res) = set.join_next().await { handle(res?); }
// drop(set) here would abort any stragglers
```

**Good — cooperative cancellation:** For graceful shutdown, prefer an explicit `tokio_util::sync::CancellationToken` over relying on drop-cancellation. Propagate the signal and check it at safe `.await` points (e.g. a `select!` branch), so tasks can flush and clean up rather than being torn down mid-operation [3].

## Shared state in async

**Good — `std::sync::Mutex` for short, sync critical sections:** "using a synchronous mutex from within asynchronous code is fine as long as contention remains low and the lock is not held across calls to `.await`" [6]. It is cheaper than the async mutex. The safest discipline: "wrap it in a struct, and lock the mutex only inside non-async methods" so the guard never appears in async state [6].

**Mistake:** Holding any `MutexGuard` across an `.await`. With `std::sync::Mutex` the guard is `!Send`, so the task won't compile for `spawn` [6]; with `tokio::sync::Mutex` it *will* compile but you've now serialized your tasks and invited deadlocks. Either way, scope the guard:

```rust
{ let mut g = state.lock().unwrap(); *g += 1; } // drop before awaiting
do_async().await;
```

**When to actually use `tokio::sync::Mutex`:** only when you genuinely must hold a lock across `.await` (e.g. guarding an async resource). It is "more expensive than an ordinary mutex," so it is the exception, not the default [6].

**Mistake — reaching for an async mutex to fix contention.** It rarely helps throughput. Under real contention, prefer **sharding** (split the keyspace across N independent `std::sync::Mutex`es) or message-passing actors over a shared lock [6]. In general, channels (`mpsc`/`oneshot`/`watch`) and the actor pattern often beat shared mutable state in async designs.

## Quick reference

| Situation | Do | Don't |
|---|---|---|
| Blocking I/O / sync call | `spawn_blocking` [2][13] | Call it inline in `async fn` [4] |
| Heavy CPU work | rayon + channel [4] | Saturate Tokio workers [4] |
| Racing futures | `select!` with cancel-safe ops + `&mut` reuse [3][8] | Non-cancel-safe branch, recreate future each loop [3] |
| Spawn task | `Send + 'static`; scope `!Send` before await [11] | Guard/`Rc` held across await [6][11] |
| Many related tasks | `JoinSet` (aborts on drop) [14] | Detached `tokio::spawn` (leaks) [11] |
| Graceful stop | `CancellationToken` [3] | Rely on implicit drop-cancellation [9] |
| Shared map/counter | `std::sync::Mutex`, lock in sync method [6] | Hold guard across `.await` [6] |
| Async trait to spawn | `#[trait_variant::make(_: Send)]` [1] | Native `async fn` in public trait expecting `Send`/`dyn` [1][5] |

## Sources

1. Rust Blog — Announcing `async fn` and return-position `impl Trait` in traits: https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/
2. Tokio — Bridging with sync code: https://tokio.rs/tokio/topics/bridging
3. Tokio — `tokio::select!` macro docs (cancellation safety): https://docs.rs/tokio/latest/tokio/macro.select.html
4. Alice Ryhl — Async: What is blocking?: https://ryhl.io/blog/async-what-is-blocking/
5. Niko Matsakis (baby steps) — What I'd like to see for Async Rust in 2024: https://smallcultfollowing.com/babysteps/blog/2024/01/03/async-rust-2024/
6. Tokio Tutorial — Shared state: https://tokio.rs/tokio/tutorial/shared-state
7. The Rust RFC Book — 3654 Return Type Notation: https://rust-lang.github.io/rfcs/3654-return-type-notation.html
8. Tokio Tutorial — Select: https://tokio.rs/tokio/tutorial/select
9. Comprehensive Rust — Async pitfalls: Cancellation: https://google.github.io/comprehensive-rust/concurrency/async-pitfalls/cancellation.html
10. Asynchronous Programming in Rust (async-book) — Composing futures concurrently: https://rust-lang.github.io/async-book/part-guide/concurrency-primitives.html
11. Tokio Tutorial — Spawning: https://tokio.rs/tokio/tutorial/spawning
12. Tokio — Reducing tail latencies with cooperative task yielding: https://tokio.rs/blog/2020-04-preemption
13. Tokio — `spawn_blocking` docs: https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
14. Tokio — `JoinSet` docs: https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html
15. Tokio — `JoinHandle` docs: https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
16. Rust Blog — Announcing Rust 1.85.0 and Rust 2024: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/

## Verification notes

Adversarially fact-checked on 2026-06-21 against current authoritative sources (Tokio docs.rs, official Rust blog). The report is accurate and current for stable Rust ~1.85+ / Edition 2024. Claims verified true include: the `spawn_blocking` pool 512-thread default; `spawn_blocking` tasks are not abortable and shutdown waits for them; the cancel-safe vs. not-cancel-safe method sets (`recv`/`accept`/`read`/`next` safe; `read_exact`/`read_to_end`/`write_all` unsafe; `Mutex::lock`/`Semaphore::acquire` unsafe because they lose queue position); dropping a `JoinHandle` detaches the task; `JoinSet` aborts all tasks on drop; AFIT/RPITIT stable since 1.75 and not object-safe (no `dyn`); the Send-bound problem and `#[trait_variant::make]` guidance; and async closures with `AsyncFn`/`AsyncFnMut`/`AsyncFnOnce` stabilized in 1.85 / Edition 2024.

One correction:

- **`tx.reserve()` is described as "mostly cancel-safe" (section "tokio::select! pitfalls", `mpsc::Sender::send` bullet) — this is inaccurate.** Tokio's docs state `reserve` is *not* cancel-safe: "This channel uses a queue to ensure that calls to `send` and `reserve` complete in the order they were requested. Cancelling a call to `reserve` makes you lose your place in the queue." The report's *recommendation* (reserve a permit first, then call the infallible `permit.send()` once a branch is chosen) is still correct and is the idiomatic fix — but the rationale should be that losing a queue position on a cancelled `reserve` is harmless, whereas a cancelled `send` silently drops the message. The phrase "reserving *is* mostly cancel-safe" should be corrected to note that `reserve` itself is not cancel-safe; the safety comes from `permit.send()` being non-async and infallible. Source: https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html
