---
type: pattern
title: "Async Message Passing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, channels, tokio]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Shared State in Async]]", "[[Tasks and spawn]]", "[[Streams]]", "[[Cancellation Safety]]", "[[select!]]", "[[The Tokio Runtime]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html", "https://doc.rust-lang.org/book/ch17-04-streams.html", "https://doc.rust-lang.org/std/sync/mpsc/"]
rust_version: "edition 2024 / 1.85+"
---

# Async Message Passing

Async message passing moves ownership through channels so tasks coordinate without sharing mutable state directly.

## What it is
Tokio channels such as `mpsc`, `oneshot`, `watch`, and `broadcast` are common ways to connect async tasks.

Message passing is especially useful when one task should own a resource and other tasks should send it commands.

A receiver is often stream-like: it yields values over time and eventually yields `None` or an error when senders are gone.

## How it works
Bounded channels provide backpressure: `send().await` waits when the buffer is full.

Dropping all senders closes the channel from the receiver's perspective. Dropping the receiver makes future sends fail.

Because sent values move through the channel, ownership boundaries are explicit and shutdown can be modeled with normal `Drop`.

Different channel types encode different state-sharing policies. `mpsc` distributes work to one receiver, `oneshot` returns exactly one response, `watch` keeps the latest value, and `broadcast` lets each receiver observe a stream of messages.

For actor-style state, messages should be commands with reply channels when the caller needs a result. That keeps the resource owner single-threaded while callers remain fully async.

## Example
```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(8);

    tokio::spawn(async move {
        for word in ["hello", "async", "rust"] {
            tx.send(word).await.unwrap();
        }
    });

    while let Some(word) = rx.recv().await {
        println!("{word}");
    }
}
```

## Another example
```rust
use tokio::sync::{mpsc, oneshot};

enum DbCommand {
    GetUser { id: u64, reply: oneshot::Sender<Option<String>> },
}

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(16);

    tokio::spawn(async move {
        while let Some(DbCommand::GetUser { id, reply }) = rx.recv().await {
            let _ = reply.send(Some(format!("user-{id}")));
        }
    });

    let (reply_tx, reply_rx) = oneshot::channel();
    tx.send(DbCommand::GetUser { id: 7, reply: reply_tx }).await.unwrap();
    assert_eq!(reply_rx.await.unwrap(), Some("user-7".to_owned()));
}
```

## Common errors
A receiver loop that never exits usually means a sender clone is still alive:

```text
while let Some(message) = rx.recv().await {
    handle(message);
}
```

Drop unused sender clones, move senders into producer tasks with `async move`, or send an explicit shutdown command.

Using `tx.send(value)` directly in `select!` can silently drop `value` if another branch wins. Reserve capacity first and keep the value outside the branch until the permit is acquired.

## Best practice
- ✅ Prefer bounded channels unless unbounded buffering is a deliberate memory tradeoff.
- ✅ Move ownership into producer tasks with `async move`.
- ✅ Drop senders deliberately so receivers can terminate.
- ✅ Use an actor task when shared state also performs async I/O.
- ✅ Choose channel semantics deliberately: latest-value config is `watch`, not usually `mpsc`.
- ✅ Use reply `oneshot` channels for request-response commands instead of shared mutable result slots.

## Pitfalls
- ⚠️ Leaving an extra sender clone alive and wondering why the receiver loop never exits.
- ⚠️ Using `send()` directly in a [[select!]] branch when losing the race could drop the message; see [[Non-Cancellation-Safe select! Branches]].
- ⚠️ Choosing shared locks for resource ownership when a single owner task would simplify invariants.
- ⚠️ Hiding unbounded queues behind convenience APIs.
- ⚠️ Treating channel capacity as arbitrary; it is a backpressure and memory policy.
- ⚠️ Forgetting that `broadcast` receivers can lag and report skipped messages.

## See also
[[Shared State in Async]] · [[Tasks and spawn]] · [[Streams]] · [[Cancellation Safety]] · [[select!]] · [[The Tokio Runtime]] · [[Non-Cancellation-Safe select! Branches]] · [[Structured Task Sets with JoinSet]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.2 "Sending Data Between Two Tasks Using Message Passing" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html
- The Rust Programming Language, ch. 17.4 "Streams: Futures in Sequence" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-04-streams.html
- Rust standard library, `std::sync::mpsc` — https://doc.rust-lang.org/std/sync/mpsc/
