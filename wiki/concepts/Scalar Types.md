---
type: concept
title: "Scalar Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, scalar-types, primitives, types]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Integer Overflow]]", "[[If Expressions]]", "[[Arrays]]", "[[Tuples]]", "[[String Slices]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html#scalar-types", "https://doc.rust-lang.org/reference/types.html#boolean-type", "https://doc.rust-lang.org/reference/types/numeric.html", "https://doc.rust-lang.org/reference/types/textual.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Integer Types"]
---

# Scalar Types

Rust's primary scalar types are integers, floating-point numbers, `bool`, and `char`; each represents one value with statically known operations.

## What it is
A scalar type represents a single value rather than a collection. Rust's introductory scalar set is:

- integers: signed `i8` through `i128`, unsigned `u8` through `u128`, plus pointer-sized `isize` and `usize`
- floats: `f32` and `f64`
- booleans: `bool`, either `true` or `false`
- characters: `char`, one Unicode scalar value

Rust is statically typed, so every value has a known type at compile time. The compiler often infers scalar types, but annotations are required when multiple choices remain possible.

## How it works
Integer literals default to `i32` when inference does not force another type. Floating-point literals default to `f64`. Integer literals may use suffixes such as `57u8` and visual separators such as `1_000`.

`usize` is the natural type for collection indexes and lengths because it matches the platform pointer width. It is not a general "bigger integer"; choose domain-specific integer widths when the size is part of the data format.

`bool` is required for [[If Expressions]] and `while` conditions. Rust does not convert integers, pointers, or collections to truthy or falsy values.

`char` is four bytes and represents a Unicode scalar value, not necessarily one user-perceived character. Text processing usually uses `&str`, `String`, or iterator methods over Unicode concepts; see [[String Slices]].

## Example
```rust
fn main() {
    let count: u32 = 42;
    let index: usize = 0;
    let ratio = 3.5; // f64 by default
    let enabled = count > 0;
    let letter = 'R';

    let values = [count, 7, 9];
    assert!(enabled);
    assert_eq!(values[index], 42);
    assert_eq!(letter.len_utf8(), 1);
    assert_eq!(ratio / 2.0, 1.75);
}
```

## Common errors
Conditions must be `bool`; Rust has no numeric truthiness:

```rust
fn main() {
    let count = 1;
    // if count { println!("nonzero"); }
}
```

Typical diagnostic:

```text
error[E0308]: mismatched types
expected `bool`, found integer
```

Fix with an explicit comparison such as `count != 0`.

## Best practice
- ✅ Let inference choose obvious local scalar types, but annotate public APIs and ambiguous parses.
- ✅ Use `usize` for indexing and lengths; use explicit integer widths for file formats, protocols, and FFI.
- ✅ Use explicit comparisons such as `number != 0` in conditions.
- ✅ Treat `char` as a Unicode scalar value; avoid assuming it equals a displayed grapheme.

## Pitfalls
- ⚠️ Assuming integer overflow behaves identically in debug and release builds; see [[Integer Overflow]] and [[Relying on Integer Overflow]].
- ⚠️ Using `as` casts casually can truncate or change meaning; prefer checked conversions where loss matters.
- ⚠️ Comparing floating-point values for exact equality can be inappropriate for computed values.
- ⚠️ Expecting `if number { ... }` to work; [[If Expressions]] require `bool`.

## See also
[[Integer Overflow]] · [[If Expressions]] · [[Arrays]] · [[Tuples]] · [[String Slices]] · [[Type Inference]] · [[Constants]] · [[Relying on Integer Overflow]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "Scalar Types" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html#scalar-types
- The Rust Reference, "Boolean type" — [[the-reference]], https://doc.rust-lang.org/reference/types/boolean.html
- The Rust Reference, "Numeric types" — [[the-reference]], https://doc.rust-lang.org/reference/types/numeric.html
- The Rust Reference, "Textual types" — [[the-reference]], https://doc.rust-lang.org/reference/types/textual.html
