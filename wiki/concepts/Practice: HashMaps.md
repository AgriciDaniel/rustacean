---
type: concept
title: "Practice: HashMaps"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, hashmaps]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[HashMap]]", "[[HashMap Method Families]]", "[[The Entry API]]", "[[Entry API for Accumulator Maps]]", "[[Hash and Eq Contracts]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: HashMaps

The hashmaps group teaches key-value storage, lookup, update, and counting patterns. The key idea is that map APIs encode whether a key may already exist, and the entry API avoids repeated lookup work.

## What it is
These exercises cover creating `HashMap`, inserting pairs, reading with `get`, overwriting values, and accumulating counts.

## How it works
`HashMap<K, V>` owns keys and values. Keys must satisfy hash and equality contracts. `entry(key).or_insert(value)` gives mutable access to the value for a key, inserting a default only when missing.

## Example
```rust
use std::collections::HashMap;

fn word_counts(words: &[&str]) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    for word in words {
        *counts.entry((*word).to_string()).or_insert(0) += 1;
    }
    counts
}

fn main() {
    println!("{:?}", word_counts(&["rust", "rust", "book"]));
}
```

## Best practice
- ✅ Use the entry API for insert-or-update logic.
- ✅ Choose owned key types when the map owns its data.
- ✅ Prefer `get` when absence is normal and should stay explicit as `Option`.

## Pitfalls
- ⚠️ Do not index a map with `map[key]` unless missing keys should panic.
- ⚠️ Do not mutate key fields in ways that change their hash or equality while stored.
- ⚠️ Avoid double lookups with `contains_key` followed by `insert` when `entry` fits.

## See also
[[Practice (Rustlings)]] · [[HashMap]] · [[HashMap Method Families]] · [[The Entry API]] · [[Entry API for Accumulator Maps]] · [[Hash and Eq Contracts]] · [[Choosing Standard Collections]]

## Sources
- Rustlings `11_hashmaps` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

