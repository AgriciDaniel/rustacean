---
type: pattern
title: "Mutex Poisoning and Recovery"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, mutex, poisoning, recovery, panic]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Shared State with Mutex]]", "[[Arc Mutex Shared State]]", "[[Condvar]]", "[[Holding Locks Too Long]]", "[[Deadlock Avoidance]]", "[[Result]]"]
sources: ["[[std]]", "[[the-book]]", "[[08-concurrency]]"]
source_urls: ["https://doc.rust-lang.org/std/sync/struct.Mutex.html", "https://doc.rust-lang.org/std/sync/struct.PoisonError.html", "https://doc.rust-lang.org/book/ch16-03-shared-state.html"]
rust_version: "edition 2024 / 1.85+"
---

# Mutex Poisoning and Recovery

Treat mutex poisoning as a warning that a panic may have interrupted an invariant update; propagate it by default, and recover only after repairing or validating the protected state.

## What it is
Standard-library `Mutex<T>` uses poisoning as an advisory panic-corruption signal.
If a thread panics while holding a mutex guard, later `lock()` calls return `Err(PoisonError<MutexGuard<'_, T>>)`.
The lock is still acquired in the error case.
The error wraps the guard so recovery code can inspect or repair the value.

Poisoning is not a memory-safety guarantee.
The standard docs explicitly frame it as advisory.
Some panic contexts and foreign exceptions may not set the poison bit.
Unsafe code must maintain its own invariants without relying on poisoning to fire.

The ordinary application default is simple: use `.lock().unwrap()` or `.expect("... poisoned")`.
That propagates the signal instead of silently continuing with possibly inconsistent data.
Recovery is a deliberate pattern for cases where the invariant is easy to rebuild or validate.

## How it works
`lock()` returns `LockResult<MutexGuard<'_, T>>`.
On success, use the guard normally.
On poison, `PoisonError::into_inner()` returns the guard anyway.
`PoisonError::get_mut()` can modify the guard before consuming the error.
`Mutex::clear_poison()` marks the mutex healthy again after you decide the state is consistent.

There are three common responses:
Fail fast by unwrapping.
Inspect and repair, then call `clear_poison`.
Extract the inner value during shutdown or test cleanup, accepting that the value may need validation.

Do not reflexively discard poison errors in helper functions.
That turns a useful panic signal into hidden shared-state corruption.
Make the recovery policy visible at the call site or encode it in a named function.

## Example
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let numbers = Arc::new(Mutex::new(vec![1, 2, 3]));
    let worker_numbers = Arc::clone(&numbers);

    let _ = thread::spawn(move || {
        let mut guard = worker_numbers.lock().unwrap();
        guard.push(999);
        panic!("panic while invariant may be broken");
    })
    .join();

    let mut guard = numbers.lock().unwrap_or_else(|mut poison| {
        poison.get_mut().clear();
        numbers.clear_poison();
        poison.into_inner()
    });

    guard.extend([4, 5, 6]);
    assert_eq!(&*guard, &[4, 5, 6]);
}
```

## Example: propagate by default
```rust
use std::sync::Mutex;

fn push_value(values: &Mutex<Vec<u32>>, value: u32) {
    let mut guard = values.lock().expect("values mutex poisoned");
    guard.push(value);
}

fn main() {
    let values = Mutex::new(Vec::new());
    push_value(&values, 10);
    assert_eq!(values.into_inner().unwrap(), vec![10]);
}
```

## Best practice
- ✅ Use `.lock().unwrap()` or `.expect("... poisoned")` when your program cannot prove recovery.
- ✅ Recover only by validating or rebuilding the protected invariant.
- ✅ Call `clear_poison` only after the value is consistent again.
- ✅ Keep recovery logic close to the invariant it repairs.
- ✅ Document recovery policy for shared infrastructure locks.
- ✅ Remember that [[Condvar]] waits also surface mutex poisoning when the lock is reacquired.

## Pitfalls
- ⚠️ Calling `poisoned.into_inner()` everywhere just hides the signal.
- ⚠️ Treating poisoning as a soundness boundary for unsafe code is unsound.
- ⚠️ Clearing poison before repairing the value lies to later callers.
- ⚠️ Assuming all panics poison all locks ignores documented edge cases.
- ⚠️ Mixing std `Mutex` expectations with third-party mutexes can be wrong; some crates deliberately do not poison.
- ⚠️ Holding the guard during recovery callbacks can create [[Holding Locks Too Long]] or [[Lock Order Reversal]].

## See also
[[Concurrency]] · [[Shared State with Mutex]] · [[Arc Mutex Shared State]] · [[Condvar]] · [[Threads]] · [[Result]] · [[Holding Locks Too Long]] · [[Deadlock Avoidance]] · [[Lock Order Reversal]] · [[Unsafe Send and Sync Implementations]]

## Sources
- Standard library, `std::sync::Mutex` poisoning and `clear_poison` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
- Standard library, `std::sync::PoisonError` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.PoisonError.html
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
