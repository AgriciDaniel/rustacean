---
type: concept
title: "Condvar"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, condvar, mutex, blocking]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Shared State with Mutex]]", "[[Threads]]", "[[Arc Mutex Shared State]]", "[[Mutex Poisoning and Recovery]]", "[[Deadlock Avoidance]]", "[[Holding Locks Too Long]]"]
sources: ["[[the-book]]", "[[std]]", "[[08-concurrency]]"]
source_urls: ["https://doc.rust-lang.org/std/sync/struct.Condvar.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html", "https://doc.rust-lang.org/book/ch16-03-shared-state.html"]
rust_version: "edition 2024 / 1.85+"
---

# Condvar

`Condvar` lets a thread sleep until shared state protected by a `Mutex` changes, then wake and re-check the condition while holding the lock again.

## What it is
A condition variable is for waiting on a predicate, not for storing the predicate.
The predicate lives in shared state, usually behind [[Shared State with Mutex]].
The `Condvar` is the blocking and notification mechanism attached to that state.

Use it when a thread has no useful work to do until another thread changes a value.
Instead of polling in a loop and wasting CPU, the waiting thread gives up the mutex, parks, and later reacquires the mutex before observing the value again.

The standard-library type is `std::sync::Condvar`.
It is a blocking thread primitive, so it belongs with [[Threads]] and OS-thread synchronization.
It is not an async waiting primitive; do not hold it across `.await` or use it to coordinate [[Tasks and spawn]].

## How it works
A condition variable is paired with a mutex guard.
`wait(guard)` atomically unlocks the mutex and blocks the current thread.
When the wait returns, the mutex has been locked again and a new guard is returned.
That return value is a `LockResult`, because the mutex can become poisoned while the waiter is asleep.

The important rule is to wait in a loop that checks the predicate.
Wakeups can be spurious, and notifications are not buffered for future waiters.
If `notify_one` runs before a thread has started waiting, the later waiter must still be able to make progress by inspecting the predicate itself.

`wait_while` and `wait_timeout_while` encode the loop shape directly.
They are often clearer than open-coded loops when the predicate is simple.
Use `notify_one` when one waiter can handle the state transition.
Use `notify_all` when the state change may unblock many waiters or when each waiter must decide for itself whether it can proceed.

## Example
```rust
use std::sync::{Arc, Condvar, Mutex};
use std::thread;

fn main() {
    let shared = Arc::new((Mutex::new(false), Condvar::new()));
    let worker_shared = Arc::clone(&shared);

    let worker = thread::spawn(move || {
        let (lock, ready) = &*worker_shared;
        let mut done = lock.lock().unwrap();
        *done = true;
        ready.notify_one();
    });

    let (lock, ready) = &*shared;
    let mut done = lock.lock().unwrap();
    while !*done {
        done = ready.wait(done).unwrap();
    }

    worker.join().unwrap();
    assert!(*done);
}
```

## Example: wait_while
```rust
use std::sync::{Arc, Condvar, Mutex};
use std::thread;

fn main() {
    let shared = Arc::new((Mutex::new(Vec::<u32>::new()), Condvar::new()));
    let producer_shared = Arc::clone(&shared);

    thread::spawn(move || {
        let (lock, available) = &*producer_shared;
        let mut queue = lock.lock().unwrap();
        queue.push(42);
        available.notify_one();
    })
    .join()
    .unwrap();

    let (lock, available) = &*shared;
    let mut queue = available
        .wait_while(lock.lock().unwrap(), |queue| queue.is_empty())
        .unwrap();

    assert_eq!(queue.pop(), Some(42));
}
```

## Best practice
- ✅ Store the condition in the mutex-protected data, and treat the `Condvar` as only the wakeup channel.
- ✅ Check the predicate before waiting and after every wakeup.
- ✅ Prefer `wait_while` for direct "sleep while this predicate is true" code.
- ✅ Notify after changing the protected state so waiters can observe the new condition.
- ✅ Keep the critical section around notification small and obvious.
- ✅ Handle poisoning deliberately; see [[Mutex Poisoning and Recovery]].

## Pitfalls
- ⚠️ Waiting without a predicate is a lost-wakeup bug waiting to happen.
- ⚠️ Assuming every wakeup means the condition is true ignores spurious wakeups.
- ⚠️ Using one `Condvar` with more than one mutex over time can panic.
- ⚠️ Holding unrelated locks while calling `wait` or `notify_all` can make [[Deadlock Avoidance]] harder.
- ⚠️ Using `Condvar` in async code blocks an OS thread; prefer async notifications for [[Shared State in Async]].
- ⚠️ Calling the deprecated `wait_timeout_ms` is outdated; use `wait_timeout` or `wait_timeout_while`.

## See also
[[Concurrency]] · [[Threads]] · [[Shared State with Mutex]] · [[Arc Mutex Shared State]] · [[Mutex Poisoning and Recovery]] · [[Deadlock Avoidance]] · [[Holding Locks Too Long]] · [[Channels]] · [[Scoped Threads]] · [[Blocking in Async]]

## Sources
- Standard library, `std::sync::Condvar` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Condvar.html
- Standard library, `std::sync::Mutex` poisoning behavior — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Mutex.html
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
