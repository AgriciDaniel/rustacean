---
type: antipattern
title: "Premature Arc Mutex"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, arc, mutex, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Concurrency]]", "[[Message Passing]]", "[[Shared State]]", "[[Ownership]]", "[[Blocking in Async]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-02-message-passing.html", "https://doc.rust-lang.org/book/ch16-03-shared-state.html", "https://doc.rust-lang.org/std/sync/struct.Arc.html", "https://doc.rust-lang.org/std/sync/struct.Mutex.html"]
rust_version: "edition 2024 / 1.85+"
---

# Premature Arc Mutex

Premature `Arc<Mutex<T>>` is wrapping state for shared mutation before proving that shared mutation is the right concurrency model.

## The mistake
`Arc<T>` provides thread-safe shared ownership. `Mutex<T>` provides mutually exclusive access. Together, `Arc<Mutex<T>>` is correct for state that many threads must access and mutate through a single shared value.

The footgun is using `Arc<Mutex<_>>` as a reflex whenever threads or tasks appear. It imports lock ordering, poisoning, contention, and lifetime complexity into code that might be simpler with ownership transfer, channels, scoped borrowing, or per-worker state.

## Why it happens
Moving data into a thread closure consumes it, and multiple threads cannot all own the same non-`Copy` value. `Arc<Mutex<T>>` is the obvious compiling shape, so it gets applied before the data-flow question is answered.

Rust's standard library presents two complementary concurrency styles: message passing and shared-state concurrency. If one thread or task can own the state, channels usually make mutation easier to reason about than locking.

`Arc` solves shared ownership by using atomic reference counts. `Mutex` solves shared mutation by blocking all but one accessor and returning a guard that unlocks on drop. Neither solves higher-level sequencing. If two operations must happen in order, or a task must not hold a lock while waiting, the design still has to encode that.

The standard mutex also has poisoning: if a thread panics while holding it, later `lock()` calls return `PoisonError`. That is a useful corruption signal for application code, but library code should decide explicitly whether to propagate, recover, or replace the protected value.

## Example
```rust
use std::sync::mpsc;
use std::thread;

enum Command {
    Add(i32),
    Total(mpsc::Sender<i32>),
}

fn main() {
    let (tx, rx) = mpsc::channel::<Command>();

    let worker = thread::spawn(move || {
        let mut total = 0;
        for command in rx {
            match command {
                Command::Add(n) => total += n,
                Command::Total(reply) => reply.send(total).unwrap(),
            }
        }
    });

    tx.send(Command::Add(2)).unwrap();
    tx.send(Command::Add(3)).unwrap();

    let (reply_tx, reply_rx) = mpsc::channel();
    tx.send(Command::Total(reply_tx)).unwrap();
    println!("total = {}", reply_rx.recv().unwrap());

    drop(tx);
    worker.join().unwrap();
}
```

## Second example: scoped threads avoid `Arc` for borrowed data
```rust
use std::thread;

fn sum_halves(values: &mut [i32]) -> i32 {
    let mid = values.len() / 2;
    let (left, right) = values.split_at_mut(mid);

    thread::scope(|scope| {
        let left_handle = scope.spawn(|| left.iter().sum::<i32>());
        let right_handle = scope.spawn(|| right.iter().sum::<i32>());

        left_handle.join().unwrap() + right_handle.join().unwrap()
    })
}

fn main() {
    let mut values = vec![1, 2, 3, 4, 5, 6];
    println!("{}", sum_halves(&mut values));
}
```

Here the threads cannot outlive the borrowed slice, so `thread::scope` expresses the lifetime directly. `Arc<Mutex<Vec<_>>>` would add allocation, locking, and serialization for no gain.

## Common errors
Move error when several closures try to own one value:

```text
error[E0382]: use of moved value: `counter`
```

Do not automatically wrap it in `Arc<Mutex<_>>`. First ask whether each thread can own a partition, whether `thread::scope` can borrow the data, or whether one worker should own state and receive commands.

Async lock mistake:

```text
error: future cannot be sent between threads safely
```

This often happens because a `std::sync::MutexGuard` is live across `.await`. Fix it by limiting the guard to a synchronous block, or by moving state into a task and communicating by messages.

## Best practice
- ✅ Start by asking who should own the state; use a channel when one worker can own it.
- ✅ Keep mutex critical sections small and synchronous.
- ✅ Use `Arc<Mutex<T>>` for genuinely shared state such as caches, registries, and counters with clear lock boundaries.
- ✅ Handle `Mutex` poisoning intentionally instead of blindly assuming every lock succeeds in library code.
- ✅ Prefer `Arc<T>` without `Mutex` for immutable shared configuration.
- ✅ Consider sharding or per-worker accumulation before protecting one large collection with one lock.

## Pitfalls
- ⚠️ Holding a mutex guard while calling unknown code can deadlock or create unexpected lock ordering.
- ⚠️ Holding a standard `MutexGuard` across an `.await` is an async footgun; see [[Blocking in Async]].
- ⚠️ `Arc<Mutex<Vec<T>>>` serializes all access even when per-item ownership would permit parallelism.
- ⚠️ Locking because "the compiler complained" can hide a simpler ownership transfer.
- ⚠️ Returning or storing a `MutexGuard` extends the critical section beyond the code that visually locked it.
- ⚠️ A mutex does not prevent deadlocks, lock-order inversions, or callbacks that reenter the same state.

## See also
[[Concurrency]] · [[Message Passing]] · [[Shared State]] · [[Ownership]] · [[Borrowing]] · [[Blocking in Async]] · [[Rc RefCell Overuse]] · [[Unwrap and Expect Overuse]] · [[Needless Clone]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 16.2 "Using Message Passing to Transfer Data Between Threads" — [[the-book]], https://doc.rust-lang.org/book/ch16-02-message-passing.html
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]], https://doc.rust-lang.org/book/ch16-03-shared-state.html
- Standard library, `Arc` — [[the-reference]], https://doc.rust-lang.org/std/sync/struct.Arc.html
- Standard library, `Mutex` — [[the-reference]], https://doc.rust-lang.org/std/sync/struct.Mutex.html
