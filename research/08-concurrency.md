# Concurrency — Send/Sync & Shared State

Rust's headline concurrency promise is *fearless concurrency*: the compiler statically rejects data races. This isn't marketing — it falls out of two marker traits (`Send`/`Sync`) interacting with ownership and borrowing. This report covers the semantics, the practical shared-state toolkit (`Arc<Mutex<T>>`, `RwLock`, channels, atomics), the std-vs-crate landscape (crossbeam, parking_lot), scoped threads, and deadlock avoidance — with the good practice and the mistake to avoid for each.

Targets current Rust: edition 2024, stable ~1.85+.

## Send and Sync: the foundation

Two auto traits encode thread-safety [1]:

- **`Send`**: "A type is `Send` if it is safe to send it to another thread." [1]
- **`Sync`**: "A type is `Sync` if it is safe to share between threads — `T` is `Sync` if and only if `&T` is `Send`." [1]

They are **unsafe auto traits**: unsafe to implement by hand, but *automatically derived* for any type composed entirely of `Send`/`Sync` members [1]. Almost every type you touch is both. The instructive exceptions:

- **`Rc<T>`** is neither `Send` nor `Sync` — its refcount is non-atomic and unsynchronized [1].
- **`UnsafeCell<T>`** is `!Sync`, which transitively makes `Cell` and `RefCell` `!Sync` [1].
- **Raw pointers** (`*const T`, `*mut T`) are neither, "because they have no safety guards" [1].

`thread::spawn` requires its closure (and everything captured) to be `Send + 'static` [3]. That single bound is what statically forbids, e.g., sharing an `Rc` across threads — the program *will not compile*. This is the mechanism behind data-race freedom: a data race requires two threads touching the same memory with at least one write and no synchronization, and the type system makes the unsynchronized-sharing case unrepresentable [1][5].

**Good practice:** Let auto-derivation do the work. Wrap thread-unsafe FFI handles in a newtype and only then add `unsafe impl Send`/`Sync` with a comment justifying *why* the invariant holds [1].

**Mistake to avoid:** Reaching for `unsafe impl Send for Wrapper {}` to silence a compiler error you don't understand. The compiler is reporting a real cross-thread hazard. `unsafe impl` is a *promise to the compiler*, not a workaround; "other unsafe code can assume that they are correctly implemented" [1]. Get it wrong and you have UB, not a logic bug.

```rust
struct RawHandle(*mut ffi::Thing);
// SAFETY: the C library serializes all access internally and the
// pointer is never aliased across the boundary.
unsafe impl Send for RawHandle {}
```

To opt *out* (rare), use negative impls on nightly: `impl !Send for SpecialToken {}` [1].

## Arc<Mutex<T>> — the default shared-state pattern

To share mutable state across threads you need shared *ownership* and *synchronized* access. `Arc<T>` gives the first (atomic refcount, so it's `Send + Sync` where `Rc` isn't); `Mutex<T>` gives the second. The canonical idiom is `Arc<Mutex<T>>` [3].

```rust
let counter = Arc::new(Mutex::new(0));
let c = Arc::clone(&counter);
thread::spawn(move || { *c.lock().unwrap() += 1; });
```

Note the layering: `Arc` for ownership, `Mutex` for mutation. `Mutex<T>` is `Sync` precisely *because* it serializes access — it turns an `&Mutex<T>` into safe mutable access, the runtime analogue of `RefCell` for threads.

**std `Mutex` is good now.** Since Rust 1.62, std locks on Linux/BSD/Wasm are a thin futex-based wrapper: non-allocating, `const`-constructible, and only ~5 bytes on Linux [9]. That removed the old "std `Mutex` boxes an OS mutex" drawback, so `static M: Mutex<T> = Mutex::new(..)` works without `lazy_static` [9].

**Good practice:** Keep critical sections tiny. Acquire, mutate, drop the guard. Compute expensive values *before* locking.

**Mistake to avoid:** Holding a `MutexGuard` across an `.await`, a blocking call, or a long computation. The guard serializes every other thread for that whole duration, and across `.await` it can deadlock an async runtime. Drop guards eagerly with an explicit scope or `drop(guard)`.

### Poisoning

If a thread panics while holding a std `Mutex`, the lock becomes *poisoned*: subsequent `lock()` calls return `Err(PoisonError)` [10]. This is advisory — the point is *detection*, not recovery: a panic mid-critical-section may have left data logically corrupt [10].

