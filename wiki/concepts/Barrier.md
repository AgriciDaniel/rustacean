---
type: concept
title: "Barrier"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, barrier, threads, synchronization]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Threads]]", "[[Scoped Threads]]", "[[Arc]]", "[[Send and Sync]]", "[[Condvar]]", "[[Deadlock Avoidance]]"]
sources: ["[[std]]", "[[the-book]]", "[[08-concurrency]]"]
source_urls: ["https://doc.rust-lang.org/std/sync/struct.Barrier.html", "https://doc.rust-lang.org/book/ch16-01-threads.html", "https://doc.rust-lang.org/std/thread/fn.scope.html"]
rust_version: "edition 2024 / 1.85+"
---

# Barrier

`Barrier` makes a fixed number of threads rendezvous at the same point before any of them continues.

## What it is
A barrier is a phase boundary for a group of threads.
Each participant calls `wait`.
The first `n - 1` callers block.
When the `n`th caller arrives, all participants are released.

Use a barrier when parallel workers must all finish setup before beginning the next phase.
It is useful for tests, simulations, staged algorithms, and benchmarks where the start of work must be coordinated.

The standard-library type is `std::sync::Barrier`.
It is `Send` and `Sync`, so it can be shared between threads through [[Arc]] or borrowed by [[Scoped Threads]].
It does not move data, protect a data invariant, or send messages.
For those jobs, use [[Channels]], [[Shared State with Mutex]], or [[Atomics]].

## How it works
`Barrier::new(n)` creates a barrier for exactly `n` participants.
Every participant that is part of the phase must call `wait`.
If fewer than `n` threads call `wait`, the callers block forever unless the process exits or panics unwind the whole setup.

`wait()` returns a `BarrierWaitResult`.
Exactly one arbitrary participant for that round sees `is_leader() == true`.
That leader result is useful for once-per-phase housekeeping, such as swapping buffers or collecting a summary after all workers arrive.

Barriers are reusable.
After a full group passes through one round, the same barrier can coordinate the next round.
The participant count is still fixed; it is not a dynamic "wait for all currently alive threads" primitive.

## Example
```rust
use std::sync::Barrier;
use std::thread;

fn main() {
    let workers = 4;
    let barrier = Barrier::new(workers);
    let mut results = vec![0; workers];

    thread::scope(|scope| {
        for (id, slot) in results.iter_mut().enumerate() {
            let barrier = &barrier;
            scope.spawn(move || {
                *slot = id * 10;
                barrier.wait();
                *slot += 1;
            });
        }
    });

    assert_eq!(results, vec![1, 11, 21, 31]);
}
```

## Example: one leader per phase
```rust
use std::sync::Barrier;
use std::thread;

fn main() {
    let barrier = Barrier::new(3);
    let mut leader_count = 0;

    thread::scope(|scope| {
        for _ in 0..2 {
            let barrier = &barrier;
            scope.spawn(move || {
                barrier.wait();
            });
        }

        if barrier.wait().is_leader() {
            leader_count += 1;
        }
    });

    assert!(leader_count <= 1);
}
```

## Best practice
- ✅ Make the participant count explicit and match it to the number of threads that will always reach the barrier.
- ✅ Prefer [[Scoped Threads]] when workers only need to borrow the barrier for a lexical phase.
- ✅ Use `is_leader` for exactly-once work after a phase, but keep that work short.
- ✅ Use a barrier for phase coordination, not for protecting shared mutable data.
- ✅ In tests, join or scope every worker so a stuck barrier is visible as a test failure rather than hidden background work.
- ✅ Consider [[Condvar]] when the number of waiters is dynamic or the wakeup depends on a predicate.

## Pitfalls
- ⚠️ Creating `Barrier::new(n)` with the wrong `n` can deadlock all waiters.
- ⚠️ Assuming the same thread is always leader is wrong; leadership is arbitrary for each round.
- ⚠️ Letting one worker return early before `wait` strands the remaining participants.
- ⚠️ Holding a mutex guard while waiting at a barrier can interact badly with [[Deadlock Avoidance]].
- ⚠️ Using a barrier for async tasks blocks OS threads; use async coordination for [[Tasks and spawn]].
- ⚠️ Treating a reusable barrier as a queue or channel confuses phase synchronization with [[Channels]].

## See also
[[Concurrency]] · [[Threads]] · [[Scoped Threads]] · [[Arc]] · [[Send and Sync]] · [[Condvar]] · [[Channels]] · [[Shared State with Mutex]] · [[Deadlock Avoidance]] · [[Blocking in Async]]

## Sources
- Standard library, `std::sync::Barrier` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Barrier.html
- Standard library, `std::thread::scope` — [[std]],
  https://doc.rust-lang.org/std/thread/fn.scope.html
- The Rust Programming Language, ch. 16.1 "Using Threads to Run Code Simultaneously" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-01-threads.html
