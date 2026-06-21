---
type: pattern
title: "LocalSet and Non-Send Futures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, send, localset]
domain: "Async Rust"
difficulty: advanced
related: ["[[Tasks and spawn]]", "[[The Tokio Runtime]]", "[[Scoping Non-Send Values Before Await]]", "[[Shared State in Async]]", "[[Send and Sync]]", "[[Futures]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html", "https://docs.rs/tokio/latest/tokio/task/fn.spawn_local.html", "https://tokio.rs/tokio/tutorial/spawning"]
rust_version: "edition 2024 / 1.85+"
---

# LocalSet and Non-Send Futures

Use Tokio `LocalSet` only when a future is intentionally `!Send` and must be driven on one thread; otherwise prefer making cross-await state `Send`.

## What it is
Tokio's multithreaded scheduler may move spawned tasks between worker threads at suspension points.

That is why `tokio::spawn` requires the spawned future and its output to be `Send + 'static`.

A future becomes `!Send` when it holds `!Send` state across `.await`.
Common examples are `Rc<T>`, `RefCell<T>`, many raw-pointer wrappers, and guard values that are not safe to move to another thread.

`LocalSet` is Tokio's tool for local tasks.
It is a set of tasks guaranteed to run on the current thread, and it supports `tokio::task::spawn_local` or `LocalSet::spawn_local` for futures that do not implement `Send`.

This is not an escape hatch for accidental design problems.
It is a deliberate single-threaded execution boundary.

## How it works
A `LocalSet` is driven by a runtime, but tasks inside it are scheduled on one thread.

The usual shape is:

1. Build a current-thread runtime or use `#[tokio::main(flavor = "current_thread")]`.
2. Create `LocalSet::new()`.
3. Call `local.run_until(async { ... }).await`.
4. Inside that future, call `tokio::task::spawn_local` for `!Send` futures.

`spawn_local` panics if it is called outside a `LocalSet` or local runtime context.

`LocalSet::spawn_local` can enqueue work before the set is running; the task starts when the set is next driven.

Local tasks still have normal task boundaries.
They can be cancelled, can panic, and return `JoinHandle`s.
Dropping a local task's `JoinHandle` still detaches it, just like ordinary Tokio tasks.

Local execution does not make `Rc<RefCell<T>>` globally safe.
It only ensures the task will not be moved to another thread.
Borrowing rules, runtime interleaving, and [[Cancellation Safety]] still apply.

## Example
```rust
use std::{cell::RefCell, rc::Rc};
use tokio::task::LocalSet;

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let local = LocalSet::new();

    local
        .run_until(async {
            let state = Rc::new(RefCell::new(0_u32));
            let task_state = Rc::clone(&state);

            let handle = tokio::task::spawn_local(async move {
                *task_state.borrow_mut() += 1;
                tokio::task::yield_now().await;
                *task_state.borrow_mut() += 1;
            });

            handle.await.unwrap();
            assert_eq!(*state.borrow(), 2);
        })
        .await;
}
```

The `Rc<RefCell<_>>` is held across an `.await`, so this future is not `Send`.
That would fail with `tokio::spawn` on the multithreaded scheduler, but it is valid as a local task driven by `LocalSet`.

## When to use it
Use `LocalSet` for real single-threaded constraints:

- GUI or platform APIs that must be touched from one thread.
- Non-thread-safe FFI handles whose wrapper type is deliberately `!Send`.
- `Rc` graphs that are inherently local to a task island.
- Tests or tools where single-threaded determinism is more important than multithreaded throughput.

Do not use it as the first fix for "future cannot be sent between threads safely."

Often the better fix is [[Scoping Non-Send Values Before Await]]:
keep the `Rc`, `RefCell`, or guard inside a synchronous block that ends before the next `.await`.

If the state really is shared by independently scheduled server tasks, use `Arc`, channels, or a dedicated owner task instead of local shared mutation.

## Best practice
- ✅ Try to shrink `!Send` lifetimes before reaching for `LocalSet`.
- ✅ Use `LocalSet` when the design has a real thread-affinity or single-threaded ownership constraint.
- ✅ Prefer `#[tokio::main(flavor = "current_thread")]` in small binaries whose main async island is local by design.
- ✅ Keep local-task ownership structured with `JoinHandle`s or `JoinSet`-like supervision where possible.
- ✅ Document why the future is intentionally `!Send`; future maintainers will otherwise "fix" it by replacing `Rc` with `Arc`.
- ✅ Keep blocking work out of local tasks; use `spawn_blocking` for blocking calls even from a `LocalSet`.

## Pitfalls
- ⚠️ Calling `tokio::task::spawn_local` outside a local context; it panics instead of silently creating a local scheduler.
- ⚠️ Using `LocalSet` to hide accidental `Rc` or guard state that could have been dropped before `.await`.
- ⚠️ Assuming one-thread execution removes the need for careful `RefCell` borrow scopes; runtime interleaving can still expose borrow panics.
- ⚠️ Dropping a local `JoinHandle` and accidentally creating [[Fire-and-Forget Tokio Tasks]].
- ⚠️ Mixing local tasks with APIs that require `Send` futures, such as `tokio::spawn`.
- ⚠️ Treating `LocalSet` as a throughput optimization; it is mainly a correctness tool for `!Send` futures.

## See also
[[Tasks and spawn]] · [[The Tokio Runtime]] · [[Scoping Non-Send Values Before Await]] · [[Send and Sync]] · [[Shared State in Async]] · [[Futures]] · [[Fire-and-Forget Tokio Tasks]] · [[Blocking the Async Executor]] · [[spawn_blocking]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Tokio tutorial, "Spawning" — https://tokio.rs/tokio/tutorial/spawning
- Tokio docs.rs `LocalSet` — https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html
- Tokio docs.rs `spawn_local` — https://docs.rs/tokio/latest/tokio/task/fn.spawn_local.html
- `docs.rs/tokio/latest` points at the current published Tokio docs; verify the exact Tokio version against your project's `Cargo.lock`.
