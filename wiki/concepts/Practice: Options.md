---
type: concept
title: "Practice: Options"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, option]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Option]]", "[[Option Combinators]]", "[[if let]]", "[[let else]]", "[[Question Mark with Option]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Options

The options group teaches representing a value that may be absent without null. The key idea is to handle `Some` and `None` explicitly, either with pattern matching or with combinators that preserve absence.

## What it is
These exercises cover `Option<T>`, `match`, `if let`, `while let`, `unwrap` alternatives, and optional transformations.

## How it works
`Option<T>` is either `Some(T)` or `None`. Methods like `map`, `and_then`, `unwrap_or`, and `ok_or` let code transform present values while keeping missing values explicit.

## Example
```rust
fn first_even(numbers: &[i32]) -> Option<i32> {
    numbers.iter().copied().find(|n| n % 2 == 0)
}

fn main() {
    let label = first_even(&[1, 3, 8])
        .map(|n| format!("first even: {n}"))
        .unwrap_or_else(|| String::from("no even values"));
    println!("{label}");
}
```

## Best practice
- ✅ Use `match` when each case needs different logic.
- ✅ Use combinators for straightforward transformations.
- ✅ Convert to `Result` when absence must become an explained error.

## Pitfalls
- ⚠️ Do not use `unwrap` in learning code unless the exercise is specifically about panics.
- ⚠️ Do not ignore the `None` branch; it is part of the type's meaning.
- ⚠️ Avoid nested matches when `and_then`, `map`, or `?` with `Option` would be clearer.

## See also
[[Practice (Rustlings)]] · [[Option]] · [[Option Combinators]] · [[if let]] · [[let else]] · [[Question Mark with Option]] · [[Predicate Checks with is_some_and and matches]]

## Sources
- Rustlings `12_options` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

