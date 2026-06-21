---
type: concept
title: "HashSet"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashset, set]
domain: "std: Collections Deep"
difficulty: basic
related: ["[[Set Collections with HashSet and BTreeSet]]", "[[HashMap]]", "[[HashMap Hashers and Key Invariants]]", "[[HashMap Iteration Order Is Arbitrary]]", "[[Mutating Collection Keys In Place]]", "[[Choosing Standard Collections]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.HashSet.html", "https://doc.rust-lang.org/std/collections/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# HashSet

`HashSet<T>` stores each distinct value at most once and is the standard unordered membership collection for fast "have we seen this?" checks.

## What it is
`HashSet<T>` is the set sibling of [[HashMap]].
Conceptually, it is a hash table that stores keys without associated values.
Use it when the value itself is the identity and there is no meaningful payload to attach.

The element type must implement `Eq` and `Hash`.
For simple owned key types, derive them together with `#[derive(PartialEq, Eq, Hash)]`.
For borrowed lookups, the stored type can often be owned while lookup uses a borrowed form, such as querying a `HashSet<String>` with `&str`.

`HashSet` lives in `std::collections`, so import it explicitly:
`use std::collections::HashSet;`.
It is unordered: membership is the point, not position or sorted traversal.

## How it works
Insertion hashes the value, compares it against equivalent values in the table, and stores it only when no equal value is already present.
`insert` returns `true` when the value was newly inserted and `false` when an equal value was already present.
`contains`, `get`, `remove`, and `take` are the normal membership and removal operations.

Set algebra is built in.
`union`, `intersection`, `difference`, and `symmetric_difference` return lazy iterators over references to elements.
These iterators are useful when you want to inspect a relationship between sets without allocating a new set.
Collect into a new `HashSet` only when you need to keep the result.

Iteration order is arbitrary for the same reason [[HashMap Iteration Order Is Arbitrary]] exists.
If output order matters for tests, display, serialization, or deterministic logs, sort the values afterward or use [[BTreeMap and BTreeSet]].

The hash and equality contract is the same as for [[HashMap Hashers and Key Invariants]]:
if two values compare equal, they must hash the same way.
Changing a stored value so its equality or hash changes while it is in the set is a logic error, usually only possible through interior mutability, global state, I/O, or unsafe code.

## Example
```rust
use std::collections::HashSet;

fn unique_words(text: &str) -> HashSet<String> {
    let mut words = HashSet::new();

    for word in text.split_whitespace() {
        words.insert(word.to_ascii_lowercase());
    }

    words
}

fn main() {
    let words = unique_words("Rust rust borrow own borrow");

    assert_eq!(words.len(), 3);
    assert!(words.contains("rust"));
    assert!(words.contains("borrow"));
    assert!(!words.contains("move"));

    let keywords = HashSet::from(["rust".to_owned(), "async".to_owned()]);
    let mut overlap: Vec<_> = words.intersection(&keywords).cloned().collect();
    overlap.sort();

    assert_eq!(overlap, vec!["rust".to_owned()]);
}
```

## Worked example
A `HashSet` is a good fit for deduplication when the program only needs to remember which values have appeared.
It also communicates intent better than `HashMap<T, ()>`.

```rust
use std::collections::HashSet;

fn first_duplicates(ids: &[u32]) -> Vec<u32> {
    let mut seen = HashSet::with_capacity(ids.len());
    let mut duplicates = Vec::new();

    for &id in ids {
        if !seen.insert(id) {
            duplicates.push(id);
        }
    }

    duplicates
}

fn main() {
    assert_eq!(first_duplicates(&[7, 3, 7, 9, 3]), vec![7, 3]);
}
```

`with_capacity` is appropriate here because the input length is a known upper bound.
The returned duplicate order is controlled by the input loop, not by set iteration.

## Common operations
- `insert(value)` stores a value and reports whether it was new.
- `contains(value)` checks membership without taking ownership of the lookup value.
- `get(value)` returns a reference to the stored value equivalent to the lookup value.
- `remove(value)` removes an equivalent value and reports whether one existed.
- `take(value)` removes and returns the stored value.
- `replace(value)` inserts a value and returns the previous equivalent value, if any.
- `retain(predicate)` keeps only values accepted by the predicate.
- `clear()` removes all values while retaining allocation for reuse.

## Best practice
- ✅ Use `HashSet` when the question is membership, uniqueness, or "already seen?".
- ✅ Derive `PartialEq`, `Eq`, and `Hash` together for simple element types.
- ✅ Sort after iteration when deterministic order is required.
- ✅ Use `with_capacity` or `try_reserve` when building a large set from known-size input.
- ✅ Prefer `BTreeSet` through [[BTreeMap and BTreeSet]] when sorted iteration or range-like behavior is part of the requirement.
- ✅ Use set algebra iterators before allocating a new result set.
- ✅ Store owned values when the set must outlive the input it was built from.
- ✅ Use `insert`'s boolean result instead of a separate `contains` check for deduplication loops.

## Pitfalls
- ⚠️ Do not rely on `HashSet` iteration order; it is arbitrary like `HashMap` order.
- ⚠️ Do not mutate a stored value's hash or equality identity in place; see [[Mutating Collection Keys In Place]].
- ⚠️ Do not implement `Hash` and `Eq` inconsistently.
- ⚠️ Do not use `HashSet<T>` as a sorted set; use [[BTreeMap and BTreeSet]] or sort explicitly.
- ⚠️ Do not use a set when a map value carries meaningful state, counts, or metadata.
- ⚠️ Do not replace the default hasher for untrusted input without understanding collision attacks.
- ⚠️ Do not assume `retain` or iteration visits only live elements in O(len); current hash-table implementations may scan empty buckets too.
- ⚠️ Do not allocate a temporary owned lookup key when borrowed lookup is available.

## See also
[[Set Collections with HashSet and BTreeSet]] · [[HashMap]] · [[HashMap Method Families]] ·
[[HashMap Hashers and Key Invariants]] · [[HashMap Iteration Order Is Arbitrary]] ·
[[Mutating Collection Keys In Place]] · [[Borrow for Equivalent Keys]] · [[Choosing Standard Collections]] ·
[[Capacity and Reallocation]] · [[try_reserve and Fallible Allocation]] · [[std: Collections Deep]]

## Sources
- Rust standard library, `HashSet` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashSet.html
- Rust standard library, collections overview - [[std]],
  https://doc.rust-lang.org/std/collections/index.html
