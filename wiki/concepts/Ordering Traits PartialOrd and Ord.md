---
type: concept
title: "Ordering Traits PartialOrd and Ord"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, ordering, partialord, ord]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[Equality Traits PartialEq and Eq]]", "[[BTreeMap and BTreeSet]]", "[[Hash and Eq Contracts]]", "[[Deriving Traits on Structs]]"]
sources: ["[[std]]", "[[the-reference]]", "[[api-guidelines]]"]
source_urls: ["https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html", "https://doc.rust-lang.org/std/cmp/trait.Ord.html", "https://doc.rust-lang.org/std/primitive.f32.html#method.total_cmp"]
rust_version: "edition 2024 / 1.85+"
---

# Ordering Traits PartialOrd and Ord

`PartialOrd` models comparisons that may be unordered, while `Ord` promises a total order where every pair of values compares consistently.

## What it is
`PartialOrd` backs `<`, `<=`, `>`, and `>=`.
Its central method is `partial_cmp`, which returns `Option<Ordering>`.
`None` means the two values are not ordered.

`Ord` backs total ordering.
Its required method is `cmp`, which always returns `Ordering`.
`Ord` requires `Eq` and `PartialOrd`.
The implementations must agree.

Floating-point values are the standard example of partial ordering.
Because of `NaN`, ordinary `f32` and `f64` do not implement `Ord`.
Use `f32::total_cmp` or a wrapper type when you need a deliberate total order.

## How it works
Deriving `Ord` on structs uses lexicographic field order.
The first field is compared first.
If it is equal, the next field breaks the tie.
Field declaration order therefore becomes part of the ordering contract.

Deriving `Ord` on enums orders variants primarily by discriminant.
By default, variants written earlier compare smaller.
Explicit discriminants can change that.
Variant fields are compared after variant order.

Manual `Ord` should usually be written first.
Then implement `PartialOrd` as `Some(self.cmp(other))`.
Then make `PartialEq` and `Eq` match the same identity rule.
This keeps sorted collections sane.

## Example
```rust
use std::cmp::Ordering;

#[derive(Debug)]
struct Score {
    points: u32,
    tiebreaker: u32,
    display_name: String,
}

impl Ord for Score {
    fn cmp(&self, other: &Self) -> Ordering {
        self.points
            .cmp(&other.points)
            .then(self.tiebreaker.cmp(&other.tiebreaker))
    }
}

impl PartialOrd for Score {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Score {
    fn eq(&self, other: &Self) -> bool {
        self.points == other.points && self.tiebreaker == other.tiebreaker
    }
}

impl Eq for Score {}

fn main() {
    let low = Score { points: 10, tiebreaker: 1, display_name: "a".into() };
    let high = Score { points: 10, tiebreaker: 2, display_name: "b".into() };
    assert!(low < high);
}
```

## Best practice
- ✅ Derive all four comparison traits together when field order is the desired order.
- ✅ For manual total order, implement `Ord` first and delegate `PartialOrd` to `cmp`.
- ✅ Use `then` and `then_with` to build lexicographic manual comparisons clearly.
- ✅ Use `sort_by_key` or `sort_by` when only one sorting operation needs a custom order.
- ✅ Document ordering when it is part of a public type's API.

## Pitfalls
- ⚠️ Do not implement `Ord` with ordinary float comparison unless `NaN` is impossible by construction.
- ⚠️ Do not let `Ord` say two values are equal while [[Equality Traits PartialEq and Eq]] says they differ.
- ⚠️ Do not forget that struct field order affects derived ordering.
- ⚠️ Avoid changing enum discriminants or variant order casually after exposing derived `Ord`.

## See also
[[std: Core Trait Catalog]] · [[Equality Traits PartialEq and Eq]] · [[Hash and Eq Contracts]] · [[BTreeMap and BTreeSet]] · [[Deriving Traits on Structs]] · [[PartialEq]] · [[Iterator Adapters]] · [[Vec]] · [[The Hash Trait]] · [[Marker Traits]]

## Sources
- Rust standard library, `std::cmp::PartialOrd` - [[std]], https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html
- Rust standard library, `std::cmp::Ord` - [[std]], https://doc.rust-lang.org/std/cmp/trait.Ord.html
- Rust standard library, `f32::total_cmp` - [[std]], https://doc.rust-lang.org/std/primitive.f32.html#method.total_cmp
