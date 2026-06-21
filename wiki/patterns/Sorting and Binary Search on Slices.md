---
type: pattern
title: "Sorting and Binary Search on Slices"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, slices, sorting, search, ordering]
domain: "std: Vec, String & Slices"
difficulty: intermediate
related: ["[[Vec Methods Reference]]", "[[The Slice Type]]", "[[Iterator Performance]]", "[[PartialEq]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.slice.html#method.sort", "https://doc.rust-lang.org/std/primitive.slice.html#method.binary_search"]
rust_version: "edition 2024 / 1.85+"
---

# Sorting and Binary Search on Slices

Sort vectors through their slice methods, and use `binary_search` only after the slice is sorted according to the same ordering.

## What it is
Sorting and searching are methods on `[T]`.
Because `Vec<T>` dereferences to `[T]`, `numbers.sort()` is a slice method call.
`sort` is stable: equal elements keep their relative order.
`sort_unstable` may reorder equal elements but can be faster and avoid some overhead.
`sort_by` and `sort_by_key` let you choose custom ordering.
`sort_by_cached_key` can help when computing keys is expensive.
`binary_search`, `binary_search_by`, and `binary_search_by_key` search sorted slices.
The search result is `Result<usize, usize>`: `Ok(index)` if found, or `Err(insertion_index)` if absent.

## How it works
Sorting mutates the slice in place.
The element type must implement `Ord` for `sort` and `sort_unstable`.
Use `sort_by` when comparing derived values, reverse order, or floating-point wrappers.
The comparator must define a consistent total order.
For floats, use `f32::total_cmp` or `f64::total_cmp` when NaN-aware total ordering is required.
Binary search assumes the slice is already sorted by the exact same ordering.
If duplicates exist, `binary_search` may return any matching index.
Use `partition_point` to find lower and upper bounds around duplicate runs.
The insertion index from `Err(i)` is where a value could be inserted while preserving sorted order.
Do not sort just to find one item unless repeated searches justify the sort cost.

## Example
```rust
fn main() {
    let mut words = vec!["pear", "fig", "banana", "kiwi"];

    words.sort_by_key(|word| word.len());
    assert_eq!(words, vec!["fig", "pear", "kiwi", "banana"]);

    let lengths: Vec<usize> = words.iter().map(|word| word.len()).collect();
    assert!(matches!(lengths.binary_search(&4), Ok(1 | 2)));
    assert_eq!(lengths.binary_search(&5), Err(3));

    let first_len_four = lengths.partition_point(|len| *len < 4);
    let after_len_four = lengths.partition_point(|len| *len <= 4);
    assert_eq!(&words[first_len_four..after_len_four], &["pear", "kiwi"]);
}
```

## Best practice
- ✅ Sort with `sort` when equal-element order matters.
- ✅ Sort with `sort_unstable` when equal-element order does not matter.
- ✅ Use `sort_by_key` for cheap derived keys.
- ✅ Use `sort_by_cached_key` for expensive key extraction.
- ✅ Use `binary_search_by_key` when searching by one field of a struct.
- ✅ Use the `Err` insertion index to maintain sorted vectors.
- ✅ Use `partition_point` for duplicate ranges and insertion positions.
- ✅ Keep comparator logic small and test it when domain ordering is subtle.

## Pitfalls
- ⚠️ Binary search on an unsorted slice returns meaningless results.
- ⚠️ Sorting by one key and searching by another violates the search precondition.
- ⚠️ `binary_search` does not guarantee the first matching duplicate.
- ⚠️ A comparator that is not transitive can make sorting panic or produce surprising order.
- ⚠️ `partial_cmp(...).unwrap()` on floats can panic on NaN.
- ⚠️ `sort_by_key` recomputes keys during sorting; use cached keys when key extraction is expensive.
- ⚠️ Inserting into the middle of a `Vec` after search is O(n) because later elements shift.
- ⚠️ Sorting invalidates assumptions tied to old indexes.

## See also
[[std: Vec, String & Slices]] · [[Vec Methods Reference]] · [[The Slice Type]] · [[Slicing and Range Indexing]] · [[Index Panics vs get]] · [[Iterator Performance]] · [[PartialEq]] · [[Stale Slice Indices]] · [[Manual Index Loops for Speed]]

## Sources
- Rust standard library, slice sorting methods — [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.sort
- Rust standard library, slice binary search methods — [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.binary_search
