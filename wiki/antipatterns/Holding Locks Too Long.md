---
type: antipattern
title: "Holding Locks Too Long"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, locks, mutex]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Shared State with Mutex]]", "[[Arc Mutex Shared State]]", "[[RwLock]]", "[[Deadlock Avoidance]]", "[[Lock Order Reversal]]", "[[Holding Locks Across Await]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html", "https://doc.rust-lang.org/std/sync/struct.RwLock.html"]
rust_version: "edition 2024 / 1.85+"
---

# Holding Locks Too Long

Holding locks too long means keeping a `MutexGuard` or `RwLock` guard alive while doing work that does not require protected access, increasing contention and deadlock risk.

## The mistake
A guard's lifetime is the lock hold.
If a guard remains in scope during parsing, allocation, I/O, callbacks, sleeps, joins, or other lock acquisitions, every competing thread waits for that whole duration.

This often happens accidentally.
The code takes a lock, computes a value, updates the collection, logs, and then calls another function while the guard is still in scope.
Rust will unlock reliably on drop, but it will not decide the best drop point for your design.

## Why it happens
RAII makes unlocking automatic, which is good, but scopes still matter.
In Rust, a binding lives until its last use or the end of its scope.
If the guard is named in a broad scope, the critical section can become broader than intended.

The fix is to separate preparation from publication.
Do expensive work before locking, then open a small block where the guard exists only long enough to touch the shared state.
Temporary guards created in a single statement, such as `*counter.lock().unwrap() += 1`, are dropped at the end of that statement.
Named guards live longer, so a named binding should be a deliberate signal that the following block is part of the critical section.

## Example
```rust
use std::sync::{Arc, Mutex};

fn main() {
    let shared = Arc::new(Mutex::new(Vec::new()));
    let input = ["1", "2", "3"];

    let parsed: Vec<i32> = input
        .iter()
        .map(|text| text.parse::<i32>().unwrap())
        .collect();

    {
        let mut guard = shared.lock().unwrap();
        guard.extend(parsed);
    }

    let len = shared.lock().unwrap().len();
    println!("stored {len} values");
}
```

## Example: snapshot before slow work
```rust
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

fn main() {
    let names = Arc::new(Mutex::new(vec!["ada".to_owned(), "grace".to_owned()]));

    let snapshot = {
        let guard = names.lock().unwrap();
        guard.clone()
    };

    thread::sleep(Duration::from_millis(5));
    println!("report: {snapshot:?}");
}
```

The lock protects the vector only long enough to clone the small snapshot.
The slow reporting step happens after the guard is dropped.

## Common errors
This antipattern rarely has a compiler error.
The observable failure is throughput collapse or a hang where other threads are blocked in `lock()` even though the protected update is tiny.
In async code, holding a `std::sync::MutexGuard` across `.await` may also make a future non-`Send`, producing a spawn error; see [[Holding Locks Across Await]] for the runtime-specific fix.

## Best practice
- ✅ Introduce a block around the lock guard to make the critical section visually obvious.
- ✅ Compute, allocate, and validate before locking whenever possible.
- ✅ Clone or copy the small result you need, drop the guard, then do slow follow-up work.
- ✅ In async code, use the existing [[Holding Locks Across Await]] guidance rather than carrying a std guard across `.await`.
- ✅ Prefer helper methods that return owned results instead of exposing guards to callers.

## Pitfalls
- ⚠️ Calling user-provided closures while locked lets unknown code participate in your lock graph.
- ⚠️ Joining a thread while holding a lock can wait for a worker that needs the same lock.
- ⚠️ Returning guards from helpers hides lock duration from callers.
- ⚠️ Holding one lock while acquiring another can become [[Lock Order Reversal]].
- ⚠️ Logging while locked can be surprisingly slow if the logger takes locks or writes to a blocking sink.

## See also
[[Concurrency]] · [[Threads]] · [[Shared State with Mutex]] · [[Arc Mutex Shared State]] · [[RwLock]] · [[Deadlock Avoidance]] · [[Lock Order Reversal]] · [[Holding Locks Across Await]] · [[Blocking in Async]]

## Sources
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
- Standard library, `std::sync::Mutex` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
- Standard library, `std::sync::RwLock` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.RwLock.html
