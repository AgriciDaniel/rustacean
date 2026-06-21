---
type: concept
title: "Practice: Vecs"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, vec]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Vec]]", "[[Vec Methods Reference]]", "[[Vec Capacity and Growth]]", "[[Iterator map and filter]]", "[[Iterating Collections]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Vecs

The vecs group teaches growable, owned sequences and the habit of transforming them with iteration. The key idea is that `Vec<T>` owns its elements, while iterators and slices let code inspect or transform them without unnecessary indexing.

## What it is
These exercises cover `Vec::new`, `vec![]`, `push`, iterating by reference, and producing a new vector from transformed values.

## How it works
A vector stores elements contiguously on the heap and grows as needed. Iterating with `iter()` borrows elements; `into_iter()` consumes the vector; `iter_mut()` gives mutable references to each element.

## Example
```rust
fn double_positive(values: &[i32]) -> Vec<i32> {
    values
        .iter()
        .copied()
        .filter(|n| *n > 0)
        .map(|n| n * 2)
        .collect()
}

fn main() {
    let numbers = vec![-1, 2, 3];
    println!("{:?}", double_positive(&numbers));
}
```

## Best practice
- ✅ Use `vec![...]` for known starting contents.
- ✅ Prefer iterator adapters for element-wise transformations.
- ✅ Pass `&[T]` when a function does not need vector-specific operations.

## Pitfalls
- ⚠️ Do not index in loops unless the index itself matters.
- ⚠️ Do not hold references into a vector while mutating it in ways that may reallocate.
- ⚠️ Avoid cloning a whole vector when borrowing or consuming it is the intended API.

## See also
[[Practice (Rustlings)]] · [[Vec]] · [[Vec Methods Reference]] · [[Vec Capacity and Growth]] · [[Iterator map and filter]] · [[Iterating Collections]] · [[std: Vec, String & Slices]]

## Sources
- Rustlings `05_vecs` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

