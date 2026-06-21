---
type: concept
title: "Practice: Clippy"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, clippy]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[rustfmt and Clippy]]", "[[Lints and Lint Levels]]", "[[Use cargo check While Editing]]", "[[Needless Clone]]", "[[Borrowed Parameter APIs]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Clippy

The clippy group teaches reading lint feedback as idiom training. The key idea is that code can compile and still be noisier, slower, or less idiomatic than Rust tooling expects.

## What it is
These exercises cover common Clippy suggestions around needless code, inefficient conversions, avoidable clones, and clearer standard-library methods.

## How it works
Clippy runs extra static analyses on top of compilation. A lint identifies a pattern, explains why it is suspicious, and often suggests a replacement that keeps behavior but improves style or performance.

## Example
```rust
fn has_rust(words: &[String]) -> bool {
    words.iter().any(|word| word == "rust")
}

fn main() {
    let words = vec![String::from("rust"), String::from("book")];
    println!("{}", has_rust(&words));
}
```

## Best practice
- ✅ Read the lint name and explanation before applying the suggestion.
- ✅ Prefer borrowed parameters when a function only reads data.
- ✅ Let Clippy teach idioms, then decide whether a local exception is justified.

## Pitfalls
- ⚠️ Do not mechanically silence lints with `allow` before understanding them.
- ⚠️ Do not clone owned values when comparison or borrowing is enough.
- ⚠️ Some lints are style guidance, not proof that the current code is wrong.

## See also
[[Practice (Rustlings)]] · [[rustfmt and Clippy]] · [[Lints and Lint Levels]] · [[Use cargo check While Editing]] · [[Needless Clone]] · [[Borrowed Parameter APIs]] · [[Idioms & API Design]]

## Sources
- Rustlings `22_clippy` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

