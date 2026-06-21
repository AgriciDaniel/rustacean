---
type: pattern
title: "Building Strings Efficiently"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, string, allocation, formatting, performance]
domain: "std: Vec, String & Slices"
difficulty: intermediate
related: ["[[String vs str Methods]]", "[[Vec Capacity and Growth]]", "[[Reducing Heap Allocations]]", "[[Borrowing Strings and Slices]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/string/struct.String.html#method.with_capacity", "https://doc.rust-lang.org/std/fmt/trait.Write.html"]
rust_version: "edition 2024 / 1.85+"
---

# Building Strings Efficiently

Build strings by reserving a realistic byte capacity and appending with `push_str`, `push`, or `write!` instead of repeatedly allocating temporary strings.

## What it is
String building is the pattern of constructing owned UTF-8 output incrementally.
The target type is usually `String`.
The input is often a collection of `&str`, numbers, tokens, or parsed fields.
The performance issue is allocation churn.
Every time a string outgrows capacity, it may allocate a larger buffer and copy existing bytes.
Using `with_capacity`, `reserve`, and append-style APIs lets one buffer grow predictably.
`write!` appends formatted data to an existing `String` through `std::fmt::Write`.
`join` is often best when you already have a slice of string-like items and a delimiter.

## How it works
`String::with_capacity(n)` allocates enough room for at least `n` bytes.
`push_str(&str)` copies UTF-8 bytes into the existing string.
`push(char)` encodes one Unicode scalar value and appends it.
`write!(&mut s, "...")` appends formatted output without creating a separate `String` first.
`format!` is still right when the whole output is one expression.
`collect::<String>()` works for iterators of `char` or `&str`.
`String::from` and `.to_owned()` are simple ways to make one owned copy.
When composing lines, reserve approximate byte length rather than scalar count.
When input size is unknown, use `reserve` before large bursts if you can estimate the burst.
Use `try_reserve` for fallible allocation behavior in robust parsers or services.

## Example
```rust
use std::fmt::Write;

fn render_list(items: &[&str]) -> String {
    let estimated = items.iter().map(|s| s.len() + 2).sum();
    let mut out = String::with_capacity(estimated);

    for (index, item) in items.iter().enumerate() {
        if index > 0 {
            out.push_str(", ");
        }
        write!(&mut out, "{index}:{item}").expect("writing to String cannot fail");
    }

    out
}

fn main() {
    assert_eq!(render_list(&["red", "blue"]), "0:red, 1:blue");
}
```

## Best practice
- ✅ Use `String::with_capacity` when the final byte length is easy to estimate.
- ✅ Use `push_str` for appending borrowed text.
- ✅ Use `push` for one `char`, not a one-character `&str` unless you already have one.
- ✅ Use `write!` for numbers and mixed formatting into an existing buffer.
- ✅ Use `join` when delimiter insertion over existing string slices is the whole job.
- ✅ Use `format!` for clear one-shot formatting.
- ✅ Use `try_reserve` when allocation failure should be reported as an error.
- ✅ Measure before adding complex pooling or reusable buffers.

## Pitfalls
- ⚠️ Repeated `s = s + part` in a loop is noisy and can allocate more than needed.
- ⚠️ `format!("{out}{part}")` in a loop constructs a new string each iteration.
- ⚠️ Capacity is bytes, not user-visible characters.
- ⚠️ Over-reserving huge buffers from untrusted input can become a denial-of-service bug.
- ⚠️ `write!` needs `use std::fmt::Write;`, while byte streams use `std::io::Write`.
- ⚠️ `expect` after `write!` to `String` is acceptable because `fmt::Write for String` cannot fail.
- ⚠️ Full Unicode case mapping can change length, so precomputed capacity may still be an estimate.
- ⚠️ Do not return `&str` pointing into a local builder; return the `String`.

## See also
[[std: Vec, String & Slices]] · [[String vs str Methods]] · [[Vec Capacity and Growth]] · [[Reducing Heap Allocations]] · [[Borrowing Strings and Slices]] · [[Bytes Chars and Unicode]] · [[Splitting Strings Without Collecting]] · [[Return Iterators Instead of Collecting]] · [[Needless Clone]]

## Sources
- Rust standard library, `String::with_capacity`, `push_str`, and `push` — [[std]], https://doc.rust-lang.org/std/string/struct.String.html
- Rust standard library, `std::fmt::Write` — [[std]], https://doc.rust-lang.org/std/fmt/trait.Write.html
