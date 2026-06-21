---
type: concept
title: "Pinning"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, pin, unpin]
domain: "Async Rust"
difficulty: advanced
related: ["[[Futures]]", "[[async and await]]", "[[Streams]]", "[[select!]]", "[[Cancellation Safety]]", "[[Tasks and spawn]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-05-traits-for-async.html", "https://doc.rust-lang.org/std/pin/", "https://doc.rust-lang.org/std/pin/struct.Pin.html"]
rust_version: "edition 2024 / 1.85+"
---

# Pinning

Pinning is Rust's way to promise that a value behind a pointer will not move, which matters for async futures that may contain self-references.

## What it is
`Pin<Ptr>` wraps a pointer-like value and restricts safe access so the pointee cannot be moved if moving would violate its invariants.

`Unpin` is the marker trait for types that do not care about pinning. Most ordinary Rust types are `Unpin`.

Compiler-generated futures can be `!Unpin` because the async state machine may borrow from itself across `.await` points.

## How it works
`Future::poll` takes `self: Pin<&mut Self>`, so polling a future requires a pinned mutable reference.

Plain `.await` handles this pinning implicitly for ordinary local futures. Pinning becomes visible when storing heterogeneous futures, polling manually, or reusing a future by `&mut` in [[select!]].

`Box::pin(future)` pins a future on the heap and gives a stable address for the future value. Moving the `Box` pointer is fine; moving the pinned future out is not.

Pinning is a library contract enforced through safe APIs. `Pin` does not magically freeze memory at the hardware level; it prevents safe code from moving a value after that value has been pinned.

Projection is the hard part: going from `Pin<&mut Struct>` to a pinned field is only sound if moving the other fields cannot invalidate the pinned field. Use established projection helpers in real low-level code rather than writing unsafe projection casually.

## Example
```rust
use std::future::Future;
use std::pin::Pin;

fn main() {
    let future: Pin<Box<dyn Future<Output = u32>>> = Box::pin(async {
        40 + 2
    });

    std::mem::drop(future);
}
```

## Another example
```rust
use std::time::Duration;

#[tokio::main]
async fn main() {
    let timeout = tokio::time::sleep(Duration::from_millis(10));
    tokio::pin!(timeout);

    tokio::select! {
        _ = &mut timeout => println!("deadline reached"),
        _ = tokio::task::yield_now() => println!("yielded first"),
    }
}
```

## Common errors
Passing `&mut future` to an API that requires `Unpin` often fails with `E0277`:

```text
error[E0277]: `{async block ...}` cannot be unpinned
```

The fix is not to implement `Unpin` by hand for a compiler-generated future. Pin the future with `tokio::pin!` or `Box::pin`, then pass `Pin<&mut _>` or `&mut` only where the API accepts the pinned form.

Another symptom is trying to put different async blocks in one `Vec` without boxing. Each async block has a distinct anonymous type, so use a homogeneous enum, a generic function, or `Pin<Box<dyn Future<Output = T>>>`.

## Best practice
- ✅ Let `.await` handle pinning until an API forces you to think about it.
- ✅ Use `Box::pin` or runtime macros such as `tokio::pin!` when you need a stable future location.
- ✅ Prefer library combinators over manual `poll` implementations unless you are writing low-level async abstractions.
- ✅ Read `std::pin` carefully before using unsafe pin-projection code.
- ✅ Keep pinned values behind their pinning pointer; move the handle, not the pointee.
- ✅ Use concrete future types where possible; box and pin mainly at dynamic dispatch or storage boundaries.

## Pitfalls
- ⚠️ Treating `Pin<Box<T>>` as pinning the box pointer rather than the `T` value it points to.
- ⚠️ Assuming all futures are `Unpin`; async blocks often are not.
- ⚠️ Moving a future after creating references into it through unsafe code.
- ⚠️ Pinning to fix a design problem that could be avoided with simpler ownership.
- ⚠️ Confusing `Unpin` with "can never move"; it means the type has no pin-sensitive invariants.
- ⚠️ Assuming `Pin<&mut T>` lets you freely access all fields mutably; pinned projection has rules.

## See also
[[Futures]] · [[async and await]] · [[Streams]] · [[select!]] · [[Cancellation Safety]] · [[Tasks and spawn]] · [[The Tokio Runtime]] · [[Async Traits]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.5 "The Pin Type and the Unpin Trait" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-05-traits-for-async.html
- Rust standard library, `std::pin` module — https://doc.rust-lang.org/std/pin/
- Rust standard library, `Pin` — https://doc.rust-lang.org/std/pin/struct.Pin.html
