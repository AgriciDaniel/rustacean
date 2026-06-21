---
type: concept
title: "async and await"
aliases: ["Async and Await"]
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, await]
domain: "Async Rust"
difficulty: basic
related: ["[[Futures]]", "[[The Tokio Runtime]]", "[[Tasks and spawn]]", "[[Cancellation Safety]]", "[[Pinning]]", "[[Async Traits]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html", "https://doc.rust-lang.org/std/keyword.async.html", "https://doc.rust-lang.org/std/keyword.await.html"]
rust_version: "edition 2024 / 1.85+"
---

# async and await

`async` turns a block, function, or closure into a future, and `.await` suspends that future until another future is ready.

## What it is
`async fn` is syntax for a function that returns an anonymous `impl Future<Output = T>`.

`.await` is postfix in Rust: it follows the future expression, which lets method chains read naturally.

Inside an async body, each `.await` is a possible suspension point where the runtime may switch to other work.

## How it works
The compiler lowers an async body into a state machine. Values needed after an `.await` are stored in that state machine.

An async function does no work when called. It captures its arguments into a future, and the body runs when that future is polled.

The special program entry point cannot simply be `async fn main` by itself; a runtime macro such as `#[tokio::main]` rewrites it into a synchronous `main` that starts a runtime.

Async closures are stable in Rust 1.85 / Edition 2024, but the same state-machine and capture rules still apply.

`.await` first converts the operand with `IntoFuture`, pins the temporary future, and polls it with the current task context. If the poll returns `Pending`, the surrounding async state machine stores its live locals and yields.

Because suspension is explicit, code between two awaits is ordinary synchronous Rust. It can move values, run destructors, hold locks, or block the thread just like non-async code.

## Example
```rust
async fn add_one(n: u32) -> u32 {
    n + 1
}

fn main() {
    let computation = async {
        let a = add_one(1).await;
        let b = add_one(a).await;
        b
    };

    std::mem::drop(computation);
}
```

## Another example
```rust
async fn load_config() -> String {
    "host=localhost".to_owned()
}

#[tokio::main]
async fn main() {
    let config = load_config().await;

    let task = tokio::spawn(async move {
        config.to_uppercase()
    });

    assert_eq!(task.await.unwrap(), "HOST=LOCALHOST");
}
```

## Common errors
Using `.await` outside an async context produces `E0728`:

```text
error[E0728]: `await` is only allowed inside `async` functions and blocks
```

Move the code into an `async fn`, an `async` block passed to a runtime, or a spawned task.

Writing a bare `async fn main()` still produces `E0752` unless a runtime macro rewrites it:

```text
error[E0752]: `main` function is not allowed to be `async`
```

Use `#[tokio::main]`, another runtime's entry macro, or a manually constructed runtime with `block_on`.

## Best practice
- ✅ Put `.await` only where suspension is acceptable and invariants are not half-updated.
- ✅ Prefer `async move` when spawning or when the future must own captured values.
- ✅ Keep synchronous setup before the first `.await` small; long setup still blocks the current task.
- ✅ Make return types explicit at the public API boundary when `impl Future` inference would obscure important bounds.
- ✅ Use `async move` when the future must outlive the current stack frame, especially with `tokio::spawn`.
- ✅ Treat each `.await` as a place where cancellation, interleaving, and destructor timing may matter.

## Pitfalls
- ⚠️ Treating `.await` like a blocking wait; it yields to the executor rather than blocking the OS thread.
- ⚠️ Holding locks or borrowed state across `.await`; see [[Holding Locks Across Await]].
- ⚠️ Assuming `async fn` in public traits solves every async trait problem; see [[Async Traits]].
- ⚠️ Forgetting that dropped futures are cancelled; see [[Cancellation Safety]].
- ⚠️ Doing expensive validation before the first `.await` in a request handler and accidentally starving peer tasks.
- ⚠️ Borrowing local data into a future that is later spawned; spawned futures generally need owned data.

## See also
[[Futures]] · [[The Tokio Runtime]] · [[Tasks and spawn]] · [[Async Traits]] · [[Cancellation Safety]] · [[Scoping Non-Send Values Before Await]] · [[Blocking the Async Executor]] · [[Pinning]] · [[select!]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.1 "Futures and the Async Syntax" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html
- Rust standard library, `async` keyword — https://doc.rust-lang.org/std/keyword.async.html
- Rust standard library, `await` keyword — https://doc.rust-lang.org/std/keyword.await.html
