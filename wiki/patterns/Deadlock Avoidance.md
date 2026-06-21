---
type: pattern
title: "Deadlock Avoidance"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, deadlock, locks]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Shared State with Mutex]]", "[[RwLock]]", "[[Arc Mutex Shared State]]", "[[Holding Locks Too Long]]", "[[Lock Order Reversal]]", "[[Channels]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html", "https://doc.rust-lang.org/std/sync/struct.RwLock.html"]
rust_version: "edition 2024 / 1.85+"
---

# Deadlock Avoidance

Deadlock avoidance is the practice of structuring lock acquisition so threads never wait forever on each other, usually by keeping locks short and acquiring multiple locks in one global order.

## What it is
Rust prevents data races, not all concurrency logic bugs.
A deadlock can still happen when two or more threads each hold a resource and wait for another resource that will never be released.

The most common lock-based cause is lock-order reversal.
Thread A locks `left` then waits for `right`; thread B locks `right` then waits for `left`.
Both programs are memory-safe, and both are stuck.

## How it works
Deadlock prevention is mostly design discipline.
Use one lock for data that must change together.
If multiple locks are unavoidable, define a total order and acquire locks only in that order everywhere.
Do not call arbitrary callbacks while holding a lock, because the callback may take another lock or re-enter the same one.

Short critical sections reduce the surface area.
Lock only after expensive computation is done, and drop guards before I/O, blocking waits, joins, or calls into user-provided code.
`try_lock` can be useful for diagnostics, fallback paths, or avoiding a wait while holding another lock, but it is not a substitute for a coherent lock order.
If an operation truly needs two resources, centralize the acquisition code so every caller inherits the same order.

## Example
```rust
use std::sync::Mutex;

struct Account {
    id: u64,
    balance: Mutex<i64>,
}

fn transfer(from: &Account, to: &Account, amount: i64) {
    let (first, second) = if from.id <= to.id { (from, to) } else { (to, from) };

    let mut first_balance = first.balance.lock().unwrap();
    let mut second_balance = second.balance.lock().unwrap();

    if from.id == first.id {
        *first_balance -= amount;
        *second_balance += amount;
    } else {
        *second_balance -= amount;
        *first_balance += amount;
    }
}

fn main() {
    let checking = Account { id: 1, balance: Mutex::new(100) };
    let savings = Account { id: 2, balance: Mutex::new(20) };
    transfer(&checking, &savings, 10);
}
```

## Example: split a wait from a lock
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let queue = Arc::new(Mutex::new(Vec::new()));
    let worker_queue = Arc::clone(&queue);

    let worker = thread::spawn(move || {
        worker_queue.lock().unwrap().push("done");
    });

    worker.join().unwrap();

    let item = queue.lock().unwrap().pop();
    println!("{item:?}");
}
```

The important detail is the order: the parent does not hold the queue lock while waiting for the worker to finish.

## Common errors
Deadlocks usually do not produce compiler diagnostics.
The symptom is a hang: stack traces show threads parked in `Mutex::lock`, `RwLock::read`, `RwLock::write`, `JoinHandle::join`, or `Receiver::recv`.

The fix is to draw the wait graph: locks, channel receives, joins, callbacks, and condition waits all count as edges.
Then remove a cycle by using one lock, imposing a total order, dropping a guard before the wait, or replacing shared state with [[Channels]].

## Best practice
- ✅ Prefer one lock for one invariant over several locks that must be coordinated.
- ✅ Give every lock a stable ordering key if it may be acquired with another lock.
- ✅ Drop guards before callbacks, thread joins, blocking receives, and slow computation.
- ✅ Use [[Channels]] to move work between owners when shared mutable state is not necessary.
- ✅ Keep multi-lock acquisition in one small function so review can verify the order once.

## Pitfalls
- ⚠️ Acquiring locks in different orders creates [[Lock Order Reversal]].
- ⚠️ Returning lock guards from helper functions hides lock lifetime and enables [[Holding Locks Too Long]].
- ⚠️ A `RwLock` can still deadlock through reentrant read locking or mixed lock ordering.
- ⚠️ Async code has its own hazard: see existing [[Holding Locks Across Await]].
- ⚠️ Waiting on a channel or joining a thread while locked can be the same shape as waiting on another lock.

## See also
[[Concurrency]] · [[Threads]] · [[Shared State with Mutex]] · [[RwLock]] · [[Arc Mutex Shared State]] · [[Holding Locks Too Long]] · [[Lock Order Reversal]] · [[Channels]] · [[Ignoring Channel Disconnects]] · [[Blocking in Async]]

## Sources
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
- Standard library, `std::sync::Mutex` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
- Standard library, `std::sync::RwLock` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.RwLock.html
