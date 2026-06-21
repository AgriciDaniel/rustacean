---
type: concept
title: "BTreeMap and BTreeSet"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, btree, ordered]
domain: "Collections & Strings"
difficulty: intermediate
related: ["[[HashMap]]", "[[The Entry API]]", "[[Choosing Collection Types]]", "[[Iterating Collections]]", "[[Ownership]]", "[[Index Panics vs get]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.BTreeMap.html", "https://doc.rust-lang.org/std/collections/struct.BTreeSet.html", "https://doc.rust-lang.org/std/collections/index.html", "https://doc.rust-lang.org/book/ch08-03-hash-maps.html"]
rust_version: "edition 2024 / 1.85+"
---

# BTreeMap and BTreeSet

`BTreeMap` and `BTreeSet` are ordered collections that keep keys or values sorted by `Ord` and iterate in that order.

## What it is
Use `BTreeMap<K, V>` when you need key-value lookup plus sorted traversal, range queries, or first/last key operations.
Use `BTreeSet<T>` when you need a sorted collection of unique values.

Unlike `HashMap`, B-tree collections require a total ordering with `Ord`.
For strings, that means lexicographic order.
For numbers, that means numeric order.

They are often the right choice for deterministic output, reproducible tests, ordered reports, and interval-like queries.

## How it works
A `BTreeMap` stores entries in a B-tree, not in hash buckets.
Lookups, insertions, and removals are logarithmic rather than expected constant time, but iteration is ordered and efficient.

The map exposes range-oriented operations such as `range`, `first_key_value`, `last_key_value`, `pop_first`, and `pop_last`.
`BTreeSet` provides analogous set operations and ordered iteration over unique values.

Keys must not be mutated in a way that changes their ordering while they are inside the collection.
Safe Rust usually prevents this for normal owned keys, but interior mutability can still create a logic error.

Unlike a hash table, a B-tree stores multiple sorted entries per node.
That gives predictable ordered traversal and good locality for range scans, while lookups and updates remain logarithmic.
The exact node layout is an implementation detail; rely on the public ordering and complexity guarantees, not internal shape.

## Example
```rust
use std::collections::{BTreeMap, BTreeSet};

fn main() {
    let mut counts = BTreeMap::new();
    for word in ["pear", "apple", "pear", "banana"] {
        *counts.entry(word).or_insert(0) += 1;
    }

    let ordered_keys: Vec<_> = counts.keys().copied().collect();
    assert_eq!(ordered_keys, ["apple", "banana", "pear"]);

    let unique = BTreeSet::from(["pear", "apple", "banana"]);
    assert_eq!(unique.iter().copied().collect::<Vec<_>>(), ["apple", "banana", "pear"]);
}
```

## More realistic example
```rust
use std::collections::BTreeMap;

fn events_in_window(events: &BTreeMap<u64, &'static str>, start: u64, end: u64) -> Vec<&'static str> {
    events
        .range(start..end)
        .map(|(_timestamp, name)| *name)
        .collect()
}

fn main() {
    let events = BTreeMap::from([
        (10, "boot"),
        (20, "connect"),
        (30, "sync"),
        (50, "shutdown"),
    ]);

    assert_eq!(events.first_key_value(), Some((&10, &"boot")));
    assert_eq!(events_in_window(&events, 15, 45), ["connect", "sync"]);
}
```

This is where `BTreeMap` earns its keep: the range query visits only the ordered span of interest,
and the output order is part of the collection's contract.

## Common errors
```text
error[E0277]: the trait bound `f64: Ord` is not satisfied
```

`BTreeMap` and `BTreeSet` need a total order.
Plain floating-point types do not implement `Ord` because `NaN` breaks ordinary total-order assumptions; use integer keys, a domain wrapper, or `total_cmp` inside a deliberate newtype.

```text
thread 'main' panicked at 'no entry found for key'
```

Like `HashMap`, indexing a `BTreeMap` with `map[&key]` panics when absent.
Use `get`, `range`, `first_key_value`, or `entry` depending on the operation.

## Best practice
- ✅ Choose `BTreeMap` over `HashMap` when sorted iteration is observable behavior.
- ✅ Use `range` for bounded traversal instead of filtering a whole unordered map.
- ✅ Use `BTreeSet` for "unique and sorted" values rather than `Vec` plus repeated sort/dedup steps.
- ✅ Keep `Ord`, `Eq`, and any borrowed lookup ordering consistent for key types.
- ✅ Use `pop_first` or `pop_last` to consume ordered work queues where priority is the key order.
- ✅ Use range bounds to express interval queries directly instead of filtering all entries after collection.
- ✅ Use `BTreeMap` in tests and snapshot-like output when deterministic ordering matters more than expected constant-time lookup.

## Pitfalls
- ⚠️ Do not mutate keys through interior mutability so their `Ord` result changes while stored.
- ⚠️ Do not assume B-tree lookup is always faster than hashing; choose based on ordering and workload.
- ⚠️ `map[&key]` panics when the key is missing; use `get` for fallible lookup. See [[Index Panics vs get]].
- ⚠️ Floating-point types like `f64` do not implement `Ord` because of NaN semantics; use a deliberate wrapper if ordering floats is required.
- ⚠️ Do not expect insertion order; iteration is sorted order, not chronological order.
- ⚠️ Do not use `BTreeSet` when duplicate counts matter; use a map from value to count.

## See also
[[HashMap]] · [[The Entry API]] · [[Set Collections with HashSet and BTreeSet]] · [[Choosing Collection Types]] · [[Iterating Collections]] · [[Index Panics vs get]] · [[Ownership]] · [[Vec]] · [[Collections & Strings]]

## Sources
- Standard library `BTreeMap` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.BTreeMap.html
- Standard library `BTreeSet` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.BTreeSet.html
- Standard library collections overview — [[std]], https://doc.rust-lang.org/std/collections/index.html
- The Rust Programming Language, ch. 8.3 for map context — [[the-book]], https://doc.rust-lang.org/book/ch08-03-hash-maps.html
