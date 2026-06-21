---
type: concept
title: "Streams"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, streams]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Futures]]", "[[async and await]]", "[[Pinning]]", "[[Async Message Passing]]", "[[Cancellation Safety]]", "[[select!]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-04-streams.html", "https://doc.rust-lang.org/book/ch17-05-traits-for-async.html", "https://doc.rust-lang.org/std/future/trait.Future.html"]
rust_version: "edition 2024 / 1.85+"
---

# Streams

A stream is an asynchronous sequence of values: it is to async code what an iterator is to synchronous code.

## What it is
Where `Future<Output = T>` produces one value, a stream produces zero or more items over time.

The common ecosystem `Stream` trait is not yet in the standard library, but crates such as `futures` and `tokio-stream` provide compatible APIs.

Most users work through `StreamExt`, especially the `.next().await` method.

## How it works
The low-level shape of a stream combines `Poll` with `Option`: `Poll::Pending` means not ready yet, `Poll::Ready(Some(item))` yields an item, and `Poll::Ready(None)` means the stream is finished.

Channels, sockets, file chunks, UI events, and timers can all be modeled as streams.

Like futures, streams are lazy and cancellation-sensitive. Dropping the future returned by `.next()` may cancel that attempt to get an item.

Most stream adapters are themselves futures or streams with internal state. For example, `filter_map` stores the upstream stream and the in-flight predicate future, so cancellation can drop whichever adapter-local state has not been yielded yet.

Because `Stream` is ecosystem-provided rather than a standard-library trait, APIs may use `futures_core::Stream`, `tokio_stream::StreamExt`, or custom receiver methods. Check which extension trait supplies the methods you are calling.

## Example
```rust
use tokio_stream::{self as stream, StreamExt};

#[tokio::main]
async fn main() {
    let mut numbers = stream::iter([1, 2, 3]);

    while let Some(n) = numbers.next().await {
        println!("{}", n * 2);
    }
}
```

## Another example
```rust
use tokio::sync::mpsc;
use tokio_stream::{wrappers::ReceiverStream, StreamExt};

#[tokio::main]
async fn main() {
    let (tx, rx) = mpsc::channel(4);
    tx.send(10).await.unwrap();
    tx.send(20).await.unwrap();
    drop(tx);

    let sum: i32 = ReceiverStream::new(rx)
        .map(|n| n / 10)
        .fold(0, |acc, n| acc + n)
        .await;

    assert_eq!(sum, 3);
}
```

## Common errors
Calling `.next().await` without importing the extension trait often produces `E0599`:

```text
error[E0599]: no method named `next` found for ...
```

Import the matching trait, commonly `use futures_util::StreamExt;` or `use tokio_stream::StreamExt;`.

Trying to iterate a stream with `for item in stream` is also wrong: `for` uses `Iterator`, not async polling. Use `while let Some(item) = stream.next().await`, or a crate-provided async iteration helper.

## Best practice
- ✅ Import the relevant `StreamExt` trait so methods like `next`, `map`, and `filter` are available.
- ✅ Use streams for unbounded or time-spaced sequences instead of collecting everything into memory.
- ✅ Consider cancellation safety when using stream operations inside [[select!]].
- ✅ Prefer bounded channels or backpressure-aware streams for producer-consumer systems.
- ✅ Convert receivers to streams when combinators make the pipeline clearer than a manual loop.
- ✅ Keep stream item types owned or cheaply cloned when they cross task boundaries.

## Pitfalls
- ⚠️ Expecting `for` loops to work directly with asynchronous streams; use `while let Some(item) = stream.next().await`.
- ⚠️ Forgetting that stream extension methods come from traits that must be in scope.
- ⚠️ Treating every stream item operation as cancellation-safe without checking docs.
- ⚠️ Boxing and pinning streams prematurely; many stream pipelines can stay concrete and generic.
- ⚠️ Forgetting to close or drop all senders, leaving stream consumers waiting forever.
- ⚠️ Building an unbounded stream pipeline whose producer can outrun every consumer.

## See also
[[Futures]] · [[async and await]] · [[Pinning]] · [[Async Message Passing]] · [[Cancellation Safety]] · [[select!]] · [[The Tokio Runtime]] · [[Non-Cancellation-Safe select! Branches]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.4 "Streams: Futures in Sequence" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-04-streams.html
- The Rust Programming Language, ch. 17.5 "The Stream Trait" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-05-traits-for-async.html
- Rust standard library, `Future` — https://doc.rust-lang.org/std/future/trait.Future.html
