---
type: pattern
title: "Using chunks windows and split_at"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, slices, chunks, windows, split_at]
domain: "std: Vec, String & Slices"
difficulty: intermediate
related: ["[[The Slice Type]]", "[[Slicing and Range Indexing]]", "[[Vec Methods Reference]]", "[[Prefer Iterator Pipelines to Manual Indexing]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.slice.html#method.chunks", "https://doc.rust-lang.org/std/primitive.slice.html#method.windows", "https://doc.rust-lang.org/std/primitive.slice.html#method.split_at"]
rust_version: "edition 2024 / 1.85+"
---

# Using chunks windows and split_at

Use slice view adapters such as `chunks`, `windows`, and `split_at` to express grouped or overlapping access without manual index arithmetic.

## What it is
Slice adapters borrow views into an existing sequence.
`chunks(n)` yields non-overlapping slices of up to `n` elements.
`chunks_exact(n)` yields only full chunks and exposes the remainder.
`windows(n)` yields overlapping slices of exactly `n` elements.
`split_at(mid)` returns the prefix and suffix around one index.
`split_at_mut(mid)` returns two mutable, non-overlapping regions.
These methods work on arrays, slices, and vectors.
They avoid off-by-one errors common in manual loops.
They do not allocate.

## How it works
`chunks` and `windows` panic if the size argument is zero.
The last `chunks` item may be shorter than the requested size.
`chunks_exact` skips the final incomplete part from iteration and lets you inspect it with `remainder`.
`windows` cannot provide mutable overlapping windows because that would create aliased mutable references.
For mutable non-overlapping groups, use `chunks_mut` or `chunks_exact_mut`.
`split_at` panics if `mid > len`.
`split_at_checked` returns `None` instead of panicking for invalid `mid`.
`split_at_mut` is the safe way to borrow two disjoint mutable parts of one slice.
Prefer these adapters when the algorithm's shape is "groups", "neighbors", or "prefix plus rest."

## Example
```rust
fn main() {
    let values = [1, 2, 3, 4, 5];

    let sums: Vec<i32> = values.windows(2).map(|pair| pair[0] + pair[1]).collect();
    assert_eq!(sums, vec![3, 5, 7, 9]);

    let chunks: Vec<Vec<i32>> = values.chunks(2).map(|chunk| chunk.to_vec()).collect();
    assert_eq!(chunks, vec![vec![1, 2], vec![3, 4], vec![5]]);

    let mut editable = [10, 20, 30, 40];
    let (left, right) = editable.split_at_mut(2);
    left[1] += 1;
    right[0] += 1;
    assert_eq!(editable, [10, 21, 31, 40]);
}
```

## Best practice
- ✅ Use `windows(2)` for adjacent pair logic.
- ✅ Use `chunks(n)` when a short final group is valid.
- ✅ Use `chunks_exact(n)` when a short final group needs separate handling.
- ✅ Use `chunks_mut` for in-place non-overlapping group mutation.
- ✅ Use `split_at_mut` to avoid unsafe code when mutating two regions.
- ✅ Use `split_at_checked` for user-provided split positions.
- ✅ Keep chunk sizes non-zero and validate them before calling.
- ✅ Prefer adapters over `for i in 0..len - 1` style loops.

## Pitfalls
- ⚠️ `windows(0)` and `chunks(0)` panic.
- ⚠️ `windows(n)` yields overlapping immutable slices only.
- ⚠️ `chunks(n)` may yield a shorter final slice.
- ⚠️ `split_at(mid)` panics when `mid` is out of bounds.
- ⚠️ Indexing inside each window can still panic if you use the wrong size.
- ⚠️ Holding chunk borrows prevents mutation of the original slice until the borrow ends.
- ⚠️ These adapters borrow data; collecting `Vec<&[T]>` still depends on the original owner.
- ⚠️ String text also has split methods, but string indexes are byte boundaries; see [[String Byte Indexing]].

## See also
[[std: Vec, String & Slices]] · [[The Slice Type]] · [[Slicing and Range Indexing]] · [[Vec Methods Reference]] · [[Prefer Iterator Pipelines to Manual Indexing]] · [[Index Panics vs get]] · [[Manual Index Loops for Speed]] · [[Iterator Adapters]] · [[Borrowing Strings and Slices]]

## Sources
- Rust standard library, `slice::chunks` — [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.chunks
- Rust standard library, `slice::windows` — [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.windows
- Rust standard library, `slice::split_at` — [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.split_at
