---
type: moc
title: "Structs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, moc]
domain: "Structs"
difficulty: basic
related: ["[[Named Field Structs]]", "[[Tuple Structs]]", "[[Methods]]", "[[Associated Functions]]", "[[Struct Update Syntax]]", "[[Deriving Traits on Structs]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-00-structs.html", "https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/book/ch05-02-example-structs.html", "https://doc.rust-lang.org/book/ch05-03-method-syntax.html"]
rust_version: "edition 2024 / 1.85+"
---

# Structs

This map links the Structs-domain notes for modeling named data, attaching behavior, and avoiding struct-specific ownership and mutability footguns.

## Concepts
- [[Named Field Structs]] — named-field product types for related data.
- [[Tuple Structs]] — tuple-shaped structs that create distinct named types.
- [[Unit-Like Structs]] — fieldless structs for stateless behavior or marker values.
- [[Methods]] — `self`-receiving functions called with dot syntax.
- [[Associated Functions]] — type-namespaced functions such as constructors.

## Patterns
- [[Field Init Shorthand]] — concise `field` syntax for `field: field`.
- [[Struct Update Syntax]] — `..base` construction for mostly reused values.
- [[Deriving Traits on Structs]] — compiler-generated standard trait implementations.

## Antipatterns
- [[Partially Moved Structs with Update Syntax]] — losing use of the base value after `..base` moves owned fields.
- [[Expecting Per-Field Mutability in Structs]] — looking for field-level `mut` instead of binding/reference mutability.
- [[Storing References in Structs Without Lifetimes]] — borrowing inside structs without modeling lifetime relationships.

## See also
[[Ownership]] · [[Borrowing]] · [[Lifetimes]] · [[Traits]] · [[Derive Macros]] · [[Newtype Pattern]] · [[Visibility and Privacy]] · [[Making Invalid States Unrepresentable]]

## Sources
- The Rust Programming Language, ch. 5 "Using Structs to Structure Related Data" — [[the-book]], https://doc.rust-lang.org/book/ch05-00-structs.html
- The Rust Programming Language, ch. 5.1 "Defining and Instantiating Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Programming Language, ch. 5.2 "An Example Program Using Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-02-example-structs.html
- The Rust Programming Language, ch. 5.3 "Method Syntax" — [[the-book]], https://doc.rust-lang.org/book/ch05-03-method-syntax.html
