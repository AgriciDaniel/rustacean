---
type: concept
title: "BTreeMap Ordering and Ranges"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, btreemap, ordering, ranges]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[BTreeMap and BTreeSet]]", "[[Choosing Standard Collections]]", "[[Entry API for Accumulator Maps]]", "[[Borrow for Equivalent Keys]]", "[[The Iterator Trait]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.BTreeMap.html", "https://doc.rust-lang.org/std/collections/index.html#use-a-btreemap-when"]
rust_version: "edition 2024 / 1.85+"
---

# BTreeMap Ordering and Ranges

`BTreeMap` is the standard sorted map: it stores keys by `Ord`, iterates in key order, and supports range, first, and last operations that `HashMap` does not provide.

## What it is
`BTreeMap<K, V>` is an ordered map backed by a B-tree.
It requires keys to implement `Ord`.
It keeps entries sorted by key.
Iteration over keys, values, and pairs follows ascending key order.
Its map operations are O(log n), with efficient sequential traversal.

Choose it when sorted keys are part of the problem.
Examples include leaderboards by score, time windows, prefix-like ranges over sortable keys, and deterministic output.
It is also a good fit when tests or serialized output should not depend on `HashMap` ordering.

## How it works
A B-tree stores multiple sorted entries per node.
This reduces allocation count and improves cache behavior compared with a simple pointer-heavy binary tree.
The public contract is not about node layout.
The public contract is sorted behavior through `Ord`.

Important method families:
- `get`, `get_mut`, `contains_key`, `insert`, `remove`
- `range` and `range_mut`
- `first_key_value`, `last_key_value`
- `pop_first`, `pop_last`
- `entry`
- `iter`, `keys`, `values`

`range` accepts Rust range syntax such as `10..20`, `10..`, `..=20`, and bound pairs.
It returns a double-ended iterator over matching key-value pairs.
`first_key_value` and `last_key_value` inspect minimum and maximum keys.
`pop_first` and `pop_last` remove entries from either end.

The key order must remain stable while a key is inside the map.
Mutating a key through interior mutability so its ordering changes is a logic error.
The standard library contains the damage inside the map, but results are unspecified.

## Example
```rust
use std::collections::BTreeMap;

fn main() {
    let mut events = BTreeMap::new();
    events.insert(10, "start");
    events.insert(20, "parse");
    events.insert(30, "render");
    events.insert(40, "finish");

    let window: Vec<_> = events
        .range(15..=35)
        .map(|(&time, &name)| (time, name))
        .collect();

    assert_eq!(window, [(20, "parse"), (30, "render")]);
    assert_eq!(events.first_key_value(), Some((&10, &"start")));
    assert_eq!(events.last_key_value(), Some((&40, &"finish")));
}
```

## Edge cases
```rust
use std::collections::BTreeMap;

fn main() {
    let mut queue = BTreeMap::from([(2, "medium"), (1, "low"), (3, "high")]);
    assert_eq!(queue.pop_last(), Some((3, "high")));
    assert_eq!(queue.pop_first(), Some((1, "low")));
    assert_eq!(queue.into_iter().collect::<Vec<_>>(), [(2, "medium")]);
}
```

## Best practice
- ✅ Use `BTreeMap` when sorted iteration is part of the output contract.
- ✅ Use `range` for submaps instead of scanning the entire collection.
- ✅ Use `first_key_value` and `last_key_value` for boundary inspection.
- ✅ Use `pop_first` or `pop_last` when consuming a sorted worklist by key.
- ✅ Derive `Ord` only when field order represents the real ordering.
- ✅ Prefer a newtype key when domain order is not the same as tuple or struct field order.
- ✅ Use `HashMap` instead when order and ranges are irrelevant and the hot operation is lookup.

## Pitfalls
- ⚠️ Mutating a key so its `Ord` changes while it is in the map is a logic error; see [[Mutating Collection Keys In Place]].
- ⚠️ `BTreeMap` lookup is O(log n), not expected O(1); use [[HashMap Method Families]] when sorted behavior is unnecessary.
- ⚠️ `range` panics for invalid ranges such as a start greater than the end.
- ⚠️ `insert` updates the value for an equivalent key but does not replace the stored key.
- ⚠️ `Ord` must be a total order; types such as raw floating-point `f32` and `f64` do not implement `Ord`.
- ⚠️ Do not use sorted maps as a substitute for a priority queue when only the top item matters; see [[BinaryHeap Priority Queues]].

## See also
[[std: Collections Deep]] · [[BTreeMap and BTreeSet]] · [[Choosing Standard Collections]] · [[Set Collections with HashSet and BTreeSet]] · [[BinaryHeap Priority Queues]] · [[HashMap Method Families]] · [[Entry API for Accumulator Maps]] · [[Borrow for Equivalent Keys]] · [[The Iterator Trait]] · [[Mutating Collection Keys In Place]]

## Sources
- Rust standard library, `BTreeMap` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BTreeMap.html
- Rust standard library, "Use a BTreeMap when" - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#use-a-btreemap-when
