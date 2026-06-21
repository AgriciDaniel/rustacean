---
type: concept
title: "Equality Traits PartialEq and Eq"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, equality, partialeq, eq]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[PartialEq]]", "[[Hash and Eq Contracts]]", "[[Ordering Traits PartialOrd and Ord]]", "[[Deriving Traits on Structs]]"]
sources: ["[[std]]", "[[the-reference]]", "[[api-guidelines]]"]
source_urls: ["https://doc.rust-lang.org/std/cmp/trait.PartialEq.html", "https://doc.rust-lang.org/std/cmp/trait.Eq.html", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#comparison-operators"]
rust_version: "edition 2024 / 1.85+"
---

# Equality Traits PartialEq and Eq

`PartialEq` defines `==` and `!=`, while `Eq` marks equality as reflexive so every value of the type equals itself.

## What it is
`PartialEq` is the trait behind equality operators.
Its required method is `eq`.
The `ne` method is provided and should almost never be overridden.

`Eq` has no methods.
It is a marker trait.
It says equality is a full equivalence relation.
In practical terms, it says `x == x` is always true.

Floating-point values implement `PartialEq` but not `Eq`.
`NaN != NaN`, so reflexivity fails.
That one fact explains much of the distinction.

The existing note [[PartialEq]] is a seed note.
This std catalog note gives the deeper implementor contract.

## How it works
Most structs and enums should derive equality.
`#[derive(PartialEq, Eq)]` compares fields or variants in a predictable fieldwise way.
Manual equality is appropriate when some fields are caches, metrics, or non-identity metadata.

If you manually implement equality, keep all dependent traits aligned.
`Hash` must hash equal values equally.
`Ord` must report equality for the same pairs that `Eq` reports equal.
`Clone` should preserve equality for values that equal themselves.

Cross-type `PartialEq<Rhs>` implementations are possible.
They can be useful, but they create coherence and transitivity hazards across crates.
Be conservative in public APIs.

## Example
```rust
#[derive(Debug)]
struct User {
    id: u64,
    name: String,
    cached_label: String,
}

impl PartialEq for User {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl Eq for User {}

fn main() {
    let a = User {
        id: 7,
        name: String::from("Ada"),
        cached_label: String::from("Ada #7"),
    };
    let b = User {
        id: 7,
        name: String::from("Ada Lovelace"),
        cached_label: String::from("cached"),
    };

    assert_eq!(a, b);
}
```

## Best practice
- ✅ Derive `PartialEq` and `Eq` together when fieldwise equality is correct and all fields support it.
- ✅ Manually implement equality from the same identity rule used by `Hash` and `Ord`.
- ✅ Keep `ne` as the default inverse of `eq`.
- ✅ Exclude cache fields only when they truly do not affect identity.
- ✅ Be cautious with cross-type equality implementations in libraries.

## Pitfalls
- ⚠️ Do not implement `Eq` for values where `x == x` can be false.
- ⚠️ Do not let equality include a field while [[Hash and Eq Contracts]] ignores it.
- ⚠️ Do not compare floats through `Ord`-style assumptions unless you have handled `NaN`.
- ⚠️ Avoid manual equality that changes over time for keys stored in maps or sets.

## See also
[[std: Core Trait Catalog]] · [[PartialEq]] · [[Hash and Eq Contracts]] · [[Ordering Traits PartialOrd and Ord]] · [[The Hash Trait]] · [[HashMap]] · [[BTreeMap and BTreeSet]] · [[Clone Semantics in std]] · [[Deriving Traits on Structs]] · [[Marker Traits]]

## Sources
- Rust standard library, `std::cmp::PartialEq` - [[std]], https://doc.rust-lang.org/std/cmp/trait.PartialEq.html
- Rust standard library, `std::cmp::Eq` - [[std]], https://doc.rust-lang.org/std/cmp/trait.Eq.html
- The Rust Reference, comparison operators - [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#comparison-operators