**Good practice:** `.lock().unwrap()` is the correct default — it propagates the "this data may be corrupt" signal. If you genuinely can recover, match and call `poisoned.into_inner()` to retrieve the guard [10]. Since Rust 1.77 you can also clear the poison bit [10].

**Mistake to avoid:** Reflexively `.into_inner()`-ing every poison error to "make the error go away." You're then operating on possibly-inconsistent state.

## RwLock — when reads dominate

`RwLock<T>` allows many concurrent readers *or* one writer. Use it only when reads vastly outnumber writes and the critical section is non-trivial — otherwise a `Mutex` is simpler and often faster (less bookkeeping).

**Mistake to avoid:** Reentrant read-locking. Acquiring a second read lock on a thread that already holds one can deadlock depending on writer-priority policy: a writer queued between the two reads may block the second read forever. Don't recursively read-lock. Also beware writer starvation under read-heavy load with reader-priority implementations.

**Good practice:** Prefer `parking_lot::RwLock` if you need predictable fairness — it uses task-fair locking that prevents reader/writer starvation and can atomically *downgrade* a write lock to a read lock [7].

## Channels — share by communicating

The other paradigm: don't share memory, pass ownership through channels. "Do not communicate by sharing memory; share memory by communicating."

- **`std::sync::mpsc`**: multi-producer, *single*-consumer [4][6].
- **`crossbeam::channel`**: multi-producer, *multi*-consumer (MPMC), plus `select!`, and lock-free internals 2–10× faster under load [4].

A key historical note: as of Rust 1.67, `std::sync::mpsc` is *itself* a thin wrapper over a vendored copy of crossbeam-channel's algorithm (a private `mpmc` module) [6]. So the raw-throughput gap narrowed dramatically; crossbeam's edge is now mostly its richer API (MPMC, `select!`, bounded/unbounded variants).

**Good practice:** Reach for std `mpsc` first (one consumer, simple fan-in). Use crossbeam when you need multiple consumers, `select!` over several channels, or scoped/lock-free patterns [4].

**Mistake to avoid:** Ignoring `send`/`recv` `Result`s. When all receivers drop, `send` returns `Err`; when all senders drop, `recv` returns `Err` [4]. Handling these is how you cleanly shut down worker threads — swallow them with `.unwrap()` and you get spurious panics or hangs. Equally, sending to a channel whose only receiver is the current thread (or vice versa) deadlocks: never recv on a channel you're the sole sender to from the same thread.

```rust
for msg in rx {            // iterates until all senders drop
    process(msg);
}                          // clean exit, no sentinel needed
```

## std vs crossbeam vs parking_lot

| Need | Reach for |
|---|---|
| Default mutex/rwlock | `std::sync` (futex-backed since 1.62 [9]) |
| Fairness, no poisoning, downgrade, deadlock detector | `parking_lot` [7] |
| MPMC channels, `select!` | `crossbeam` [4] |
| Lock-free deques, epoch GC, scoped threads (pre-1.63) | `crossbeam` |

**parking_lot** trades a few things for speed and features [7]:

- 1.5× faster uncontended, up to 5× contended; `RwLock` "up to 50× faster" in reader-heavy cases [7].
- 1-byte `Mutex`/`Once`, 1-word `Condvar`/`RwLock` [7].
- **No poisoning** — a deliberate choice; simpler API, but you lose the panic-corruption signal [7].
- Eventual fairness, no spurious `Condvar` wakeups, `ReentrantMutex`, write→read downgrade, and an opt-in deadlock detector [7].

**Good practice:** Default to std locks now — the historical performance argument for parking_lot is weaker post-1.62 [9], and one fewer dependency matters. Adopt parking_lot deliberately when you measure contention, need fairness guarantees, or want its features (downgrade, deadlock detector) [7].

**Mistake to avoid:** Cargo-culting parking_lot "because it's faster" without benchmarking your workload, and being surprised when poisoning silently disappears — code that relied on poison-as-corruption-signal now hides bugs.

## Scoped threads (std 1.63+)

`std::thread::scope` lets spawned threads **borrow non-`'static` local data**, because "the scope guarantees all threads will be joined at the end of the scope" — any unjoined thread is automatically joined before `scope` returns [2][8].

```rust
let mut a = vec![1, 2, 3];
let mut x = 0;
thread::scope(|s| {
    s.spawn(|| { dbg!(&a); });        // borrow &a — no 'static needed
    s.spawn(|| { x += a[0] + a[2]; }); // even &mut x
});
a.push(4);                            // usable again after scope
```

