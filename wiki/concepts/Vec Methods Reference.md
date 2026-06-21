---
type: concept
title: "Vec Methods Reference"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, vec, std, collections, methods]
domain: "std: Vec, String & Slices"
difficulty: basic
related: ["[[Vec Capacity and Growth]]", "[[Slicing and Range Indexing]]", "[[Filtering Vecs with dedup retain and drain]]", "[[Borrowing Strings and Slices]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html"]
rust_version: "edition 2024 / 1.85+"
---

# Vec Methods Reference

`Vec<T>` is Rust's standard growable, contiguous, owned sequence; most work falls into construction, capacity management, element access, mutation, filtering, and conversion to slices.

## What it is
`Vec<T>` owns elements of one type in insertion order.
It dereferences to `[T]`, so slice methods such as `sort`, `binary_search`, `chunks`, and `windows` are available on a vector value.
A vector has a length, which counts initialized elements, and a capacity, which counts how many elements fit before reallocation.
The core mental model is "owned buffer plus slice view."
Use `Vec<T>` when the collection length changes or when ownership of the elements belongs to this value.
Use `&[T]` or `&mut [T]` when a function only needs to inspect or mutate an existing sequence.
This note is a routing reference; deeper notes cover capacity, slicing, filtering, sorting, and chunking.

## How it works
Construction APIs include `Vec::new`, `Vec::with_capacity`, `vec![]`, `Vec::from`, and `Iterator::collect`.
Inspection APIs include `len`, `is_empty`, `capacity`, `first`, `last`, `get`, and `as_slice`.
Stack-like APIs include `push`, `pop`, and, when order does not matter, `swap_remove`.
Insertion and removal APIs such as `insert` and `remove` preserve order but shift later elements.
Bulk APIs include `extend`, `extend_from_slice`, `append`, `clear`, `truncate`, `resize`, and `split_off`.
Filtering APIs include `retain`, `retain_mut`, `dedup`, `dedup_by`, `dedup_by_key`, and `drain`.
Capacity APIs include `reserve`, `reserve_exact`, `try_reserve`, `shrink_to`, and `shrink_to_fit`.
Conversion APIs include `as_slice`, `as_mut_slice`, `into_boxed_slice`, and `leak`.
Indexing with `v[i]` panics when `i` is out of bounds; `get` and `get_mut` return `Option`.
Mutation that grows the vector may reallocate and invalidate pointers, raw addresses, and borrowed element references.

## Example
```rust
fn main() {
    let mut numbers = Vec::with_capacity(4);
    numbers.extend([10, 20, 30]);
    numbers.push(40);

    assert_eq!(numbers.len(), 4);
    assert!(numbers.capacity() >= 4);
    assert_eq!(numbers.first(), Some(&10));
    assert_eq!(numbers.get(10), None);

    let removed = numbers.swap_remove(1);
    assert_eq!(removed, 20);
    numbers.sort();
    assert_eq!(numbers.as_slice(), &[10, 30, 40]);

    let tail = numbers.split_off(2);
    assert_eq!(numbers, vec![10, 30]);
    assert_eq!(tail, vec![40]);
}
```

## Best practice
- ✅ Accept `&[T]` for read-only sequence parameters unless the function must own or grow the collection.
- ✅ Accept `&mut [T]` for in-place algorithms that do not change length.
- ✅ Use `Vec<T>` in return positions when the function constructs a new owned sequence.
- ✅ Use `get` and `get_mut` when the index may come from input or stale state.
- ✅ Use `extend` or `collect` for iterator-driven construction.
- ✅ Use `reserve` or `with_capacity` when the approximate final size is known.
- ✅ Use `swap_remove` for O(1) removal when preserving order is irrelevant.
- ✅ Convert to a slice with `as_slice` or by coercion when calling slice-oriented code.

## Pitfalls
- ⚠️ `v[i]`, `insert`, `remove`, and `split_off` panic when their index is out of bounds; see [[Index Panics vs get]].
- ⚠️ Holding `&v[i]` and then calling `push` is rejected because growth can move the buffer; see [[Holding Collection Element References Across Mutation]].
- ⚠️ `remove(0)` in a loop is usually quadratic because every removal shifts elements.
- ⚠️ `reserve_exact` is not a promise that capacity will equal the requested amount.
- ⚠️ `clear` drops elements but does not necessarily release allocation.
- ⚠️ `dedup` only removes consecutive duplicates, not duplicates anywhere in the vector.
- ⚠️ `drain` removes elements even if you only partly consume the returned iterator.
- ⚠️ Raw-part APIs are unsafe escape hatches; prefer safe conversions.

## See also
[[std: Vec, String & Slices]] · [[Vec]] · [[Vec Capacity and Growth]] · [[Slicing and Range Indexing]] · [[Filtering Vecs with dedup retain and drain]] · [[Sorting and Binary Search on Slices]] · [[Using chunks windows and split_at]] · [[Borrowing Strings and Slices]] · [[Index Panics vs get]] · [[Stale Slice Indices]]

## Sources
- Rust standard library, `std::vec::Vec` — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html
- Rust standard library, slice methods available through `Deref<Target = [T]>` — [[std]], https://doc.rust-lang.org/std/primitive.slice.html
