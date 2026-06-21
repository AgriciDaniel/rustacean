---
type: concept
title: "Set Collections with HashSet and BTreeSet"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashset, btreeset, sets]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[BTreeMap and BTreeSet]]", "[[HashMap Method Families]]", "[[BTreeMap Ordering and Ranges]]", "[[Choosing Standard Collections]]", "[[HashMap Hashers and Key Invariants]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.HashSet.html", "https://doc.rust-lang.org/std/collections/struct.BTreeSet.html", "https://doc.rust-lang.org/std/collections/index.html#use-the-set-variant-of-any-of-these-maps-when"]
rust_version: "edition 2024 / 1.85+"
---

# Set Collections with HashSet and BTreeSet

Use `HashSet` or `BTreeSet` when membership is the data; choose `HashSet` for unordered expected O(1) membership and `BTreeSet` for sorted iteration and range-like order operations.

## What it is
A set stores unique values with no separate associated value.
`HashSet<T>` is implemented as a hash table.
`BTreeSet<T>` is implemented as an ordered tree.
They are the set counterparts of `HashMap<T, ()>` and `BTreeMap<T, ()>`.

Sets are useful for:
- de-duplication
- visited markers
- allowlists and denylists
- membership tests
- set algebra such as union and intersection

`HashSet` requires `Eq + Hash`.
`BTreeSet` requires `Ord`.
Both require that the identity of an element remains stable while stored.

## How it works
`HashSet` uses hashing and equality.
Membership checks are expected O(1).
Iteration order is arbitrary.
It inherits the same hasher and key-invariant concerns as `HashMap`.

`BTreeSet` uses total ordering.
Membership checks are O(log n).
Iteration order is sorted.
It is useful when deterministic output or ordered traversal is needed.

Common methods include:
- `insert`
- `contains`
- `remove`
- `is_empty`
- `len`
- `iter`
- `union`
- `intersection`
- `difference`
- `symmetric_difference`

Set algebra methods return iterators.
They do not allocate unless you collect their results.
This makes them flexible for loops, filters, and conversions into another collection.

## Example
```rust
use std::collections::{BTreeSet, HashSet};

fn main() {
    let mut seen = HashSet::new();
    assert!(seen.insert("rust"));
    assert!(!seen.insert("rust"));
    assert!(seen.contains("rust"));

    let ordered: BTreeSet<_> = ["beta", "alpha", "gamma"].into_iter().collect();
    let names: Vec<_> = ordered.iter().copied().collect();
    assert_eq!(names, ["alpha", "beta", "gamma"]);
}
```

## Edge cases
```rust
use std::collections::HashSet;

fn main() {
    let a: HashSet<_> = [1, 2, 3].into_iter().collect();
    let b: HashSet<_> = [3, 4].into_iter().collect();

    let mut union: Vec<_> = a.union(&b).copied().collect();
    union.sort_unstable();
    assert_eq!(union, [1, 2, 3, 4]);

    let intersection: Vec<_> = a.intersection(&b).copied().collect();
    assert_eq!(intersection, [3]);
}
```

## Best practice
- ✅ Use a set instead of a map when the value would only be `true` or `()`.
- ✅ Use `HashSet` for fast membership when order is irrelevant.
- ✅ Use `BTreeSet` when sorted iteration is part of the behavior.
- ✅ Collect set-operation iterators only when you need an owned collection.
- ✅ Sort `HashSet` results before comparing or printing deterministic output.
- ✅ Derive `Hash + Eq` or `Ord` on small value objects when all fields define identity.
- ✅ Use newtype keys when only some fields should define membership.

## Pitfalls
- ⚠️ Mutating a stored set element through interior mutability so its hash, equality, or order changes is a logic error; see [[Mutating Collection Keys In Place]].
- ⚠️ Relying on `HashSet` iteration order has the same problem as `HashMap`; see [[HashMap Iteration Order Is Arbitrary]].
- ⚠️ Using `Vec` for repeated membership checks can turn simple code into O(n) scans.
- ⚠️ Using `BTreeSet` for hot unordered membership can be slower than `HashSet`.
- ⚠️ Floating-point values do not implement `Ord`, so `BTreeSet<f64>` is not directly available.
- ⚠️ Set algebra borrows both sets; avoid mutating either set while consuming those iterators.

## See also
[[std: Collections Deep]] · [[BTreeMap and BTreeSet]] · [[HashMap Method Families]] · [[BTreeMap Ordering and Ranges]] · [[HashMap Hashers and Key Invariants]] · [[Choosing Standard Collections]] · [[HashMap Iteration Order Is Arbitrary]] · [[Mutating Collection Keys In Place]] · [[Iterating Collections]] · [[The Iterator Trait]]

## Sources
- Rust standard library, `HashSet` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashSet.html
- Rust standard library, `BTreeSet` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BTreeSet.html
- Rust standard library, set variants - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#use-the-set-variant-of-any-of-these-maps-when
