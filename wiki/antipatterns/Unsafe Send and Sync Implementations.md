---
type: antipattern
title: "Unsafe Send and Sync Implementations"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, unsafe, send, sync]
domain: "Concurrency"
difficulty: advanced
related: ["[[Send and Sync]]", "[[Arc]]", "[[Shared State with Mutex]]", "[[Atomics]]", "[[Threads]]", "[[Unsafe Rust]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html#implementing-send-and-sync-manually-is-unsafe", "https://doc.rust-lang.org/reference/special-types-and-traits.html#auto-traits", "https://doc.rust-lang.org/nomicon/send-and-sync.html"]
rust_version: "edition 2024 / 1.85+"
---

# Unsafe Send and Sync Implementations

Unsafe `Send` or `Sync` implementations are a footgun when used to silence compiler errors; they are only valid when you can prove the type's cross-thread invariants yourself.

## The mistake
The compiler rejects moving or sharing a type across threads because one of its parts is not thread-safe.
Instead of redesigning ownership or synchronization, code adds `unsafe impl Send` or `unsafe impl Sync` to the wrapper.

That does not make the data safe.
It tells the compiler and other unsafe code that the data was already safe under an invariant the compiler cannot see.
If the promise is false, the result can be undefined behavior.

## Why it happens
`Send` and `Sync` are auto traits, so most ordinary Rust types just work.
When they do not, the error appears at a boundary like `thread::spawn`, which can make the marker trait look like an arbitrary obstacle.
It is not arbitrary: it is the type system preventing an unsynchronized cross-thread access pattern.

Manual implementations are appropriate for low-level synchronization primitives, carefully wrapped foreign handles, and other types whose safety depends on external invariants.
They are not appropriate for `Rc`, `RefCell`, raw pointers, or FFI handles unless you have a documented synchronization story.
`unsafe impl Send` allows ownership to move to another thread.
`unsafe impl Sync` is stronger in a different direction: it allows `&T` to be shared from multiple threads, so every method callable through `&self` must be thread-safe under the promised invariant.

## Example
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // Correct alternative: use a synchronization primitive whose Send/Sync
    // implementations are supplied by the standard library.
    let value = Arc::new(Mutex::new(0_usize));
    let worker_value = Arc::clone(&value);

    let worker = thread::spawn(move || {
        *worker_value.lock().unwrap() += 1;
    });

    worker.join().unwrap();
    println!("{}", *value.lock().unwrap());
}
```

## Example: what a safety argument must cover
```rust
use std::sync::Mutex;

struct Handle {
    raw: *mut u8,
    lock: Mutex<()>,
}

// SAFETY: all operations that dereference `raw` would take `lock`; the pointed
// resource outlives `Handle`; no method exposes `raw` or aliases it without
// synchronization.
unsafe impl Send for Handle {}

// SAFETY: shared references are safe because `&self` methods synchronize all
// access through `lock`, and mutation of the foreign resource never happens
// without that lock.
unsafe impl Sync for Handle {}

fn main() {
    let mut byte = 1_u8;
    let handle = Handle {
        raw: &mut byte,
        lock: Mutex::new(()),
    };
    let _guard = handle.lock.lock().unwrap();
    assert!(!handle.raw.is_null());
}
```

## Common errors
The compiler error that tempts this antipattern is usually:

```text
error[E0277]: `*mut T` cannot be sent between threads safely
help: the trait `Send` is not implemented for `*mut T`
```

The safe fix is often to keep the raw pointer thread-confined, wrap access in [[Shared State with Mutex]], or move ownership through an API that proves exclusive access.
If the only proposed fix is `unsafe impl`, the design is not ready.

## Best practice
- ✅ Prefer composing safe primitives: [[Arc]], [[Shared State with Mutex]], [[RwLock]], and [[Atomics]].
- ✅ Let compiler-derived `Send` and `Sync` stand for ordinary structs.
- ✅ If an unsafe impl is genuinely necessary, write a safety comment explaining ownership, aliasing, and synchronization invariants.
- ✅ Keep wrappers around raw handles small, private, and tested at their thread-safety boundary.
- ✅ Audit every `&self` method before implementing `Sync`; shared-reference methods are the surface area being promised safe.

## Pitfalls
- ⚠️ `unsafe impl Send` for a raw pointer wrapper does not make pointed-to data synchronized.
- ⚠️ Marking a type `Sync` is stronger than allowing moves; it permits shared references from multiple threads.
- ⚠️ Hiding `Rc<RefCell<T>>` inside a newtype and declaring it thread-safe is unsound unless external synchronization really exists.
- ⚠️ Negative implementations for your own auto-trait opt-outs are not stable user-facing syntax; do not design stable code around them.
- ⚠️ Depending on mutex poisoning for memory safety is invalid; poisoning is advisory and can be skipped in some panic contexts.

## See also
[[Concurrency]] · [[Send and Sync]] · [[Arc]] · [[Shared State with Mutex]] · [[RwLock]] · [[Atomics]] · [[Threads]] · [[Unsafe Rust]] · [[Ownership]]

## Sources
- The Rust Programming Language, ch. 16.4 "Implementing `Send` and `Sync` Manually Is Unsafe" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html#implementing-send-and-sync-manually-is-unsafe
- The Rust Reference, "Auto traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html#auto-traits
- The Rustonomicon, "Send and Sync" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/send-and-sync.html
