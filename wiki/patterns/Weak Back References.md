---
type: pattern
title: "Weak Back References"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, weak, rc, pattern, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Reference Cycles and Weak]]", "[[Rc]]", "[[RefCell]]", "[[Interior Mutability]]", "[[Rc RefCell Overuse]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-06-reference-cycles.html#preventing-reference-cycles-using-weakt", "https://doc.rust-lang.org/std/rc/struct.Weak.html", "https://doc.rust-lang.org/std/rc/struct.Rc.html"]
rust_version: "edition 2024 / 1.85+"
---

# Weak Back References

Weak back references model non-owning reverse links in `Rc` graphs so that children, observers, or cache entries can find a target without keeping it alive.

## What it is
This pattern separates ownership direction from navigation direction.
Forward edges that determine lifetime use strong [[Rc]] pointers.
Reverse or optional edges use `Weak<T>` because they should not keep the target alive.

The classic example is a tree.
Parents own children with `Rc<Node>`.
Children can point back to parents with `Weak<Node>`.

## How it works
Store `Weak<T>` in the back-reference field.
When wiring the graph, assign `Rc::downgrade(&owner)` into that field.
When reading the back reference, call `upgrade()` and handle the `Option<Rc<T>>`.
This keeps lifetime ownership one-directional even when navigation is bidirectional.
The back reference can disappear at any time after the last strong owner is dropped, so callers must treat absence as a normal state.

The `None` case is part of the design, not an error in the type system.
It says the non-owning target has already been dropped.
Good APIs either expose that possibility directly or remove weak links when their owner goes away.

When mutation is needed to wire links after allocation, put only the changing field in [[RefCell]], not the whole object by default.
For self-references, consider `Rc::new_cyclic`, but store only `Weak<Self>` inside the value; storing `Rc<Self>` inside itself creates a permanent strong cycle.

## Example
```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Panel {
    title: String,
    parent: RefCell<Weak<Panel>>,
}

impl Panel {
    fn parent_title(&self) -> Option<String> {
        self.parent
            .borrow()
            .upgrade()
            .map(|panel| panel.title.clone())
    }
}

fn main() {
    let root = Rc::new(Panel {
        title: String::from("root"),
        parent: RefCell::new(Weak::new()),
    });
    let child = Rc::new(Panel {
        title: String::from("child"),
        parent: RefCell::new(Rc::downgrade(&root)),
    });

    assert_eq!(child.parent_title().as_deref(), Some("root"));
}
```

## Worked example: registry entries that do not keep owners alive
```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Document {
    title: String,
}

#[derive(Default)]
struct Recent {
    entries: RefCell<Vec<Weak<Document>>>,
}

impl Recent {
    fn remember(&self, document: &Rc<Document>) {
        self.entries.borrow_mut().push(Rc::downgrade(document));
    }

    fn live_titles(&self) -> Vec<String> {
        self.entries
            .borrow()
            .iter()
            .filter_map(Weak::upgrade)
            .map(|document| document.title.clone())
            .collect()
    }
}

fn main() {
    let recent = Recent::default();
    let doc = Rc::new(Document {
        title: String::from("notes.md"),
    });

    recent.remember(&doc);
    assert_eq!(recent.live_titles(), vec![String::from("notes.md")]);

    drop(doc);
    assert!(recent.live_titles().is_empty());
}
```

## Common errors
A strong back reference has no immediate compiler error, but it can stop destructors from running because the cycle keeps the strong count above zero.
The fix is to make the reverse edge `Weak<T>` and upgrade only while using it.

`upgrade().unwrap()` can panic when a registry, observer list, or parent link outlives the owner.
Expose `Option`, filter dead weak entries, or prune the list during normal maintenance.

## Best practice
- ✅ Make the strong ownership direction obvious in field names and constructors.
- ✅ Use `Weak<T>` for parent, owner, observer, and cache links that should not extend lifetime.
- ✅ Keep `RefCell` scopes tiny when wiring back references.
- ✅ Return `Option` or a domain-specific result when a weak target has disappeared.
- ✅ Periodically remove dead weak entries from long-lived registries so they do not accumulate stale metadata.
- ✅ Keep the mutable field narrow, such as `RefCell<Weak<Parent>>`, instead of wrapping every node field in [[RefCell]].

## Pitfalls
- ⚠️ Replacing back references with strong `Rc<T>` can create leaks; see [[Reference Cycles and Weak]].
- ⚠️ Calling `upgrade().unwrap()` is only acceptable when a local invariant truly proves the owner is alive.
- ⚠️ Putting every field behind [[RefCell]] makes borrow panics harder to reason about.
- ⚠️ This is a single-threaded pattern with `Rc`; use `Arc` and `Weak` from `std::sync` for thread-shared ownership.
- ⚠️ Weak links do not define ordering or validity beyond the moment of `upgrade`; do not cache raw references derived from an upgraded `Rc`.

## See also
[[Reference Cycles and Weak]] · [[Rc]] · [[RefCell]] · [[Interior Mutability]] · [[Rc RefCell Overuse]] · [[Arc]] · [[Ownership]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.6 "Preventing Reference Cycles Using `Weak<T>`" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-06-reference-cycles.html#preventing-reference-cycles-using-weakt
- Standard library, `std::rc::Weak` - [[std]],
  https://doc.rust-lang.org/std/rc/struct.Weak.html
