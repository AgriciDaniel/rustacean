---
type: concept
title: "Copy and Clone"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, copy, clone]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Move Semantics]]", "[[The Drop Trait]]", "[[The Stack and the Heap]]", "[[Needless Clone]]", "[[Derive Macros]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/book/appendix-03-derivable-traits.html#clone-and-copy-for-duplicating-values", "https://doc.rust-lang.org/std/clone/trait.Clone.html", "https://doc.rust-lang.org/core/marker/trait.Copy.html"]
rust_version: "edition 2024 / 1.85+"
---

# Copy and Clone

`Clone` is explicit duplication that may run code and allocate; `Copy` is implicit bitwise duplication for simple values where moves should leave the source usable. `Copy` types are also `Clone`, but most owning resource types are not `Copy`.

## What it is
`Clone` is a trait for making another value from an existing one by calling `.clone()`.
The operation can be cheap or expensive depending on the type.
Cloning a `String` copies heap data; cloning an `Arc<T>` increments a reference count.

`Copy` is a marker trait for types whose values can be duplicated by copying their bits.
When a type is `Copy`, assignment and by-value function calls copy the value instead of moving it.
Integers, booleans, floats, `char`, shared references, and tuples of `Copy` values are common examples.

Rust forbids `Copy` on types that implement `Drop`.
A type that owns a resource needing cleanup cannot safely have two implicit owners of the same resource.

## How it works
Deriving `Clone` calls `clone` on each field.
Deriving `Copy` is allowed only when all fields are `Copy`, and the type must also implement `Clone`.

The distinction is part of Rust's performance model.
If code says `.clone()`, readers know duplication may execute arbitrary code.
If a value is copied implicitly, readers can assume the operation is trivial by Rust's rules.

You can always use `Clone` where duplication is needed.
Use `Copy` only for small, plain values where move semantics would be annoying and where implicit duplication cannot hide meaningful work.

`Clone` is part of a type's semantic contract, not merely a memory operation.
For `String`, `clone` creates an independent heap allocation with the same bytes.
For `Rc<T>` and `Arc<T>`, `clone` creates another owner of the same allocation by updating a
reference count.
For custom types, a manual `Clone` implementation can preserve invariants, reuse buffers, or avoid
unnecessary generic bounds that derive would add.

`Copy` has no methods and cannot be customized.
Once a type is `Copy`, every move-looking use is allowed to leave the old place usable, so adding or
removing `Copy` from a public type is an API-significant decision.

## Example
```rust
#[derive(Debug, Clone, Copy)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let a = Point { x: 3, y: 4 };
    let b = a;

    println!("{a:?} {b:?}");

    let s1 = String::from("owned");
    let s2 = s1.clone();
    println!("{s1} {s2}");
}
```

## Worked example
```rust
#[derive(Debug, Clone)]
struct Buffer {
    name: String,
    bytes: Vec<u8>,
}

#[derive(Debug, Clone, Copy)]
struct BufferId(u32);

fn main() {
    let id = BufferId(42);
    let same_id = id;
    println!("{id:?} {same_id:?}");

    let original = Buffer {
        name: String::from("packet"),
        bytes: vec![1, 2, 3],
    };
    let duplicate = original.clone();

    println!("{} {}", original.bytes.len(), duplicate.bytes.len());
}
```

## Common errors
Deriving `Copy` for a type that owns non-`Copy` data fails:

```text
error[E0204]: the trait `Copy` cannot be implemented for this type
```

Use only `Clone` for resource-owning types, or wrap the data in a cheap shared owner such as `Arc<T>`
when sharing is the actual design:

```rust
#[derive(Clone)]
struct Label {
    text: String,
}
```

## Best practice
- ✅ Derive `Copy` for small value types with no resource ownership, such as coordinates, IDs, flags, and simple enums.
- ✅ Derive or implement `Clone` when callers may explicitly need another owned value.
- ✅ Treat `.clone()` as a design signal: make sure a second owned value is actually needed.
- ✅ Document clone cost when a public type's clone is meaningfully expensive or intentionally cheap.
- ✅ Consider manual `Clone` for generic wrapper types when derive would impose unnecessary `T: Clone`
  bounds.
- ✅ Keep `Copy` types boring: no hidden resource ownership, no surprising large payload, no semantic
  uniqueness.

## Pitfalls
- ⚠️ Do not implement `Copy` for handles that conceptually own cleanup, uniqueness, locks, or external resources; Rust blocks many of these through `Drop`.
- ⚠️ Do not rely on `.clone()` to hide ownership design problems in hot paths. See [[Needless Clone]].
- ⚠️ Do not assume `clone` means deep copy for every type; smart pointers may clone shared ownership instead.
- ⚠️ Do not add `Copy` to large structs just because it compiles; implicit copying can obscure cost at call sites.
- ⚠️ Do not treat `Clone` as failure-free business logic; `clone` cannot return `Result`, so expensive
  or fallible duplication may deserve an explicit method instead.

## See also
[[Ownership]] · [[Move Semantics]] · [[Borrowing]] · [[The Drop Trait]] · [[The Stack and the Heap]] · [[Needless Clone]] · [[Derive Macros]] · [[Arc]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.1 "Clone" and "Copy" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- The Rust Programming Language, Appendix C "Clone and Copy for Duplicating Values" — [[the-book]],
  https://doc.rust-lang.org/book/appendix-03-derivable-traits.html#clone-and-copy-for-duplicating-values
- Standard library docs for `Clone` and `Copy`,
  https://doc.rust-lang.org/std/clone/trait.Clone.html
  https://doc.rust-lang.org/core/marker/trait.Copy.html
