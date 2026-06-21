---
type: concept
title: "Practice: Generics"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, generics]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Generics]]", "[[Trait Bounds]]", "[[Where Clauses]]", "[[Type Inference]]", "[[Static Dispatch with Generics]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Generics

The generics group teaches writing one definition that works for many concrete types. The key idea is that type parameters become useful only when their required behavior is expressed through bounds.

## What it is
These exercises cover generic structs, generic functions, type parameters in `impl` blocks, and adding bounds when the body needs operations on `T`.

## How it works
`T` is a placeholder for a concrete type chosen at compile time. If code prints, compares, clones, or otherwise operates on `T`, the signature must say which trait makes that operation legal.

## Example
```rust
use std::fmt::Display;

struct Pair<T> {
    left: T,
    right: T,
}

impl<T: Display> Pair<T> {
    fn describe(&self) -> String {
        format!("{} and {}", self.left, self.right)
    }
}

fn main() {
    let pair = Pair { left: 1, right: 2 };
    println!("{}", pair.describe());
}
```

## Best practice
- ✅ Add the narrowest trait bounds needed by the implementation.
- ✅ Use generics to remove meaningful duplication across types.
- ✅ Move complex bounds into `where` clauses when readability improves.

## Pitfalls
- ⚠️ Do not assume every `T` can be copied, printed, ordered, or default-constructed.
- ⚠️ Avoid generic parameters that do not affect the API or implementation.
- ⚠️ Remember that `impl<T>` for a generic type must repeat the type parameter.

## See also
[[Practice (Rustlings)]] · [[Generics]] · [[Trait Bounds]] · [[Where Clauses]] · [[Type Inference]] · [[Static Dispatch with Generics]] · [[Readable Generic APIs]]

## Sources
- Rustlings `14_generics` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

