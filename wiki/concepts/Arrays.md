---
type: concept
title: "Arrays"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, arrays, compound-types, indexing]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Tuples]]", "[[Scalar Types]]", "[[While and For Loops]]", "[[Slices]]", "[[Vectors]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html#the-array-type", "https://doc.rust-lang.org/reference/types/array.html", "https://doc.rust-lang.org/reference/expressions/array-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Arrays

A Rust array `[T; N]` is a fixed-size sequence of `N` initialized values of the same type `T`, with bounds-checked indexing in safe Rust.

## What it is
Arrays are primitive compound types for homogeneous fixed-size data. The length is part of the type, so `[i32; 3]` and `[i32; 4]` are different types.

Use arrays when the number of elements is fixed by the domain, such as weekdays, RGB channels, protocol bytes, or small lookup tables. Use [[Vectors]] when the collection must grow or shrink at runtime.

Array indexing uses `usize`: `array[0]`, `array[1]`, and so on.

## How it works
The array type is written `[T; N]`, where `N` is a constant expression that evaluates to `usize`. All elements are initialized, either by listing values or by repetition syntax such as `[0; 16]`.

Safe array indexing checks bounds. If an index is out of range at runtime, the program panics instead of reading invalid memory. When you want fallible access, use methods such as `.get(index)` on arrays or slices.

Arrays coerce naturally to slices in many borrowing contexts. A function that does not care about the exact length often accepts `&[T]` instead of `&[T; N]`.

## Example
```rust
fn main() {
    let months = ["Jan", "Feb", "Mar"];
    let zeros: [u8; 4] = [0; 4];

    assert_eq!(months[0], "Jan");
    assert_eq!(zeros, [0, 0, 0, 0]);

    let maybe_month = months.get(2);
    assert_eq!(maybe_month, Some(&"Mar"));
}
```

## Common errors
Indexing is bounds checked. If the compiler can prove the index is always invalid, it rejects the code:

```rust
fn main() {
    let values = [10, 20, 30];
    // let value = values[3];
}
```

Typical diagnostic:

```text
error: this operation will panic at runtime
index out of bounds: the length is 3 but the index is 3
```

Fix uncertain indexing with `.get(index)` and handle `Option`.

## Best practice
- ✅ Use arrays for fixed-size data where the length is a meaningful invariant.
- ✅ Prefer `for item in array` or `for item in &array` over manual index loops.
- ✅ Accept `&[T]` in APIs when any length should work.
- ✅ Use `.get()` when an index may be invalid and panic is not acceptable.

## Pitfalls
- ⚠️ Manual `while index < len` loops are easy to desynchronize; see [[While and For Loops]].
- ⚠️ Indexing with `array[index]` panics on out-of-bounds access.
- ⚠️ Expecting arrays to resize like [[Vectors]]; their length is fixed.
- ⚠️ Forgetting that `[expr; N]` repeats one value expression, which matters for non-`Copy` and const-evaluation rules.

## See also
[[Tuples]] · [[Slices]] · [[Vectors]] · [[While and For Loops]] · [[Scalar Types]] · [[panic!]] · [[Iterator Method Trio]] · [[Type Inference]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "The Array Type" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html#the-array-type
- The Rust Reference, "Array types" — [[the-reference]], https://doc.rust-lang.org/reference/types/array.html
- The Rust Reference, "Array expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/array-expr.html
