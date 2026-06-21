---
type: concept
title: "Practice: Functions"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, functions]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Functions]]", "[[Statements vs Expressions]]", "[[Type Inference]]", "[[Methods]]", "[[Associated Functions]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Functions

The functions group teaches Rust's explicit function signatures and expression-based returns. The key idea is that parameters and return types are part of the contract, while the last expression can be the returned value without `return`.

## What it is
These exercises cover defining functions, passing arguments, adding type annotations, and returning values from expression tails.

## How it works
Rust requires parameter types in function definitions. A function that returns a value declares `-> Type`; the body can end with an expression of that type, or use `return` for early exits.

## Example
```rust
fn square(n: i32) -> i32 {
    n * n
}

fn describe_count(count: usize) -> String {
    format!("items: {}", square(count as i32))
}

fn main() {
    println!("{}", describe_count(4));
}
```

## Best practice
- ✅ Let the final expression carry the normal return value.
- ✅ Keep parameter types explicit and choose owned versus borrowed parameters deliberately.
- ✅ Use small functions to name meaningful transformations, not to hide simple syntax.

## Pitfalls
- ⚠️ A trailing semicolon turns an expression into a statement returning `()`.
- ⚠️ Function argument types are not inferred from call sites.
- ⚠️ `return` is useful for early exits, but it is not required for ordinary tail returns.

## See also
[[Practice (Rustlings)]] · [[Functions]] · [[Statements vs Expressions]] · [[Type Inference]] · [[Methods]] · [[Associated Functions]] · [[The Never Type]]

## Sources
- Rustlings `02_functions` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

