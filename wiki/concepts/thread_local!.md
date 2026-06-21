---
type: concept
title: "thread_local!"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, thread-local, tls, interior-mutability]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Threads]]", "[[Interior Mutability]]", "[[Shared State with Mutex]]", "[[Send and Sync]]", "[[Scoped Threads]]", "[[Ownership]]"]
sources: ["[[std]]", "[[the-book]]", "[[08-concurrency]]"]
source_urls: ["https://doc.rust-lang.org/std/macro.thread_local.html", "https://doc.rust-lang.org/std/thread/struct.LocalKey.html", "https://doc.rust-lang.org/book/ch16-01-threads.html"]
rust_version: "edition 2024 / 1.85+"
---

# thread_local!

`thread_local!` declares a static key whose value is separate for each OS thread, giving per-thread state without sharing one mutable value across threads.

## What it is
The `thread_local!` macro creates a `std::thread::LocalKey<T>`.
Each thread that accesses the key gets its own instance of `T`.
Updates in one thread are not visible in another thread.

Thread-local storage is useful for per-thread counters, scratch buffers, caches, and context that is inherently tied to a running thread.
It can avoid locks because there is no cross-thread access to the same value.

The API yields only shared references to the stored value.
That restriction still matters even though the value is per-thread: two call frames in the same thread can try to access the same key at once.
For mutation, use [[Interior Mutability]] types such as `Cell<T>` for `Copy` values or `RefCell<T>` for richer values.

## How it works
The macro wraps one or more `static` declarations.
The value is initialized lazily the first time a thread touches that key, unless the `const { ... }` form can enable a more efficient implementation.
Values that need `Drop` are best-effort destroyed when the thread exits, with platform-specific caveats.

Access normally happens through `with`, which passes `&T` into a closure.
The reference cannot escape the closure.
For `LocalKey<Cell<T>>`, stable helpers such as `get`, `set`, `replace`, and `take` make common operations direct.
For `LocalKey<RefCell<T>>`, `with_borrow` and `with_borrow_mut` avoid spelling out the `RefCell` borrow calls.

Thread-local state is tied to OS threads, not async tasks.
An async task may move between executor threads, so thread-local state is usually the wrong place for per-request async context.

## Example
```rust
use std::cell::Cell;
use std::thread;

thread_local! {
    static REQUESTS: Cell<u32> = const { Cell::new(0) };
}

fn record_request() -> u32 {
    REQUESTS.set(REQUESTS.get() + 1);
    REQUESTS.get()
}

fn main() {
    assert_eq!(record_request(), 1);
    assert_eq!(record_request(), 2);

    let handle = thread::spawn(|| {
        assert_eq!(record_request(), 1);
        assert_eq!(record_request(), 2);
    });

    handle.join().unwrap();
    assert_eq!(REQUESTS.get(), 2);
}
```

## Example: RefCell thread-local buffer
```rust
use std::cell::RefCell;

thread_local! {
    static BUFFER: RefCell<String> = const { RefCell::new(String::new()) };
}

fn render_number(n: u32) -> String {
    BUFFER.with_borrow_mut(|buffer| {
        buffer.clear();
        buffer.push_str("n=");
        buffer.push_str(&n.to_string());
        buffer.clone()
    })
}

fn main() {
    assert_eq!(render_number(7), "n=7");
}
```

## Best practice
- ✅ Use `const { ... }` initialization when the initializer can be const.
- ✅ Prefer `Cell<T>` for small `Copy` thread-local state.
- ✅ Prefer `RefCell<T>` when each thread needs mutable owned state such as a buffer or vector.
- ✅ Keep thread-local state narrow and local to infrastructure code.
- ✅ Use [[Shared State with Mutex]], [[RwLock]], or [[Atomics]] when state must actually be shared across threads.
- ✅ Use `try_with` from destructors or shutdown-sensitive code when TLS access may fail.

## Pitfalls
- ⚠️ Thread-local values are not task-local values; async work can move between threads.
- ⚠️ `RefCell` borrow rules still apply and can panic at runtime on overlapping borrows.
- ⚠️ Destructors for thread-local values have platform caveats and should not perform complex synchronization.
- ⚠️ On Windows, blocking synchronization in TLS destructors can deadlock during loader-lock-sensitive teardown.
- ⚠️ Hiding global state in TLS can make tests order-dependent and APIs harder to reason about.
- ⚠️ Expecting one thread's update to be visible elsewhere confuses TLS with [[Arc Mutex Shared State]].

## See also
[[Concurrency]] · [[Threads]] · [[Scoped Threads]] · [[Interior Mutability]] · [[Shared State with Mutex]] · [[Arc Mutex Shared State]] · [[Send and Sync]] · [[Ownership]] · [[Borrowing]] · [[Blocking in Async]]

## Sources
- Standard library, `thread_local!` macro — [[std]],
  https://doc.rust-lang.org/std/macro.thread_local.html
- Standard library, `std::thread::LocalKey` — [[std]],
  https://doc.rust-lang.org/std/thread/struct.LocalKey.html
- The Rust Programming Language, ch. 16.1 "Using Threads to Run Code Simultaneously" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-01-threads.html
