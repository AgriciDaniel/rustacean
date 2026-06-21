---
type: concept
title: "Threads"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, threads]
domain: "Concurrency"
difficulty: basic
related: ["[[Move Closures with Threads]]", "[[Scoped Threads]]", "[[Channels]]", "[[Shared State with Mutex]]", "[[Send and Sync]]", "[[Deadlock Avoidance]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-01-threads.html", "https://doc.rust-lang.org/std/thread/fn.spawn.html"]
rust_version: "edition 2024 / 1.85+"
---

# Threads

Threads are independently scheduled flows of execution; in Rust, `std::thread::spawn` runs a `Send + 'static` closure on an operating-system thread and returns a `JoinHandle` for synchronization.

## What it is
Rust's standard threads use a 1:1 model: one Rust thread maps to one operating-system thread.
Use them for CPU parallelism, blocking work, or integration points where an OS thread is the right unit.

The main thread does not automatically wait for detached spawned work to finish.
If `main` exits, spawned threads may be terminated before completing their closures.
Keeping the `JoinHandle` and calling `join` makes completion explicit.

## How it works
`thread::spawn` takes a closure and transfers it to a new thread.
The closure must be `Send` because it crosses a thread boundary, and it must be `'static` because the spawned thread may outlive the stack frame that created it.
The handle's `join` method blocks the caller until the thread finishes and returns `Result<T, Box<dyn Any + Send + 'static>>`; an `Err` means the thread panicked.
Dropping a `JoinHandle` detaches the thread: the thread may keep running, but no code can later observe its return value or panic through that handle.

Scheduling is nondeterministic.
Interleaving between the parent thread and worker threads is an implementation and operating-system detail, so correct code must not depend on a particular execution order unless it synchronizes explicitly with [[Channels]], [[Shared State with Mutex]], [[Atomics]], or joins.
`thread::Builder` is the escape hatch when you need a name or stack size, while `thread::spawn` is the default for ordinary OS-thread work.

## Example
```rust
use std::thread;

fn main() {
    let worker = thread::spawn(|| {
        (1..=4).sum::<u32>()
    });

    let main_total = (5..=8).sum::<u32>();
    let worker_total = worker.join().expect("worker thread panicked");

    println!("total = {}", main_total + worker_total);
}
```

## Example: naming a worker and handling panic
```rust
use std::thread;

fn main() {
    let worker = thread::Builder::new()
        .name("indexer".to_owned())
        .spawn(|| {
            let name = thread::current().name().unwrap_or("unnamed").to_owned();
            format!("{name} finished")
        })
        .expect("failed to create worker thread");

    match worker.join() {
        Ok(message) => println!("{message}"),
        Err(payload) => {
            if let Some(text) = payload.downcast_ref::<&str>() {
                eprintln!("worker panicked: {text}");
            }
        }
    }
}
```

## Common errors
Capturing a borrowed local in `thread::spawn` fails because the spawned thread may outlive the stack frame:

```text
error[E0373]: closure may outlive the current function, but it borrows `v`
help: to force the closure to take ownership of `v`, use the `move` keyword
```

The fix is to move owned data into the closure, clone intentionally, wrap shared data in [[Arc]], or use [[Scoped Threads]] when the thread should only borrow within a lexical scope.

## Best practice
- ✅ Store every `JoinHandle` you care about and join it at a deliberate boundary.
- ✅ Treat thread panics as part of the API: propagate with `.expect(...)` in examples, or handle the `Err` in robust services.
- ✅ Prefer [[Scoped Threads]] when worker threads only need to borrow local data for a fork-join computation.
- ✅ Prefer [[Channels]] or [[Arc Mutex Shared State]] over ad hoc shared globals for communication.
- ✅ Name long-lived service threads with `thread::Builder` so panic logs and debuggers identify the owner.

## Pitfalls
- ⚠️ Spawning and ignoring the handle creates fire-and-forget behavior; the worker may be cut off when the process exits.
- ⚠️ Assuming output order or mutation order without synchronization is a race in the program design, even when Rust prevents data races.
- ⚠️ Capturing non-`'static` borrows with `thread::spawn` fails; use [[Move Closures with Threads]] or [[Scoped Threads]].
- ⚠️ Blocking many OS threads for tiny tasks can be expensive; async tasks belong in [[async and await]] and [[The Tokio Runtime]], not on unbounded OS threads.
- ⚠️ Joining while holding a mutex can deadlock if the joined thread needs that same lock; see [[Holding Locks Too Long]].

## See also
[[Concurrency]] · [[Move Closures with Threads]] · [[Scoped Threads]] · [[Channels]] · [[Shared State with Mutex]] · [[Arc]] · [[Send and Sync]] · [[Deadlock Avoidance]] · [[Holding Locks Too Long]] · [[Tasks and spawn]]

## Sources
- The Rust Programming Language, ch. 16.1 "Using Threads to Run Code Simultaneously" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-01-threads.html
- Standard library, `std::thread::spawn` — [[std]],
  https://doc.rust-lang.org/std/thread/fn.spawn.html
