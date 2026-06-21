---
type: concept
title: "Slicing and Range Indexing"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, slices, ranges, indexing, borrowing]
domain: "std: Vec, String & Slices"
difficulty: basic
related: ["[[The Slice Type]]", "[[Index Panics vs get]]", "[[String Byte Indexing]]", "[[Using chunks windows and split_at]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.slice.html#method.get", "https://doc.rust-lang.org/std/primitive.str.html#method.get"]
rust_version: "edition 2024 / 1.85+"
---

# Slicing and Range Indexing

Slicing borrows a contiguous region with a range, producing `&[T]`, `&mut [T]`, `&str`, or `&mut str` without copying elements.

## What it is
A slice is a borrowed view into a sequence.
For `[T]`, range bounds are element indexes.
For `str`, range bounds are byte offsets that must land on UTF-8 character boundaries.
Range syntax includes `a..b`, `a..`, `..b`, `..=b`, and `..`.
Index syntax such as `items[1..3]` panics when the range is invalid.
`get` and `get_mut` return `Option` instead of panicking.
`split_at` gives two non-overlapping slices at one index.
`split_at_checked` is the checked version for code that accepts an arbitrary split point.

## How it works
Slicing does not allocate.
The returned slice borrows the same backing storage as the original array, vector, or string.
Immutable slices allow many readers.
Mutable slices require unique access to the borrowed region.
For ordinary slices, `&items[1..3]` means "borrow elements at indexes 1 and 2."
For strings, `&text[1..3]` means "borrow bytes 1 through 2 if those bytes form complete UTF-8 code point boundaries."
That difference is why string slicing by numeric offsets is often wrong in user-facing text.
Use `char_indices` when a string algorithm must convert character positions to valid byte ranges.
Use `split_at_mut` when you need two mutable, disjoint regions of one slice.
Use pattern-based string splitting for delimiters instead of manual byte math.

## Example
```rust
fn main() {
    let mut values = [10, 20, 30, 40, 50];

    assert_eq!(&values[1..4], &[20, 30, 40]);
    assert_eq!(values.get(10), None);

    let (left, right) = values.split_at_mut(2);
    left[0] = 11;
    right[0] = 33;
    assert_eq!(values, [11, 20, 33, 40, 50]);

    let text = "aé日";
    assert_eq!(text.get(0..1), Some("a"));
    assert_eq!(text.get(1..3), Some("é"));
    assert_eq!(text.get(2..3), None);
}
```

## Best practice
- ✅ Use range syntax when bounds are local, obvious, and already known valid.
- ✅ Use `get` or `get_mut` for indexes derived from input, parsing, or cached state.
- ✅ Use `split_at_checked` for a checked split point that should not panic.
- ✅ Prefer `split_at_mut` to unsafe pointer tricks for two mutable regions.
- ✅ For strings, use `char_indices`, `split`, `split_once`, or parser state that stores byte offsets from the string itself.
- ✅ Keep slice borrows short if the owner will be mutated afterward.
- ✅ Accept slices in APIs to support arrays, vectors, and boxed slices.
- ✅ Document whether indexes in a string API are bytes, scalar values, or grapheme clusters.

## Pitfalls
- ⚠️ String indexes are byte offsets, not character indexes; see [[String Byte Indexing]] and [[Assuming String Indexes Are Characters]].
- ⚠️ `items[a..b]` panics if `a > b` or `b > len`.
- ⚠️ `text[a..b]` also panics if either bound is not a UTF-8 boundary.
- ⚠️ Cached indexes can go stale after insertion, removal, filtering, or sorting; see [[Stale Slice Indices]].
- ⚠️ A mutable slice borrow blocks other access to the same owner while it is live.
- ⚠️ Slicing a `Vec<T>` does not freeze its allocation after the borrow ends.
- ⚠️ `split_at` panics for an out-of-bounds midpoint; choose `split_at_checked` for untrusted input.
- ⚠️ Slices do not own data, so they cannot outlive the owner.

## See also
[[std: Vec, String & Slices]] · [[The Slice Type]] · [[Vec Methods Reference]] · [[String vs str Methods]] · [[Bytes Chars and Unicode]] · [[Using chunks windows and split_at]] · [[Index Panics vs get]] · [[String Byte Indexing]] · [[Stale Slice Indices]]

## Sources
- Rust standard library, primitive slice indexing and `get` — [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.get
- Rust standard library, primitive `str` indexing and `get` — [[std]], https://doc.rust-lang.org/std/primitive.str.html#method.get
