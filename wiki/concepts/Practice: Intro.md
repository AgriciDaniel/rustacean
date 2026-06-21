---
type: concept
title: "Practice: Intro"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, intro]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[The rustc Compiler]]", "[[Cargo Build Run Check Test]]", "[[rustup and Installation]]", "[[Comments]]", "[[The Guessing Game Tutorial]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Intro

The Rustlings intro group teaches the exercise loop: edit a tiny Rust file, run the checker, and use compiler output as the next instruction. The skill is not syntax breadth; it is learning to make one precise fix at a time.

## What it is
This group is the warm-up for the rest of Rustlings. It confirms that the toolchain works, that comments can disable placeholder code, and that the compiler is the primary feedback surface.

## How it works
Rust files are compiled before they run. When a file has placeholder text or an intentionally wrong line, `rustc` reports the exact location and often suggests the shape of the fix. Treat each message as a constraint to satisfy, then rerun quickly.

## Example
```rust
fn main() {
    // A complete Rust program can be this small.
    let language = "Rust";
    println!("Hello, {language}!");
}
```

## Best practice
- ✅ Make the smallest edit that answers the current compiler error.
- ✅ Read the first error first; later errors often disappear after the first fix.
- ✅ Keep example files simple until the exercise asks for a new concept.

## Pitfalls
- ⚠️ Do not edit generated or source material outside the exercise file.
- ⚠️ Do not ignore warnings forever; many Rustlings lessons are about making code idiomatic, not merely compiling.
- ⚠️ Do not guess from line numbers alone; read the diagnostic text and suggested fix.

## See also
[[Practice (Rustlings)]] · [[The rustc Compiler]] · [[Cargo Build Run Check Test]] · [[rustup and Installation]] · [[Comments]] · [[The Guessing Game Tutorial]] · [[Tooling & Getting Started]]

## Sources
- Rustlings `00_intro` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

