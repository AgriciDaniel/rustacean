---
type: antipattern
title: "Long-Lived RefCell Borrows"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, refcell, borrowing, antipattern, interior-mutability]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[RefCell]]", "[[Interior Mutability]]", "[[Rc]]", "[[Rc RefCell Overuse]]", "[[Borrowing]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-05-interior-mutability.html#tracking-borrows-at-runtime", "https://doc.rust-lang.org/std/cell/struct.RefCell.html"]
rust_version: "edition 2024 / 1.85+"
---

# Long-Lived RefCell Borrows

Long-lived `RefCell` borrow guards are a footgun because the runtime borrow remains active until the guard is dropped, often much longer than the programmer intended.

## The mistake
The mistake is treating `cell.borrow()` or `cell.borrow_mut()` like a momentary operation when it actually returns a guard.
That guard keeps the shared or mutable borrow active for its whole lexical lifetime.

The bug often appears when code stores a `RefMut<T>` in a variable and then calls another method that also tries to borrow the same `RefCell<T>`.
The compiler accepts this because `RefCell<T>` checks at runtime, but the program can panic with a borrow error.

## Why it happens
`RefCell<T>` deliberately moves borrow enforcement from compile time to runtime.
`borrow()` increments the active shared-borrow state.
`borrow_mut()` marks an active exclusive borrow.
Those states are reset only when the returned `Ref<T>` or `RefMut<T>` guard is dropped.

Temporaries usually drop at the end of the statement.
Named guards last until the end of their scope unless you introduce a smaller block or call `drop(guard)`.
This matters around callbacks, logging hooks, observers, UI updates, and any code that can reenter the same object.
Non-lexical lifetimes can shorten ordinary reference borrows, but a `RefMut<T>` is still a value with a destructor.
The runtime borrow state is released when that guard is dropped, so the safest fix is often a visible block around the exact mutation.

## Example
```rust
use std::cell::RefCell;

struct Queue {
    items: RefCell<Vec<String>>,
}

impl Queue {
    fn push(&self, item: &str) {
        self.items.borrow_mut().push(item.to_owned());
    }

    fn len_after_push(&self, item: &str) -> usize {
        {
            let mut items = self.items.borrow_mut();
            items.push(item.to_owned());
        }

        self.items.borrow().len()
    }
}

fn main() {
    let queue = Queue {
        items: RefCell::new(Vec::new()),
    };
    queue.push("first");
    assert_eq!(queue.len_after_push("second"), 2);
}
```

## Common errors
The usual failure is a runtime panic, not a compiler diagnostic:

```text
thread 'main' panicked at src/main.rs:18:20:
RefCell already mutably borrowed
```

It often comes from code shaped like this: hold `let mut items = self.items.borrow_mut();`, then call a helper that also borrows `self.items`.
Move the helper call after the guard's block, or extract the data the helper needs before taking the mutable borrow.

`try_borrow_mut()` turns the same conflict into a recoverable `BorrowMutError`.
Use it when reentrancy is expected, but do not use it to paper over unclear ownership in core logic.

## Worked example: callback after the guard drops
```rust
use std::cell::RefCell;

struct Notifier {
    events: RefCell<Vec<String>>,
}

impl Notifier {
    fn push_then_notify(&self, event: &str, notify: impl FnOnce(usize)) {
        let len = {
            let mut events = self.events.borrow_mut();
            events.push(event.to_owned());
            events.len()
        };

        notify(len);
    }
}

fn main() {
    let notifier = Notifier {
        events: RefCell::new(Vec::new()),
    };

    notifier.push_then_notify("saved", |len| assert_eq!(len, 1));
}
```

## Best practice
- ✅ Keep `Ref` and `RefMut` guards in the smallest block that needs access.
- ✅ Extract the value you need, drop the guard, then call other methods or user-provided code.
- ✅ Use `try_borrow` and `try_borrow_mut` where borrow conflicts are expected and recoverable.
- ✅ Prefer plain `&mut self` when the operation does not truly require [[Interior Mutability]].
- ✅ Name guard variables deliberately (`items_guard`, `state`) so their lifetime is visible during review.
- ✅ In callback-heavy code, compute a snapshot first, release the guard, then invoke observers.

## Pitfalls
- ⚠️ A named `RefMut` can stay alive across far more code than intended.
- ⚠️ Calling callbacks while holding a `RefMut` invites reentrant borrow panics.
- ⚠️ Chaining `borrow_mut()` through complex expressions can hide where the guard lives.
- ⚠️ Using [[Rc]] plus [[RefCell]] broadly can turn ordinary control-flow mistakes into runtime panics; see [[Rc RefCell Overuse]].
- ⚠️ Returning guards from helper functions extends the dynamic borrow into the caller; document that explicitly or return copied/owned data instead.

## See also
[[RefCell]] · [[Interior Mutability]] · [[Rc]] · [[Rc RefCell Overuse]] · [[Borrowing]] · [[Deref and DerefMut]] · [[Reference Cycles and Weak]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.5 "Tracking Borrows at Runtime" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-05-interior-mutability.html#tracking-borrows-at-runtime
- Standard library, `std::cell::RefCell` - [[std]],
  https://doc.rust-lang.org/std/cell/struct.RefCell.html
