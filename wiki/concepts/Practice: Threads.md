---
type: concept
title: "Practice: Threads"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, threads]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Threads]]", "[[Scoped Threads]]", "[[Channels]]", "[[Send and Sync]]", "[[Shared State with Mutex]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Threads

The threads group teaches spawning work, moving data into threads, sending messages, and sharing state safely. The key idea is that thread boundaries make ownership and `Send` requirements explicit.

## What it is
These exercises cover `thread::spawn`, `move` closures, `JoinHandle`, channels, mutex-protected shared state, and atomic reference counting.

## How it works
A spawned thread may outlive the function that created it, so captured values usually need to be moved into the closure. Shared mutable state across threads requires synchronization, commonly `Arc<Mutex<T>>`.

## Example
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let worker_counter = Arc::clone(&counter);

    let handle = thread::spawn(move || {
        let mut value = worker_counter.lock().expect("lock poisoned");
        *value += 1;
    });

    handle.join().expect("thread panicked");
    println!("{}", *counter.lock().expect("lock poisoned"));
}
```

## Best practice
- ✅ Use `move` closures to make thread ownership explicit.
- ✅ Join spawned threads when the result or completion matters.
- ✅ Prefer channels for ownership transfer and mutexes for truly shared state.

## Pitfalls
- ⚠️ Do not use `Rc<T>` across threads; it is not `Send` or `Sync`.
- ⚠️ Do not hold locks longer than needed.
- ⚠️ Handle `join` and `lock` errors deliberately instead of hiding panics.

## See also
[[Practice (Rustlings)]] · [[Threads]] · [[Scoped Threads]] · [[Channels]] · [[Send and Sync]] · [[Shared State with Mutex]] · [[Move Closures with Threads]]

## Sources
- Rustlings `20_threads` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

