---
type: moc
title: "std: Vec, String & Slices"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, vec, string, slices, moc]
domain: "std: Vec, String & Slices"
difficulty: basic
related: ["[[Vec Methods Reference]]", "[[String vs str Methods]]", "[[Slicing and Range Indexing]]", "[[Bytes Chars and Unicode]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html", "https://doc.rust-lang.org/std/string/struct.String.html", "https://doc.rust-lang.org/std/primitive.slice.html", "https://doc.rust-lang.org/std/primitive.str.html"]
rust_version: "edition 2024 / 1.85+"
---

# std: Vec, String & Slices

This domain covers Rust's owned contiguous buffers (`Vec<T>` and `String`) and their borrowed views (`[T]` and `str`), with emphasis on method choice, allocation, slicing, and Unicode boundaries.

## Concepts
Start with [[Vec Methods Reference]] for the shape of vector APIs.
Use [[Vec Capacity and Growth]] when allocation behavior matters.
Use [[Slicing and Range Indexing]] for range syntax, checked indexing, and split points.
Use [[String vs str Methods]] to decide between owned text and borrowed text.
Use [[Bytes Chars and Unicode]] before writing text algorithms.
Link back to existing foundation notes for background: [[Vec]], [[The Slice Type]], and [[String and str]].
The key recurring distinction is ownership versus borrowing.
`Vec<T>` and `String` own allocation.
`&[T]`, `&mut [T]`, `&str`, and `&mut str` borrow views.

## Patterns
Use [[Building Strings Efficiently]] when constructing output incrementally.
Use [[Splitting Strings Without Collecting]] when processing delimited text.
Use [[Sorting and Binary Search on Slices]] for ordered in-place data and repeated lookup.
Use [[Filtering Vecs with dedup retain and drain]] for in-place vector filtering and removal.
Use [[Using chunks windows and split_at]] for grouped, overlapping, and disjoint slice views.
These patterns prefer std adapters over manual indexing.
They also prefer borrowed views over unnecessary owned copies.
They are intended to be used together: parse with split iterators, build with capacity, store in vectors, and pass around slices.

## Antipatterns
Use [[Assuming String Indexes Are Characters]] when reviewing string slicing bugs.
Also link to existing notes [[String Byte Indexing]], [[Index Panics vs get]], and [[Stale Slice Indices]].
The most common bug family is assuming a number has the same meaning across bytes, elements, scalar values, and displayed characters.
The second common bug family is caching an index before mutation and reusing it after sorting, filtering, insertion, or deletion.
The third common bug family is accepting owned collections where a borrowed slice would be more flexible.
Prefer APIs that make the unit and ownership obvious.

## API Design
Accept `&[T]` for read-only element sequences.
Accept `&mut [T]` for in-place algorithms that do not change length.
Accept `Vec<T>` when the function must consume, store, grow, or return ownership.
Accept `&str` for read-only text.
Accept `String` when the function must take ownership or mutate a growable text buffer.
Return iterators when callers can consume results lazily.
Return `Vec<T>` or `String` when the function creates owned output.
Avoid exposing indexes unless the unit is documented.
For string indexes, say "byte offset" when you mean byte offset.

## Method Families
Construction: `Vec::new`, `Vec::with_capacity`, `vec![]`, `String::new`, `String::with_capacity`, `From`, and `collect`.
Capacity: `capacity`, `reserve`, `reserve_exact`, `try_reserve`, `shrink_to`, and `shrink_to_fit`.
Access: `len`, `is_empty`, `first`, `last`, `get`, `get_mut`, `as_slice`, `as_str`, and `as_bytes`.
Mutation: `push`, `push_str`, `insert`, `remove`, `swap_remove`, `truncate`, `clear`, and `split_off`.
Filtering: `retain`, `retain_mut`, `dedup`, `dedup_by`, `dedup_by_key`, and `drain`.
Slice views: `chunks`, `chunks_exact`, `chunks_mut`, `windows`, `split_at`, `split_at_mut`, and `split_at_checked`.
Ordering: `sort`, `sort_by`, `sort_by_key`, `sort_unstable`, `binary_search`, and `partition_point`.
Text: `split`, `split_once`, `lines`, `trim`, `find`, `chars`, `bytes`, and `char_indices`.

## Review Checklist
Does the function accept `&str` or `&[T]` when ownership is unnecessary?
Does code use `get` or checked splitting when indexes come from input?
Does string code treat `len()` as bytes?
Does Unicode-sensitive code test non-ASCII input?
Does binary search happen only after sorting by the same order?
Does `dedup` operate on adjacent duplicates, or should the vector be sorted first?
Does a `Drain` iterator stay scoped tightly?
Does string building reserve a realistic capacity instead of formatting in a loop?
Does chunking validate a non-zero chunk size?
Does mutation happen after borrowed views have ended?

## See also
[[Vec Methods Reference]] · [[Vec Capacity and Growth]] · [[Slicing and Range Indexing]] · [[String vs str Methods]] · [[Bytes Chars and Unicode]] · [[Building Strings Efficiently]] · [[Splitting Strings Without Collecting]] · [[Sorting and Binary Search on Slices]] · [[Filtering Vecs with dedup retain and drain]] · [[Using chunks windows and split_at]] · [[Assuming String Indexes Are Characters]] · [[Borrowing Strings and Slices]] · [[String Byte Indexing]] · [[The Slice Type]]

## Sources
- Rust standard library, `Vec` — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html
- Rust standard library, `String` — [[std]], https://doc.rust-lang.org/std/string/struct.String.html
- Rust standard library, primitive slice — [[std]], https://doc.rust-lang.org/std/primitive.slice.html
- Rust standard library, primitive `str` — [[std]], https://doc.rust-lang.org/std/primitive.str.html
