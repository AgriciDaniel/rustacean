---
type: concept
title: "Channels"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, channels, message-passing]
domain: "Concurrency"
difficulty: basic
related: ["[[Threads]]", "[[Move Closures with Threads]]", "[[Shared State with Mutex]]", "[[Send and Sync]]", "[[Ignoring Channel Disconnects]]", "[[Async Message Passing]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-02-message-passing.html", "https://doc.rust-lang.org/std/sync/mpsc/index.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Message Passing"]
---

# Channels

Channels move values between threads by message passing; `std::sync::mpsc` provides multi-producer, single-consumer queues whose disconnect state is reported through `Result`.

## What it is
A channel has a sending half and a receiving half.
Sending transfers ownership of a value into the channel; receiving transfers ownership out to the consumer.
This is the core concurrency style behind "share memory by communicating."

The standard library channel is `mpsc`: multiple producers may send by cloning `Sender<T>`, but there is one `Receiver<T>`.
For multiple consumers or `select!` over several channels, use a crate such as crossbeam, but the std API is the correct first tool for simple fan-in.

## How it works
`mpsc::channel()` creates an unbounded asynchronous channel.
`send` returns `Err(SendError<T>)` when the receiver is gone, giving the message back.
`recv` blocks until a message arrives or all senders are dropped; `try_recv` checks without blocking.
`sync_channel(bound)` creates a bounded channel whose `send` blocks when the buffer is full; `sync_channel(0)` is a rendezvous channel where sender and receiver meet at the same time.

Iterating over a receiver is a clean shutdown pattern.
The loop ends when every sender has been dropped, so workers can exit without a separate sentinel message.
The close condition is part of the synchronization design, not an afterthought.
The ownership transfer is real: after `send(value)` succeeds, the sender no longer owns `value`, which prevents accidental use-after-send of non-`Copy` messages.

## Example
```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    let tx2 = tx.clone();

    let first = thread::spawn(move || {
        for word in ["hello", "from"] {
            tx.send(word.to_owned()).expect("receiver is alive");
        }
    });

    let second = thread::spawn(move || {
        for word in ["another", "thread"] {
            tx2.send(word.to_owned()).expect("receiver is alive");
        }
    });

    let messages: Vec<String> = rx.into_iter().collect();
    first.join().unwrap();
    second.join().unwrap();

    println!("{messages:?}");
}
```

## Example: bounded backpressure
```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = mpsc::sync_channel::<u32>(2);

    let producer = thread::spawn(move || {
        for n in 0..5 {
            tx.send(n).expect("consumer still running");
        }
    });

    while let Ok(n) = rx.recv() {
        println!("processing {n}");
        thread::sleep(Duration::from_millis(5));
    }

    producer.join().unwrap();
}
```

## Common errors
Sending a non-`Copy` value moves it into the channel:

```text
error[E0382]: borrow of moved value: `message`
```

The fix is to log or inspect before sending, send a clone intentionally, or send a cheap identifier instead of the whole owned value.
Another common bug has no compiler error: keeping one extra `Sender` clone alive makes `for msg in rx` wait forever because the channel is still open.

## Best practice
- ✅ Use channels when one thread owns work and another thread owns the result or side effect.
- ✅ Clone `Sender<T>` for multiple producers; keep the `Receiver<T>` owned by the one consumer.
- ✅ Let dropping all senders close the channel and end receiver iteration naturally.
- ✅ Handle `send` and `recv` results as normal shutdown signals, not exceptional mysteries.
- ✅ Use `sync_channel` when producers must slow down instead of buffering unbounded work.

## Pitfalls
- ⚠️ Ignoring `send`/`recv` errors causes panics or hangs during ordinary shutdown; see [[Ignoring Channel Disconnects]].
- ⚠️ Keeping an extra `Sender` clone alive prevents receiver iteration from ending.
- ⚠️ Using a channel as hidden shared mutable state can be less clear than [[Shared State with Mutex]] for tightly coupled data.
- ⚠️ Calling blocking `recv` on a thread that must also send the only message can deadlock; see [[Deadlock Avoidance]].
- ⚠️ Assuming messages from multiple producers arrive in a global order is wrong; per-producer sequencing is not the same as system-wide ordering.

## See also
[[Concurrency]] · [[Threads]] · [[Move Closures with Threads]] · [[Shared State with Mutex]] · [[Arc Mutex Shared State]] · [[Send and Sync]] · [[Async Message Passing]] · [[Deadlock Avoidance]]

## Sources
- The Rust Programming Language, ch. 16.2 "Using Message Passing to Transfer Data Between Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-02-message-passing.html
- Standard library, `std::sync::mpsc` — [[std]],
  https://doc.rust-lang.org/std/sync/mpsc/index.html
