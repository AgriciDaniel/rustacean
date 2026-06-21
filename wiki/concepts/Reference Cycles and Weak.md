---
type: concept
title: "Reference Cycles and Weak"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, weak, rc, reference-cycles, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Rc]]", "[[RefCell]]", "[[Interior Mutability]]", "[[Weak Back References]]", "[[Rc RefCell Overuse]]", "[[Ownership]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-06-reference-cycles.html", "https://doc.rust-lang.org/std/rc/struct.Weak.html", "https://doc.rust-lang.org/std/rc/struct.Rc.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Reference Cycles"]
---

# Reference Cycles and Weak

Reference cycles happen when strong reference-counted owners keep each other alive forever; `Weak<T>` represents a non-owning edge that can break the cycle.

## What it is
`Rc<T>` drops its allocation only when the strong count reaches zero.
If two or more values hold strong `Rc` links in a cycle, each keeps the other alive, so the values are leaked even though the program remains memory safe.

`Weak<T>` is the standard non-owning companion to `Rc<T>`.
It points at the same allocation but does not increase the strong count and therefore does not keep the value alive.

## How it works
Create a weak pointer with `Rc::downgrade(&rc)`.
The weak count increases, but the strong count does not.
To use the value later, call `weak.upgrade()`, which returns `Option<Rc<T>>`.

`Some(rc)` means at least one strong owner still exists and the value is alive.
`None` means the value has already been dropped.
This explicit `Option` prevents dangling pointer access.
When the strong count reaches zero, the inner `T` is dropped even if weak handles still exist.
The allocation's bookkeeping remains only long enough for existing `Weak<T>` handles to observe that upgrade now fails.

Use strong `Rc<T>` for ownership edges and `Weak<T>` for observation, parent links, cache entries, or back references.
The Book's tree example uses strong child links and weak parent links because children should not keep parents alive.
`Rc::new_cyclic` can build a value that stores a weak pointer to itself, but `upgrade()` inside the construction closure returns `None` because the `Rc<T>` is not fully initialized yet.

## Example
```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Node {
    name: String,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}

fn main() {
    let leaf = Rc::new(Node {
        name: String::from("leaf"),
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(Vec::new()),
    });

    let branch = Rc::new(Node {
        name: String::from("branch"),
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

    let parent = leaf.parent.borrow().upgrade().unwrap();
    assert_eq!(parent.name.as_str(), "branch");
    assert_eq!(branch.children.borrow().len(), 1);
}
```

## Worked example: observing expiration
```rust
use std::rc::{Rc, Weak};

fn main() {
    let weak: Weak<String>;

    {
        let owner = Rc::new(String::from("session"));
        weak = Rc::downgrade(&owner);
        assert_eq!(weak.upgrade().as_deref().map(String::as_str), Some("session"));
        assert_eq!(Rc::strong_count(&owner), 1);
        assert_eq!(Rc::weak_count(&owner), 1);
    }

    assert!(weak.upgrade().is_none());
}
```

## Common errors
The cycle bug usually has no compiler error and no panic.
The symptom is that `Drop` for the nodes never runs because strong counts never reach zero.
Add a small `Drop` log in tests or assert expected `strong_count` changes while designing graph ownership.

Calling `upgrade().unwrap()` can panic after the owner is dropped:

```text
called `Option::unwrap()` on a `None` value
```

Return `Option<Rc<T>>`, remove stale entries, or convert absence into a domain-specific error instead of assuming the weak target is alive.

## Best practice
- ✅ Draw ownership edges explicitly: strong `Rc` owns, `Weak` observes.
- ✅ Use `Weak` for parent pointers, subscribers, caches, and other back links.
- ✅ Always handle `upgrade()` returning `None`.
- ✅ Add tests or review checks for cyclic graph structures that combine [[Rc]] and [[RefCell]].
- ✅ Prefer acyclic ownership plus indexes or IDs when graph lifetime has a natural arena or table owner.
- ✅ Use `std::sync::Weak` with [[Arc]] for thread-shared graphs; do not mix it up with `std::rc::Weak`.

## Pitfalls
- ⚠️ Rust does not automatically detect `Rc` cycles; leaks are memory safe but still bugs.
- ⚠️ `Weak<T>` cannot be used directly as `&T`; upgrading is required because the target may be gone.
- ⚠️ Using strong `Rc` for every graph edge can make lifetimes impossible to reason about.
- ⚠️ Debug-printing a strong cycle can recurse until stack overflow.
- ⚠️ `Weak` solves lifetime ownership cycles, not logical cycles in algorithms; traversal still needs visited sets when cycles are possible.

## See also
[[Rc]] · [[RefCell]] · [[Interior Mutability]] · [[Weak Back References]] · [[Rc RefCell Overuse]] · [[Ownership]] · [[The Drop Trait]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.6 "Reference Cycles Can Leak Memory" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-06-reference-cycles.html
- Standard library, `std::rc::Weak` - [[std]],
  https://doc.rust-lang.org/std/rc/struct.Weak.html
