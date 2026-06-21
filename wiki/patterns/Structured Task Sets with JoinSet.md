---
type: pattern
title: "Structured Task Sets with JoinSet"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, tasks]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Tasks and spawn]]", "[[Fire-and-Forget Tokio Tasks]]", "[[Cancellation Safety]]", "[[The Tokio Runtime]]", "[[Async Message Passing]]", "[[select!]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html", "https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/std/future/trait.Future.html"]
rust_version: "edition 2024 / 1.85+"
---

# Structured Task Sets with JoinSet

`JoinSet` groups related Tokio tasks so their results are collected and unfinished tasks are aborted when the set is dropped.

## What it is
Use `tokio::task::JoinSet` when you spawn a dynamic number of homogeneous related tasks.

It is a structured alternative to storing many loose `JoinHandle`s or dropping handles accidentally.

Each spawned task belongs to the set, and `join_next().await` yields completions as tasks finish.

## How it works
`JoinSet::spawn` schedules a task and records its handle internally.

The parent task loops on `join_next()` until the set is empty, handling panics, cancellation, and task outputs.

If the `JoinSet` is dropped with tasks still running, Tokio aborts those tasks. That gives the task group a clear owner.

All tasks in a `JoinSet` have the same output type, which keeps collection logic simple. When tasks have different outputs, wrap them in an enum or use separate sets.

`join_next()` returns completions in finish order, not spawn order. That is usually what you want for fan-out work, but callers that need stable ordering should include an index in each task's output.

## Example
```rust
#[tokio::main]
async fn main() {
    let mut set = tokio::task::JoinSet::new();

    for n in 1..=3 {
        set.spawn(async move { n * n });
    }

    let mut total = 0;
    while let Some(result) = set.join_next().await {
        total += result.expect("task panicked");
    }

    assert_eq!(total, 14);
}
```

## Another example
```rust
#[tokio::main]
async fn main() {
    let mut set = tokio::task::JoinSet::new();

    for (index, word) in ["red", "green", "blue"].into_iter().enumerate() {
        set.spawn(async move { (index, word.len()) });
    }

    let mut lengths = vec![0; 3];
    while let Some(result) = set.join_next().await {
        let (index, len) = result.expect("task panicked");
        lengths[index] = len;
    }

    assert_eq!(lengths, [3, 5, 4]);
}
```

## Common errors
Spawning a borrowed value into the set has the same lifetime failure as `tokio::spawn`, often `E0373`:

```text
error[E0373]: async block may outlive the current function, but it borrows ...
```

Use `async move` and move owned data into each task. For borrowed scoped concurrency, use APIs designed for scoped tasks instead of detached runtime tasks.

Ignoring `JoinError` loses panics and cancellations. Treat it as a real result branch, not as noise to `unwrap` in production services.

## Best practice
- ✅ Use `JoinSet` when spawned tasks share a parent scope and output type.
- ✅ Drain the set and handle `JoinError` explicitly.
- ✅ Drop the set intentionally when aborting remaining work is the desired cancellation behavior.
- ✅ Combine with explicit shutdown messages when tasks need graceful cleanup.
- ✅ Include job IDs in outputs when callers need to map finish-order results back to inputs.
- ✅ Use one set per logical parent operation so cancellation has the right scope.

## Pitfalls
- ⚠️ Assuming abort equals graceful shutdown; dropped futures cannot perform async cleanup.
- ⚠️ Using loose `tokio::spawn` calls when task lifetime should be tied to a request or subsystem.
- ⚠️ Ignoring panics returned through `JoinError`.
- ⚠️ Spawning non-`Send` futures into a multithreaded set; see [[Scoping Non-Send Values Before Await]].
- ⚠️ Assuming results come back in input order.
- ⚠️ Dropping the set at the end of a function while expecting unfinished tasks to continue.

## See also
[[Tasks and spawn]] · [[Fire-and-Forget Tokio Tasks]] · [[Cancellation Safety]] · [[The Tokio Runtime]] · [[select!]] · [[Async Message Passing]] · [[Futures]] · [[Scoping Non-Send Values Before Await]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.2 "Creating a New Task" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Tokio `JoinSet` docs — https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html
