---
type: antipattern
title: "Rc RefCell Overuse"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rc, refcell, interior-mutability, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Ownership]]", "[[Borrowing]]", "[[Smart Pointers]]", "[[Interior Mutability]]", "[[Reference Cycles]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-04-rc.html", "https://doc.rust-lang.org/book/ch15-05-interior-mutability.html", "https://doc.rust-lang.org/std/cell/struct.RefCell.html", "https://doc.rust-lang.org/std/rc/struct.Rc.html"]
rust_version: "edition 2024 / 1.85+"
---

# Rc RefCell Overuse

`Rc<RefCell<T>>` overuse is turning ordinary ownership problems into shared mutable runtime borrow checks instead of designing clear owners, borrows, or indices.

## The mistake
`Rc<T>` enables multiple owners in one thread. `RefCell<T>` enables interior mutability checked at runtime. Together, `Rc<RefCell<T>>` is useful for single-threaded graphs, test doubles, and callback-heavy structures that genuinely need shared ownership plus mutation.

The antipattern is using it as the default object model. That recreates "everyone can mutate everything" architecture, except Rust now panics at runtime if the borrow rules are violated.

## Why it happens
The compiler rejects many ambiguous ownership designs. Wrapping data in `Rc<RefCell<_>>` often makes those errors disappear because callers only clone an `Rc` and borrow dynamically later.

The cost is delayed failure. `RefCell` tracks active borrows at runtime; two mutable borrows or a mutable borrow while immutable borrows are live cause a panic. `Rc` can also create reference cycles unless back edges use `Weak<T>`.

Mechanically, `Rc<T>` stores a non-atomic strong count and weak count next to the allocation. Cloning an `Rc` increments the strong count; dropping one decrements it; the inner value drops only when the strong count reaches zero. `RefCell<T>` stores an `UnsafeCell<T>` plus a borrow flag. `borrow()` increments shared state, `borrow_mut()` requires exclusive state, and violations panic.

That makes the combination powerful but blunt: the compiler sees shared ownership of a cell, not your higher-level graph invariant. Every dynamic borrow becomes a runtime contract you must preserve across callbacks, recursion, and logging.

## Example
```rust
#[derive(Debug)]
struct Node {
    label: String,
    children: Vec<usize>,
}

#[derive(Debug)]
struct Arena {
    nodes: Vec<Node>,
}

impl Arena {
    fn add(&mut self, label: impl Into<String>) -> usize {
        let id = self.nodes.len();
        self.nodes.push(Node {
            label: label.into(),
            children: Vec::new(),
        });
        id
    }

    fn link(&mut self, parent: usize, child: usize) {
        self.nodes[parent].children.push(child);
    }
}

fn main() {
    let mut arena = Arena { nodes: Vec::new() };
    let root = arena.add("root");
    let leaf = arena.add("leaf");
    arena.link(root, leaf);

    println!("{} -> {:?}", arena.nodes[root].label, arena.nodes[root].children);
}
```

## Second example: use `Weak` for back edges
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
    let root = Rc::new(Node {
        name: String::from("root"),
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(Vec::new()),
    });

    let leaf = Rc::new(Node {
        name: String::from("leaf"),
        parent: RefCell::new(Rc::downgrade(&root)),
        children: RefCell::new(Vec::new()),
    });

    root.children.borrow_mut().push(Rc::clone(&leaf));

    if let Some(parent) = leaf.parent.borrow().upgrade() {
        println!("{} belongs to {}", leaf.name, parent.name);
    }
}
```

This is a legitimate use: shared identity is part of the model, child lists mutate after allocation, and the parent edge is weak so the tree can be dropped.

## Common errors
Runtime borrow failure:

```text
thread 'main' panicked at 'already borrowed: BorrowMutError'
```

Fix it by ending the earlier `borrow()`/`borrow_mut()` before taking the next borrow, often with a smaller block or by copying out a small value. Avoid calling user callbacks while a `Ref` or `RefMut` is live.

Threading error:

```text
error[E0277]: `Rc<RefCell<T>>` cannot be sent between threads safely
```

Fix it by redesigning ownership for threads. The direct thread-safe analogue is not always `Arc<Mutex<T>>`; a channel, scoped thread, or per-thread owner may be simpler.

## Best practice
- ✅ Model trees with one owner and borrowed access from the root downward.
- ✅ Model graphs with stable IDs, arenas, or slot maps when shared identity matters more than pointer ownership.
- ✅ Use `Rc<RefCell<T>>` when the runtime shape truly requires shared single-threaded mutation and document the borrowing discipline.
- ✅ Use `Weak<T>` for parent links or observer back references to avoid cycles.
- ✅ Prefer returning data from methods over letting callers hold `RefMut` guards while performing unrelated work.
- ✅ Keep `RefCell` fields private when possible so one module owns the dynamic-borrow protocol.

## Pitfalls
- ⚠️ `RefCell` borrow failures are panics, not compile errors.
- ⚠️ Keeping a `RefMut` alive while calling user code invites reentrant borrow panics.
- ⚠️ `Rc<T>` is not thread-safe; do not "upgrade" to threads without revisiting the design. See [[Premature Arc Mutex]].
- ⚠️ Cloning `Rc` handles can obscure who is responsible for ending a lifetime.
- ⚠️ Reference cycles leak memory because strong counts never reach zero.
- ⚠️ `try_borrow` can avoid panics, but it does not make a confused ownership model easier to reason about.

## See also
[[Ownership]] · [[Borrowing]] · [[Smart Pointers]] · [[Interior Mutability]] · [[Reference Cycles]] · [[Premature Arc Mutex]] · [[Needless Clone]] · [[Message Passing]] · [[Shared State]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 15.4 "`Rc<T>`, the Reference Counted Smart Pointer" — [[the-book]], https://doc.rust-lang.org/book/ch15-04-rc.html
- The Rust Programming Language, ch. 15.5 "`RefCell<T>` and the Interior Mutability Pattern" — [[the-book]], https://doc.rust-lang.org/book/ch15-05-interior-mutability.html
- Standard library, `RefCell` — [[the-reference]], https://doc.rust-lang.org/std/cell/struct.RefCell.html
- Standard library, `Rc` — [[the-reference]], https://doc.rust-lang.org/std/rc/struct.Rc.html
