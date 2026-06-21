---
type: antipattern
title: "Fire-and-Forget Tokio Tasks"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, tasks]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Tasks and spawn]]", "[[Structured Task Sets with JoinSet]]", "[[Cancellation Safety]]", "[[The Tokio Runtime]]", "[[Async Message Passing]]", "[[select!]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html", "https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/std/thread/struct.JoinHandle.html"]
rust_version: "edition 2024 / 1.85+"
---

# Fire-and-Forget Tokio Tasks

Fire-and-forget spawning drops a Tokio `JoinHandle`, detaching the task so its result, panic, lifetime, and cancellation policy are no longer owned by the caller.

## The mistake
The mistake is writing `tokio::spawn(async { ... });` and immediately ignoring the returned handle.

The task continues running in the background. Its output is lost, and panics are noticed only if someone awaits or otherwise observes the handle.

Detached tasks can keep sockets, channels, locks, and shutdown-sensitive resources alive longer than intended.

## Why it happens
Spawning feels like starting a thread, and some background tasks really are meant to live for the process lifetime.

Most tasks, though, belong to a request, connection, subsystem, or shutdown scope.

If the code does not encode that ownership, failure and cancellation behavior becomes accidental.

Tokio deliberately detaches a task when its `JoinHandle` is dropped. That behavior is useful for supervised background services, but accidental detachment makes it impossible for the local caller to observe completion, panic, or cancellation.

Fire-and-forget also hides backpressure. If every request spawns detached cleanup work, the request path can appear fast while memory, sockets, or queued writes pile up elsewhere.

## Example
```rust
#[tokio::main]
async fn main() {
    let mut set = tokio::task::JoinSet::new();

    set.spawn(async { "finished" });

    while let Some(result) = set.join_next().await {
        println!("{}", result.expect("task panicked"));
    }
}
```

## Another example
```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (shutdown_tx, mut shutdown_rx) = mpsc::channel::<()>(1);

    let worker = tokio::spawn(async move {
        shutdown_rx.recv().await;
        "stopped"
    });

    shutdown_tx.send(()).await.unwrap();
    assert_eq!(worker.await.unwrap(), "stopped");
}
```

## Common errors
The compiler usually accepts detached tasks. The failure is semantic: panics disappear into logs or metrics, results are dropped, and shutdown hangs because some detached task still owns a sender or socket.

Code review should flag this shape:

```text
tokio::spawn(async move {
    do_work().await;
});
```

Fix it by storing the handle, awaiting it, adding it to a `JoinSet`, or registering it with a supervisor that owns its lifetime.

## Best practice
- ✅ Await single task handles when the parent needs the result.
- ✅ Use [[Structured Task Sets with JoinSet]] for dynamic groups of related tasks.
- ✅ Store handles in a supervisor when tasks intentionally outlive their caller.
- ✅ Use explicit cancellation signals for graceful shutdown.
- ✅ Name intentionally detached tasks and route their errors to logs, metrics, or a supervisor channel.
- ✅ Tie per-request and per-connection tasks to the request or connection owner.

## Pitfalls
- ⚠️ Dropping handles for tasks that own resources or produce errors.
- ⚠️ Assuming a detached task is cancelled when the spawning function returns.
- ⚠️ Losing panic information by never awaiting the handle.
- ⚠️ Using detached tasks to hide backpressure or ordering bugs.
- ⚠️ Letting detached tasks keep channel senders alive so receivers never terminate.
- ⚠️ Assuming process shutdown gives tasks time to flush async cleanup.

## See also
[[Tasks and spawn]] · [[Structured Task Sets with JoinSet]] · [[Cancellation Safety]] · [[The Tokio Runtime]] · [[Async Message Passing]] · [[select!]] · [[spawn_blocking]] · [[Blocking the Async Executor]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.2 "Creating a New Task" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Rust standard library, `JoinHandle` — https://doc.rust-lang.org/std/thread/struct.JoinHandle.html
- Tokio `JoinHandle` docs — https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
