---
type: concept
title: "Tasks and spawn"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, tasks]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Futures]]", "[[The Tokio Runtime]]", "[[Structured Task Sets with JoinSet]]", "[[Fire-and-Forget Tokio Tasks]]", "[[Scoping Non-Send Values Before Await]]", "[[Cancellation Safety]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html", "https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/std/future/trait.Future.html"]
rust_version: "edition 2024 / 1.85+"
---

# Tasks and spawn

A task is a runtime-managed unit of async execution; `tokio::spawn` schedules a future as an independent task and returns a `JoinHandle`.

## What it is
Tasks are similar to lightweight threads, but they are scheduled by the async runtime rather than directly by the operating system.

`tokio::spawn` accepts a future whose output is `Send + 'static`, schedules it, and returns a handle that can be awaited, aborted, or dropped.

Spawning creates concurrency between tasks; it does not automatically make CPU-heavy work appropriate for async workers.

## How it works
The spawned future is owned by the runtime. On a multithreaded runtime, Tokio may move it between worker threads when it is suspended.

That movement is why the spawned future must be `Send`. The `'static` bound means the task must own its data or use data that can safely live long enough; it does not mean the task leaks forever.

Awaiting a `JoinHandle` waits for task completion and yields a `Result` because tasks can panic or be cancelled.

Dropping a `JoinHandle` detaches the task in Tokio, so the task continues running and its result is lost.

`tokio::spawn` starts the task as soon as the scheduler gets a chance to poll it; it is not lazy in the same way a merely-created future is lazy. The returned handle is only the observation and control point.

Aborting a task drops its future at a suspension boundary. Destructors for already-owned synchronous values run, but async cleanup code does not run unless the task cooperatively observes a shutdown signal and performs it before returning.

## Example
```rust
#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        21 * 2
    });

    let answer = handle.await.expect("task panicked");
    assert_eq!(answer, 42);
}
```

## Another example
```rust
#[tokio::main]
async fn main() {
    let input = String::from("owned by the task");

    let handle = tokio::spawn(async move {
        input.len()
    });

    match handle.await {
        Ok(len) => assert_eq!(len, 17),
        Err(err) if err.is_cancelled() => eprintln!("task was cancelled"),
        Err(err) => std::panic::resume_unwind(err.into_panic()),
    }
}
```

## Common errors
Capturing a borrow into `tokio::spawn` often produces `E0373`:

```text
error[E0373]: async block may outlive the current function, but it borrows ...
```

Use `async move` and move owned data into the task, or keep the future in the current scope and await it without spawning.

Holding `Rc`, `RefCell`, or a non-`Send` guard across `.await` usually produces:

```text
future cannot be sent between threads safely
```

Scope the non-`Send` value before the await, switch to thread-safe types such as `Arc`, or use a `LocalSet` when the design is intentionally single-threaded.

## Best practice
- ✅ Await, abort, or group every task handle so task lifetime remains intentional.
- ✅ Use `async move` with `spawn` so the task owns the values it needs.
- ✅ Use [[Structured Task Sets with JoinSet]] for many related tasks.
- ✅ Keep CPU-heavy or blocking work out of spawned async tasks; use [[spawn_blocking]] or a dedicated thread pool.
- ✅ Treat `JoinError` as part of the API: distinguish panic, cancellation, and successful output.
- ✅ Prefer explicit shutdown channels or cancellation tokens for long-running tasks.

## Pitfalls
- ⚠️ Dropping a `JoinHandle` as fire-and-forget; see [[Fire-and-Forget Tokio Tasks]].
- ⚠️ Capturing borrowed stack data into `tokio::spawn`; spawned tasks need owned or `'static` data.
- ⚠️ Holding `Rc`, `RefCell`, or non-`Send` guards across `.await`; see [[Scoping Non-Send Values Before Await]].
- ⚠️ Treating tasks as cancellation-safe by default; aborted tasks drop their future at an `.await` boundary.
- ⚠️ Spawning just to get concurrency inside one expression when `join!` or `select!` would keep ownership clearer.
- ⚠️ Assuming `'static` means the task must run forever; it means the future cannot borrow short-lived stack data.

## See also
[[Futures]] · [[The Tokio Runtime]] · [[async and await]] · [[Structured Task Sets with JoinSet]] · [[Fire-and-Forget Tokio Tasks]] · [[Cancellation Safety]] · [[spawn_blocking]] · [[Scoping Non-Send Values Before Await]] · [[Async Message Passing]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.2 "Applying Concurrency with Async" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Tokio tutorial, "Spawning" — https://tokio.rs/tokio/tutorial/spawning
