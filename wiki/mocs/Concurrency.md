---
type: moc
title: "Concurrency"
aliases: ["concurrency"]
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, moc]
domain: "Concurrency"
---

# Concurrency

Concurrency in Rust is built from ownership, borrowing, and thread-safety traits: values either move between threads, are borrowed within a guaranteed scope, or are shared through explicit synchronization.

## Concepts
- [[Threads]] — operating-system threads, `JoinHandle`, joining, and scheduling boundaries.
- [[Channels]] — message passing with `std::sync::mpsc` and ownership transfer.
- [[Shared State with Mutex]] — serialized mutable access with `Mutex<T>` and guards.
- [[Arc]] — atomic reference-counted shared ownership across threads.
- [[Send and Sync]] — marker traits that encode whether values can cross or be shared across threads.
- [[RwLock]] — many-reader or one-writer synchronization for read-heavy state.
- [[Atomics]] — lock-free primitive synchronization and memory ordering.
- [[Scoped Threads]] — borrowing local data across threads within `thread::scope`.
- [[Condvar]] — block threads until a mutex-protected predicate changes.
- [[OnceLock and LazyLock]] — one-time and first-use thread-safe initialization for shared values.
- [[Barrier]] — rendezvous a fixed group of threads at phase boundaries.
- [[thread_local!]] — per-OS-thread static storage via `LocalKey`.

## Patterns
- [[Move Closures with Threads]] — transfer captured values into spawned thread closures.
- [[Arc Mutex Shared State]] — combine shared ownership with synchronized mutation.
- [[Deadlock Avoidance]] — keep lock lifetimes short and acquire multiple locks in a stable order.
- [[Mutex Poisoning and Recovery]] — propagate poison by default and recover only after repairing invariants.

## Antipatterns
- [[Holding Locks Too Long]] — letting guards live across slow or unrelated work.
- [[Lock Order Reversal]] — taking the same locks in inconsistent orders.
- [[Unsafe Send and Sync Implementations]] — promising thread-safety manually without proving it.
- [[Ignoring Channel Disconnects]] — treating channel close errors as impossible.

## Related Existing Notes
[[Premature Arc Mutex]] · [[Holding Locks Across Await]] · [[Shared State in Async]] · [[Async Message Passing]] · [[Blocking in Async]] · [[Tasks and spawn]]

## Sources
- The Rust Programming Language, ch. 16 "Fearless Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-00-concurrency.html
- The Rust Reference, "Special types and traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html
- Standard library, `std::sync` — [[std]],
  https://doc.rust-lang.org/std/sync/index.html
