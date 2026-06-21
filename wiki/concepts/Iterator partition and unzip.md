---
type: concept
title: "Iterator partition and unzip"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, partition, unzip, collection]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator zip and enumerate]]", "[[Iterator collect and FromIterator]]", "[[Consuming Adapters]]", "[[Tuples]]", "[[Vec]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.partition", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.unzip"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator partition and unzip

`partition` consumes items into two collections based on a predicate, while `unzip` consumes pairs into two collections by tuple position.

## What it is
`Iterator::partition` splits one stream into two destination collections.
The predicate sees each item by reference.
Items for which the predicate returns `true` go into the first collection.
Items for which it returns `false` go into the second collection.
Both output collections have the same type.
`Iterator::unzip` splits an iterator of pairs into two destination collections.
Left tuple elements go into the first collection.
Right tuple elements go into the second collection.
The two output collection types may differ.
Both methods are consuming operations.
Both require destination collection types that can be default-constructed and extended.

## How it works
`partition::<B, _>(predicate)` creates two `B` values with `Default`.
Then it extends one or the other with each input item.
The item is moved into exactly one side.
This is a stable allocation-friendly way to divide data without writing two manual pushes.
The relative order of items is preserved inside each output collection for ordered collections such as `Vec`.
`unzip` expects each iterator item to be a tuple `(A, B)`.
It creates two collections and extends them with tuple fields separately.
Nested tuple unzipping is supported through the trait implementations.
Because both methods consume the whole iterator, they do not short-circuit.
For a single matching item or index, use `find` or `position` instead.
For in-place partitioning, the stable method here is not the nightly `partition_in_place`.

## Example
```rust
fn main() {
    let values = [1, 2, 3, 4, 5];

    let (even, odd): (Vec<_>, Vec<_>) = values
        .into_iter()
        .partition(|n| n % 2 == 0);

    assert_eq!(even, [2, 4]);
    assert_eq!(odd, [1, 3, 5]);
}
```

## Edge cases
```rust
fn main() {
    let pairs = [("a", 1), ("b", 2), ("c", 3)];
    let (letters, numbers): (Vec<_>, Vec<_>) = pairs.into_iter().unzip();

    assert_eq!(letters, ["a", "b", "c"]);
    assert_eq!(numbers, [1, 2, 3]);

    let empty: [i32; 0] = [];
    let split: (Vec<_>, Vec<_>) = empty.into_iter().partition(|n| n > &0);
    assert_eq!(split, (vec![], vec![]));
}
```

## Best practice
- ✅ Use `partition` when every item belongs to exactly one of two groups.
- ✅ Use `unzip` to reverse a `zip` or split computed pair streams.
- ✅ Add an explicit output type, usually `(Vec<_>, Vec<_>)`, to guide inference.
- ✅ Use `filter` plus separate consumers only when the groups are not both needed at once.
- ✅ Use `find` or `any` when you only need existence, not both partitions.
- ✅ Use named variables for the returned tuple immediately.
- ✅ Prefer preserving errors before partitioning fallible results.
- ✅ Consider a map or custom struct when more than two groups are needed.

## Pitfalls
- ⚠️ `partition` collects both sides completely, so it can allocate for both.
- ⚠️ The predicate receives `&Self::Item`, so reference-heavy inputs can create double references.
- ⚠️ Both `partition` outputs have the same collection type.
- ⚠️ `unzip` requires pair items; use `map` first if you need to compute pairs.
- ⚠️ Type inference often needs help for `unzip`.
- ⚠️ Partitioning into `Vec`s does not sort either side.
- ⚠️ `partition` is not a stable in-place reorder operation.
- ⚠️ Collecting before partitioning is usually an [[Unnecessary Collect]].

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator zip and enumerate]] · [[Iterator collect and FromIterator]] · [[Iterator map and filter]] · [[Iterator predicate search adapters]] · [[Consuming Adapters]] · [[Tuples]] · [[Vec]] · [[Type Inference]] · [[Unnecessary Collect]] · [[Iterating Collections]]

## Sources
- Rust standard library, `Iterator::partition` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.partition
- Rust standard library, `Iterator::unzip` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.unzip
