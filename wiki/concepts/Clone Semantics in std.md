---
type: concept
title: "Clone Semantics in std"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, clone, copy, ownership]
domain: "std: Core Trait Catalog"
difficulty: basic
related: ["[[Copy and Clone]]", "[[Needless Clone]]", "[[Ownership]]", "[[Move Semantics]]"]
sources: ["[[std]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/clone/trait.Clone.html", "https://doc.rust-lang.org/std/marker/trait.Copy.html", "https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html"]
rust_version: "edition 2024 / 1.85+"
---

# Clone Semantics in std

`Clone` is explicit duplication, while `Copy` is implicit duplication for small value-like types; a clone may allocate, share ownership, or run arbitrary code.

## What it is
`Clone` has one required method: `fn clone(&self) -> Self`.
Calling it always produces a new value.
That new value may or may not own independent underlying data.

`Copy` is different.
It is a marker trait for values that can be duplicated implicitly by assignment, argument passing, and pattern binding.
Every `Copy` type must also implement `Clone`.
For `Copy` types, cloning should be equivalent to dereferencing a shared reference.

The existing note [[Copy and Clone]] covers the basic user-facing distinction.
This note highlights the standard-library contract for implementors and generic code.

## How it works
Deriving `Clone` calls `clone()` on each field.
Deriving `Copy` is possible only when all fields are `Copy`.
For generic structs, derive may add bounds on generic parameters.
Sometimes those bounds are stronger than necessary.
The standard docs show function-pointer wrappers as a case where manual impls avoid unnecessary `T: Clone` and `T: Copy` bounds.

Cloning smart pointers is especially important.
`Rc<T>` and `Arc<T>` clones share the same allocation and increment a reference count.
`Arc<Mutex<T>>` clones share the same mutable state protected by the same mutex.
That is often intended, but it is not a deep copy.

`Clone::clone_from` is a provided method.
Types can override it to reuse allocation in an existing destination.
Most code calls `clone`; collection implementations can benefit from `clone_from`.

## Example
```rust
use std::sync::{Arc, Mutex};

#[derive(Clone)]
struct SharedLog {
    lines: Arc<Mutex<Vec<String>>>,
}

impl SharedLog {
    fn push(&self, line: impl Into<String>) {
        self.lines.lock().unwrap().push(line.into());
    }

    fn snapshot(&self) -> Vec<String> {
        self.lines.lock().unwrap().clone()
    }
}

fn main() {
    let first = SharedLog {
        lines: Arc::new(Mutex::new(Vec::new())),
    };
    let second = first.clone();

    first.push("started");
    second.push("ready");

    assert_eq!(first.snapshot(), vec!["started", "ready"]);
}
```

## Best practice
- ✅ Derive `Clone` when fieldwise duplication is exactly the intended behavior.
- ✅ Derive `Copy` only for small, plain, value-like types with no destructor and no surprising ownership cost.
- ✅ Make cloning cost visible in API names and docs when it can allocate or share mutable state.
- ✅ Prefer borrowing over cloning when the caller only needs temporary access.
- ✅ Use `Arc::clone(&value)` style when you want to emphasize reference-counted sharing.

## Pitfalls
- ⚠️ Do not use `.clone()` as the first response to borrow-checker errors; see [[Needless Clone]].
- ⚠️ Do not assume `#[derive(Clone)]` performs a deep copy through `Arc`, `Rc`, or references.
- ⚠️ Do not manually implement `Clone` for a `Copy` type with behavior different from `*self`.
- ⚠️ Do not derive bounds blindly when a generic wrapper can be copied regardless of `T`.

## See also
[[std: Core Trait Catalog]] · [[Copy and Clone]] · [[Needless Clone]] · [[Ownership]] · [[Move Semantics]] · [[Borrowing]] · [[Arc]] · [[Rc]] · [[Shared State with Mutex]] · [[Deriving Traits on Structs]]

## Sources
- Rust standard library, `std::clone::Clone` - [[std]], https://doc.rust-lang.org/std/clone/trait.Clone.html
- Rust standard library, `std::marker::Copy` - [[std]], https://doc.rust-lang.org/std/marker/trait.Copy.html
- The Rust Programming Language, ownership - [[the-book]], https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
