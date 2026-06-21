---
type: concept
title: "Shared State with Mutex"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, mutex, shared-state]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Arc]]", "[[Arc Mutex Shared State]]", "[[RwLock]]", "[[Atomics]]", "[[Deadlock Avoidance]]", "[[Holding Locks Too Long]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Shared State"]
---

# Shared State with Mutex

`Mutex<T>` protects shared data by allowing only one thread at a time to access `T`, returning a guard that unlocks automatically when dropped.

## What it is
A mutex is mutual exclusion around a value.
Before reading or mutating the protected data, a thread must acquire the lock.
Rust makes that discipline part of the type: you cannot access the inner `T` without obtaining a `MutexGuard<T>`.

`Mutex<T>` is also an interior-mutability primitive.
An immutable `&Mutex<T>` can yield mutable access to `T`, but only while the runtime lock is held.
That is why `Mutex<T>` is the thread-safe cousin of `RefCell<T>` rather than a replacement for ordinary `&mut T`.

## How it works
`Mutex::new(value)` constructs the lock and protected value.
`lock()` blocks until the lock is available and returns `LockResult<MutexGuard<'_, T>>`.
The guard dereferences to `T` and releases the lock in its `Drop` implementation.

The `LockResult` exists because std mutexes are poisoned.
If a thread panics while holding the lock, later `lock()` calls return `Err(PoisonError<_>)` as a warning that the protected data may be logically inconsistent.
In many applications, `.lock().unwrap()` is a reasonable default because it propagates the corruption signal.
Poisoning is advisory, not a soundness boundary for `unsafe` code: some panic paths and foreign exceptions may not poison, so memory safety must not depend on poisoning firing.
`Mutex::new` is `const` on stable Rust, so a plain `static Mutex<T>` is possible when `T` can be built in a constant context.

## Example
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = Vec::new();

    for _ in 0..4 {
        let counter = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            let mut guard = counter.lock().expect("counter mutex poisoned");
            *guard += 1;
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("count = {}", *counter.lock().unwrap());
}
```

## Example: recovering from poison deliberately
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let state = Arc::new(Mutex::new(vec![1, 2, 3]));
    let worker_state = Arc::clone(&state);

    let _ = thread::spawn(move || {
        let mut guard = worker_state.lock().unwrap();
        guard.push(4);
        panic!("worker failed after updating state");
    })
    .join();

    let mut guard = match state.lock() {
        Ok(guard) => guard,
        Err(poisoned) => {
            let mut guard = poisoned.into_inner();
            guard.clear();
            guard
        }
    };

    guard.push(10);
    println!("{guard:?}");
}
```

## Common errors
Moving a bare `Mutex<T>` into multiple spawned closures fails because the first move consumes it:

```text
error[E0382]: borrow of moved value: `counter`
```

The fix is not `Rc<Mutex<T>>`; `Rc` cannot cross threads. Use [[Arc Mutex Shared State]], [[Channels]], or [[Scoped Threads]] depending on whether ownership is shared, transferred, or only borrowed temporarily.

## Best practice
- ✅ Keep critical sections small: lock, inspect or mutate, then let the guard drop.
- ✅ Put data that must stay consistent together behind one mutex instead of scattering invariants across several locks.
- ✅ Treat poisoning as useful information; recover with `into_inner` only when you have a real recovery story.
- ✅ Prefer [[Atomics]] for simple counters and flags, and [[RwLock]] for genuinely read-heavy shared state.
- ✅ Use an inner block or explicit `drop(guard)` before waits, joins, callbacks, or expensive follow-up work.

## Pitfalls
- ⚠️ Holding a guard across slow work, callbacks, I/O, or `.await` creates [[Holding Locks Too Long]].
- ⚠️ Taking multiple mutexes without a consistent order creates [[Lock Order Reversal]].
- ⚠️ Wrapping everything in `Arc<Mutex<_>>` by default can be [[Premature Arc Mutex]].
- ⚠️ Returning `MutexGuard` from public APIs hides lock lifetime from the caller and makes [[Deadlock Avoidance]] harder.
- ⚠️ Using poisoning as an `unsafe` code invariant is unsound; poisoning is a diagnostic signal, not a guarantee.

## See also
[[Concurrency]] · [[Arc]] · [[Arc Mutex Shared State]] · [[RwLock]] · [[Atomics]] · [[Deadlock Avoidance]] · [[Holding Locks Too Long]] · [[Shared State in Async]]

## Sources
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
- Standard library, `std::sync::Mutex` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
