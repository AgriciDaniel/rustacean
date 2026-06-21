---
type: concept
title: "Shared State in Async"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, shared-state, tokio]
domain: "Async Rust"
difficulty: intermediate
related: ["[[The Tokio Runtime]]", "[[Holding Locks Across Await]]", "[[Async Message Passing]]", "[[Tasks and spawn]]", "[[Scoping Non-Send Values Before Await]]", "[[Blocking the Async Executor]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html", "https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html"]
rust_version: "edition 2024 / 1.85+"
---

# Shared State in Async

Shared state in async Rust is ordinary shared state plus suspension points, so the core discipline is to keep locks short and never hold guards across `.await` unless the API explicitly requires it.

## What it is
Async tasks often share counters, caches, connection maps, and configuration through `Arc`, mutexes, channels, or actor tasks.

`std::sync::Mutex` is acceptable inside async code for short, low-contention, non-async critical sections.

`tokio::sync::Mutex` is useful when a guard truly must be held across `.await`, but it is more expensive and easier to serialize too much work with.

## How it works
A synchronous mutex blocks the current thread while waiting for the lock. In Tokio, that can block a runtime worker.

The safe pattern is to hide the mutex behind synchronous methods. Async code calls the method, gets a plain result, drops the guard, and then awaits.

For high contention or async resources, prefer sharding, channels, or an actor that owns the mutable state.

`std::sync::Mutex` is often the right primitive for small in-memory data because locking and unlocking are fast and no await is needed. The danger is not the word "sync"; the danger is waiting too long or awaiting while the guard is live.

`tokio::sync::Mutex` queues waiters asynchronously and allows holding the guard across `.await`. That makes it useful for resources with async protocols, but it can turn one slow network call into a bottleneck for every caller of the protected resource.

## Example
```rust
use std::sync::{Arc, Mutex};

struct Counter(Mutex<u64>);

impl Counter {
    fn increment(&self) -> u64 {
        let mut guard = self.0.lock().unwrap();
        *guard += 1;
        *guard
    }
}

#[tokio::main]
async fn main() {
    let counter = Arc::new(Counter(Mutex::new(0)));
    let value = counter.increment();
    tokio::task::yield_now().await;
    println!("{value}");
}
```

## Another example
```rust
use tokio::sync::{mpsc, oneshot};

enum Command {
    Increment { reply: oneshot::Sender<u64> },
}

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(8);

    tokio::spawn(async move {
        let mut counter = 0;
        while let Some(Command::Increment { reply }) = rx.recv().await {
            counter += 1;
            let _ = reply.send(counter);
        }
    });

    let (reply_tx, reply_rx) = oneshot::channel();
    tx.send(Command::Increment { reply: reply_tx }).await.unwrap();
    assert_eq!(reply_rx.await.unwrap(), 1);
}
```

## Common errors
Holding a `std::sync::MutexGuard` across `.await` inside a spawned task commonly produces:

```text
future cannot be sent between threads safely
```

The fix is to end the guard's lexical scope before `.await`, return a copied or owned value from a sync helper, or redesign the state as an actor.

With `tokio::sync::Mutex`, the same code may compile but still be wrong: the guard remains held while the task is suspended, so unrelated callers are serialized behind the awaited operation.

## Best practice
- ✅ Keep mutex guards out of async state machines by locking inside non-async methods.
- ✅ Use `std::sync::Mutex` for short, uncontended data access.
- ✅ Use channels or actor tasks when the state owner performs async work.
- ✅ Shard hot maps or counters instead of putting all traffic behind one lock.
- ✅ Prefer immutable snapshots or copy-on-write config for read-mostly shared data.
- ✅ Keep poison handling explicit when using `std::sync::Mutex`; `unwrap` is fine only if panic means process failure.

## Pitfalls
- ⚠️ Holding a `MutexGuard` across `.await`; see [[Holding Locks Across Await]].
- ⚠️ Replacing every mutex with `tokio::sync::Mutex` to "make it async"; that can hide serialization.
- ⚠️ Blocking on high-contention synchronous locks from runtime worker threads.
- ⚠️ Sharing state when message passing would make ownership and shutdown simpler.
- ⚠️ Protecting an async client with one mutex and then awaiting every request while the guard is held.
- ⚠️ Keeping extra channel senders inside shared state and preventing receivers from observing shutdown.

## See also
[[Holding Locks Across Await]] · [[Async Message Passing]] · [[Tasks and spawn]] · [[The Tokio Runtime]] · [[Blocking the Async Executor]] · [[Scoping Non-Send Values Before Await]] · [[Cancellation Safety]] · [[Structured Task Sets with JoinSet]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.2 "Sending Data Between Two Tasks Using Message Passing" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html
- Rust standard library, `Mutex` — https://doc.rust-lang.org/std/sync/struct.Mutex.html
- Tokio tutorial, "Shared state" — https://tokio.rs/tokio/tutorial/shared-state
