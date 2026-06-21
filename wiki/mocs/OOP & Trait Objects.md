---
type: moc
title: "OOP & Trait Objects"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, oop, trait-objects]
domain: "OOP & Trait Objects"
difficulty: intermediate
related: ["[[Object-Oriented Rust]]", "[[Trait Objects]]", "[[dyn Compatibility (Object Safety)]]", "[[Static vs Dynamic Dispatch]]", "[[The State Pattern]]", "[[Composition over Inheritance]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-00-oop.html", "https://doc.rust-lang.org/book/ch18-01-what-is-oo.html", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/book/ch18-03-oo-design-patterns.html", "https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility", "https://doc.rust-lang.org/reference/types/trait-object.html"]
rust_version: "edition 2024 / 1.85+"
---

# OOP & Trait Objects

This map covers Rust's object-oriented features: encapsulation, trait-based polymorphism, dispatch choices, and state-pattern designs without class inheritance.

## Concepts
- [[Object-Oriented Rust]] — how Rust maps OOP goals onto structs, enums, methods, traits, generics, and trait objects.
- [[Encapsulation in Rust]] — using privacy and public APIs to protect invariants and hide representation.
- [[Trait Objects]] — using `dyn Trait` behind pointers for runtime polymorphism and heterogeneous values.
- [[dyn Compatibility (Object Safety)]] — the rules a trait must follow to be usable as `dyn Trait`.
- [[Static vs Dynamic Dispatch]] — choosing between monomorphized generic calls and runtime trait-object calls.

## Patterns
- [[Composition over Inheritance]] — building behavior from fields, traits, and delegation instead of parent classes.
- [[The State Pattern]] — representing internal runtime states as private trait objects.
- [[Type-State State Machines]] — encoding states as distinct types so invalid transitions fail at compile time.

## Antipatterns
- [[Overusing Trait Objects]] — erasing concrete types when generics, enums, or concrete types would be clearer.
- [[Non-dyn-Compatible Traits as Trait Objects]] — trying to use a trait as `dyn Trait` when its API cannot support dynamic dispatch.

## See also
[[Traits]] · [[Generics]] · [[Trait Bounds]] · [[Dynamically Sized Types]] · [[Box]] · [[Enums]] · [[Making Invalid States Unrepresentable]] · [[Default Implementations]]

## Sources
- The Rust Programming Language, ch. 18 "Object-Oriented Programming Features" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-00-oop.html
- The Rust Reference, "Dyn compatibility" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility
- The Rust Reference, "Trait object types" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/trait-object.html
