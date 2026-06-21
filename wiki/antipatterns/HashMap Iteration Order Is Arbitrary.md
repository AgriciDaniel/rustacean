---
type: antipattern
title: "HashMap Iteration Order Is Arbitrary"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashmap, testing, determinism]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[HashMap Method Families]]", "[[Choosing Standard Collections]]", "[[BTreeMap Ordering and Ranges]]", "[[Set Collections with HashSet and BTreeSet]]", "[[Index Panics vs get]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.iter", "https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/collections/index.html#iterators"]
rust_version: "edition 2024 / 1.85+"
---

# HashMap Iteration Order Is Arbitrary

Do not write logic, tests, or output formats that depend on `HashMap` or `HashSet` iteration order; collect and sort, or choose an ordered collection.

## The mistake
The mistake is treating unordered collection iteration as if it were insertion order or sorted order.
`HashMap::iter`, `keys`, and `values` visit entries in arbitrary order.
`HashSet` has the same issue.
That order can change across runs, platforms, Rust versions, capacities, insertion histories, and hasher seeds.

This often appears in:
- brittle unit tests
- unstable JSON or text output
- flaky snapshots
- accidental API contracts
- examples that pass locally but fail elsewhere

## Why it happens
`HashMap` is optimized for expected O(1) lookup, insertion, and removal.
Its internal bucket layout is an implementation detail.
The default hasher is randomly seeded.
Capacity changes can also rearrange buckets.
Iteration follows the internal table, not semantic key order.

Even if one input appears to produce a stable order today, that is not a promise.
The standard docs describe the iterator order as arbitrary.
For deterministic order, use an ordered collection or sort explicitly.

`BTreeMap` iterates by key order.
`BTreeSet` iterates by value order.
Sorting a collected vector is often best when a hash table is still the right working structure.

## Example
```rust
use std::collections::HashMap;

fn main() {
    let map = HashMap::from([("b", 2), ("a", 1), ("c", 3)]);

    let mut pairs: Vec<_> = map.iter().map(|(&key, &value)| (key, value)).collect();
    pairs.sort_unstable_by_key(|&(key, _)| key);

    assert_eq!(pairs, [("a", 1), ("b", 2), ("c", 3)]);
}
```

## Edge cases
```rust
use std::collections::BTreeMap;

fn main() {
    let map = BTreeMap::from([("b", 2), ("a", 1), ("c", 3)]);
    let pairs: Vec<_> = map.into_iter().collect();

    assert_eq!(pairs, [("a", 1), ("b", 2), ("c", 3)]);
}
```

## Best practice
- ✅ Sort collected keys or pairs before assertions or display.
- ✅ Use `BTreeMap` when sorted order is a real part of the data model.
- ✅ Keep `HashMap` for working storage when fast unordered lookup is the important operation.
- ✅ Make ordering explicit at API boundaries.
- ✅ Document output order when an API returns collections or serialized data.
- ✅ Use snapshot tests only after normalizing unordered data.
- ✅ Prefer `BTreeSet` over `HashSet` when stable sorted membership output matters.

## Pitfalls
- ⚠️ A passing test that compares direct `HashMap` iteration can still be invalid.
- ⚠️ Insertion order is not preserved by `HashMap`.
- ⚠️ Rehashing after growth can change iteration order.
- ⚠️ A fixed custom hasher may make order look stable while still not promising a semantic order.
- ⚠️ Using `BTreeMap` only to make tests deterministic may be slower than sorting at the boundary.
- ⚠️ Serializing a hash map directly can produce noisy diffs when consumers expect stable output.

## See also
[[std: Collections Deep]] · [[HashMap Method Families]] · [[HashMap Hashers and Key Invariants]] · [[Choosing Standard Collections]] · [[BTreeMap Ordering and Ranges]] · [[Set Collections with HashSet and BTreeSet]] · [[Index Panics vs get]] · [[Untested Documentation Examples]] · [[Iterator Performance]] · [[Avoiding Premature Optimization]]

## Sources
- Rust standard library, `HashMap::iter` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.iter
- Rust standard library, `HashMap` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Rust standard library, collection iterators - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#iterators
