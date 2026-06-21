---
type: concept
title: "Practice: Move Semantics"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, ownership]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Move Semantics]]", "[[Ownership]]", "[[Borrowing]]", "[[References]]", "[[Mutable References]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Move Semantics

The move semantics group teaches when values are transferred, borrowed, mutably borrowed, copied, or cloned. The key idea is to choose the access mode that matches the function's real need.

## What it is
These exercises make ownership errors concrete: using a moved value, borrowing instead of taking ownership, mutating through `&mut`, and cloning only when a second owned value is required.

## How it works
Passing a `String` by value moves it; passing `&String` or better `&str` borrows it. Only one mutable borrow may be active at a time, and mutable access cannot overlap with immutable borrows.

## Example
```rust
fn shout(name: &str) -> String {
    format!("HELLO, {}!", name.to_uppercase())
}

fn add_suffix(name: &mut String) {
    name.push_str(" Ferris");
}

fn main() {
    let mut name = String::from("rust");
    println!("{}", shout(&name));
    add_suffix(&mut name);
    println!("{name}");
}
```

## Best practice
- ✅ Borrow when reading, mutably borrow when updating in place, and move when taking ownership.
- ✅ Prefer `&str` and `&[T]` parameters for flexible borrowed APIs.
- ✅ Use `.clone()` only when two independent owners are genuinely needed.

## Pitfalls
- ⚠️ Do not use `.clone()` only to silence a compiler error; revisit the ownership path.
- ⚠️ Do not try to use a non-`Copy` value after moving it.
- ⚠️ Do not overlap `&mut T` with any other borrow of the same value.

## See also
[[Practice (Rustlings)]] · [[Move Semantics]] · [[Ownership]] · [[Borrowing]] · [[References]] · [[Mutable References]] · [[Copy and Clone]]

## Sources
- Rustlings `06_move_semantics` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

