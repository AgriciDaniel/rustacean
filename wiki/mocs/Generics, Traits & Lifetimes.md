---
type: moc
title: "Generics, Traits & Lifetimes"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, generics, traits, lifetimes]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Generics]]", "[[Traits]]", "[[Lifetimes]]", "[[Trait Bounds]]", "[[Associated Types]]", "[[Coherence and the Orphan Rule]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-00-generics.html", "https://doc.rust-lang.org/reference/items/generics.html", "https://doc.rust-lang.org/reference/items/traits.html"]
rust_version: "edition 2024 / 1.85+"
---

# Generics, Traits & Lifetimes

Generics, traits, and lifetimes are Rust's compile-time abstraction toolkit: they remove duplication, state behavioral contracts, and prove borrowed data remains valid.

## Concepts
- [[Generics]]
- [[Traits]]
- [[Trait Bounds]]
- [[Default Implementations]]
- [[Associated Types]]
- [[Generic Associated Types]]
- [[Lifetimes]]
- [[Lifetime Elision]]
- [[The 'static Lifetime]]
- [[Where Clauses]]
- [[Blanket Implementations]]
- [[Marker Traits]]
- [[Supertraits]]
- [[Coherence and the Orphan Rule]]

## Patterns
- [[Static Dispatch with Generics]]
- [[Use a Newtype to Implement Foreign Traits]]
- [[Sealed Traits]]

## Antipatterns
- [[Overconstraining Lifetimes]]
- [[Unnecessary Bounds on Data Types]]
- [[Overgeneric Public APIs]]

## Example
```rust
use std::fmt::Display;

fn announce_largest<'a, T>(left: &'a T, right: &'a T, label: impl Display) -> &'a T
where
    T: PartialOrd,
{
    println!("{label}");
    if left >= right { left } else { right }
}

fn main() {
    let a = 10;
    let b = 20;
    assert_eq!(*announce_largest(&a, &b, "numbers"), 20);
}
```

## Reading Path
Start with [[Generics]], [[Traits]], and [[Lifetimes]].
Then read [[Trait Bounds]], [[Where Clauses]], and [[Lifetime Elision]] to understand signatures.
Move to [[Associated Types]], [[Generic Associated Types]], and [[Blanket Implementations]] when designing reusable traits.
Finish with [[Coherence and the Orphan Rule]], [[Use a Newtype to Implement Foreign Traits]], and [[Sealed Traits]] before publishing trait-heavy APIs.

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[The Iterator Trait]] · [[Dynamically Sized Types]] · [[Fully Qualified Syntax]] · [[Newtype Pattern]] · [[Zero-Cost Abstractions]]

## Sources
- The Rust Programming Language, ch. 10 "Generic Types, Traits, and Lifetimes" — [[the-book]], https://doc.rust-lang.org/book/ch10-00-generics.html
- The Rust Reference, "Generic parameters" — [[the-reference]], https://doc.rust-lang.org/reference/items/generics.html
- The Rust Reference, "Traits" — [[the-reference]], https://doc.rust-lang.org/reference/items/traits.html
