---
type: pattern
title: "Entry API for Accumulator Maps"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, entry-api, hashmap, btreemap]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[The Entry API]]", "[[HashMap Method Families]]", "[[BTreeMap Ordering and Ranges]]", "[[Choosing Standard Collections]]", "[[Iterator Method Trio]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/index.html#entries", "https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry", "https://doc.rust-lang.org/std/collections/struct.BTreeMap.html#method.entry"]
rust_version: "edition 2024 / 1.85+"
---

# Entry API for Accumulator Maps

Use the entry API when a map update depends on whether the key is already present; it performs one lookup and returns a handle for insertion or in-place mutation.

## What it is
The entry API is an idiom for conditional map updates.
It exists on both `HashMap` and `BTreeMap`.
It avoids the common two-step pattern of checking for a key and then inserting.
It is especially useful for counters, grouping, indexes, caches, and frequency tables.

This note is a focused collections-deep companion to [[The Entry API]].
The existing note covers the general idiom.
Here the emphasis is on accumulator maps and choosing the right method.

Useful entry combinators include:
- `or_insert(value)`
- `or_insert_with(|| value)`
- `and_modify(|value| ...)`
- `or_default()`

`entry(key)` takes ownership of the key because the map may need to store it.
If the key is already present, the new key is not inserted.
The returned mutable reference points to the value in the map.

## How it works
Calling `map.entry(key)` searches the map.
If the key is absent, the result is vacant and can insert a value.
If the key is present, the result is occupied and can expose or replace the value.
The convenience methods collapse that enum handling into common cases.

For counters, `or_insert(0)` creates the first count.
For grouped vectors, `or_default()` creates an empty `Vec`.
For expensive defaults, `or_insert_with` delays construction until the key is actually missing.
For "modify if present, otherwise insert" behavior, chain `and_modify(...).or_insert(...)`.

The same pattern works for ordered and unordered maps.
Pick `HashMap` when order is irrelevant and expected O(1) lookup is enough.
Pick `BTreeMap` when deterministic sorted iteration or range queries matter.

## Example
```rust
use std::collections::HashMap;

fn main() {
    let words = ["red", "blue", "red", "green", "blue", "red"];
    let mut counts: HashMap<&str, usize> = HashMap::new();

    for word in words {
        *counts.entry(word).or_insert(0) += 1;
    }

    assert_eq!(counts.get("red"), Some(&3));
    assert_eq!(counts.get("blue"), Some(&2));
    assert_eq!(counts.get("green"), Some(&1));
}
```

## Edge cases
```rust
use std::collections::BTreeMap;

fn main() {
    let pairs = [("db", "slow"), ("ui", "bug"), ("db", "timeout")];
    let mut by_component: BTreeMap<&str, Vec<&str>> = BTreeMap::new();

    for (component, issue) in pairs {
        by_component.entry(component).or_default().push(issue);
    }

    assert_eq!(by_component["db"], ["slow", "timeout"]);
    assert_eq!(by_component.keys().copied().collect::<Vec<_>>(), ["db", "ui"]);
}
```

## Best practice
- ✅ Use `or_default()` when the value type has the obvious empty value, such as `Vec::new()` or `usize::default()`.
- ✅ Use `or_insert_with` when constructing the default value allocates, clones, or performs work.
- ✅ Use `and_modify(...).or_insert(...)` when existing and missing cases differ.
- ✅ Choose `BTreeMap` for accumulator output that must be sorted without a later sort.
- ✅ Keep entry mutation small and local so the mutable borrow of the map does not outlive its purpose.
- ✅ Prefer borrowed key types such as `&str` only when the borrowed data clearly outlives the map.

## Pitfalls
- ⚠️ `entry(key)` moves `key`; clone only when you still need a separate owned key afterward.
- ⚠️ `or_insert(expensive())` evaluates `expensive()` even when the key exists; use `or_insert_with`.
- ⚠️ You cannot use the same map immutably while an entry's mutable value reference is alive.
- ⚠️ `HashMap` accumulator output is unordered; sort before display or use `BTreeMap`.
- ⚠️ Avoid `contains_key` followed by `insert` for counters; it repeats intent and may repeat lookup work.
- ⚠️ Storing references in a map can be correct, but owned keys are usually simpler for long-lived maps.

## See also
[[std: Collections Deep]] · [[The Entry API]] · [[HashMap Method Families]] · [[BTreeMap Ordering and Ranges]] · [[Choosing Standard Collections]] · [[HashMap Iteration Order Is Arbitrary]] · [[Borrowing]] · [[Iterator Method Trio]] · [[Unnecessary Collect]] · [[Needless Clone]]

## Sources
- Rust standard library, collections entries - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#entries
- Rust standard library, `HashMap::entry` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry
- Rust standard library, `BTreeMap::entry` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BTreeMap.html#method.entry
