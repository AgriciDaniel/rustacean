---
type: concept
title: "Async Traits"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, traits]
domain: "Async Rust"
difficulty: advanced
related: ["[[async and await]]", "[[Futures]]", "[[Tasks and spawn]]", "[[Scoping Non-Send Values Before Await]]", "[[The Tokio Runtime]]", "[[Pinning]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/traits.html", "https://doc.rust-lang.org/reference/items/functions.html#async-functions", "https://doc.rust-lang.org/std/future/trait.Future.html"]
rust_version: "edition 2024 / 1.85+"
---

# Async Traits

Async traits let trait methods return futures, but native `async fn` in traits still has important public API, `Send`, and object-safety limits.

## What it is
Rust supports `async fn` in traits on stable Rust, as well as return-position `impl Trait` in traits.

An async trait method desugars conceptually to a method returning an opaque future.

This is ergonomic for static dispatch, but it does not automatically make the returned future `Send`, and such traits are not dyn-compatible in the same way object-safe synchronous traits are.

## How it works
When a generic function calls an async trait method, the concrete implementor determines the hidden future type.

For spawned Tokio tasks, the future returned by the method often needs to be `Send + 'static`. Native async trait syntax cannot always express downstream-added bounds on that hidden returned future in stable ergonomic form.

For public traits, consider whether callers need `dyn` dispatch, boxed futures, or a generated `Send` variant before choosing native syntax.

Native async trait methods are best understood as return-position `impl Future` in traits. That preserves static dispatch and avoids boxing, but the hidden concrete future type remains part of the implementor's contract.

The `async-trait` crate uses a different tradeoff: it erases the method future behind a boxed trait object. That can support `dyn` usage, but it adds allocation and dynamic dispatch unless optimized away by surrounding design.

## Example
```rust
trait Greeter {
    async fn greet(&self) -> String;
}

struct English;

impl Greeter for English {
    async fn greet(&self) -> String {
        "hello".to_owned()
    }
}

#[tokio::main]
async fn main() {
    let greeter = English;
    println!("{}", greeter.greet().await);
}
```

## Another example
```rust
use std::{future::Future, pin::Pin};

trait DynGreeter {
    fn greet(&self) -> Pin<Box<dyn Future<Output = String> + Send + '_>>;
}

struct English;

impl DynGreeter for English {
    fn greet(&self) -> Pin<Box<dyn Future<Output = String> + Send + '_>> {
        Box::pin(async { "hello".to_owned() })
    }
}

#[tokio::main]
async fn main() {
    let greeter: Box<dyn DynGreeter + Send + Sync> = Box::new(English);
    assert_eq!(greeter.greet().await, "hello");
}
```

## Common errors
Trying to put a native async trait behind `dyn` can produce `E0038`:

```text
error[E0038]: the trait `Greeter` is not dyn compatible
```

Use static dispatch, a boxed-future method signature, or a helper crate that deliberately boxes the returned futures.

Spawning a future returned by an async trait method can also fail with "future cannot be sent between threads safely" when the implementation captures `!Send` state across `.await`. The trait design must expose or guarantee the needed `Send` bound.

## Best practice
- ✅ Use native `async fn` in traits for internal, generic, statically dispatched APIs.
- ✅ Be cautious in public traits unless you can anticipate `Send`, lifetime, and dyn-dispatch needs.
- ✅ Use `trait_variant` or boxed-future patterns when callers must spawn returned futures.
- ✅ Document whether implementors may return `!Send` futures.
- ✅ Use associated types or explicit boxed futures when callers need to name bounds on the returned future.
- ✅ Keep object safety, allocation, and `Send` requirements as separate API decisions.

## Pitfalls
- ⚠️ Expecting `dyn MyAsyncTrait` to work like a synchronous object-safe trait.
- ⚠️ Publishing a native async trait and later needing to add `Send` to the hidden future without breaking users.
- ⚠️ Assuming `async-trait` and native async traits have identical allocation and dispatch behavior.
- ⚠️ Capturing non-`Send` state across `.await` in trait implementations that callers want to spawn.
- ⚠️ Publishing a trait before deciding whether it is runtime-generic, Tokio-specific, or local-task-only.
- ⚠️ Hiding borrowed outputs behind async methods without thinking through lifetimes of the returned future.

## See also
[[async and await]] · [[Futures]] · [[Tasks and spawn]] · [[Scoping Non-Send Values Before Await]] · [[The Tokio Runtime]] · [[Pinning]] · [[Streams]] · [[Cancellation Safety]] · [[Async Rust]]

## Sources
- The Rust Reference, "Traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/traits.html
- The Rust Reference, "Async functions" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/functions.html#async-functions
- Rust standard library, `Future` — https://doc.rust-lang.org/std/future/trait.Future.html
- Rust Blog, async fn and RPIT in traits — https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/
