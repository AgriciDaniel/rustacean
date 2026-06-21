---
type: pattern
title: "spawn_blocking"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, blocking]
domain: "Async Rust"
difficulty: intermediate
related: ["[[The Tokio Runtime]]", "[[Blocking the Async Executor]]", "[[Tasks and spawn]]", "[[Cancellation Safety]]", "[[Shared State in Async]]", "[[Futures]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html", "https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://doc.rust-lang.org/std/thread/fn.spawn.html"]
rust_version: "edition 2024 / 1.85+"
---

# spawn_blocking

`spawn_blocking` is the Tokio pattern for running short blocking or synchronous work on a dedicated blocking pool instead of on async worker threads.

## What it is
Use `tokio::task::spawn_blocking` when async code must call a synchronous API that may block: legacy file APIs, compression, parsing, database clients, or CPU work that is small and bounded.

It returns a `JoinHandle`, so the async caller awaits the result without occupying a runtime worker during the blocking operation.

This is an escape hatch, not a replacement for choosing async APIs where they exist.

## How it works
Tokio sends the closure to a separate blocking thread pool. The closure is synchronous and cannot `.await`.

The closure should own its inputs with `move`, return a normal value or `Result`, and finish in bounded time.

Once a `spawn_blocking` closure has started, aborting its handle does not stop the closure. Runtime shutdown may wait for it unless shutdown is bounded.

The blocking pool is deliberately separate from the async worker pool so a slow filesystem call or legacy client does not prevent timers, sockets, and other tasks from being polled.

This does not make the work magically cheap. Many simultaneous CPU-heavy closures can still oversubscribe the machine, and queued blocking jobs can become a latency source.

## Example
```rust
#[tokio::main]
async fn main() -> std::io::Result<()> {
    let path = "Cargo.toml".to_owned();

    let text = tokio::task::spawn_blocking(move || {
        std::fs::read_to_string(path)
    })
    .await
    .expect("blocking task panicked")?;

    println!("{} bytes", text.len());
    Ok(())
}
```

## Another example
```rust
fn parse_numbers(input: String) -> Result<Vec<u64>, std::num::ParseIntError> {
    input.split(',').map(str::parse).collect()
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let input = "1,2,3,5,8".to_owned();

    let numbers = tokio::task::spawn_blocking(move || parse_numbers(input))
        .await
        .expect("blocking parser panicked")?;

    assert_eq!(numbers, [1, 2, 3, 5, 8]);
    Ok(())
}
```

## Common errors
Trying to `.await` inside the blocking closure produces `E0728`:

```text
error[E0728]: `await` is only allowed inside `async` functions and blocks
```

Move async work outside the closure. Use the closure for the synchronous section only, then await the `JoinHandle` back in async code.

Capturing borrowed data can produce lifetime errors because the closure must be `'static`. Use `move` and pass owned data such as `String`, `PathBuf`, or `Arc<T>`.

## Best practice
- ✅ Use `spawn_blocking` around short, bounded blocking calls from async code.
- ✅ Return errors from the closure and handle both join errors and operation errors.
- ✅ Use a dedicated CPU pool such as Rayon for heavy parallel compute.
- ✅ Consider a real `std::thread::spawn` for long-lived blocking workers.
- ✅ Bound inputs and time spent in the closure so shutdown and backpressure remain predictable.
- ✅ Propagate two layers of failure: `JoinError` from the task and the operation's own `Result`.

## Pitfalls
- ⚠️ Assuming `spawn_blocking` work is cancellable after it starts.
- ⚠️ Running unbounded CPU loops on Tokio's blocking pool.
- ⚠️ Calling blocking code inline in async tasks; see [[Blocking the Async Executor]].
- ⚠️ Capturing non-owned references that cannot satisfy the closure lifetime.
- ⚠️ Using `spawn_blocking` for an infinite loop; that permanently consumes a blocking-thread slot.
- ⚠️ Assuming `abort` cancels a started blocking closure; design a cooperative stop flag if needed.

## See also
[[Blocking the Async Executor]] · [[The Tokio Runtime]] · [[Tasks and spawn]] · [[Cancellation Safety]] · [[Futures]] · [[Shared State in Async]] · [[Async Message Passing]] · [[Fire-and-Forget Tokio Tasks]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.6 "Futures, Tasks, and Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- Rust standard library, `thread::spawn` — https://doc.rust-lang.org/std/thread/fn.spawn.html
- Tokio `spawn_blocking` docs — https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
