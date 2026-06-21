---
type: antipattern
title: "Non-Cancellation-Safe select! Branches"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, cancellation, select]
domain: "Async Rust"
difficulty: advanced
related: ["[[select!]]", "[[Cancellation Safety]]", "[[Async Message Passing]]", "[[Pinning]]", "[[Futures]]", "[[Tasks and spawn]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://doc.rust-lang.org/std/future/trait.Future.html", "https://doc.rust-lang.org/std/pin/"]
rust_version: "edition 2024 / 1.85+"
---

# Non-Cancellation-Safe select! Branches

A non-cancellation-safe `select!` branch can lose partially completed work because Tokio drops every losing branch future.

## The mistake
The mistake is racing an operation whose future owns important partial state: exact reads, write-all loops, channel sends, lock acquisition, or semaphore acquisition.

If another branch wins, the losing future is dropped. Any state that lived only inside it is gone.

This is silent because cancellation is normal `Drop`, not a compile-time error.

## Why it happens
`select!` is designed to pick one completed branch. Dropping the rest is how the macro stops waiting on them.

Some operations are built so cancellation is a no-op. Others consume a message, buffer bytes, or queue for fairness while waiting.

For `mpsc::Sender::send`, cancellation can drop the message. Reserving a permit first can still lose queue position if cancelled, but the message remains in caller-owned state until `permit.send(value)` is called.

Exact I/O helpers are risky for the same reason. A helper such as `read_exact` may have already copied some bytes into a caller buffer or internal state before another branch wins; retrying blindly may duplicate protocol work or leave the framing code confused.

Fair waiters such as mutexes and semaphores are different: cancellation usually loses queue position rather than data. That can still matter for latency and fairness, especially in loops that repeatedly cancel and re-enter the queue.

## Example
```rust
use std::time::Duration;
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(1);
    let mut message = Some("important");

    tokio::select! {
        permit = tx.reserve() => {
            permit.unwrap().send(message.take().unwrap());
        }
        _ = tokio::time::sleep(Duration::from_millis(1)) => {}
    }

    if let Some(message) = message {
        println!("not sent yet: {message}");
    }

    drop(tx);
    while let Some(message) = rx.recv().await {
        println!("sent: {message}");
    }
}
```

## Another example
```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(1);
    let permit = tx.reserve().await.unwrap();
    permit.send("durable until sent");

    tokio::select! {
        msg = rx.recv() => assert_eq!(msg, Some("durable until sent")),
        _ = tokio::task::yield_now() => {}
    }
}
```

## Common errors
There is usually no compiler diagnostic. The bug is a race: tests pass until a timeout, shutdown signal, or faster branch wins at the wrong moment.

A typical bad branch is:

```text
tokio::select! {
    _ = tx.send(message) => {}
    _ = shutdown.recv() => {}
}
```

If `shutdown` wins, `message` was moved into the send future and can be dropped. Keep it in `Option<T>`, acquire capacity first, and only move it into `permit.send(value)` after the branch wins.

## Best practice
- ✅ Put only documented cancellation-safe futures directly in racing branches.
- ✅ Keep important data outside the branch future until the branch wins.
- ✅ Pin and reuse long-running futures when progress must survive loop iterations.
- ✅ Treat "losing branch is dropped" as the first design constraint of [[select!]].
- ✅ Separate "wait until ready" from "commit the data" when the API provides permits or reservations.
- ✅ Write tests with forced timeouts and shutdown races for protocol code that uses `select!`.

## Pitfalls
- ⚠️ Using `tx.send(value)` directly in a `select!` branch and losing `value` when another branch wins.
- ⚠️ Racing `read_exact`, `read_to_end`, or `write_all` without external buffers and retry logic.
- ⚠️ Assuming `reserve()` is fully cancellation-safe; cancelling it can lose queue position, but it need not lose the message.
- ⚠️ Hiding cancellation-unsafe work inside a helper future whose name looks harmless.
- ⚠️ Retrying exact reads after cancellation without knowing how much progress the first attempt made.
- ⚠️ Putting lock or semaphore acquisition in a looped race and accidentally starving yourself by losing queue position.

## See also
[[select!]] · [[Cancellation Safety]] · [[Async Message Passing]] · [[Pinning]] · [[Futures]] · [[Tasks and spawn]] · [[Structured Task Sets with JoinSet]] · [[Streams]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.3 "Working With Any Number of Futures" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-03-more-futures.html
- Rust standard library, `Future` — https://doc.rust-lang.org/std/future/trait.Future.html
- Tokio `select!` docs — https://docs.rs/tokio/latest/tokio/macro.select.html
- Tokio `mpsc::Sender` docs — https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html
