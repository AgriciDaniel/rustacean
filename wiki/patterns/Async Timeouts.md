---
type: pattern
title: "Async Timeouts"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, timeout, cancellation]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Cancellation Safety]]", "[[select!]]", "[[Futures]]", "[[The Tokio Runtime]]", "[[Tasks and spawn]]", "[[Blocking the Async Executor]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://docs.rs/tokio/latest/tokio/time/fn.timeout.html", "https://docs.rs/tokio/latest/tokio/time/", "https://tokio.rs/tokio/tutorial/select"]
rust_version: "edition 2024 / 1.85+"
---

# Async Timeouts

An async timeout races work against a timer and, when the timer wins, drops the unfinished future; that makes timeouts a cancellation design, not just an error branch.

## What it is
Timeouts put an upper bound on how long an async operation is allowed to wait.

In Tokio, the usual API is `tokio::time::timeout(duration, future).await`.

If the future finishes first, the result is `Ok(output)`.
If the duration elapses first, the result is `Err(Elapsed)` and the wrapped future is cancelled by being dropped.

The Book introduces the same idea by building a timeout from `select` and `sleep`: race the work future with a timer future and return whichever finishes first.

Tokio's timeout is the production helper for that pattern.

## How it works
`timeout` returns another future.

That wrapper polls the timer and the inner future.
If the timer has elapsed before the inner future completes, the wrapper returns `Elapsed` and drops the inner future.

Dropping the wrapper before it completes also cancels the timeout wrapper itself.
Tokio documents that this requires no extra cleanup, and `Timeout::into_inner` can recover the original future if you still own the wrapper.

Timeouts are cooperative.
Tokio checks the timeout before polling the future.
If the future then runs for a long time without yielding, it can exceed the wall-clock duration and still finish without an error.

That is the same underlying rule as [[Blocking the Async Executor]]: async tasks only give the scheduler control at `.await` points or explicit yields.

## Example
```rust
use std::{error::Error, time::Duration};

async fn fetch_config() -> Result<&'static str, std::io::Error> {
    tokio::time::sleep(Duration::from_millis(5)).await;
    Ok("ready")
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    match tokio::time::timeout(Duration::from_millis(50), fetch_config()).await {
        Ok(Ok(config)) => assert_eq!(config, "ready"),
        Ok(Err(err)) => return Err(err.into()),
        Err(_elapsed) => eprintln!("fetch_config timed out"),
    }

    Ok(())
}
```

The outer `Result` is the timeout result.
The inner `Result` is the operation's own result.

Keep those two layers separate in API design.
A timeout does not mean the operation returned an I/O error; it means the operation did not finish in time and was cancelled.

## Timeout versus task timeout
Timing out a future and timing out a spawned task are different.

If you wrap the original work future in `timeout`, the work future is dropped on timeout.

If you wrap a `JoinHandle` in `timeout`, the timeout drops the `JoinHandle`, not necessarily the task.
Dropping a Tokio `JoinHandle` detaches the task; it keeps running in the background.

To bound a spawned task, keep the handle and decide the policy explicitly:

```rust
use std::time::Duration;

#[tokio::main]
async fn main() {
    let mut handle = tokio::spawn(async {
        tokio::time::sleep(Duration::from_secs(60)).await;
    });

    if tokio::time::timeout(Duration::from_millis(10), &mut handle).await.is_err() {
        handle.abort();
        assert!(handle.await.unwrap_err().is_cancelled());
    }
}
```

The important details are the mutable binding, the explicit `abort`, and the final await that observes the cancellation result.

A better design is often to avoid spawning until after the timeout boundary, or use [[Structured Task Sets with JoinSet]] plus explicit cancellation policy.

## Cancellation policy
A timeout is only safe when the cancelled future is safe to abandon at that point.

For pure waiting operations, that is often fine.
For protocol operations, it can be dangerous.

`read_exact`, `read_to_end`, and `write_all` may have partially transferred bytes when cancelled.
Using a timeout around those helpers has the same risk as placing them directly in [[select!]].

Prefer lower-level cancel-safe operations with external progress state, or isolate the operation in a task that completes or reports a controlled shutdown.

Timeouts should also be placed at the right layer.
A per-read timeout is different from a whole-request deadline.
A whole-request deadline usually gives clearer user-facing behavior, while small per-operation timeouts can accidentally cancel protocol progress repeatedly.

## Best practice
- ✅ Treat timeout expiration as cancellation of the wrapped future.
- ✅ Keep operation errors and elapsed-time errors as separate `Result` layers until you intentionally map them.
- ✅ Put timeouts around the smallest operation that is safe to abandon, or around a whole request with a clear retry policy.
- ✅ For spawned work, call `abort` or send a shutdown signal explicitly; do not assume timing out a `JoinHandle` stops the task.
- ✅ Ensure long CPU loops yield or move to `spawn_blocking`/rayon; a timeout cannot preempt synchronous work.
- ✅ Test timeout paths, not only success paths.

## Pitfalls
- ⚠️ Wrapping non-cancellation-safe I/O helpers and retrying blindly; see [[Cancellation-Safe I/O]] and [[Non-Cancellation-Safe select! Branches]].
- ⚠️ Converting every timeout to `std::io::ErrorKind::TimedOut` too early and losing whether the inner operation actually failed.
- ⚠️ Creating Tokio timers outside a runtime or without enabling the time driver.
- ⚠️ Assuming elapsed time is checked continuously while the future is running; cooperative async cannot interrupt a poll that does not yield.
- ⚠️ Timing out a `JoinHandle` and accidentally detaching [[Fire-and-Forget Tokio Tasks]].
- ⚠️ Retrying timeout failures without considering idempotency.

## See also
[[Cancellation Safety]] · [[select!]] · [[Futures]] · [[The Tokio Runtime]] · [[Tasks and spawn]] · [[Cancellation-Safe I/O]] · [[Non-Cancellation-Safe select! Branches]] · [[Blocking the Async Executor]] · [[Structured Task Sets with JoinSet]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.3 "Working With Any Number of Futures" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-03-more-futures.html
- Tokio tutorial, "Select" — https://tokio.rs/tokio/tutorial/select
- Tokio docs.rs `tokio::time` — https://docs.rs/tokio/latest/tokio/time/
- Tokio docs.rs `tokio::time::timeout` — https://docs.rs/tokio/latest/tokio/time/fn.timeout.html
- `docs.rs/tokio/latest` points at the current published Tokio docs; verify the exact Tokio version against your project's `Cargo.lock`.
