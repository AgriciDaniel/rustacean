---
type: concept
title: "RefCell"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, refcell, interior-mutability, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Interior Mutability]]", "[[Cell]]", "[[Rc]]", "[[Deref and DerefMut]]", "[[Long-Lived RefCell Borrows]]", "[[Rc RefCell Overuse]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-05-interior-mutability.html", "https://doc.rust-lang.org/std/cell/struct.RefCell.html"]
rust_version: "edition 2024 / 1.85+"
---

# RefCell

`RefCell<T>` is a single-owner interior-mutability container that enforces Rust's borrowing rules at runtime instead of compile time.

## What it is
`RefCell<T>` lets code borrow an inner `T` through `borrow()` and `borrow_mut()` even when the `RefCell<T>` itself is reached through a shared reference.
It is useful when a memory-safe access pattern is too dynamic for the compiler to prove.

The tradeoff is timing and failure mode.
References and `Box<T>` reject invalid borrows at compile time.
`RefCell<T>` accepts the code but panics at runtime if borrowing rules are violated.

## How it works
`borrow()` returns `Ref<T>`, a smart pointer for a shared borrow.
`borrow_mut()` returns `RefMut<T>`, a smart pointer for an exclusive borrow.
Both implement [[Deref and DerefMut]] as appropriate, so the guards behave like references while they are alive.

Internally, `RefCell<T>` tracks active borrows.
Many shared borrows are allowed.
One mutable borrow is allowed.
A mutable borrow while shared borrows exist, or a second mutable borrow, causes a panic.
The tracking is stored beside the value, and the state is updated when `Ref` or `RefMut` guards are created and dropped.
This is why the lifetime of the guard, not the visual length of the expression, determines whether a later borrow is legal.

`try_borrow()` and `try_borrow_mut()` expose the same runtime check without panicking.
They return `Result<Ref<'_, T>, BorrowError>` or `Result<RefMut<'_, T>, BorrowMutError>`, which is better for caches, UI event loops, and other code where reentrancy is possible.

`RefCell<T>` is for single-threaded code.
For thread-safe shared mutation, use [[Shared State with Mutex]], [[RwLock]], or [[Atomics]] depending on the problem.

## Example
```rust
use std::cell::RefCell;

struct Recorder {
    events: RefCell<Vec<String>>,
}

impl Recorder {
    fn record(&self, event: &str) {
        self.events.borrow_mut().push(event.to_owned());
    }

    fn count(&self) -> usize {
        self.events.borrow().len()
    }
}

fn main() {
    let recorder = Recorder {
        events: RefCell::new(Vec::new()),
    };

    recorder.record("opened");
    recorder.record("saved");
    assert_eq!(recorder.count(), 2);
}
```

## Worked example: handling borrow conflicts
```rust
use std::cell::RefCell;

struct Scratch {
    buffer: RefCell<String>,
}

impl Scratch {
    fn append_if_free(&self, text: &str) -> bool {
        if let Ok(mut buffer) = self.buffer.try_borrow_mut() {
            buffer.push_str(text);
            true
        } else {
            false
        }
    }
}

fn main() {
    let scratch = Scratch {
        buffer: RefCell::new(String::new()),
    };

    let held = scratch.buffer.borrow();
    assert!(!scratch.append_if_free("busy"));
    drop(held);

    assert!(scratch.append_if_free("free"));
    assert_eq!(scratch.buffer.borrow().as_str(), "free");
}
```

## Common errors
A conflicting `borrow_mut()` panics at runtime rather than producing a compile error:

```text
thread 'main' panicked at src/main.rs:10:25:
RefCell already borrowed
```

The fix is to shorten the `Ref`/`RefMut` guard scope, call `drop(guard)` before the next borrow, or use `try_borrow_mut()` and handle the error.

`E0277` appears if a `RefCell<T>` is shared across threads because it is not `Sync`.
Use [[Shared State with Mutex]] or [[RwLock]] when multiple threads must access the same mutable value.

## Best practice
- ✅ Use `RefCell<T>` when the public API must take `&self` but internal bookkeeping must mutate.
- ✅ Keep `Ref` and `RefMut` guards in the smallest possible scope.
- ✅ Prefer `try_borrow` and `try_borrow_mut` when a borrow conflict should be handled instead of panicking.
- ✅ Combine with [[Rc]] only when the data truly needs shared single-threaded ownership and mutation.
- ✅ Borrow the smallest field that needs dynamic checking; `RefCell<Vec<T>>` is often clearer than `RefCell<WholeObject>`.
- ✅ Extract plain values from a guard before calling callbacks, logging hooks, or methods that may reenter the same object.

## Pitfalls
- ⚠️ Borrow conflicts are runtime panics with `borrow` and `borrow_mut`.
- ⚠️ Holding a guard while calling user code can create reentrant panics; see [[Long-Lived RefCell Borrows]].
- ⚠️ `RefCell<T>` is not thread-safe and is not a substitute for [[Shared State with Mutex]].
- ⚠️ `Rc<RefCell<T>>` can hide unclear ownership and create cycles; see [[Rc RefCell Overuse]] and [[Reference Cycles and Weak]].
- ⚠️ Returning `Ref<T>` or `RefMut<T>` from public APIs exposes dynamic-borrow lifetime constraints to callers; often a closure-based method or copied value is easier to use.

## See also
[[Interior Mutability]] · [[Cell]] · [[Rc]] · [[Deref and DerefMut]] · [[Long-Lived RefCell Borrows]] · [[Rc RefCell Overuse]] · [[Shared State with Mutex]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.5 "`RefCell<T>` and the Interior Mutability Pattern" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-05-interior-mutability.html
- Standard library, `std::cell::RefCell` - [[std]],
  https://doc.rust-lang.org/std/cell/struct.RefCell.html
