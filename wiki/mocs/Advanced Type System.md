---
type: moc
title: "Advanced Type System"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, advanced-type-system, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Generics]]", "[[Traits]]", "[[Lifetimes]]", "[[Associated Types]]", "[[Coherence and the Orphan Rule]]", "[[Generic Associated Types]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/", "https://doc.rust-lang.org/nomicon/"]
rust_version: "edition 2024 / 1.85+"
---

# Advanced Type System

Advanced Rust type-system work is about moving invariants into types without making APIs impossible to use.
This map links the notes in this domain and points outward to the foundational concepts they rely on.

## Core concepts
[[Const Generics and Const Parameters]]
Use compile-time values as generic parameters when the value is part of the type contract.

[[Generic Associated Types]]
Existing note for associated types parameterized by lifetimes, types, or consts.

[[Required Bounds on Generic Associated Types]]
Why lending-style GATs often need `where Self: 'a` and how those bounds are derived.

[[Higher-Ranked Trait Bounds]]
Use `for<'a>` when a trait obligation must hold for every lifetime.

[[Return-Position impl Trait in Traits]]
Trait methods can return hidden concrete types through anonymous associated types.

[[PhantomData]]
Communicate logical ownership, borrowing, variance, drop-check, and auto-trait relationships.

[[Drop Check]]
Understand how destructors constrain generic lifetimes and why `PhantomData` affects drop analysis.

[[Zero-Sized Types]]
Represent marker values and type-level states without runtime storage.

[[Type layout]]
Know which size, alignment, field-offset, and enum-discriminant facts Rust actually guarantees.

[[Type Layout and repr]]
Use `repr(C)`, primitive reprs, `repr(transparent)`, `align`, and `packed` only when layout is a contract.

[[Variance]]
Understand when lifetime subtyping passes through generic type constructors.

[[Trait Coherence and Covered Implementations]]
A deeper coherence/orphan-rule note focused on covered parameters and impl space.

[[Coherence and the Orphan Rule]]
Existing note for the broader baseline rule.

## Patterns
[[Lending Iterators with GATs]]
Return items tied to the borrow of the iterator itself.

[[Phantom Type Parameters]]
Use marker parameters to distinguish IDs, states, units, or capabilities with the same representation.

[[Type-State Pattern]]
Represent protocol states in types instead of runtime flags.

[[Type-State State Machines]]
Model transitions by consuming one typed state and returning another.

[[Use a Newtype to Implement Foreign Traits]]
Create a local nominal type when coherence forbids a direct impl.

[[Sealed Traits]]
Reserve impl authority for public traits whose implementor set must remain controlled.

[[Static Dispatch with Generics]]
Use generic monomorphization when behavior should be selected at compile time.

[[Return Iterators Instead of Collecting]]
Expose lazy behavior without naming long concrete iterator types.

## Antipatterns
[[Uncovered Type Parameters in Foreign Impl]]
Do not write foreign impl headers that claim generic impl space before a local type anchors them.

[[Using Type Aliases as Newtypes]]
Aliases do not create fresh nominal types and do not bypass orphan rules.

[[Overgeneric Public APIs]]
Do not move every choice into a generic parameter just because the type system can express it.

[[Unnecessary Bounds on Data Types]]
Avoid putting bounds on structs and enums unless their fields require them.

[[Non-dyn-Compatible Traits as Trait Objects]]
Advanced associated types and `impl Trait` often make a trait unsuitable for `dyn` use.

[[Unsafe Send and Sync Implementations]]
Marker fields and raw pointers can change auto-trait behavior; unsafe impls need a proof.

## Reading path
Start with [[Generics]], [[Traits]], [[Associated Types]], and [[Lifetimes]] if the syntax is the obstacle.
Then read [[Const Generics and Const Parameters]] for value-level parameters.
Read [[Generic Associated Types]] before [[Required Bounds on Generic Associated Types]].
Read [[Higher-Ranked Trait Bounds]] before designing callback APIs that borrow local values.
Read [[Variance]] and [[PhantomData]] before writing unsafe abstractions with raw pointers.
Read [[Trait Coherence and Covered Implementations]] before publishing blanket impls or conversion traits.
Use [[Lending Iterators with GATs]] and [[Phantom Type Parameters]] as concrete design patterns.
Review [[Uncovered Type Parameters in Foreign Impl]] when an orphan-rule error appears in a generic impl.

## Design questions
Is the invariant truly part of the type, or would a field be clearer?
Will callers need to name the returned type, or is [[Return-Position impl Trait in Traits]] enough?
Does the API need dynamic dispatch, and does that conflict with [[dyn Compatibility (Object Safety)]]?
Will a blanket impl reserve impl space that downstream users reasonably expect to own?
Does a marker field change [[Send and Sync]], [[Variance]], or drop-check behavior?
Can a [[Newtype Pattern]] keep coherence simple while preserving ergonomics?
Are GAT bounds minimal, or are they overfitted to one implementation?
Would a callback with [[Higher-Ranked Trait Bounds]] be simpler than returning a borrowed associated type?

## Source anchors
The Rust Reference is the authority for syntax and stable language rules in this domain.
The Rustonomicon is most useful for unsafe-code consequences of variance, ZSTs, and `PhantomData`.
Use current standard library docs for concrete marker types such as `PhantomData`, `PhantomPinned`, `Send`, and `Sync`.
For third-party crates that abstract these patterns, cite docs.rs and verify the latest version before recommending an API.
This MOC targets Rust edition 2024 / stable 1.85+.

## Sources
- The Rust Reference — [[the-reference]],
  https://doc.rust-lang.org/reference/
- The Rustonomicon — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/
