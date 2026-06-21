---
type: concept
title: "Arc"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, arc, smart-pointers]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Ownership]]", "[[Shared State with Mutex]]", "[[Arc Mutex Shared State]]", "[[Send and Sync]]", "[[Move Closures with Threads]]", "[[Premature Arc Mutex]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-03-shared-state.html#atomic-reference-counting-with-arct", "https://doc.rust-lang.org/std/sync/struct.Arc.html"]
rust_version: "edition 2024 / 1.85+"
---

# Arc

`Arc<T>` is atomically reference-counted shared ownership: it lets multiple threads own the same allocation when `T` is safe to share across threads.

## What it is
`Arc` stands for atomic reference counting.
It is the thread-safe counterpart to `Rc<T>`: cloning an `Arc<T>` increments an atomic count, and dropping one clone decrements it.
The inner value is dropped when the last strong reference is gone.

`Arc<T>` only gives shared ownership.
It does not by itself make `T` mutable from multiple threads.
For shared mutation, combine it with synchronization such as [[Shared State with Mutex]], [[RwLock]], or [[Atomics]].

## How it works
`Arc::clone(&value)` creates another owner of the same allocation.
The clone is cheap compared with cloning `T`, but it still uses atomic operations.
That cost is why ordinary single-threaded code should prefer `Rc<T>` or plain ownership unless cross-thread ownership is required.

`Arc<T>` implements `Send` and `Sync` only when the contained type satisfies the necessary bounds.
This matters: `Arc<RefCell<T>>` does not become thread-safe merely because it is inside `Arc`.
The protected thing must be safe to share, or be wrapped in a primitive that makes sharing safe.
When the strong count reaches zero, `T` is dropped.
`Weak<T>` references do not keep `T` alive, which is how cyclic ownership graphs avoid leaks.
If an `Arc` is uniquely owned, `Arc::get_mut` can give `&mut T`; if it is shared, `Arc::make_mut` provides clone-on-write mutation.

## Example
```rust
use std::sync::Arc;
use std::thread;

fn main() {
    let words = Arc::new(vec!["fearless", "concurrency", "rust"]);
    let mut handles = Vec::new();

    for index in 0..words.len() {
        let words = Arc::clone(&words);
        handles.push(thread::spawn(move || words[index].len()));
    }

    let total: usize = handles
        .into_iter()
        .map(|handle| handle.join().unwrap())
        .sum();

    println!("total bytes = {total}");
}
```

## Example: clone-on-write before sharing
```rust
use std::sync::Arc;

fn main() {
    let mut config = Arc::new(vec!["base".to_owned()]);

    Arc::make_mut(&mut config).push("local".to_owned());

    let shared = Arc::clone(&config);
    Arc::make_mut(&mut config).push("private copy".to_owned());

    assert_eq!(shared.len(), 2);
    assert_eq!(config.len(), 3);
}
```

## Common errors
Wrapping a non-thread-safe type in `Arc` does not make the inner type safe to share:

```text
error[E0277]: `RefCell<i32>` cannot be shared between threads safely
```

The fix is to use `Arc<Mutex<T>>`, `Arc<RwLock<T>>`, or an atomic type when multiple threads must mutate or coordinate through the value.

## Best practice
- ✅ Use `Arc<T>` for cross-thread shared ownership of immutable data.
- ✅ Add `Mutex`, `RwLock`, or atomics when shared owners also need mutation.
- ✅ Clone `Arc` with `Arc::clone(&x)` to make shared ownership visually explicit.
- ✅ Consider [[Scoped Threads]] when the data only needs to be borrowed during a bounded scope.
- ✅ Use `Weak<T>` for back-pointers or observer lists that must not keep the object alive.

## Pitfalls
- ⚠️ `Arc<T>` is not a synchronization primitive for `T`; `Arc<Vec<T>>` does not permit mutation from several threads.
- ⚠️ `Arc<RefCell<T>>` is not a thread-safe substitute for `Arc<Mutex<T>>`; `RefCell<T>` is not [[Send and Sync]].
- ⚠️ Reaching for `Arc<Mutex<_>>` everywhere can be [[Premature Arc Mutex]].
- ⚠️ Reference cycles can still leak memory; use weak references when ownership graphs can cycle.
- ⚠️ Atomically cloning an `Arc` in a hot loop is not free; pass borrowed references inside [[Scoped Threads]] when possible.

## See also
[[Concurrency]] · [[Ownership]] · [[Shared State with Mutex]] · [[Arc Mutex Shared State]] · [[RwLock]] · [[Atomics]] · [[Send and Sync]] · [[Premature Arc Mutex]]

## Sources
- The Rust Programming Language, ch. 16.3 "Atomic Reference Counting with `Arc<T>`" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html#atomic-reference-counting-with-arct
- Standard library, `std::sync::Arc` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.Arc.html
