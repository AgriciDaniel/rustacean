---
type: concept
title: "Practice: Primitive Types"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, primitive-types]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Scalar Types]]", "[[Tuples]]", "[[Arrays]]", "[[The Slice Type]]", "[[Slicing and Range Indexing]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Primitive Types

The primitive types group teaches Rust's fixed-size building blocks: scalars, tuples, arrays, and slices. The key idea is to distinguish owned fixed-size values from borrowed views into contiguous data.

## What it is
These exercises drill numeric and boolean scalars, characters, tuples, arrays, destructuring, indexing, and slice syntax.

## How it works
Arrays have a length that is part of their type, such as `[i32; 3]`. Slices like `&[i32]` borrow a contiguous region without owning it. Tuples group a fixed set of values that may have different types.

## Example
```rust
fn first_two_sum(values: &[i32]) -> Option<i32> {
    if values.len() >= 2 {
        Some(values[0] + values[1])
    } else {
        None
    }
}

fn main() {
    let point = (3, 4);
    let numbers = [10, 20, 30];
    println!("x={}, sum={:?}", point.0, first_two_sum(&numbers));
}
```

## Best practice
- ✅ Use arrays for fixed-size homogeneous data.
- ✅ Accept slices when a function only needs to read a sequence.
- ✅ Destructure tuples when named intermediate bindings improve clarity.

## Pitfalls
- ⚠️ Array indexing can panic if the index is out of bounds.
- ⚠️ `[T; N]` and `[T; M]` are different types when `N != M`.
- ⚠️ `char` is a Unicode scalar value, not a single byte.

## See also
[[Practice (Rustlings)]] · [[Scalar Types]] · [[Tuples]] · [[Arrays]] · [[The Slice Type]] · [[Slicing and Range Indexing]] · [[Destructuring]]

## Sources
- Rustlings `04_primitive_types` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

