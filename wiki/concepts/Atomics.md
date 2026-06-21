---
type: concept
title: "Atomics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, atomics, memory-ordering]
domain: "Concurrency"
difficulty: advanced
related: ["[[Shared State with Mutex]]", "[[Arc]]", "[[Send and Sync]]", "[[Deadlock Avoidance]]", "[[Integer Overflow]]", "[[Unsafe Send and Sync Implementations]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html#atomic-reference-counting-with-arct", "https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic", "https://doc.rust-lang.org/std/sync/atomic/index.html", "https://doc.rust-lang.org/nomicon/atomics.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Atomic Types"]
---

# Atomics

Atomics are primitive shared-memory synchronization types whose operations are indivisible and whose `Ordering` controls what other memory effects become visible between threads.

## What it is
The `std::sync::atomic` module provides types such as `AtomicBool`, `AtomicUsize`, and `AtomicPtr`.
They are useful for simple counters, flags, reference counts, and building blocks of higher-level synchronization.

Atomics are not "mutexes but faster."
They protect only the atomic value and require a correct memory-ordering argument when the atomic coordinates access to other data.
When the invariant spans a collection or several fields, [[Shared State with Mutex]] is usually clearer.

## How it works
Every load, store, swap, compare-exchange, or fetch operation takes an `Ordering`.
`Relaxed` gives atomicity for that variable but does not establish happens-before relationships for other memory.
`Release` on a write and `Acquire` on a read of the same atomic can publish and observe preceding writes.
`SeqCst` adds a single global order among sequentially consistent operations, which is simple but not always necessary.

Availability can depend on target support.
The Reference exposes this through `target_has_atomic`; when a width is present, the stable atomic APIs for that width are available.
Atomic operations act on one memory location at a time.
They can coordinate larger invariants only when the ordering creates a correct happens-before edge and all non-atomic data is accessed in a way that avoids data races.
For lock-free algorithms, `compare_exchange` is the usual primitive for conditional updates, and failed exchanges need their own ordering.

## Example
```rust
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::thread;

fn main() {
    let hits = Arc::new(AtomicUsize::new(0));
    let mut handles = Vec::new();

    for _ in 0..4 {
        let hits = Arc::clone(&hits);
        handles.push(thread::spawn(move || {
            hits.fetch_add(1, Ordering::Relaxed);
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("hits = {}", hits.load(Ordering::Relaxed));
}
```

## Example: publishing a one-time flag
```rust
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::thread;

struct Shared {
    value: AtomicUsize,
    ready: AtomicBool,
}

fn main() {
    let shared = Arc::new(Shared {
        value: AtomicUsize::new(0),
        ready: AtomicBool::new(false),
    });

    let writer_shared = Arc::clone(&shared);
    let writer = thread::spawn(move || {
        writer_shared.value.store(42, Ordering::Relaxed);
        writer_shared.ready.store(true, Ordering::Release);
    });

    while !shared.ready.load(Ordering::Acquire) {
        thread::yield_now();
    }

    assert_eq!(shared.value.load(Ordering::Relaxed), 42);
    writer.join().unwrap();
}
```

## Common errors
Most atomic mistakes compile.
The typical bug is using `Ordering::Relaxed` for a flag that publishes other data; the reader sees the flag but has no acquire edge that guarantees visibility of the writes that happened before the flag was set.

Another frequent compiler error is target support on embedded or custom targets:

```text
error[E0432]: unresolved import `std::sync::atomic::AtomicU64`
```

The fix is to gate widths with `#[cfg(target_has_atomic = "64")]`, use a narrower atomic, or fall back to a lock.

## Best practice
- ✅ Use `Relaxed` for standalone statistics counters where only the numeric value matters.
- ✅ Use `Acquire`/`Release` when an atomic flag publishes access to other memory.
- ✅ Prefer [[Shared State with Mutex]] when a lock makes the invariant obvious and contention is not proven hot.
- ✅ Keep atomic code small and reviewed; it is easy to write code that compiles and is still logically wrong.
- ✅ Document the synchronization edge in comments when an atomic coordinates access to non-atomic state.

## Pitfalls
- ⚠️ Using `Relaxed` to publish non-atomic data is a memory-ordering bug.
- ⚠️ Defaulting every operation to `SeqCst` can hide the lack of a design and cost more on weakly ordered hardware.
- ⚠️ Combining several atomics rarely gives one atomic invariant; use a lock when fields must change together.
- ⚠️ Integer atomic operations still have integer semantics; understand [[Integer Overflow]] for counters that can wrap.
- ⚠️ Busy-wait loops can waste a CPU core; prefer blocking primitives unless the spin is short and justified.

## See also
[[Concurrency]] · [[Shared State with Mutex]] · [[Arc]] · [[Send and Sync]] · [[Deadlock Avoidance]] · [[Integer Overflow]] · [[Unsafe Send and Sync Implementations]] · [[Ownership]]

## Sources
- Standard library, `std::sync::atomic` — [[std]],
  https://doc.rust-lang.org/std/sync/atomic/index.html
- Standard library, `Ordering` — [[std]],
  https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html
- The Rust Reference, `target_has_atomic` — [[the-reference]],
  https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic
- The Rustonomicon, "Atomics" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/atomics.html
