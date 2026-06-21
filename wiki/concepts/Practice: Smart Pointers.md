---
type: concept
title: "Practice: Smart Pointers"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, smart-pointers]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Box]]", "[[Rc]]", "[[Arc]]", "[[Deref and DerefMut]]", "[[RefCell]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Smart Pointers

The smart pointers group teaches heap allocation, shared ownership, deref coercions, and runtime borrow checking. The key idea is that each pointer type buys a specific capability with a specific constraint.

## What it is
These exercises cover `Box<T>`, `Rc<T>`, `Arc<T>`, `Deref`, reference counts, and interior mutability patterns used with shared ownership.

## How it works
`Box<T>` owns one heap allocation. `Rc<T>` enables single-threaded shared ownership, while `Arc<T>` enables atomic shared ownership across threads. `RefCell<T>` moves borrowing checks from compile time to runtime.

## Example
```rust
use std::rc::Rc;

#[derive(Debug)]
struct Node {
    name: String,
}

fn main() {
    let shared = Rc::new(Node { name: String::from("root") });
    let left = Rc::clone(&shared);
    let right = Rc::clone(&shared);

    println!("{} {} {}", shared.name, left.name, right.name);
}
```

## Best practice
- ✅ Use `Box<T>` for ownership indirection and recursive types.
- ✅ Use `Rc<T>` only for single-threaded shared ownership.
- ✅ Use `Arc<T>` for shared ownership that crosses thread boundaries.

## Pitfalls
- ⚠️ `Rc<T>` is not thread-safe; use `Arc<T>` when sharing across threads.
- ⚠️ `RefCell<T>` can panic at runtime if borrow rules are violated.
- ⚠️ Shared ownership can create reference cycles unless weak references break back edges.

## See also
[[Practice (Rustlings)]] · [[Box]] · [[Rc]] · [[Arc]] · [[Deref and DerefMut]] · [[RefCell]] · [[Smart Pointers & Interior Mutability]]

## Sources
- Rustlings `19_smart_pointers` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

