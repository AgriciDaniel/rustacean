---
type: concept
title: "Practice: Structs"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, structs]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Named Field Structs]]", "[[Tuple Structs]]", "[[Unit-Like Structs]]", "[[Methods]]", "[[Struct Update Syntax]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Structs

The structs group teaches grouping related data under one named type and attaching behavior with methods. The key idea is that structs make invariants easier to see than loose tuples or repeated parameters.

## What it is
These exercises cover named-field structs, tuple structs, method `impl` blocks, derived traits, and update syntax.

## How it works
A struct definition names the fields and their types. Methods live in `impl Type` blocks and take `self`, `&self`, or `&mut self` depending on whether they consume, read, or mutate the value.

## Example
```rust
#[derive(Debug, Clone)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

fn main() {
    let rect = Rectangle { width: 3, height: 4 };
    println!("{rect:?} area={}", rect.area());
}
```

## Best practice
- ✅ Use named fields when field meaning matters at construction sites.
- ✅ Put behavior that depends on the struct's fields in methods.
- ✅ Derive standard traits when the derived behavior matches the type's semantics.

## Pitfalls
- ⚠️ Do not expose public fields when constructors or methods must preserve invariants.
- ⚠️ Struct update syntax may move non-`Copy` fields from the source value.
- ⚠️ Do not use tuple structs when named fields would prevent argument-order mistakes.

## See also
[[Practice (Rustlings)]] · [[Named Field Structs]] · [[Tuple Structs]] · [[Unit-Like Structs]] · [[Methods]] · [[Struct Update Syntax]] · [[Deriving Traits on Structs]]

## Sources
- Rustlings `07_structs` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

