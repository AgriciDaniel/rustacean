---
type: moc
title: "std: Core Trait Catalog"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, moc]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[Generics, Traits & Lifetimes]]", "[[Idioms & API Design]]", "[[Collections & Strings]]", "[[Ownership & Memory]]"]
sources: ["[[std]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/", "https://doc.rust-lang.org/std/convert/index.html", "https://doc.rust-lang.org/std/ops/index.html", "https://doc.rust-lang.org/std/cmp/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# std: Core Trait Catalog

This MOC groups the standard-library traits that most often define Rust API boundaries: conversion, formatting, equality, ordering, hashing, iteration, operators, reference views, and destruction.

## What it is
The standard library is full of small traits with large design consequences.
Many of them are automatically used by syntax.
Many of them are imported through the prelude.
Many of them are expected by collections, formatters, and generic APIs.

This domain is a catalog, not a replacement for [[Traits]].
It answers a narrower question: which core std trait should an API implement, derive, or bound on?

Use these notes when choosing between `From` and `TryFrom`.
Use them when deciding whether `Default` is honest.
Use them when deriving equality, ordering, and hashing.
Use them when operator syntax is tempting.
Use them when a type owns cleanup behavior.

## Conversion traits
[[Infallible Conversion Traits (std)]] covers `From` and `Into`.
It emphasizes infallible, lossless, value-preserving, obvious conversions.
It links to the existing pattern [[From and Into]].

[[Fallible Conversion Traits (std)]] covers `TryFrom` and `TryInto`.
It emphasizes explicit validation, checked narrowing, and `Result`.
It links to the existing pattern [[TryFrom and TryInto]].

[[AsRef and AsMut Conversion Traits]] covers cheap reference-to-reference views.
It distinguishes `AsRef` from ownership conversion, `Borrow`, and `Deref`.
It links to [[AsRef for Flexible Arguments]] and [[Borrowed Parameter APIs]].

## Construction and duplication
[[The Default Trait]] covers conventional baseline values.
It explains derive behavior for structs and enums.
It warns against fake defaults for types with required invariants.

[[Clone Semantics in std]] covers explicit duplication and its relationship to `Copy`.
It distinguishes deep copies from shared ownership through `Arc` and `Rc`.
It links to the existing note [[Copy and Clone]] and the antipattern [[Needless Clone]].

## Formatting and errors
[[Display and Debug Formatting Traits]] covers `{}` and `{:?}`.
It distinguishes user-facing `Display` from diagnostic `Debug`.
It explains why `Display` enables `ToString`.
It links to [[The Display Trait]], [[The Debug Trait]], and [[The Error Trait]].

The existing note [[The Error Trait]] belongs nearby because `Error: Debug + Display`.
Custom errors often combine `Display`, `Debug`, `Error`, and `From` conversions.
Use [[Custom Error Types]] and [[Error Sources and Chains]] for broader error design.

## Equality, ordering, and hashing
[[Equality Traits PartialEq and Eq]] covers `==`, `!=`, and reflexive equality.
It explains why floats implement `PartialEq` but not `Eq`.
It links to [[PartialEq]].

[[Ordering Traits PartialOrd and Ord]] covers partial and total ordering.
It explains derived lexicographic order, enum discriminants, and manual `Ord`.
It warns about `NaN` and ordinary float comparison.

[[Hash and Eq Contracts]] covers `Hash` as a collection contract.
It emphasizes that equal keys must hash equally.
It links to [[The Hash Trait]], [[HashMap]], and [[BTreeMap and BTreeSet]].

## Iteration and collection boundaries
[[Iterator Conversion Traits IntoIterator and FromIterator]] covers `for` loops and `collect()`.
It explains by-value, shared-reference, and mutable-reference iteration.
It connects collection APIs with [[Iterators]], [[The Iterator Trait]], and [[Unnecessary Collect]].

The existing notes [[Iterator Adapters]], [[Consuming Adapters]], and [[Iterating Collections]] remain the next layer down.
Use this catalog note when the question is trait selection.
Use those notes when the question is iterator pipeline behavior.

## Operator and indexing traits
[[Arithmetic Operator Traits Add and Mul]] covers arithmetic operator overloading.
It keeps operator meaning central.
It explains by-value operands and reference-based implementations.

[[Index and IndexMut Traits]] covers `container[index]`.
It emphasizes that indexing conventionally panics on invalid access.
It links to [[Index Panics vs get]] for the API-design footgun.

The existing note [[Operator Overloading]] remains the broader language overview.
This catalog splits arithmetic and indexing because their API risks are different.

## Destruction and RAII
[[Destructor Semantics with Drop]] covers `Drop`, cleanup, and destructor timing.
It links to the existing note [[The Drop Trait]].
It connects cleanup behavior to [[Ownership]], [[Move Semantics]], and [[Panic Unwinding and Abort]].

Use [[RAII and Drop Guards]] for the idiom of creating guard values that release resources on scope exit.
Use [[Holding Locks Too Long]] and [[Holding Locks Across Await]] for lock-specific pitfalls.

## Example
```rust
use std::collections::HashSet;

#[derive(Debug, Clone, Default, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct ServiceId(String);

impl From<&str> for ServiceId {
    fn from(value: &str) -> Self {
        Self(value.to_owned())
    }
}

fn unique_ids<I>(ids: I) -> HashSet<ServiceId>
where
    I: IntoIterator,
    I::Item: Into<ServiceId>,
{
    ids.into_iter().map(Into::into).collect()
}

fn main() {
    let ids = unique_ids(["api", "worker", "api"]);
    assert_eq!(ids.len(), 2);
    assert!(ids.contains(&ServiceId::from("api")));
}
```

## Existing notes intentionally linked, not overwritten
[[From and Into]] already exists as an API design pattern.
[[TryFrom and TryInto]] already exists as an API design pattern.
[[Copy and Clone]] already exists as a concept note.
[[The Display Trait]] already exists as a concept note.
[[The Debug Trait]] already exists as a concept note.
[[PartialEq]] already exists as a seed concept note.
[[Operator Overloading]] already exists as a concept note.
[[The Drop Trait]] already exists as a concept note.

## Best practice
- ✅ Implement the smallest trait that expresses the real semantic promise.
- ✅ Derive trait families together when fieldwise behavior is correct.
- ✅ Keep conversion traits infallible or fallible according to their return type.
- ✅ Keep equality, ordering, and hashing consistent before using a type as a collection key.
- ✅ Prefer named methods when trait syntax would hide policy, failure, allocation, or side effects.

## Pitfalls
- ⚠️ Do not implement std traits just to unlock cute syntax.
- ⚠️ Do not make `From`, `AsRef`, `Hash`, `Ord`, or `Drop` panic in ordinary use.
- ⚠️ Do not derive traits on public types without checking that field order and field identity match the public contract.
- ⚠️ Do not treat formatting, hashing, or debug output as stable serialization.

## See also
[[Infallible Conversion Traits (std)]] · [[Fallible Conversion Traits (std)]] · [[The Default Trait]] · [[Clone Semantics in std]] · [[Display and Debug Formatting Traits]] · [[Equality Traits PartialEq and Eq]] · [[Ordering Traits PartialOrd and Ord]] · [[Hash and Eq Contracts]] · [[Iterator Conversion Traits IntoIterator and FromIterator]] · [[Arithmetic Operator Traits Add and Mul]] · [[Index and IndexMut Traits]] · [[AsRef and AsMut Conversion Traits]] · [[Destructor Semantics with Drop]] · [[Traits]] · [[Trait Bounds]] · [[Deriving Traits on Structs]]

## Sources
- Rust standard library - [[std]], https://doc.rust-lang.org/std/
- Rust standard library, conversion traits - [[std]], https://doc.rust-lang.org/std/convert/index.html
- Rust standard library, operator traits - [[std]], https://doc.rust-lang.org/std/ops/index.html
- Rust standard library, comparison traits - [[std]], https://doc.rust-lang.org/std/cmp/index.html
