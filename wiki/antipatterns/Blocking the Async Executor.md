---
type: antipattern
title: "Blocking the Async Executor"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, blocking]
domain: "Async Rust"
difficulty: intermediate
related: ["[[The Tokio Runtime]]", "[[spawn_blocking]]", "[[Tasks and spawn]]", "[[Shared State in Async]]", "[[Cancellation Safety]]", "[[async and await]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/std/thread/fn.sleep.html"]
rust_version: "edition 2024 / 1.85+"
---

# Blocking the Async Executor

Blocking the executor means doing long synchronous work on an async worker thread, preventing unrelated tasks on that worker from making progress.

## The mistake
The mistake is calling blocking APIs such as `std::thread::sleep`, blocking file or network I/O, synchronous clients, or long CPU loops inside async tasks.

Async Rust is cooperative. A task gives the runtime a chance to run something else mainly at `.await` points.

If code spends too long between awaits, it monopolizes a worker.

## Why it happens
Blocking code often looks harmless because it is hidden behind normal function calls.

In a synchronous program, blocking the current thread is expected. In Tokio, that current thread may be one of a small number of runtime workers serving many tasks.

Blocking can also deadlock if the blocked operation waits for another async task that cannot run because the worker is occupied.

The runtime cannot preempt ordinary Rust code in the middle of a loop or function call. It can only poll another task when the current task returns `Pending`, awaits a pending future, yields, or completes.

This is why `std::thread::sleep` is worse than a slow `tokio::time::sleep`: the Tokio sleep registers a timer and yields, while the thread sleep parks the worker itself.

## Example
```rust
#[tokio::main]
async fn main() {
    let data = tokio::task::spawn_blocking(|| {
        std::thread::sleep(std::time::Duration::from_millis(10));
        "done"
    })
    .await
    .expect("blocking task panicked");

    println!("{data}");
}
```

## Another example
```rust
use std::time::Duration;

#[tokio::main]
async fn main() {
    let ticker = tokio::spawn(async {
        for _ in 0..3 {
            tokio::time::sleep(Duration::from_millis(10)).await;
            println!("tick");
        }
    });

    tokio::task::spawn_blocking(|| {
        std::thread::sleep(Duration::from_millis(30));
    })
    .await
    .unwrap();

    ticker.await.unwrap();
}
```

## Common errors
The compiler often cannot detect executor blocking. This antipattern usually appears as high latency, missed heartbeats, timeout cascades, or tests that pass on a quiet machine and fail under load.

A common misleading fix is adding `tokio::task::yield_now().await` after a long blocking call. That yields only after the damage has already happened. Move the blocking call to [[spawn_blocking]] or replace it with an async API.

## Best practice
- ✅ Use async-native APIs such as `tokio::time::sleep` and Tokio I/O in async tasks.
- ✅ Wrap short blocking work with [[spawn_blocking]].
- ✅ Use dedicated CPU pools or threads for heavy parallel computation.
- ✅ Add yield points only for cooperative CPU loops that are intentionally async.
- ✅ Audit request handlers for hidden sync APIs, especially DNS, filesystem, compression, and database clients.
- ✅ Put explicit bounds around CPU loops and consider cancellation checks in long-running async tasks.

## Pitfalls
- ⚠️ Using `std::thread::sleep` instead of `tokio::time::sleep`.
- ⚠️ Running blocking filesystem or network clients directly in handlers.
- ⚠️ Assuming Tokio will detect blocking and add replacement workers automatically.
- ⚠️ Using a mutex under high contention as accidental blocking; see [[Holding Locks Across Await]].
- ⚠️ Treating a fast local filesystem call as harmless in a server path; latency tails matter under load.
- ⚠️ Running CPU-heavy parsing on every connection inside `tokio::spawn`.

## See also
[[spawn_blocking]] · [[The Tokio Runtime]] · [[Tasks and spawn]] · [[async and await]] · [[Shared State in Async]] · [[Holding Locks Across Await]] · [[Futures]] · [[Cancellation Safety]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.3 "Yielding Control to the Runtime" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-03-more-futures.html
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Rust standard library, `thread::sleep` — https://doc.rust-lang.org/std/thread/fn.sleep.html
