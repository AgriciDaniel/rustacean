---
type: moc
title: "Ownership & Memory"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, memory, moc]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Borrowing]]", "[[References]]", "[[Move Semantics]]", "[[The Drop Trait]]", "[[The Slice Type]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[ownership-borrowing-lifetimes]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/book/ch04-03-slices.html", "https://doc.rust-lang.org/reference/destructors.html"]
rust_version: "edition 2024 / 1.85+"
---

# Ownership & Memory

Ownership and memory notes explain how Rust decides who owns data, who may temporarily access it, and when cleanup runs. Start with [[Ownership]], then connect moves, borrows, slices, copying, and destructors into one mental model.

## Concepts
- [[Ownership]]
- [[The Stack and the Heap]]
- [[Move Semantics]]
- [[Borrowing]]
- [[References]]
- [[Mutable References]]
- [[The Slice Type]]
- [[Copy and Clone]]
- [[The Drop Trait]]

## Patterns
- [[Borrowed Parameter APIs]]
- [[Borrowing Strings and Slices]]
- [[AsRef for Flexible Arguments]]
- [[Borrow for Equivalent Keys]]
- [[RAII and Drop Guards]]
- [[Move Closures with Threads]]

## Antipatterns
- [[Returning References to Locals]]
- [[Stale Slice Indices]]
- [[Needless Clone]]
- [[Holding Collection Element References Across Mutation]]
- [[Rc RefCell Overuse]]
- [[Premature Arc Mutex]]

## Learning path
Read [[The Stack and the Heap]] before [[Move Semantics]] if the pointer/heap distinction is still fuzzy.
Read [[Borrowing]], [[References]], and [[Mutable References]] together; they are one rule set seen from three angles.
Read [[The Slice Type]] before designing APIs that expose parts of strings or collections.
Read [[Copy and Clone]] and [[The Drop Trait]] together to understand why resource owners move by default.

## Example
```rust
fn main() {
    let owned = String::from("rust");
    let borrowed = owned.as_str();

    println!("{borrowed}");

    let moved = owned;
    println!("{moved}");
}
```

## Best practice
- ✅ Start from [[Ownership]], then use [[Borrowing]] when a function only needs temporary access.
- ✅ Reach for [[The Slice Type]] when returning or accepting views into contiguous data.
- ✅ Treat [[Copy and Clone]] as explicit API design: cheap implicit copies are different from potentially expensive clones.
- ✅ Let [[The Drop Trait]] and scope release resources instead of writing manual cleanup paths.

## Pitfalls
- ⚠️ Do not clone by reflex; check [[Needless Clone]] and [[Borrowed Parameter APIs]] first.
- ⚠️ Do not return references to values created inside a function. See [[Returning References to Locals]].
- ⚠️ Do not keep numeric positions into changing data as if they were checked borrows. See [[Stale Slice Indices]].
- ⚠️ Do not hold references into collections across mutations that can reallocate. See [[Holding Collection Element References Across Mutation]].

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[Mutable References]] · [[The Slice Type]] · [[Move Semantics]] · [[Copy and Clone]] · [[The Drop Trait]] · [[The Stack and the Heap]] · [[Lifetimes]]

## Sources
- The Rust Programming Language, ch. 4 "Understanding Ownership" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
  https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
  https://doc.rust-lang.org/book/ch04-03-slices.html
- The Rust Reference, "Destructors" — [[the-reference]],
  https://doc.rust-lang.org/reference/destructors.html
