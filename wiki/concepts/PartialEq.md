---
type: concept
title: "PartialEq"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, equality, traits, derive]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[The Debug Trait]]", "[[Scalar Types]]", "[[Pattern Matching]]", "[[Testing]]", "[[Readable Generic APIs]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-01-writing-tests.html", "https://doc.rust-lang.org/std/cmp/trait.PartialEq.html", "https://doc.rust-lang.org/reference/patterns.html#constant-patterns"]
rust_version: "edition 2024 / 1.85+"
---

# PartialEq

`PartialEq`/`Eq` define value equality (`==`); commonly derived with `#[derive(PartialEq, Eq)]`.

## What it is
`PartialEq` is the trait behind `==` and `!=`. It defines when two values should be considered equal
for a type's domain.

`Eq` is a marker trait for equality that is reflexive: every value equals itself. Floating-point types
implement `PartialEq` but not `Eq` because `NaN != NaN`.

Most plain data structs and enums should derive `PartialEq`, and derive `Eq` too when all fields have
full equivalence semantics.

## How it works
The `==` operator calls `PartialEq::eq`; `!=` uses `ne`, whose default implementation negates `eq`.
Derived `PartialEq` compares structs field by field and enums by variant plus fields.

`PartialEq<Rhs = Self>` has a right-hand-side type parameter, so cross-type equality is possible, but
it should be used sparingly and consistently. Incoherent equality relationships are confusing even if
they compile.

Tests rely heavily on `PartialEq`, and `assert_eq!` also wants [[The Debug Trait]] so failure output
can show both sides.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct UserId(u64);

fn main() {
    assert_eq!(UserId(7), UserId(7));
    assert_ne!(UserId(7), UserId(8));
}
```

## Edge cases
Manual implementations are useful when equality ignores cached or derived fields:

```rust
struct SearchTerm {
    original: String,
    normalized: String,
}

impl PartialEq for SearchTerm {
    fn eq(&self, other: &Self) -> bool {
        self.normalized == other.normalized
    }
}

impl Eq for SearchTerm {}

fn main() {
    let a = SearchTerm { original: "Rust".into(), normalized: "rust".into() };
    let b = SearchTerm { original: "rust".into(), normalized: "rust".into() };
    assert!(a == b);
}
```

## Common errors
Comparing custom values without `PartialEq` produces E0369:

```rust
struct Token(String);

fn main() {
    // let same = Token("a".into()) == Token("a".into());
}
```

Typical diagnostic:

```text
error[E0369]: binary operation `==` cannot be applied to type `Token`
help: consider annotating `Token` with `#[derive(PartialEq)]`
```

Fix it with a derive when field-by-field equality is correct:

```rust
#[derive(PartialEq, Eq)]
struct Token(String);
```

## Best practice
- ✅ Derive `PartialEq` and `Eq` for transparent value types.
- ✅ Pair equality derives with `Debug` for high-quality test failures.
- ✅ Implement equality manually only when the domain rule differs from field-by-field comparison.
- ✅ Keep `eq` cheap, deterministic, and side-effect free.
- ✅ Test edge cases for manual equality, especially ignored fields and normalization.

## Pitfalls
- ⚠️ Do not derive equality for types whose fields include caches that should be ignored.
- ⚠️ Do not implement cross-type equality unless transitivity remains easy to reason about.
- ⚠️ Remember that `f32` and `f64` are not `Eq`.
- ⚠️ Do not use approximate floating equality inside `PartialEq` unless the type's whole invariant is designed around that.
- ⚠️ Constants in patterns interact with structural equality rules; do not assume any `PartialEq` impl is pattern-compatible.

## See also
[[The Debug Trait]] · [[The Display Trait]] · [[Testing]] · [[Pattern Matching]] · [[Scalar Types]] · [[Readable Generic APIs]] · [[Type Inference]] · [[Statements vs Expressions]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 11.1 "Checking Results with the assert_eq! and assert_ne! Macros" — [[the-book]], https://doc.rust-lang.org/book/ch11-01-writing-tests.html
- Standard library, `std::cmp::PartialEq` — https://doc.rust-lang.org/std/cmp/trait.PartialEq.html
- The Rust Reference, "Constant patterns" — [[the-reference]], https://doc.rust-lang.org/reference/patterns.html#constant-patterns
