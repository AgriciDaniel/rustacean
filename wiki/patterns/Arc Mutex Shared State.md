---
type: pattern
title: "Arc Mutex Shared State"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, arc, mutex, shared-state]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Arc]]", "[[Shared State with Mutex]]", "[[Threads]]", "[[Send and Sync]]", "[[Deadlock Avoidance]]", "[[Premature Arc Mutex]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html", "https://doc.rust-lang.org/std/sync/struct.Arc.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html"]
rust_version: "edition 2024 / 1.85+"
---

# Arc Mutex Shared State

Use `Arc<Mutex<T>>` when multiple threads need shared ownership of one mutable value and every access must be serialized.

## What it is
`Arc<Mutex<T>>` combines two separate responsibilities.
`Arc<T>` gives multiple threads ownership of the same allocation.
`Mutex<T>` gives synchronized mutable access to the protected value.

The order matters conceptually: the `Arc` is cloned and moved into threads, while each thread locks the same mutex before touching `T`.
This is the standard-library default for simple shared mutable state.

## How it works
Create one `Arc::new(Mutex::new(value))`.
Before each spawn, call `Arc::clone(&shared)` and move that clone into the closure.
Inside the closure, call `lock`, use the guard, and let the guard drop promptly.

`Arc<Mutex<T>>` is not a license to make every part of a program global.
It is best when the shared invariant is small, lock duration is short, and ownership genuinely spans threads.
For one-way transfer, [[Channels]] is often clearer.
For read-heavy data, [[RwLock]] may fit better.
For simple counters, [[Atomics]] are smaller.
The inner `Mutex<T>` controls access, not the `Arc`; cloning the `Arc` only gives another handle to the same lock.
When all worker handles are joined and only one `Arc` remains, `Arc::try_unwrap(shared).unwrap().into_inner().unwrap()` can recover the owned `T` without cloning it.

## Example
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let shared = Arc::new(Mutex::new(Vec::new()));
    let mut handles = Vec::new();

    for worker_id in 0..3 {
        let shared = Arc::clone(&shared);
        handles.push(thread::spawn(move || {
            let result = worker_id * worker_id;
            shared.lock().unwrap().push(result);
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let mut results = Arc::try_unwrap(shared).unwrap().into_inner().unwrap();
    results.sort();
    println!("{results:?}");
}
```

## Example: publish computed results, not work in the lock
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let results = Arc::new(Mutex::new(Vec::new()));
    let inputs = [3, 4, 5, 6];
    let mut handles = Vec::new();

    for input in inputs {
        let results = Arc::clone(&results);
        handles.push(thread::spawn(move || {
            let computed = input * input;
            results.lock().unwrap().push((input, computed));
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let mut results = results.lock().unwrap();
    results.sort_by_key(|(input, _)| *input);
    println!("{results:?}");
}
```

## Common errors
Using `Rc<Mutex<T>>` with threads produces:

```text
error[E0277]: `Rc<std::sync::Mutex<i32>>` cannot be sent between threads safely
help: the trait `Send` is not implemented for `Rc<...>`
```

The fix is `Arc<Mutex<T>>` when shared mutable ownership is required.
If mutation is unnecessary, use `Arc<T>`; if ownership should flow to one consumer, use [[Channels]].

## Best practice
- ✅ Compute expensive work before locking, then lock only to publish the result.
- ✅ Keep the protected `T` focused on one coherent invariant.
- ✅ Clone the `Arc`, not the inner data, when passing ownership to threads.
- ✅ Document lock ordering if this mutex is ever acquired with another lock.
- ✅ Recover the inner value with `Arc::try_unwrap` only after all other strong references are gone.

## Pitfalls
- ⚠️ Using `Arc<Mutex<T>>` when ownership is not actually shared is [[Premature Arc Mutex]].
- ⚠️ Holding a guard while doing slow work creates [[Holding Locks Too Long]].
- ⚠️ Nesting several `Arc<Mutex<_>>` values without a global order creates [[Lock Order Reversal]].
- ⚠️ Ignoring mutex poisoning can hide a panic that interrupted an invariant update.
- ⚠️ Locking once per tiny update can dominate runtime; batch per-thread work and publish in fewer lock acquisitions when possible.

## See also
[[Concurrency]] · [[Arc]] · [[Shared State with Mutex]] · [[Threads]] · [[Channels]] · [[RwLock]] · [[Atomics]] · [[Send and Sync]] · [[Deadlock Avoidance]] · [[Holding Locks Too Long]] · [[Premature Arc Mutex]]

## Sources
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
- Standard library, `std::sync::Arc` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Arc.html
- Standard library, `std::sync::Mutex` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
