---
type: concept
title: "Practice: If"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, if]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[If Expressions]]", "[[Statements vs Expressions]]", "[[The match Expression]]", "[[Patterns]]", "[[Scalar Types]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: If

The `if` group teaches that Rust branches require `bool` conditions and can produce values. The key idea is that every branch of a value-producing `if` must have one compatible type.

## What it is
These exercises cover `if`, `else if`, `else`, branch conditions, and assigning the result of a branch expression to a binding.

## How it works
Rust does not coerce integers into booleans: conditions must be `true` or `false`. When an `if` is used as an expression, each branch must evaluate to the same type because the receiving binding has one type.

## Example
```rust
fn size_label(n: usize) -> &'static str {
    if n == 0 {
        "empty"
    } else if n < 10 {
        "small"
    } else {
        "large"
    }
}

fn main() {
    println!("{}", size_label(7));
}
```

## Best practice
- ✅ Use `if` for simple boolean decisions.
- ✅ Use `match` when branching by shape, variant, or many exact values.
- ✅ Return the branch expression directly when it keeps the function clear.

## Pitfalls
- ⚠️ Do not write `if n { ... }`; compare explicitly, such as `if n != 0`.
- ⚠️ Do not mix branch result types like `i32` in one branch and `&str` in another.
- ⚠️ Watch trailing semicolons inside expression branches.

## See also
[[Practice (Rustlings)]] · [[If Expressions]] · [[Statements vs Expressions]] · [[The match Expression]] · [[Patterns]] · [[Scalar Types]] · [[Option]]

## Sources
- Rustlings `03_if` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

