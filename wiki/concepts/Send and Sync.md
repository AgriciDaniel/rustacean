---
type: concept
title: "Send and Sync"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, send, sync, auto-traits]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Threads]]", "[[Move Closures with Threads]]", "[[Arc]]", "[[Shared State with Mutex]]", "[[Unsafe Send and Sync Implementations]]", "[[Ownership]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html", "https://doc.rust-lang.org/reference/special-types-and-traits.html#send", "https://doc.rust-lang.org/nomicon/send-and-sync.html"]
rust_version: "edition 2024 / 1.85+"
---

# Send and Sync

`Send` means a value can be transferred to another thread; `Sync` means shared references to a value can be used from multiple threads safely.

## What it is
`Send` and `Sync` are marker traits that encode Rust's thread-safety rules.
They have no methods, but their presence or absence decides whether types may cross or be shared across thread boundaries.

Most Rust types are `Send` and `Sync` automatically.
Important exceptions are instructive: `Rc<T>` is not thread-safe because its reference count is not atomic, `RefCell<T>` is not `Sync` because its runtime borrow flag is unsynchronized, and raw pointers have no safety guard.

## How it works
The Reference defines `Send` as safe to send from one thread to another, and `Sync` as safe to share between multiple threads.
The standard shorthand is: `T: Sync` when `&T: Send`.

These traits are auto traits.
If a struct, enum, tuple, closure, or other composite type is made only of fields and captures that satisfy the trait, the compiler implements the trait automatically.
For closures, the exact capture mode matters: moved or uniquely borrowed captures must be `Send` for the closure to be `Send`, while shared-reference captures depend on the referenced value being `Sync`.

Manual implementations are `unsafe`.
An `unsafe impl Send` or `unsafe impl Sync` is a promise to all unsafe code that your type upholds the thread-safety invariant the compiler could not verify.
The two traits are related but not interchangeable: `Send` is about moving ownership, while `Sync` is about allowing `&T` to be shared.
For example, `Mutex<T>` can be `Sync` even though it hands out mutable access internally, because the lock serializes that access.

## Example
```rust
use std::sync::{Arc, Mutex};

fn requires_send<T: Send>(_: T) {}
fn requires_sync<T: Sync>(_: &T) {}

fn main() {
    let shared = Arc::new(Mutex::new(0_u32));

    requires_send(Arc::clone(&shared));
    requires_sync(&shared);

    println!("Arc<Mutex<u32>> can cross and be shared between threads");
}
```

## Example: API bounds that say what crosses threads
```rust
use std::thread;

fn run_in_background<F, T>(job: F) -> thread::JoinHandle<T>
where
    F: FnOnce() -> T + Send + 'static,
    T: Send + 'static,
{
    thread::spawn(job)
}

fn main() {
    let handle = run_in_background(|| String::from("done"));
    println!("{}", handle.join().unwrap());
}
```

## Common errors
Trying to move `Rc<T>` or `Rc<Mutex<T>>` into a spawned thread produces:

```text
error[E0277]: `Rc<...>` cannot be sent between threads safely
help: the trait `Send` is not implemented for `Rc<...>`
```

The fix is to use [[Arc]] for shared ownership across threads, or to keep the value on one thread and communicate with [[Channels]].
Do not add [[Unsafe Send and Sync Implementations]] unless you are writing a low-level abstraction with a documented safety proof.

## Best practice
- ✅ Let auto-trait derivation do the work for ordinary Rust types.
- ✅ Read a `Send` or `Sync` compiler error as a design signal, not as noise to suppress.
- ✅ Use [[Arc]] instead of `Rc<T>` when ownership must cross threads.
- ✅ Use [[Shared State with Mutex]], [[RwLock]], or [[Atomics]] to make shared mutation explicit.
- ✅ Put `Send + 'static` bounds on thread-pool jobs and return values that may run beyond the caller's stack frame.

## Pitfalls
- ⚠️ Adding [[Unsafe Send and Sync Implementations]] to silence `thread::spawn` errors can create undefined behavior.
- ⚠️ `Arc<T>` does not make a non-`Sync` `T` safe to share; `Arc<RefCell<T>>` remains the wrong tool for threads.
- ⚠️ Capturing a non-`Send` value in [[Move Closures with Threads]] prevents `thread::spawn` from compiling.
- ⚠️ Trait objects must carry thread-safety bounds explicitly when needed, such as `Box<dyn FnOnce() + Send + 'static>`.
- ⚠️ A type can be `Send` but not `Sync`; do not infer shared-reference safety from move safety.

## See also
[[Concurrency]] · [[Threads]] · [[Move Closures with Threads]] · [[Arc]] · [[Shared State with Mutex]] · [[RwLock]] · [[Atomics]] · [[Unsafe Send and Sync Implementations]]

## Sources
- The Rust Programming Language, ch. 16.4 "Extensible Concurrency with `Send` and `Sync`" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html
- The Rust Reference, "Special types and traits: `Send`, `Sync`, auto traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html#send
- The Rustonomicon, "Send and Sync" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/send-and-sync.html
