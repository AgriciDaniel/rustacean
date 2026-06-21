---
type: antipattern
title: "Lock Order Reversal"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, deadlock, locks]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Deadlock Avoidance]]", "[[Shared State with Mutex]]", "[[RwLock]]", "[[Arc Mutex Shared State]]", "[[Holding Locks Too Long]]", "[[Threads]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html"]
rust_version: "edition 2024 / 1.85+"
---

# Lock Order Reversal

Lock order reversal is taking the same locks in different orders on different paths, creating a classic deadlock where each thread waits for a lock held by the other.

## The mistake
Two locks are individually safe, but the pair has no global acquisition rule.
One function locks `a` then `b`.
Another function locks `b` then `a`.
Under the wrong timing, each thread holds one guard and blocks forever trying to obtain the other.

The compiler cannot reject this.
The program is memory-safe because protected data is still accessed only through guards.
Deadlock is a liveness bug, so the solution is API and lock-graph design.

## Why it happens
Lock order tends to grow organically.
The first helper locks whatever data it needs.
Later, another helper is written from the opposite perspective and chooses the reverse order.
Both helpers look locally reasonable.

The correction is to make the ordering explicit and reusable.
For keyed resources, sort by stable key before locking.
For fixed subsystem locks, document levels and acquire only from lower level to higher level.
The order must include every blocking edge in the operation, not just `Mutex` calls.
An operation that locks `a`, waits on a channel, and then locks `b` can still participate in a cycle if another thread holds `b` and sends only after taking `a`.

## Example
```rust
use std::sync::Mutex;

struct Bucket {
    id: u32,
    value: Mutex<i32>,
}

fn add_pair(left: &Bucket, right: &Bucket) -> i32 {
    let (first, second) = if left.id <= right.id { (left, right) } else { (right, left) };

    let first_guard = first.value.lock().unwrap();
    let second_guard = second.value.lock().unwrap();

    *first_guard + *second_guard
}

fn main() {
    let a = Bucket { id: 1, value: Mutex::new(10) };
    let b = Bucket { id: 2, value: Mutex::new(20) };
    println!("{}", add_pair(&b, &a));
}
```

## Example: centralize two-lock acquisition
```rust
use std::sync::{Mutex, MutexGuard};

struct Pair {
    low: Mutex<i32>,
    high: Mutex<i32>,
}

impl Pair {
    fn lock_in_order(&self) -> (MutexGuard<'_, i32>, MutexGuard<'_, i32>) {
        let low = self.low.lock().unwrap();
        let high = self.high.lock().unwrap();
        (low, high)
    }
}

fn main() {
    let pair = Pair {
        low: Mutex::new(1),
        high: Mutex::new(2),
    };

    let (mut low, mut high) = pair.lock_in_order();
    *low += 10;
    *high += 20;
}
```

## Common errors
There is no borrow-checker error for lock-order reversal.
The typical production clue is that two threads are both alive but each is blocked inside a lock acquisition.
Tests may pass for months because the failing interleaving is timing-dependent.

The fix is to remove local choice: sort resources by key, expose one helper that locks both, or redesign the data so the invariant lives behind one [[Shared State with Mutex]].

## Best practice
- ✅ Assign a stable order to resources and lock in that order everywhere.
- ✅ Encapsulate multi-lock acquisition in one helper instead of duplicating it.
- ✅ Consider merging tightly coupled data under one [[Shared State with Mutex]].
- ✅ Release the first lock before taking the second if the operation can be split safely.
- ✅ Include `RwLock` read/write guards and channel waits when documenting a subsystem's lock order.

## Pitfalls
- ⚠️ Ordering by memory address is rarely a good public invariant; prefer stable ids or explicit levels.
- ⚠️ Mixing `Mutex` and `RwLock` still needs a single order across both kinds of lock.
- ⚠️ Calling arbitrary code while holding a lock can introduce new hidden lock orders.
- ⚠️ Trying to "fix" deadlock with sleeps only changes timing; use [[Deadlock Avoidance]].
- ⚠️ Locking a resource by user-provided order, such as request order, reintroduces reversal unless you sort before locking.

## See also
[[Concurrency]] · [[Deadlock Avoidance]] · [[Shared State with Mutex]] · [[RwLock]] · [[Arc Mutex Shared State]] · [[Holding Locks Too Long]] · [[Threads]] · [[Channels]]

## Sources
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
- Standard library, `std::sync::Mutex` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
