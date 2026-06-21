---
type: antipattern
title: "Holding Locks Across Await"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, locks, mutex]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Shared State in Async]]", "[[Scoping Non-Send Values Before Await]]", "[[Blocking the Async Executor]]", "[[Tasks and spawn]]", "[[Cancellation Safety]]", "[[The Tokio Runtime]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html", "https://doc.rust-lang.org/std/marker/trait.Send.html"]
rust_version: "edition 2024 / 1.85+"
---

# Holding Locks Across Await

Holding a lock guard across `.await` lets unrelated scheduling delay extend a critical section, causing deadlocks, lost throughput, or non-`Send` spawn failures.

## The mistake
The mistake is acquiring a `MutexGuard`, `RwLock` guard, or semaphore permit and then awaiting before releasing it.

With `std::sync::Mutex`, the guard may make the future `!Send`, so `tokio::spawn` rejects it.

With `tokio::sync::Mutex`, the code may compile, but it still serializes every task waiting for that guard across the awaited operation.

## Why it happens
Async state machines store local variables that are live across `.await`.

A guard live across `.await` remains held while the task is suspended, even though the task is not actively using the protected data.

This is easy to miss when the await is inside a helper call or when a guard's lifetime extends to the end of a scope.

With a synchronous mutex, the guard can also make the future `!Send`, which conflicts with `tokio::spawn` on a multithreaded runtime. With an async mutex, the guard is designed to cross awaits, but that should be a resource-protocol decision rather than the default way to protect ordinary data.

The runtime has no way to know that a suspended task is blocking a logical critical section. It will happily run other tasks that then queue behind the same lock.

## Example
```rust
use std::sync::{Arc, Mutex};

#[tokio::main]
async fn main() {
    let value = Arc::new(Mutex::new(0));

    {
        let mut guard = value.lock().unwrap();
        *guard += 1;
    }

    tokio::task::yield_now().await;
    println!("{}", *value.lock().unwrap());
}
```

## Another example
```rust
use std::sync::Mutex;

struct Cache {
    hits: Mutex<u64>,
}

impl Cache {
    fn record_hit(&self) -> u64 {
        let mut hits = self.hits.lock().unwrap();
        *hits += 1;
        *hits
    }
}

async fn serve(cache: &Cache) {
    let hits = cache.record_hit();
    tokio::task::yield_now().await;
    println!("hit {hits}");
}
```

## Common errors
With `std::sync::MutexGuard`, the compiler may report:

```text
future cannot be sent between threads safely
```

The note usually says the guard is used across an await. Put the lock in a smaller block or a non-async method.

With `tokio::sync::Mutex`, there may be no compiler error. Look for symptoms instead: requests stuck behind one slow operation, deadlocks during shutdown, or tasks awaiting a child task that needs the same lock.

## Best practice
- ✅ End the guard's lexical scope before every `.await`.
- ✅ Move lock operations into non-async methods that return plain values.
- ✅ Use message passing when the protected state needs to perform async work.
- ✅ Use `tokio::sync::Mutex` only when holding across `.await` is truly part of the resource protocol.
- ✅ Copy, clone, or `take` the small piece of data needed for async work, then release the guard.
- ✅ Keep lock acquisition and awaited I/O in separate helper functions so reviews can see the boundary.

## Pitfalls
- ⚠️ Relying on indentation while the guard actually lives until the end of the outer scope.
- ⚠️ Using an async mutex to paper over a design that should avoid locking across awaits.
- ⚠️ Waiting for a task that needs the same lock while still holding it.
- ⚠️ Losing fairness queue position when cancelling `lock().await`; see [[Cancellation Safety]].
- ⚠️ Returning a guard from a helper and then awaiting in the caller.
- ⚠️ Protecting an entire service client with a mutex when a channel-owned actor would preserve ordering better.

## See also
[[Shared State in Async]] · [[Scoping Non-Send Values Before Await]] · [[Blocking the Async Executor]] · [[Tasks and spawn]] · [[Cancellation Safety]] · [[The Tokio Runtime]] · [[Async Message Passing]] · [[Structured Task Sets with JoinSet]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.2 "Applying Concurrency with Async" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html
- Rust standard library, `Mutex` — https://doc.rust-lang.org/std/sync/struct.Mutex.html
- Tokio tutorial, "Shared state" — https://tokio.rs/tokio/tutorial/shared-state
