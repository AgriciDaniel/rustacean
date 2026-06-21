---
type: concept
title: "Rc"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rc, reference-counting, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Ownership]]", "[[Box]]", "[[RefCell]]", "[[Reference Cycles and Weak]]", "[[Arc]]", "[[Rc RefCell Overuse]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-04-rc.html", "https://doc.rust-lang.org/std/rc/struct.Rc.html"]
rust_version: "edition 2024 / 1.85+"
---

# Rc

`Rc<T>` is single-threaded reference-counted shared ownership: cloning it creates another owner of the same allocation, and the value drops when the last strong owner is gone.

## What it is
`Rc` stands for reference counting.
It is useful when one value is conceptually owned by multiple parts of a single-threaded program and the compiler cannot know which owner will finish last.

`Rc<T>` gives shared ownership, not shared mutation.
Through an `Rc<T>`, callers normally get shared access to `T`; use [[RefCell]] inside `Rc` only when the design genuinely needs single-threaded shared mutation.

## How it works
`Rc::new(value)` allocates `value` and starts the strong reference count at 1.
`Rc::clone(&rc)` creates another `Rc<T>` handle to the same allocation and increments the strong count.
Dropping an `Rc<T>` decrements the strong count.
When it reaches zero, Rust drops the inner `T`.
The allocation also tracks weak references used by [[Reference Cycles and Weak]].
Weak references do not keep `T` alive, but the allocation metadata remains until both the strong count is zero and the weak handles are gone.

The Book recommends `Rc::clone(&value)` rather than `value.clone()` to make reference-count increments visually distinct from deep data clones.
`Rc<T>` is not atomic and is not for cross-thread sharing; use [[Arc]] for thread-safe reference counting.
If an `Rc<T>` is uniquely owned, `Rc::get_mut` can return `&mut T`.
If cloning on write is acceptable and `T: Clone`, `Rc::make_mut` gives mutable access by cloning the inner value when other strong owners exist.

## Example
```rust
use std::rc::Rc;

#[derive(Debug)]
struct Config {
    app_name: String,
}

fn main() {
    let shared = Rc::new(Config {
        app_name: String::from("vault"),
    });

    let left_panel = Rc::clone(&shared);
    let right_panel = Rc::clone(&shared);

    assert_eq!(Rc::strong_count(&shared), 3);
    assert_eq!(left_panel.app_name.as_str(), "vault");

    drop(right_panel);
    assert_eq!(Rc::strong_count(&shared), 2);
}
```

## Worked example: clone-on-write with `Rc::make_mut`
```rust
use std::rc::Rc;

fn main() {
    let mut left = Rc::new(vec![1, 2, 3]);
    let right = Rc::clone(&left);

    Rc::make_mut(&mut left).push(4);

    assert_eq!(&*left, &[1, 2, 3, 4]);
    assert_eq!(&*right, &[1, 2, 3]);
    assert_eq!(Rc::strong_count(&left), 1);
    assert_eq!(Rc::strong_count(&right), 1);
}
```

`make_mut` is useful when most values are shared read-only, but an occasional writer can pay for a clone instead of requiring [[RefCell]].

## Common errors
`E0382` appears when trying to share a `Box<T>` or owned value by moving it twice:

```text
error[E0382]: use of moved value: `a`
```

The fix is not usually a deep clone of the whole structure; use `Rc::new(a)` and `Rc::clone(&a)` when the model is shared ownership.

`E0277` appears when sending `Rc<T>` to another thread:

```text
error[E0277]: `Rc<T>` cannot be sent between threads safely
```

Use [[Arc]] for cross-thread shared ownership, and pair it with [[Shared State with Mutex]], [[RwLock]], or [[Atomics]] when mutation is needed.

## Best practice
- ✅ Use `Rc<T>` for immutable shared data in one thread.
- ✅ Write `Rc::clone(&x)` when adding another owner.
- ✅ Use [[Reference Cycles and Weak]] for parent links, caches, observers, or any relationship that should not keep the target alive.
- ✅ Prefer plain ownership, borrowing, or indexes when the ownership graph has a clear owner.
- ✅ Reach for `Rc::get_mut` or `Rc::make_mut` before `Rc<RefCell<T>>` when mutation happens only while a handle is unique or can be clone-on-write.
- ✅ Keep count assertions in tests only; production logic should rarely depend on exact `strong_count` values.

## Pitfalls
- ⚠️ `Rc<T>` is not `Send` or `Sync`; use [[Arc]] when ownership crosses threads.
- ⚠️ `Rc<T>` does not permit mutable access by itself.
- ⚠️ `Rc<RefCell<T>>` is powerful but easy to overuse; see [[Rc RefCell Overuse]].
- ⚠️ Strong `Rc` cycles leak memory because counts never reach zero; see [[Reference Cycles and Weak]].
- ⚠️ `Rc::make_mut` can clone unexpectedly when another strong owner exists; this is a feature, but it should be visible in performance-sensitive code.

## See also
[[Ownership]] · [[Box]] · [[RefCell]] · [[Reference Cycles and Weak]] · [[Weak Back References]] · [[Arc]] · [[Rc RefCell Overuse]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.4 "`Rc<T>`, the Reference-Counted Smart Pointer" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-04-rc.html
- Standard library, `std::rc::Rc` - [[std]],
  https://doc.rust-lang.org/std/rc/struct.Rc.html
