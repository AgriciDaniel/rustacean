---
type: concept
title: "Practice: Macros"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, macros]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[macro_rules!]]", "[[Declarative Macros]]", "[[Macro Fragment Specifiers]]", "[[Macro Repetitions]]", "[[Macro Hygiene]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Macros

The macros group teaches small `macro_rules!` definitions and how token patterns expand into Rust code. The key idea is that declarative macros match syntax fragments before type checking.

## What it is
These exercises cover macro invocation syntax, defining a macro, fragment specifiers, repetitions, and expanding repeated inputs into generated code.

## How it works
`macro_rules!` arms match token trees using fragment specifiers like `expr`, `ident`, and `ty`. The expansion substitutes captured fragments into the output pattern, then the compiler checks the generated Rust.

## Example
```rust
macro_rules! make_vec {
    ($($value:expr),* $(,)?) => {{
        let mut values = Vec::new();
        $(values.push($value);)*
        values
    }};
}

fn main() {
    let numbers = make_vec![1, 2, 3];
    println!("{numbers:?}");
}
```

## Best practice
- ✅ Use macros when syntax repetition is the problem, not ordinary runtime branching.
- ✅ Pick the narrowest fragment specifier that matches the intended input.
- ✅ Include optional trailing comma handling for list-like macros.

## Pitfalls
- ⚠️ Macro errors often point at expanded code; reduce the input to the smallest failing case.
- ⚠️ Do not use a macro where a function or generic would be clearer.
- ⚠️ Remember that macros must be defined or imported before ordinary use in many contexts.

## See also
[[Practice (Rustlings)]] · [[macro_rules!]] · [[Declarative Macros]] · [[Macro Fragment Specifiers]] · [[Macro Repetitions]] · [[Macro Hygiene]] · [[Function-like Macros]]

## Sources
- Rustlings `21_macros` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

