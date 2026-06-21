---
type: antipattern
title: "Blocking in Async"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, blocking, futures, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: advanced
related: ["[[Async and Await]]", "[[Futures]]", "[[Concurrency]]", "[[Premature Arc Mutex]]", "[[Panic Unwinding and Abort]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html", "https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/std/thread/fn.sleep.html"]
rust_version: "edition 2024 / 1.85+"
---

# Blocking in Async

Blocking in async is doing long synchronous work inside a future, preventing the runtime from polling other futures until that work returns or the future reaches an `.await`.

## The mistake
An `async fn` does not make every operation inside it nonblocking. Work between `.await` points is ordinary synchronous Rust. CPU-heavy loops, blocking file or network calls, `std::thread::sleep`, and standard mutex waits can monopolize an executor thread.

The footgun is assuming that adding `async` to a function automatically makes it cooperative. Rust futures only yield when they return `Poll::Pending`, commonly through `.await` on an operation that is itself asynchronous.

## Why it happens
Rust's async model is poll-based. The executor runs a future until it cannot make progress and yields. If the future calls a blocking function, the executor thread is occupied for the duration of that call.

This is especially harmful on single-threaded runtimes and still harmful on multithreaded runtimes under load. Blocking work should be moved to a blocking thread pool, a dedicated worker thread, or replaced with an async API from the runtime in use.

An `async fn` is compiled into a state machine. Local variables that live across an `.await` become fields in that state machine. The runtime does not preempt arbitrary CPU loops; it polls futures cooperatively. If a future never awaits, it keeps control until it returns.

That also explains the lock footgun. A guard held across `.await` is stored inside the future while other tasks run. With `std::sync::Mutex`, this can make the future `!Send`; with an async mutex, it can serialize unrelated work or deadlock if the awaited operation needs the same state.

## Example
```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

async fn make_request_id() -> u64 {
    // Mistake in real async code:
    // std::thread::sleep(Duration::from_millis(50));
    42
}

fn blocking_worker() -> mpsc::Receiver<u64> {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        thread::sleep(Duration::from_millis(10));
        tx.send(42).unwrap();
    });
    rx
}

fn main() {
    let future = make_request_id();
    drop(future);

    let rx = blocking_worker();
    println!("worker returned {}", rx.recv().unwrap());
}
```

## Second example: isolate synchronous work
```rust
use std::thread;
use std::time::Duration;

fn parse_report_sync(input: String) -> usize {
    thread::sleep(Duration::from_millis(5));
    input.lines().filter(|line| !line.is_empty()).count()
}

async fn parse_report(input: String) -> usize {
    // In Tokio this should be `tokio::task::spawn_blocking(move || ...)`.
    // This standalone example keeps the blocking work out of the future body.
    let handle = thread::spawn(move || parse_report_sync(input));
    handle.join().expect("worker thread should not panic")
}

fn main() {
    let future = parse_report(String::from("a\n\nb\n"));
    drop(future);
}
```

The exact offload primitive is runtime-specific, but the design point is stable: the future should not perform long blocking work on the executor thread.

## Common errors
Non-`Send` future when spawning:

```text
error: future cannot be sent between threads safely
```

This often means an `Rc`, `RefCell`, or `std::sync::MutexGuard` lives across an `.await`. Put it in a smaller scope so it is dropped before the await, or use a local task set when `!Send` is truly required.

Starvation with no compiler error:

```text
symptom: timers, sockets, or other tasks stop making progress while one async task runs
```

Fix it by adding real asynchronous waits, chunking CPU work, or offloading blocking/CPU-heavy work to the runtime's blocking facility or a bounded worker pool.

## Best practice
- ✅ Treat each `.await` as a possible yield point and everything between awaits as synchronous work.
- ✅ Use runtime-specific async I/O, timers, and mutexes for work that must cooperate with async scheduling.
- ✅ Move CPU-bound or blocking operations to a dedicated blocking mechanism.
- ✅ Drop synchronous locks before `.await`; redesign around ownership or messages when a lock must span asynchronous work.
- ✅ Use `spawn_blocking` or an equivalent runtime API for blocking filesystem, compression, parsing, or legacy library calls.
- ✅ For sustained CPU-heavy work, prefer a bounded CPU pool such as Rayon rather than an unbounded pile of blocking tasks.

## Pitfalls
- ⚠️ `std::thread::sleep` is documented as blocking and should not be used in async functions.
- ⚠️ A loop with no `.await` can starve other futures even when it is inside `async`.
- ⚠️ Holding a `std::sync::MutexGuard` across `.await` can deadlock or make a future non-`Send`; see [[Premature Arc Mutex]].
- ⚠️ Wrapping blocking work in `async` only delays where the blocking happens.
- ⚠️ `spawn_blocking` work is not cancelled just because the async caller is dropped once the closure has started.
- ⚠️ `tokio::sync::Mutex` is not a throughput fix; it is for cases where a lock must be held across `.await`.

## See also
[[Async and Await]] · [[Futures]] · [[Concurrency]] · [[Premature Arc Mutex]] · [[Message Passing]] · [[Shared State]] · [[Panic Unwinding and Abort]] · [[Unwrap and Expect Overuse]] · [[Rc RefCell Overuse]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 17.1 "Futures and the Async Syntax" — [[the-book]], https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html
- The Rust Programming Language, ch. 17.3 "Working with Any Number of Futures" — [[the-book]], https://doc.rust-lang.org/book/ch17-03-more-futures.html
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]], https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Standard library, `std::thread::sleep` — [[the-reference]], https://doc.rust-lang.org/std/thread/fn.sleep.html
