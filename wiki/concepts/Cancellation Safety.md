---
type: concept
title: "Cancellation Safety"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, cancellation, tokio]
domain: "Async Rust"
difficulty: advanced
related: ["[[Futures]]", "[[select!]]", "[[Non-Cancellation-Safe select! Branches]]", "[[Tasks and spawn]]", "[[Structured Task Sets with JoinSet]]", "[[Async Message Passing]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html", "https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://doc.rust-lang.org/std/future/trait.Future.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cancellation Safety

Cancellation safety means dropping and recreating an unfinished future does not lose data, corrupt state, or violate the operation's observable contract.

## What it is
In Rust, dropping a future is cancellation. There is no universal cancellation exception or callback.

A future is cancellation-safe when cancelling it before completion is equivalent to doing nothing and trying again later.

The issue is most visible in [[select!]], because losing branches are dropped as normal control flow.

## How it works
Cancellation drops the future's stored state. If important partial progress lives only inside that future, the progress is lost.

APIs such as `mpsc::Receiver::recv`, `TcpListener::accept`, single-buffer reads, and many stream `next` operations are designed to be safe to cancel and retry.

APIs such as `read_exact`, `read_to_end`, `write_all`, `Mutex::lock`, `Semaphore::acquire`, and `mpsc::Sender::send` can lose progress, queue position, or message ownership when cancelled.

The compiler does not infer this property for you; it is a semantic API contract.

The key distinction is where progress is stored. If progress is stored in an external object that survives cancellation, retrying can continue safely. If progress is stored only in the in-flight future, dropping that future drops the progress.

Cancellation is also not the same thing as graceful shutdown. Dropping a future runs synchronous destructors, but it cannot await cleanup work such as flushing a socket or sending a final message.

## Example
```rust
use std::time::Duration;
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(1);
    tx.send("event").await.unwrap();
    drop(tx);

    tokio::select! {
        msg = rx.recv() => println!("received {:?}", msg),
        _ = tokio::time::sleep(Duration::from_secs(1)) => println!("timeout"),
    }
}
```

## Another example
```rust
use std::time::Duration;
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(1);
    let mut message = Some("audit-record");

    tokio::select! {
        permit = tx.reserve() => {
            permit.unwrap().send(message.take().unwrap());
        }
        _ = tokio::time::sleep(Duration::from_millis(1)) => {}
    }

    if let Some(message) = message {
        assert_eq!(message, "audit-record");
    }

    drop(rx);
}
```

## Common errors
The compiler usually does not emit an error for cancellation unsafety. The program compiles and then loses messages, bytes, queue position, or protocol state under timing-dependent races.

A typical review smell is this shape:

```text
tokio::select! {
    result = writer.write_all(&bytes) => result?,
    _ = shutdown.recv() => return Ok(()),
}
```

The fix is to move the operation into a task with an explicit shutdown protocol, use a lower-level cancel-safe operation with external state, or accept that shutdown may abandon the write and document that behavior.

## Best practice
- ✅ Keep accumulators and protocol state outside futures that may be cancelled.
- ✅ Check method docs for cancellation-safety sections before using an operation in [[select!]].
- ✅ Prefer explicit shutdown signals for graceful cancellation of task trees.
- ✅ Use `JoinSet`, channels, and cancellation tokens to make cancellation policy visible.
- ✅ Decide separately for each operation whether cancellation may abandon, retry, or complete it.
- ✅ Make partially accumulated data a field in a connection/session object rather than a branch-local variable.

## Pitfalls
- ⚠️ Assuming cancellation unwinds through async code with a special error; it is just `Drop`.
- ⚠️ Putting non-cancel-safe I/O helpers in race branches; see [[Non-Cancellation-Safe select! Branches]].
- ⚠️ Relying on `abort` for cleanup that must run asynchronously.
- ⚠️ Losing queue position by cancelling fair waiters such as mutex or semaphore acquisition.
- ⚠️ Calling a helper future "timeout-safe" without checking whether it owns partial buffers internally.
- ⚠️ Assuming dropping a task reports cancellation to the code that task was communicating with.

## See also
[[Futures]] · [[select!]] · [[Non-Cancellation-Safe select! Branches]] · [[Tasks and spawn]] · [[Structured Task Sets with JoinSet]] · [[Async Message Passing]] · [[Fire-and-Forget Tokio Tasks]] · [[Streams]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.1 "Futures and the Async Syntax" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html
- The Rust Programming Language, ch. 17.3 "Working With Any Number of Futures" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-03-more-futures.html
- Tokio `select!` docs, cancellation safety — https://docs.rs/tokio/latest/tokio/macro.select.html
