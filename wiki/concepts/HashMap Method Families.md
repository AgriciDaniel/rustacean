---
type: concept
title: "HashMap Method Families"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashmap, std, maps]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[HashMap]]", "[[The Entry API]]", "[[Borrow for Equivalent Keys]]", "[[HashMap Hashers and Key Invariants]]", "[[Choosing Standard Collections]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/collections/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# HashMap Method Families

`HashMap` methods fall into a few practical families: construction and capacity, lookup, mutation, entry-based conditional mutation, iteration, and draining/removal.

## What it is
`HashMap<K, V>` is the standard unordered key-value table.
It is the default map when keys implement `Eq + Hash`.
Its core operations are expected O(1), with occasional resizing costs.
The method surface is large because the type supports several ownership modes.
Some methods borrow keys, some move keys, some move values, and some yield iterators.

The most common methods are:
- `new`, `with_capacity`, `reserve`, `try_reserve`
- `insert`, `get`, `get_mut`, `contains_key`, `remove`
- `entry`, `or_insert`, `or_insert_with`, `and_modify`
- `iter`, `iter_mut`, `keys`, `values`, `into_iter`
- `retain`, `drain`, `clear`, `shrink_to_fit`

## How it works
Construction methods decide allocation and hasher state.
`HashMap::new()` starts empty and does not allocate until insertion.
`HashMap::with_capacity(n)` asks for enough buckets for at least `n` entries.
`reserve(additional)` grows ahead of time.
`try_reserve(additional)` reports allocation failure instead of panicking.

Lookup methods usually accept a borrowed form of the key.
For example, a `HashMap<String, V>` can often be queried with `&str`.
This works through `Borrow<Q>` when the borrowed form has matching `Hash` and `Eq`.
Use `get` when absence is ordinary.
Use indexing only when missing keys should be a panic.

Mutation methods differ in whether they replace, edit, or remove.
`insert` returns the old value if the key already existed.
`get_mut` gives `&mut V` without moving the key or value.
`remove` returns the owned value.
`retain` keeps only entries selected by a predicate.
`drain` removes all entries while yielding owned pairs.

Iteration order is arbitrary.
Do not sort tests by relying on the map's natural iteration.
Collect and sort keys when order matters to output or assertions.

## Example
```rust
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::with_capacity(3);
    scores.insert("blue".to_string(), 10);
    scores.insert("red".to_string(), 7);

    if let Some(score) = scores.get_mut("blue") {
        *score += 5;
    }

    let green = scores.entry("green".to_string()).or_insert(0);
    *green += 3;

    assert_eq!(scores.get("blue"), Some(&15));
    assert!(scores.contains_key("red"));

    let removed = scores.remove("red");
    assert_eq!(removed, Some(7));

    let mut keys: Vec<_> = scores.keys().map(String::as_str).collect();
    keys.sort_unstable();
    assert_eq!(keys, ["blue", "green"]);
}
```

## Best practice
- ✅ Use `with_capacity` or `reserve` when a large approximate size is known.
- ✅ Prefer `get` or `get_mut` over indexing when absence is part of normal control flow.
- ✅ Prefer `entry` over `contains_key` followed by `insert` for conditional updates.
- ✅ Sort collected keys or pairs before comparing unordered map output in tests.
- ✅ Use `try_reserve` in code paths that must handle allocation failure explicitly.
- ✅ Use `clear` when you want to reuse allocation for another batch.
- ✅ Use `shrink_to_fit` only when releasing memory matters more than likely reuse.

## Pitfalls
- ⚠️ Treating iteration order as stable makes tests and serialized output fragile; see [[HashMap Iteration Order Is Arbitrary]].
- ⚠️ Calling `contains_key` and then `insert` repeats a lookup when `entry` would express the operation once.
- ⚠️ Using indexing syntax for optional data turns a normal miss into a panic; see [[Index Panics vs get]].
- ⚠️ Holding references from `get` across mutation will often fail to compile for good reasons; see [[Holding Collection Element References Across Mutation]].
- ⚠️ Calling `shrink_to_fit` after every removal can create avoidable allocation churn.
- ⚠️ Custom key equality or hashing that ignores fields means `insert` updates the value but keeps the existing stored key.

## See also
[[std: Collections Deep]] · [[HashMap]] · [[The Entry API]] · [[Entry API for Accumulator Maps]] · [[HashMap Hashers and Key Invariants]] · [[HashMap Iteration Order Is Arbitrary]] · [[Choosing Standard Collections]] · [[Borrow for Equivalent Keys]] · [[Index Panics vs get]] · [[Capacity and Reallocation]]

## Sources
- Rust standard library, `HashMap` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Rust standard library, collections overview - [[std]],
  https://doc.rust-lang.org/std/collections/index.html
