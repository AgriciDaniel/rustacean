---
type: pattern
title: "Filtering Vecs with dedup retain and drain"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, vec, filtering, drain, dedup]
domain: "std: Vec, String & Slices"
difficulty: intermediate
related: ["[[Vec Methods Reference]]", "[[Sorting and Binary Search on Slices]]", "[[Unnecessary Collect]]", "[[Iterator Method Trio]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html#method.retain", "https://doc.rust-lang.org/std/vec/struct.Vec.html#method.dedup", "https://doc.rust-lang.org/std/vec/struct.Vec.html#method.drain"]
rust_version: "edition 2024 / 1.85+"
---

# Filtering Vecs with dedup retain and drain

Use `retain` to keep selected elements in place, `dedup` to remove adjacent duplicates, and `drain` to remove a range while optionally consuming removed values.

## What it is
Filtering a vector means changing which elements remain.
`retain` walks elements in order and keeps only those whose predicate returns `true`.
`retain_mut` also lets the predicate mutate each element before deciding.
`dedup` removes consecutive equal elements.
`dedup_by` and `dedup_by_key` define what "same run" means.
`drain(range)` removes a range and returns an iterator over removed elements.
These methods preserve the vector allocation for future use.
They are often clearer and faster than building a second vector manually.

## How it works
`retain` visits each element exactly once in original order.
The predicate receives `&T`.
`retain_mut` receives `&mut T`.
Elements that fail the predicate are dropped.
`dedup` compares adjacent elements and removes later items in each equal run.
To remove all duplicates regardless of position, sort first and then dedup, or use a set when order constraints differ.
`drain` holds a mutable borrow of the vector until the drain iterator is dropped.
Removed elements are yielded by value.
If a `Drain` is leaked, the vector may lose elements outside the obvious consumed part, so do not intentionally leak it.
Use `clear` when removing everything without needing removed values.

## Example
```rust
fn main() {
    let mut numbers = vec![3, 1, 2, 3, 2, 1, 4];

    numbers.retain(|n| *n % 2 == 1);
    assert_eq!(numbers, vec![3, 1, 3, 1]);

    numbers.sort();
    numbers.dedup();
    assert_eq!(numbers, vec![1, 3]);

    let mut words = vec!["zero", "one", "two", "three"];
    let removed: Vec<_> = words.drain(1..3).collect();
    assert_eq!(removed, vec!["one", "two"]);
    assert_eq!(words, vec!["zero", "three"]);
}
```

## Best practice
- ✅ Use `retain` for simple keep/drop filtering.
- ✅ Use `retain_mut` when normalization and filtering can happen in one pass.
- ✅ Sort before `dedup` when you want uniqueness and sorted order is acceptable.
- ✅ Use `dedup_by_key` for run-based uniqueness by a derived field.
- ✅ Use `drain` when removed elements need to be processed or collected.
- ✅ Drop or fully consume `Drain` before using the vector again.
- ✅ Use `clear` for "remove all" when removed values do not matter.
- ✅ Prefer these methods over manual index removal loops.

## Pitfalls
- ⚠️ `dedup` does not remove non-adjacent duplicates.
- ⚠️ `retain` keeps elements where the predicate is `true`; the naming is easy to invert mentally.
- ⚠️ `remove(i)` inside a forward loop can skip elements and is often quadratic.
- ⚠️ `drain(..)` empties the vector even if you do not collect the iterator.
- ⚠️ The vector is mutably borrowed while a drain iterator exists.
- ⚠️ Sorting before dedup changes order.
- ⚠️ Using a `HashSet` to track seen items can change performance and requires hashing.
- ⚠️ Filtering invalidates cached indexes and element positions; see [[Stale Slice Indices]].

## See also
[[std: Vec, String & Slices]] · [[Vec Methods Reference]] · [[Sorting and Binary Search on Slices]] · [[Unnecessary Collect]] · [[Iterator Method Trio]] · [[Stale Slice Indices]] · [[Index Panics vs get]] · [[Reducing Heap Allocations]] · [[HashMap]]

## Sources
- Rust standard library, `Vec::retain` and `Vec::retain_mut` — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#method.retain
- Rust standard library, `Vec::dedup` family — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#method.dedup
- Rust standard library, `Vec::drain` — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#method.drain
