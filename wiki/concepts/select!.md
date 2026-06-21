---
type: concept
title: "select!"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, select]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Futures]]", "[[Cancellation Safety]]", "[[Non-Cancellation-Safe select! Branches]]", "[[Pinning]]", "[[Async Message Passing]]", "[[Tasks and spawn]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://doc.rust-lang.org/std/future/trait.Future.html", "https://doc.rust-lang.org/std/pin/"]
rust_version: "edition 2024 / 1.85+"
---

# select!

`select!` races multiple async branches and runs the first branch whose future completes, cancelling the losing branch futures.

## What it is
Tokio's `select!` macro lets one task wait on several asynchronous operations at once: a channel receive, a timer, a shutdown signal, or another future.

It is a concurrency primitive, not a parallelism primitive. The branches are polled on the current task until one branch completes.

The key semantic detail is cancellation: losing branch futures are dropped.

## How it works
Each branch expression creates or references a future. Tokio polls enabled branches and evaluates the handler for the first completed one.

If `select!` appears in a loop, constructing a fresh future each iteration can discard progress. To resume a long-running future, pin it once and pass `&mut` into the macro.

Branch preconditions are evaluated before polling. They are useful, but they are not a substitute for designing race-free state transitions.

Tokio's macro randomizes branch polling order by default for fairness. Adding `biased;` makes order deterministic, but then the earlier branches can starve later ready branches if the code is not designed carefully.

The branch handler runs only for the winning branch. Values moved into losing branch futures are dropped with those futures, which is why channel sends and exact I/O helpers need special care.

## Example
```rust
use std::time::Duration;
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(1);
    tokio::spawn(async move {
        tx.send("ready").await.unwrap();
    });

    tokio::select! {
        msg = rx.recv() => println!("got {:?}", msg),
        _ = tokio::time::sleep(Duration::from_secs(1)) => println!("timed out"),
    }
}
```

## Another example
```rust
use std::time::Duration;

#[tokio::main]
async fn main() {
    let deadline = tokio::time::sleep(Duration::from_millis(50));
    tokio::pin!(deadline);

    loop {
        tokio::select! {
            _ = &mut deadline => break,
            _ = tokio::task::yield_now() => {
                // The same deadline future is reused instead of reset.
            }
        }
    }
}
```

## Common errors
Reusing a non-`Unpin` future by mutable reference without pinning commonly produces `E0277`:

```text
error[E0277]: `{async block ...}` cannot be unpinned
```

Use `tokio::pin!` for a stack-local future, or `Box::pin` when the future must be stored.

Moving a value into two different branch futures can also produce `E0382`. Keep ownership outside the branches until one branch wins, or clone only when duplication is intended and cheap.

## Best practice
- ✅ Use only cancellation-safe operations in branches, or preserve state outside the branch future.
- ✅ Pin and reuse a future when you need progress to survive loop iterations.
- ✅ Treat `select!` as a boundary where partial work may be dropped.
- ✅ Add explicit shutdown or timeout branches to make waiting behavior visible.
- ✅ Prefer simple `recv().await` or `join!` when no race is actually needed.
- ✅ Document cancellation assumptions near complex branch bodies.

## Pitfalls
- ⚠️ Putting `read_exact`, `read_to_end`, `write_all`, or `mpsc::Sender::send` directly in a racing branch; see [[Non-Cancellation-Safe select! Branches]].
- ⚠️ Recreating a sleep or operation every loop when the intended behavior is one continuous deadline.
- ⚠️ Assuming branch order or fairness unless the macro documentation promises it.
- ⚠️ Hiding important state inside a branch-local future; see [[Cancellation Safety]].
- ⚠️ Using `biased;` without putting shutdown or low-frequency branches where they can still be observed.
- ⚠️ Resetting timers by constructing `sleep(duration)` inside a loop when you intended one absolute deadline.

## See also
[[Cancellation Safety]] · [[Non-Cancellation-Safe select! Branches]] · [[Pinning]] · [[Async Message Passing]] · [[Futures]] · [[Tasks and spawn]] · [[The Tokio Runtime]] · [[Streams]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.3 "Working With Any Number of Futures" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-03-more-futures.html
- Rust standard library, `Future` — https://doc.rust-lang.org/std/future/trait.Future.html
- Tokio `select!` macro docs — https://docs.rs/tokio/latest/tokio/macro.select.html
