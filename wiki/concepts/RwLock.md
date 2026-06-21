---
type: concept
title: "RwLock"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, rwlock, locks]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Shared State with Mutex]]", "[[Arc]]", "[[Arc Mutex Shared State]]", "[[Deadlock Avoidance]]", "[[Holding Locks Too Long]]", "[[Lock Order Reversal]]"]
sources: ["[[std]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/sync/struct.RwLock.html", "https://doc.rust-lang.org/reference/special-types-and-traits.html#sync"]
rust_version: "edition 2024 / 1.85+"
---

# RwLock

`RwLock<T>` protects shared data with either many concurrent readers or one exclusive writer, making it useful only when read-heavy access outweighs its extra locking complexity.

## What it is
A read-write lock is a synchronization primitive for data that is often read and rarely written.
Readers acquire shared read guards and can run concurrently with other readers.
Writers acquire an exclusive write guard and exclude both readers and other writers.

This tradeoff is not automatically faster than a mutex.
`RwLock` has more bookkeeping, and its fairness policy is platform-dependent in the standard library.
Use it when profiling or the shape of the workload shows real read dominance.

## How it works
`read()` blocks until no writer holds the lock, then returns an `RwLockReadGuard`.
`write()` blocks until no reader or writer holds the lock, then returns an `RwLockWriteGuard`.
Both methods return lock results because std `RwLock` is poisoned if a thread panics while holding an exclusive write lock.

Like `Mutex`, guards unlock on drop.
The lifetime of a guard is the lifetime of the lock hold, so scopes are the primary control surface.
Short scopes keep readers and writers from blocking each other longer than necessary.
Only writer panics poison a standard-library `RwLock`; a panic while holding a read guard does not poison because readers cannot mutate the protected value through that guard.
There is no stable guarantee that std `RwLock` prefers readers or writers, so portable code must avoid designs that depend on a particular fairness policy.

## Example
```rust
use std::sync::{Arc, RwLock};
use std::thread;

fn main() {
    let values = Arc::new(RwLock::new(vec![1, 2, 3]));
    let reader_values = Arc::clone(&values);

    let reader = thread::spawn(move || {
        let guard = reader_values.read().expect("values lock poisoned");
        guard.iter().sum::<i32>()
    });

    {
        let mut guard = values.write().expect("values lock poisoned");
        guard.push(4);
    }

    println!("reader saw sum {}", reader.join().unwrap());
    println!("final values {:?}", values.read().unwrap());
}
```

## Example: read-heavy snapshot update
```rust
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::thread;

fn main() {
    let cache = Arc::new(RwLock::new(HashMap::from([("host", "localhost")])));
    let reader_cache = Arc::clone(&cache);

    let reader = thread::spawn(move || {
        let guard = reader_cache.read().unwrap();
        guard.get("host").copied().unwrap_or("missing").to_owned()
    });

    {
        let mut guard = cache.write().unwrap();
        guard.insert("port", "8080");
    }

    println!("reader saw {}", reader.join().unwrap());
}
```

## Common errors
`RwLock` failures are usually runtime liveness bugs, not compiler errors.
The common symptom is a thread stuck in `read()` or `write()` because another guard is held longer than expected.
A self-deadlock can happen if code holds a read guard, calls into a helper, and that helper tries to acquire a write guard for the same lock.

The fix is to shorten guard scopes, avoid calling unknown code while locked, and prefer [[Shared State with Mutex]] when read concurrency is not buying anything measurable.

## Best practice
- ✅ Start with [[Shared State with Mutex]] unless read concurrency is a clear requirement.
- ✅ Keep read guards short too; many long readers can starve a writer on some platforms.
- ✅ Treat write poisoning as a sign that protected invariants may be broken.
- ✅ Document lock-order rules when combining `RwLock` with other locks; see [[Deadlock Avoidance]].
- ✅ Copy or clone a small snapshot under a read guard, then drop the guard before expensive formatting, I/O, or callbacks.

## Pitfalls
- ⚠️ Reentrant read locking can deadlock if a writer queues between the first and second read.
- ⚠️ Holding a read guard while calling user code can become [[Holding Locks Too Long]].
- ⚠️ Assuming a specific reader/writer fairness policy is non-portable for std `RwLock`.
- ⚠️ Taking an `RwLock` and a `Mutex` in inconsistent orders creates [[Lock Order Reversal]].
- ⚠️ Upgrading a read lock to a write lock is not an atomic std operation; drop the read guard before taking the write guard and re-check the condition.

## See also
[[Concurrency]] · [[Shared State with Mutex]] · [[Arc]] · [[Arc Mutex Shared State]] · [[Deadlock Avoidance]] · [[Holding Locks Too Long]] · [[Lock Order Reversal]] · [[Send and Sync]]

## Sources
- Standard library, `std::sync::RwLock` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.RwLock.html
- The Rust Reference, "`Sync`" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html#sync
