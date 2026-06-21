---
type: moc
title: "Enums & Pattern Matching"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, enums, pattern-matching]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Enums]]", "[[Patterns]]", "[[The match Expression]]", "[[Option]]", "[[Exhaustiveness]]", "[[Destructuring]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-00-enums.html", "https://doc.rust-lang.org/book/ch19-00-patterns.html"]
rust_version: "edition 2024 / 1.85+"
---

# Enums & Pattern Matching

Enums and pattern matching are Rust's tools for modeling closed sets of possibilities and handling every shape of data explicitly.

## Concepts
- [[Enums]] - defining one-of-many domain types.
- [[Enum Variants with Data]] - attaching variant-specific payloads.
- [[Option]] - representing presence or absence without null.
- [[The match Expression]] - branching on ordered patterns.
- [[Patterns]] - the syntax shared by `match`, `let`, `if let`, loops, and parameters.
- [[Refutable and Irrefutable Patterns]] - knowing where patterns are allowed to fail.
- [[Exhaustiveness]] - compiler checking that all match cases are covered.
- [[Destructuring]] - breaking structs, tuples, and enum payloads into bindings.
- [[Match Guards]] - adding `if` conditions to match arms.
- [[Binding with @]] - binding while testing a subpattern.

## Patterns
- [[if let]] - concise handling for one interesting refutable case.
- [[let else]] - early-exit extraction that keeps the happy path left-aligned.
- [[Catch-All and Wildcard Patterns]] - using `_`, named fallbacks, and `..` intentionally.

## Antipatterns
- [[Overbroad Catch-All Match Arms]] - hiding future domain decisions behind `_`.
- [[Pattern Variable Shadowing]] - accidentally binding a new name instead of comparing with an outer one.

## Example
```rust
enum Input {
    Number(i32),
    Empty,
}

fn classify(input: Input) -> &'static str {
    match input {
        Input::Number(n) if n > 0 => "positive",
        Input::Number(_) => "non-positive",
        Input::Empty => "empty",
    }
}

fn main() {
    assert_eq!(classify(Input::Number(3)), "positive");
    assert_eq!(classify(Input::Empty), "empty");
}
```

## Best practice
- ✅ Model closed domain alternatives with [[Enums]] instead of strings or sentinel values.
- ✅ Reach first for [[The match Expression]] when every case matters.
- ✅ Use [[if let]] and [[let else]] only when ignoring or exiting on other cases is intentional.

## Pitfalls
- ⚠️ Do not lose [[Exhaustiveness]] by replacing meaningful matches with broad wildcards.
- ⚠️ Do not mistake pattern bindings for equality checks; see [[Pattern Variable Shadowing]].
- ⚠️ Do not unwrap `Option` just to get at a payload; use patterns or combinators.

## See also
[[Enums]] · [[Enum Variants with Data]] · [[Option]] · [[The match Expression]] · [[Patterns]] · [[Exhaustiveness]] · [[Destructuring]] · [[Match Guards]] · [[Binding with @]] · [[if let]] · [[let else]] · [[Catch-All and Wildcard Patterns]] · [[Overbroad Catch-All Match Arms]] · [[Pattern Variable Shadowing]]

## Sources
- The Rust Programming Language, ch. 6 "Enums and Pattern Matching" - [[the-book]], https://doc.rust-lang.org/book/ch06-00-enums.html
- The Rust Programming Language, ch. 19 "Patterns and Matching" - [[the-book]], https://doc.rust-lang.org/book/ch19-00-patterns.html
