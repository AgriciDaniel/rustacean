---
type: pattern
title: "Move Closures with Threads"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, threads, closures]
domain: "Concurrency"
difficulty: basic
related: ["[[Threads]]", "[[Ownership]]", "[[Move Semantics]]", "[[Send and Sync]]", "[[Scoped Threads]]", "[[Needless Clone]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch16-01-threads.html#using-move-closures-with-threads", "https://doc.rust-lang.org/reference/types/closure.html#other-traits", "https://doc.rust-lang.org/std/thread/fn.spawn.html"]
rust_version: "edition 2024 / 1.85+"
---

# Move Closures with Threads

Use `move ||` with `thread::spawn` when the spawned thread needs values from the parent scope; it transfers ownership into the closure instead of borrowing stack data that may disappear.

## What it is
A `move` closure captures used variables by value.
For spawned threads, that is usually exactly what you want: the new thread owns its inputs, and the parent can no longer invalidate them.

Without `move`, the compiler may infer a borrow because the closure body only reads the value.
That borrow is not valid for `thread::spawn`, because the spawned thread can outlive the function that created it.

## How it works
`thread::spawn` requires `F: FnOnce() -> T + Send + 'static`.
The `Send` bound says the closure can cross into another thread.
The `'static` bound says the closure does not contain borrowed references that might expire before the worker is done.

`move` does not bypass ownership.
After a `Vec<T>` or `String` is moved into the closure, the parent binding is no longer usable.
If both threads need access, choose a different design: clone cheap data intentionally, use [[Arc]] for shared ownership, use [[Channels]] to transfer values, or use [[Scoped Threads]] for bounded borrows.
The closure is usually `FnOnce` because it may consume captured values.
That matches `thread::spawn`: the closure runs once on the new thread, then its captured environment is dropped on that thread when the closure finishes.

## Example
```rust
use std::thread;

fn main() {
    let values = vec![2, 4, 6, 8];

    let handle = thread::spawn(move || {
        values.into_iter().sum::<i32>()
    });

    let total = handle.join().expect("worker thread panicked");
    println!("sum = {total}");
}
```

## Example: split ownership before spawning
```rust
use std::thread;

fn main() {
    let jobs = vec!["parse", "index", "render", "ship"];
    let first_half = jobs[..2].to_vec();
    let second_half = jobs[2..].to_vec();

    let first = thread::spawn(move || first_half.join(","));
    let second = thread::spawn(move || second_half.join(","));

    println!("{} / {}", first.join().unwrap(), second.join().unwrap());
}
```

## Common errors
Without `move`, `thread::spawn` often borrows a local:

```text
error[E0373]: closure may outlive the current function, but it borrows `values`
help: to force the closure to take ownership of `values`, use the `move` keyword
```

After adding `move`, using the moved value in the parent fails:

```text
error[E0382]: use of moved value: `values`
```

The fix is to decide ownership explicitly: parent no longer uses it, parent clones a cheap value, both share through [[Arc]], or both borrow within [[Scoped Threads]].

## Best practice
- ✅ Use `move` on closures passed to `thread::spawn` whenever they capture parent-scope values.
- ✅ Move owned input data into workers when the parent no longer needs it.
- ✅ Use [[Scoped Threads]] when a worker should borrow stack data only until a lexical scope ends.
- ✅ Clone deliberately and visibly when the data is small or immutable sharing via [[Arc]] is the real intent.
- ✅ Prepare per-thread input before spawning so each closure owns exactly the data it needs.

## Pitfalls
- ⚠️ Treating `move` as a workaround for lifetimes misses the design point; ownership is transferred, not magically extended.
- ⚠️ Cloning large buffers just to satisfy `thread::spawn` can become [[Needless Clone]]; prefer ownership transfer, slices with scoped threads, or channels.
- ⚠️ Moving `Rc<T>` into a thread fails because `Rc<T>` is not [[Send and Sync]]; use [[Arc]] when shared ownership must cross threads.
- ⚠️ Capturing a lock guard in a spawned closure often extends the critical section too far; see [[Holding Locks Too Long]].
- ⚠️ `move` copies `Copy` captures but moves non-`Copy` captures; do not assume every capture invalidates the parent binding.

## See also
[[Concurrency]] · [[Threads]] · [[Scoped Threads]] · [[Ownership]] · [[Move Semantics]] · [[Send and Sync]] · [[Arc]] · [[Channels]] · [[Needless Clone]]

## Sources
- The Rust Programming Language, ch. 16.1 "Using `move` Closures with Threads" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-01-threads.html#using-move-closures-with-threads
- The Rust Reference, "Closure types: other traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/closure.html#other-traits
- Standard library, `std::thread::spawn` — [[std]],
  https://doc.rust-lang.org/std/thread/fn.spawn.html