This replaces the old `Arc`-everything-just-to-share-read-only-data dance. Crossbeam's `scope` is now soft-deprecated in favor of the std version [2]. Historical aside: a pre-1.0 `thread::scoped` was *removed* after the "leakpocalypse" soundness hole (`mem::forget` could skip the join, causing use-after-free); the 1.63 design is leak-safe because the join is structurally guaranteed by the closure, not a guard you could forget [2].

**Good practice:** Use `thread::scope` for fork-join parallelism over borrowed data (e.g., splitting a `&mut [T]` across threads). No `Arc`, no `'static`, no clone.

**Mistake to avoid:** Using `thread::spawn` + `Arc::clone` for short-lived parallelism over stack data when scoped threads would be simpler and allocation-free.

## Atomics and memory ordering

`std::sync::atomic` types (`AtomicUsize`, `AtomicBool`, …) provide lock-free synchronization. Every operation takes an `Ordering` specifying the happens-before relationship it establishes [11][12]:

- **`Relaxed`** — weakest; no happens-before, freely reorderable. Correct for standalone counters where you only need atomicity, not ordering of *other* memory [11].
- **`Acquire`/`Release`** — paired. A `Release` store followed by an `Acquire` load of the *same* location means every write before the release is visible after the acquire. This is exactly how locks are built [11].
- **`SeqCst`** — total global order across all `SeqCst` ops; "rarely necessary for correctness," but the safe default if unsure [11].

The nomicon's guidance: it's mechanically trivial to *strengthen* later, so don't reach for `SeqCst` reflexively as a thought-terminator [11]. For the deep model — happens-before, fences, building a mutex from atomics — Mara Bos's *Rust Atomics and Locks* (free online; she was Rust libs-team lead) is the canonical reference [13].

**Good practice:** Use a plain `AtomicUsize` with `Relaxed` for a statistics counter — no lock, no ordering cost [11].

```rust
COUNT.fetch_add(1, Ordering::Relaxed); // pure counter, ordering irrelevant
```

**Mistake to avoid:** Using `Relaxed` to publish data behind a flag. `data = 42; ready.store(true, Relaxed);` does **not** guarantee another thread sees `data == 42` when it observes `ready`. You need `Release`/`Acquire` to establish the happens-before edge [11]. Conversely, defaulting everything to `SeqCst` "to be safe" leaves performance on the table on weakly-ordered hardware (ARM).

## Deadlock avoidance

Rust prevents *data races*, **not deadlocks** — a deadlock is a logic bug the type system can't catch. The classic cause is lock-order reversal: thread A takes lock 1 then 2, thread B takes 2 then 1 [14].

**Good practice — global lock ordering:** Whenever you must hold more than one lock, always acquire them in the *same* order everywhere. A robust formalization: assign each lock a numeric "level" and only ever acquire a lock with a higher level than any currently held [14].

**Good practice — single lock for coupled data:** Put data that must stay mutually consistent under *one* lock rather than several, eliminating the multi-lock problem entirely [14].

**Mistakes to avoid:**

- **Invoking a closure or callback while holding a lock** — you're "at the mercy of whatever closure gets added in the future," which might try to re-acquire the same lock [14].
- **Returning a `MutexGuard` from a function** — "like handing out a loaded gun, from a deadlock perspective"; the caller now controls lock lifetime invisibly [14].
- **Holding a lock across `.await`** in async code — combine with another task's lock and you deadlock the executor.

**Tooling:** Wire deadlock detection into CI — `parking_lot`'s deadlock feature, ThreadSanitizer, or `tracing_mutex`, which tracks the per-thread lock stack and flags cycles in the acquisition graph [14].

## Summary cheat-sheet

- Share mutable state: `Arc<Mutex<T>>`; `.lock().unwrap()` and keep the section short.
- Read-heavy: `RwLock` (prefer `parking_lot` for fairness/downgrade).
- Pass ownership: `mpsc` (1 consumer) or `crossbeam` (MPMC + `select!`).
- Borrow stack data across threads: `thread::scope` (1.63+).
- Counters/flags: atomics — `Relaxed` for counters, `Acquire`/`Release` to publish.
- Multiple locks: one global order, or merge under one lock; never lock across `.await` or callbacks.
- Trust the compiler on `Send`/`Sync`; `unsafe impl` only with a written safety argument.

