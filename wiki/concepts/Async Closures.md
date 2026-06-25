---
type: concept
title: "Async Closures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, closures, futures]
domain: "Async Rust"
difficulty: intermediate
related: ["[[async and await]]", "[[Futures]]", "[[Async Traits]]", "[[Borrowing]]", "[[Lifetimes]]", "[[Tasks and spawn]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/", "https://doc.rust-lang.org/std/ops/trait.AsyncFn.html", "https://rust-lang.github.io/rfcs/3668-async-closures.html", "https://tokio.rs/tokio/tutorial/async"]
rust_version: "edition 2024 / 1.85+"
---

# Async Closures

Async closures are closure literals written `async |args| { ... }` or `async || { ... }` that return a future when called and can borrow from their captures while that future runs.

## What it is
Rust 1.85 stabilized async closures as part of the Rust 2024 work.

They fill the gap between `async fn` and ordinary closures: an async function can be generic over arguments, and a closure can capture local state, but pre-1.85 callback APIs often had to accept a closure returning an `async` block.

The old shape was usually `|x| async move { ... }`.

The new shape is `async |x| { ... }`.

That looks small, but the type model is different.

An async closure is not merely a closure whose output is an unrelated future.
The future returned from an async closure may borrow from the closure's own captured environment.

That borrowing behavior is why async closures come with async-aware callable traits: `AsyncFn`, `AsyncFnMut`, and `AsyncFnOnce`.

Those traits mirror `Fn`, `FnMut`, and `FnOnce`, but their call returns a future that the caller awaits.
In bounds, the idiomatic user-facing spelling is `async Fn`, `async FnMut`, or `async FnOnce`.

## How it works
Calling an async closure creates a future.

The closure body does not run until that future is polled, just like any other [[Futures]] value.

The closure kind depends on how it uses captures.
If the returned future only reads captures, the closure can implement `AsyncFn`.
If it mutates captures, it usually needs `AsyncFnMut`.
If it consumes captures, it needs `AsyncFnOnce`.

This matters most for callback APIs.

Use `AsyncFnOnce` when the callback is called once.
Use `AsyncFnMut` when it is called sequentially and may mutate state.
Use `AsyncFn` when the callback can be called through `&self` and does not require unique access to captured state.

Unlike `FnMut`, an `AsyncFnMut` callback can express "the returned future borrows from the callback until it is awaited."
That is the core feature that `|x| async { ... }` could not express well.

Async closures also improve higher-ranked callback signatures, such as callbacks taking references with any lifetime.
The Rust 1.85 announcement shows this as a major motivation for adding `AsyncFn` traits.

## Example
```rust
use std::time::Duration;

async fn apply_twice<F>(mut f: F) -> Vec<String>
where
    F: AsyncFnMut(&str) -> String,
{
    let first = f("alpha").await;
    tokio::time::sleep(Duration::from_millis(1)).await;
    let second = f("beta").await;
    vec![first, second]
}

#[tokio::main]
async fn main() {
    let mut calls = 0;

    let results = apply_twice(async |name: &str| {
        calls += 1;
        tokio::task::yield_now().await;
        format!("{calls}:{name}")
    })
    .await;

    assert_eq!(results, ["1:alpha", "2:beta"]);
}
```

This example uses an `AsyncFnMut` callback because the closure mutates `calls`.
The two calls are awaited sequentially, so there is never more than one mutable borrow of the closure active at a time.

## Comparison with `|x| async move { ... }`
The older closure-returning-async-block pattern is still useful when it naturally fits the API.

It works especially well when the future owns everything it needs:

```rust
use std::future::Future;

fn make_job(name: String) -> impl Future<Output = String> {
    async move {
        tokio::task::yield_now().await;
        name.to_uppercase()
    }
}
```

But it is weaker for borrowing callbacks.
A regular closure has an ordinary `Fn*` output type, and that output is difficult to express when the future needs to borrow from the closure itself.

Async closures encode that lending relationship directly.

Prefer an async closure when the callback body needs `.await` and naturally refers to local state by borrow.

Prefer an `async fn` when there is no captured environment and the operation has a stable name.

Prefer a plain closure returning a future when you are adapting older APIs that are already written as `FnMut(...) -> Fut`.

## API design notes
For a local helper, accepting an async closure by `impl async FnMut(...) -> Output` is usually the readable form.

For public APIs, be conservative.
Async closure trait bounds are stable, but some advanced associated-type details remain harder to name than boxed futures or dedicated traits.

If callers must spawn the returned future on Tokio's multithreaded runtime, make sure the future's `Send` requirement is expressible in the API.
Native `AsyncFn*` bounds do not magically solve every `Send`-bound problem from [[Async Traits]].

When in doubt, start with the simplest local signature and only generalize after a concrete caller needs it.

## Best practice
- ✅ Use `async |arg| { ... }` when a callback needs `.await` and borrows from local state.
- ✅ Match the bound to the call pattern: `AsyncFnOnce` for one call, `AsyncFnMut` for sequential repeated calls, `AsyncFn` for shared immutable calls.
- ✅ Await the future returned by an `AsyncFnMut` callback before calling the callback again.
- ✅ Keep callback bodies small; move large workflows into named `async fn`s and call them from the closure.
- ✅ Use `async move || { ... }` when the closure must own captured values.
- ✅ Treat each call as creating a fresh future with ordinary [[Cancellation Safety]] concerns.

## Pitfalls
- ⚠️ Assuming `async |x| { ... }` implements ordinary `FnMut` in every place `|x| async { ... }` did; async closures use `AsyncFn*` for their async-aware behavior.
- ⚠️ Calling an `AsyncFnMut` callback again before awaiting the previous returned future; that can require overlapping mutable borrows.
- ⚠️ Capturing non-`Send` state and then trying to pass the resulting future to `tokio::spawn`; see [[Scoping Non-Send Values Before Await]].
- ⚠️ Hiding long-running work inside a callback passed to a combinator; it can still [[Blocking the Async Executor]] if it does CPU work without await points.
- ⚠️ Assuming async closures make async trait object dispatch automatic; `AsyncFn` itself is not dyn-compatible in the current standard library docs.
- ⚠️ Forgetting that `async move` moves captures into the closure, not necessarily into every future in a way that permits unlimited repeated calls.

## See also
[[async and await]] · [[Futures]] · [[Async Traits]] · [[Closures]] · [[Borrowing]] · [[Lifetimes]] · [[Tasks and spawn]] · [[Scoping Non-Send Values Before Await]] · [[Cancellation Safety]] · [[Async Rust]]

## Sources
- Rust Blog, "Announcing Rust 1.85.0 and Rust 2024", async closures — [[04-async-rust]],
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Rust standard library, `std::ops::AsyncFn` — https://doc.rust-lang.org/std/ops/trait.AsyncFn.html
- RFC 3668, "async closures" — https://rust-lang.github.io/rfcs/3668-async-closures.html
- Tokio tutorial, "Async in depth" — https://tokio.rs/tokio/tutorial/async
