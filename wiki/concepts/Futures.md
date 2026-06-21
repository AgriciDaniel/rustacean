---
type: concept
title: "Futures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, futures]
domain: "Async Rust"
difficulty: basic
related: ["[[async and await]]", "[[The Tokio Runtime]]", "[[Tasks and spawn]]", "[[Pinning]]", "[[Cancellation Safety]]", "[[Streams]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html", "https://doc.rust-lang.org/std/future/trait.Future.html", "https://doc.rust-lang.org/reference/items/functions.html#async-functions"]
rust_version: "edition 2024 / 1.85+"
---

# Futures

A future is a value representing work that may finish later; in Rust it is lazy and only makes progress when polled by an executor or awaited by async code.

## What it is
A `Future` is Rust's core abstraction for one eventual result. It has an associated `Output` type and a `poll` method that reports either `Poll::Pending` or `Poll::Ready(output)`.

Most application code does not implement `Future` manually. It writes `async fn` and `async` blocks, and the compiler generates anonymous future types.

The important practical rule is laziness: calling an async function creates a future, but the function body does not run immediately.

## How it works
An executor owns or borrows futures and repeatedly polls them. When a future cannot continue, it returns `Pending` and arranges for its task to be woken later.

Each `.await` point gives control back to the runtime. Local variables that live across that `.await` become part of the compiler-generated state machine.

Once a future returns `Ready`, callers generally must not poll it again unless its documentation explicitly says that is allowed.

Dropping a future before it is ready cancels it, which is why future design is inseparable from [[Cancellation Safety]].

At the trait level, `poll` receives `Pin<&mut Self>` and a task `Context`. The context contains a `Waker` that lets I/O drivers, timers, or other tasks put this future back on the executor's ready queue.

That means a well-behaved future must not busy-loop by returning `Pending` without arranging a wakeup. It should either make progress immediately, register interest, or delegate to another future that does.

## Example
```rust
use std::future::Future;

async fn double(n: u32) -> u32 {
    n * 2
}

fn returns_a_future(n: u32) -> impl Future<Output = u32> {
    async move { double(n).await + 1 }
}

fn main() {
    let future = returns_a_future(20);
    std::mem::drop(future); // created, but never polled, so it never runs
}
```

## Another example
```rust
async fn make_name() -> String {
    "ferris".to_owned()
}

#[tokio::main]
async fn main() {
    let fut = make_name();
    let name = fut.await; // awaiting consumes this future
    assert_eq!(name, "ferris");

    let again = make_name().await;
    assert_eq!(again.len(), 6);
}
```

## Common errors
Awaiting a future moves it. Reusing the same future after `.await` usually produces `E0382`:

```text
error[E0382]: use of moved value: `fut`
```

The fix is to create a new future for the second operation, or pin and poll the same future only through APIs that explicitly support repeated polling before completion. Once `.await` completes, the one-shot future is done.

Another common diagnostic is the `unused implementer of Future that must be used` warning. It means an async function was called but the returned future was neither awaited, spawned, nor deliberately dropped.

## Best practice
- ✅ Treat futures as values: compose them, pass them around, and await them at the boundary where progress is required.
- ✅ Keep work between `.await` points short enough that other tasks can make progress; see [[Blocking the Async Executor]].
- ✅ Let `async fn` produce compiler-generated futures unless you are writing a low-level library or runtime.
- ✅ Read API docs for cancellation behavior before using a future inside [[select!]].
- ✅ Keep future outputs small and owned when crossing task boundaries; spawned tasks need `Send + 'static` outputs.
- ✅ Prefer explicit `tokio::spawn` or `JoinSet` when work should start independently of the current future.

## Pitfalls
- ⚠️ Assuming a future starts when you call an async function. It starts only when polled or awaited.
- ⚠️ Polling a completed future again; many futures panic after returning `Ready`.
- ⚠️ Forgetting that local state across `.await` becomes stored state, affecting `Send`, lifetimes, and cancellation.
- ⚠️ Dropping futures casually in race code; see [[Non-Cancellation-Safe select! Branches]].
- ⚠️ Returning a future that borrows a local temporary; the returned state machine cannot outlive data already dropped.
- ⚠️ Hand-writing `Future` without understanding wakeups; missed wakeups become hangs, not type errors.

## See also
[[async and await]] · [[The Tokio Runtime]] · [[Tasks and spawn]] · [[Pinning]] · [[Streams]] · [[Cancellation Safety]] · [[Blocking the Async Executor]] · [[select!]] · [[Async Traits]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.1 "Futures and the Async Syntax" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html
- Rust standard library, `std::future::Future` — https://doc.rust-lang.org/std/future/trait.Future.html
- The Rust Reference, "Async functions" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/functions.html#async-functions
