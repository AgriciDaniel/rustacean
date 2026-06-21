---
type: pattern
title: "Scoping Non-Send Values Before Await"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, send, tokio]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Tasks and spawn]]", "[[async and await]]", "[[Futures]]", "[[Shared State in Async]]", "[[Holding Locks Across Await]]", "[[Async Traits]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/reference/special-types-and-traits.html", "https://doc.rust-lang.org/std/marker/trait.Send.html"]
rust_version: "edition 2024 / 1.85+"
---

# Scoping Non-Send Values Before Await

Scope `!Send` values so they are dropped before `.await`; then the future can still satisfy `tokio::spawn`'s `Send` requirement.

## What it is
A future is `Send` only if all state held across suspension points is `Send`.

Common `!Send` values include `Rc`, `RefCell`, many raw pointers, and some guard types.

On Tokio's multithreaded runtime, `tokio::spawn` requires the whole future to be `Send + 'static` because the scheduler may move it between worker threads.

## How it works
The compiler stores variables that are live across `.await` in the future's state machine.

If a `!Send` value is created, used, and dropped before the next `.await`, it does not become part of the cross-await state.

A lexical block is the clearest way to force that lifetime boundary.

This is a liveness issue, not merely a type annotation issue. A variable can make a future `!Send` even if it is no longer logically needed, as long as its lifetime extends across the await point.

The same rule applies to guard types. A `std::sync::MutexGuard` live across `.await` both holds the lock and prevents a spawned future from being `Send`.

## Example
```rust
use std::rc::Rc;

async fn work() {
    let value = {
        let local = Rc::new(42);
        *local
    };

    tokio::task::yield_now().await;
    println!("{value}");
}

#[tokio::main]
async fn main() {
    tokio::spawn(work()).await.unwrap();
}
```

## Another example
```rust
use std::cell::RefCell;

async fn compute() -> u32 {
    let value = {
        let cell = RefCell::new(40);
        *cell.borrow_mut() += 2;
        *cell.borrow()
    };

    tokio::task::yield_now().await;
    value
}

#[tokio::main]
async fn main() {
    assert_eq!(tokio::spawn(compute()).await.unwrap(), 42);
}
```

## Common errors
The usual Tokio diagnostic is:

```text
future cannot be sent between threads safely
```

The note often points at an `.await` and says a value such as `Rc<T>`, `RefCell<T>`, or `MutexGuard` is used across it. Move that value into a smaller lexical block, return an owned result, or switch to `Arc`/thread-safe primitives when sharing across tasks is actually required.

Using `drop(value)` may not always shorten the future's stored state as clearly as a block. Prefer a block when the goal is to prove the value is gone before `.await`.

## Best practice
- ✅ Use inner scopes to end `!Send` lifetimes before `.await`.
- ✅ Prefer `Arc` over `Rc` when data really must cross tasks or threads.
- ✅ Keep synchronous lock guards inside non-async helper methods.
- ✅ Use `LocalSet` and `spawn_local` only when a deliberately single-threaded `!Send` design is appropriate.
- ✅ Read the compiler note that names the value held across await; that is usually the exact scope to shrink.
- ✅ Return plain owned data from pre-await setup instead of carrying helper objects forward.

## Pitfalls
- ⚠️ Holding `Rc` or `RefCell` across `.await` and then trying to `tokio::spawn` the future.
- ⚠️ Assuming `drop(value)` always convinces the compiler as clearly as a lexical scope.
- ⚠️ Capturing `&self` in a spawned future when `self` is not owned for `'static`.
- ⚠️ Letting async trait methods hide non-`Send` returned futures; see [[Async Traits]].
- ⚠️ Switching from `Rc` to `Arc` while still holding a non-`Send` borrow or guard across `.await`.
- ⚠️ Using `LocalSet` to avoid fixing accidental cross-await state in server code that should be multithreaded.

## See also
[[Tasks and spawn]] · [[async and await]] · [[Futures]] · [[Shared State in Async]] · [[Holding Locks Across Await]] · [[Async Traits]] · [[The Tokio Runtime]] · [[Cancellation Safety]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Rust standard library, `Send` — https://doc.rust-lang.org/std/marker/trait.Send.html
- The Rust Reference, "Special types and traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html
