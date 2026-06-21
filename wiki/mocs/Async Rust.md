---
type: moc
title: "Async Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, moc]
domain: "Async Rust"
difficulty: intermediate
related: ["[[Futures]]", "[[async and await]]", "[[The Tokio Runtime]]", "[[Tasks and spawn]]", "[[Cancellation Safety]]", "[[Shared State in Async]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-00-async-await.html", "https://doc.rust-lang.org/std/future/trait.Future.html", "https://doc.rust-lang.org/std/pin/"]
rust_version: "edition 2024 / 1.85+"
---

# Async Rust

Async Rust is Rust's future-driven model for cooperative concurrency, typically executed by Tokio and shaped by cancellation, `Send`, pinning, and task-lifetime rules.

## Concepts
- [[Futures]]
- [[async and await]]
- [[The Tokio Runtime]]
- [[Tasks and spawn]]
- [[select!]]
- [[Pinning]]
- [[Streams]]
- [[Cancellation Safety]]
- [[Async Traits]]
- [[Async Closures]]
- [[Shared State in Async]]

## Patterns
- [[spawn_blocking]]
- [[Structured Task Sets with JoinSet]]
- [[Async Message Passing]]
- [[Scoping Non-Send Values Before Await]]
- [[LocalSet and Non-Send Futures]]
- [[Async Timeouts]]
- [[Cancellation-Safe I/O]]

## Antipatterns
- [[Blocking the Async Executor]]
- [[Holding Locks Across Await]]
- [[Fire-and-Forget Tokio Tasks]]
- [[Non-Cancellation-Safe select! Branches]]

## See also
[[Futures]] · [[async and await]] · [[The Tokio Runtime]] · [[Tasks and spawn]] · [[select!]] · [[Pinning]] · [[Streams]] · [[Cancellation Safety]]

## Sources
- The Rust Programming Language, ch. 17 "Fundamentals of Asynchronous Programming" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-00-async-await.html
- Rust standard library, `Future` — https://doc.rust-lang.org/std/future/trait.Future.html
- Rust standard library, `std::pin` — https://doc.rust-lang.org/std/pin/
