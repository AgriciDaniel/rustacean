---
type: concept
title: "Practice: Variables"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, variables]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Variables and Mutability]]", "[[Constants]]", "[[Shadowing]]", "[[Type Inference]]", "[[Scalar Types]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Variables

The variables group teaches that bindings are immutable by default, can be made mutable deliberately, and can be shadowed with a new binding. The key habit is choosing between `mut`, shadowing, constants, and type annotations intentionally.

## What it is
These exercises drill `let`, `let mut`, `const`, explicit type annotations, and shadowing. They make Rust's default immutability visible immediately.

## How it works
A plain `let x = ...;` binding cannot be reassigned. `let mut x = ...;` allows assignment to the same binding, while `let x = ...;` again creates a new binding that shadows the old one and may even have a different type.

## Example
```rust
const MAX_POINTS: u32 = 100;

fn main() {
    let score = 40;
    let score = score + 2; // shadowing creates a new immutable binding

    let mut attempts = 1;
    attempts += 1; // mutation changes the same binding

    println!("{score}/{MAX_POINTS} after {attempts} attempts");
}
```

## Best practice
- ✅ Prefer immutable bindings until mutation expresses the simplest state change.
- ✅ Use shadowing for transformations where each step has a clear new value.
- ✅ Add type annotations when they clarify intent or inference lacks enough information.

## Pitfalls
- ⚠️ Do not mark everything `mut`; it hides where state actually changes.
- ⚠️ Do not confuse shadowing with mutation; shadowing creates a fresh binding.
- ⚠️ Constants need an explicit type and are evaluated with stricter rules than runtime `let` bindings.

## See also
[[Practice (Rustlings)]] · [[Variables and Mutability]] · [[Constants]] · [[Shadowing]] · [[Type Inference]] · [[Scalar Types]] · [[Statements vs Expressions]]

## Sources
- Rustlings `01_variables` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