## Sources

1. The Rustonomicon — Send and Sync: https://doc.rust-lang.org/nomicon/send-and-sync.html
2. std::thread::scope (function docs): https://doc.rust-lang.org/std/thread/fn.scope.html
3. The Rust Book — Shared-State Concurrency / Extensible Concurrency with Send and Sync: https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html
4. crossbeam::channel docs: https://docs.rs/crossbeam/latest/crossbeam/channel/index.html
5. RFC 3151 — Scoped threads: https://rust-lang.github.io/rfcs/3151-scoped-threads.html
6. PR #93563 — Merge crossbeam-channel into std::sync::mpsc: https://github.com/rust-lang/rust/pull/93563
7. parking_lot README (Amanieu): https://github.com/Amanieu/parking_lot/blob/master/README.md
8. Tracking issue #93203 — Scoped threads: https://github.com/rust-lang/rust/issues/93203
9. Announcing Rust 1.62.0 (futex-based std locks): https://blog.rust-lang.org/2022/06/30/Rust-1.62.0/
10. std::sync::Mutex docs (poisoning, PoisonError, into_inner): https://doc.rust-lang.org/std/sync/struct.Mutex.html
11. The Rustonomicon — Atomics: https://doc.rust-lang.org/nomicon/atomics.html
12. std::sync::atomic::Ordering docs: https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html
13. Mara Bos — Rust Atomics and Locks (free online): https://marabos.nl/atomics/
14. Effective Rust, Item 17 — Be wary of shared-state parallelism (deadlock): https://www.lurklurk.org/effective-rust/deadlock.html

## Verification notes

Adversarially fact-checked 2026-06-21 against current stable Rust (edition 2024, ~1.85+). The report is accurate and current; nearly every claim was confirmed against its cited source. One minor version slip and a few notes:

- **Line 47 — `const`-constructible attributed to Rust 1.62 (citation [9]).** Slightly conflated. Rust 1.62 brought the futex-based, non-allocating, ~5-byte std lock implementation on Linux/BSD/Wasm (the [9] blog post confirms the futex/size/no-allocation claims but does *not* mention const construction). `Mutex::new` (and `RwLock::new`) became a `const fn` one release later, in **Rust 1.63** — which is exactly what enables `static M: Mutex<T> = Mutex::new(..)` without `lazy_static`. The const-ness was only possible *because* the 1.62 rewrite removed the need to pin an OS mutex at a fixed address, so the two are causally linked, but the milestone is 1.63, not 1.62. The body text grouping it under 1.62/[9] should read 1.63. Sources: https://blog.rust-lang.org/2022/06/30/Rust-1.62.0/ and the std docs stability line "1.0.0 (const: 1.63.0)" at https://doc.rust-lang.org/std/sync/struct.Mutex.html

- **Confirmed correct:** Send/Sync as unsafe auto traits, `Rc`/`UnsafeCell`/raw-pointer exceptions, and the "other unsafe code can assume they are correctly implemented" wording — all verbatim-accurate per https://doc.rust-lang.org/nomicon/send-and-sync.html . Negative impls (`impl !Send`) remain nightly-only (require `#![feature(negative_impls)]`), as the report states (line 33).

- **Confirmed correct:** Poisoning, `PoisonError::into_inner`, and `clear_poison` since **Rust 1.77** (line 57) — verified at https://doc.rust-lang.org/std/sync/struct.Mutex.html .

- **Confirmed correct:** `std::sync::mpsc` rewritten in **Rust 1.67** as a thin wrapper over a vendored crossbeam-channel algorithm in a private `mpmc` module (lines 76, [6]) — verified via PR #93563. https://github.com/rust-lang/rust/pull/93563

- **Confirmed correct:** `thread::scope` stable since **Rust 1.63**, borrows non-`'static` data, auto-joins all threads before returning (lines 108–110) — verified at https://doc.rust-lang.org/std/thread/fn.scope.html .

- **Confirmed correct:** parking_lot figures (1.5× uncontended, up to 5× contended, RwLock up to 50× reader-heavy), 1-byte Mutex, no poisoning, ReentrantMutex, write→read downgrade, eventual fairness, experimental deadlock detector (lines 97–104, [7]) — verified at https://github.com/Amanieu/parking_lot/blob/master/README.md .

No outdated, incorrect, or materially uncited claims beyond the single 1.62-vs-1.63 const-construction slip noted above.
