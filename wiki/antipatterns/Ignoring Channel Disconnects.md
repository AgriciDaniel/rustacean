---
type: antipattern
title: "Ignoring Channel Disconnects"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, channels, shutdown]
domain: "Concurrency"
difficulty: basic
related: ["[[Channels]]", "[[Threads]]", "[[Move Closures with Threads]]", "[[Deadlock Avoidance]]", "[[Async Message Passing]]", "[[Unwrap and Expect Overuse]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-02-message-passing.html", "https://doc.rust-lang.org/std/sync/mpsc/index.html", "https://doc.rust-lang.org/std/sync/mpsc/struct.SendError.html", "https://doc.rust-lang.org/std/sync/mpsc/struct.RecvError.html"]
rust_version: "edition 2024 / 1.85+"
---

# Ignoring Channel Disconnects

Ignoring channel disconnects means treating `send` and `recv` errors as impossible, even though they are the normal signal that the other half of the channel has shut down.

## The mistake
Channel operations return `Result` because channel endpoints can be dropped.
When every receiver is gone, `send` fails and returns the unsent value.
When every sender is gone, `recv` fails because no future message can arrive.

Blind `.unwrap()` is acceptable in tiny examples where panic is the desired test failure.
In production worker code, it often turns graceful shutdown into a panic or turns a missing drop into a hang.

## Why it happens
Examples focus on the happy path and often use `unwrap` to keep attention on message passing.
Real systems need shutdown behavior.
A channel closing is not automatically a bug; it may mean the consumer finished, the producer stopped, or the system is intentionally draining work.

Receiver iteration is the simplest robust shape.
It keeps receiving until all senders are dropped, then exits the loop.
On the send side, match `send` if losing the receiver is an expected way to stop.
`SendError<T>` returns the unsent message so the producer can log it, retry elsewhere, or account for dropped work.
`RecvError` carries no value because it means the stream is permanently closed.

## Example
```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    let producer = thread::spawn(move || {
        for n in 0..3 {
            if tx.send(n).is_err() {
                return;
            }
        }
    });

    for n in rx {
        println!("received {n}");
    }

    producer.join().unwrap();
}
```

## Example: recover the unsent value
```rust
use std::sync::mpsc;

fn main() {
    let (tx, rx) = mpsc::channel::<String>();
    drop(rx);

    match tx.send("shutdown".to_owned()) {
        Ok(()) => println!("sent"),
        Err(error) => {
            let message = error.0;
            println!("receiver gone before message: {message}");
        }
    }
}
```

## Common errors
The compiler cannot tell whether a disconnect is expected, because it depends on runtime ownership of channel endpoints.
The usual failures are:

```text
thread '<name>' panicked at 'called `Result::unwrap()` on an `Err` value'
```

or a receiver loop that never ends because one `Sender` clone is still alive.
The fix is to model shutdown: drop unused senders, iterate the receiver for drain-and-exit, and match `send` when consumer shutdown is normal.

## Best practice
- ✅ Treat `send` failure as "receiver is gone"; decide whether to stop, retry elsewhere, or report shutdown.
- ✅ Treat `recv` failure as "all senders are gone"; use it to terminate worker loops.
- ✅ Drop unused `Sender` clones so receiver iteration can finish.
- ✅ Use explicit sentinel messages only when the protocol needs more states than open versus closed.
- ✅ In worker pools, close the work channel before joining workers so blocking receivers can wake and exit.

## Pitfalls
- ⚠️ Keeping a `Sender` clone in the parent while waiting on `for msg in rx` prevents the loop from ending.
- ⚠️ Calling blocking `recv` before any possible sender runs can deadlock the current design.
- ⚠️ `unwrap` on `send` turns ordinary receiver shutdown into a panic.
- ⚠️ Async channels have the same conceptual issue, but use [[Async Message Passing]] patterns and runtime-aware APIs.
- ⚠️ Using a sentinel while also keeping extra senders alive can make shutdown depend on message ordering instead of endpoint ownership.

## See also
[[Concurrency]] · [[Channels]] · [[Threads]] · [[Move Closures with Threads]] · [[Deadlock Avoidance]] · [[Arc Mutex Shared State]] · [[Async Message Passing]] · [[Unwrap and Expect Overuse]] · [[Swallowing Errors]]

## Sources
- The Rust Programming Language, ch. 16.2 "Using Message Passing to Transfer Data Between Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-02-message-passing.html
- Standard library, `std::sync::mpsc` — [[std]],
  https://doc.rust-lang.org/std/sync/mpsc/index.html
- Standard library, `SendError` and `RecvError` — [[std]],
  https://doc.rust-lang.org/std/sync/mpsc/struct.SendError.html
  https://doc.rust-lang.org/std/sync/mpsc/struct.RecvError.html
