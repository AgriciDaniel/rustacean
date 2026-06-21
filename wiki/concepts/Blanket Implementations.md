---
type: concept
title: "Blanket Implementations"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, blanket-impls, coherence]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Traits]]", "[[Trait Bounds]]", "[[Generics]]", "[[Coherence and the Orphan Rule]]", "[[Marker Traits]]", "[[Overgeneric Public APIs]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html#using-trait-bounds-to-conditionally-implement-methods", "https://doc.rust-lang.org/reference/items/implementations.html"]
rust_version: "edition 2024 / 1.85+"
---

# Blanket Implementations

A blanket implementation implements a trait for every type satisfying a bound, turning one impl into behavior for an open set of types.

## What it is
The standard library's `impl<T: Display> ToString for T` is the canonical example.
Any type implementing `Display` automatically gets `ToString`.
Blanket impls make trait ecosystems compose: implement one core trait and receive derived behavior.
They are also a common way to define marker traits for all types satisfying a set of bounds.
Because blanket impls cover many types, they interact strongly with coherence and overlap rules.

## How it works
Write a generic impl whose implementing type is a parameter: `impl<T: Bound> Trait for T`.
The impl applies to every concrete `T` that meets the bound.
Rust rejects overlapping impls because method lookup must always have one coherent answer.
After a broad blanket impl, you usually cannot add a more specific impl of the same trait for one covered type on stable Rust.
Public blanket impls are semver-significant because they reserve a large part of the impl space.
Trait solving treats the blanket impl as a candidate for every type that can satisfy its `where` clause.
If two impls could both apply to the same future type, Rust rejects the overlap even when no current type triggers it.
Negative impls and specialization are limited tools, not general escape hatches for public blanket impl mistakes.
Documentation for standard traits often lists blanket impls, which explains why methods such as `to_string` appear on every `Display` type.

## Example
```rust
use std::fmt::Display;

trait Label {
    fn label(&self) -> String;
}

impl<T> Label for T
where
    T: Display,
{
    fn label(&self) -> String {
        format!("[{self}]")
    }
}

fn main() {
    assert_eq!(42.label(), "[42]");
    assert_eq!("rust".label(), "[rust]");
}
```

## Common errors
A specific impl that overlaps a blanket impl reports:

```text
error[E0119]: conflicting implementations of trait `Label`
```

Narrow the blanket impl before publishing it, split the trait, or use a newtype for the exceptional case.
Trying to write a blanket impl of a foreign trait for a type parameter, such as `impl<T: Display> ForeignTrait for T`, also runs into coherence because neither the trait nor implementing type is local in the required way.
The fix is to define a local trait, implement the foreign trait for a local wrapper, or rely on an existing standard-library blanket impl.
Do not expect stable Rust to pick the "more specific" impl automatically.

## Best practice
- ✅ Use blanket impls when a trait is mechanically true for every type satisfying another trait.
- ✅ Keep blanket impl bodies simple and faithful to the source bound's semantics.
- ✅ Think through future impl space before publishing `impl<T> MyTrait for T where ...`.
- ✅ Check trait documentation for blanket impls; they explain why methods appear on many types.
- ✅ Use blanket marker impls to reduce repetitive empty implementations when the marker contract is exactly the bound set.

## Pitfalls
- ⚠️ A blanket impl can prevent future specialized impls because stable Rust does not have general specialization.
- ⚠️ Broad impls can create surprising method availability and trait resolution errors.
- ⚠️ Blanket impls of public traits are hard to retract without breaking users.
- ⚠️ A blanket impl that overpromises semantics creates bugs for every covered type, not just one implementation.

## See also
[[Traits]] · [[Trait Bounds]] · [[Generics]] · [[Coherence and the Orphan Rule]] · [[Marker Traits]] · [[Default Implementations]] · [[The Iterator Trait]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.2 "Using Trait Bounds to Conditionally Implement Methods" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html#using-trait-bounds-to-conditionally-implement-methods
- The Rust Reference, "Implementations" — [[the-reference]], https://doc.rust-lang.org/reference/items/implementations.html
