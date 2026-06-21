---
type: concept
title: "Integer Overflow"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, integers, overflow, arithmetic]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Scalar Types]]", "[[Relying on Integer Overflow]]", "[[panic!]]", "[[Result]]", "[[Constants]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow"]
rust_version: "edition 2024 / 1.85+"
---

# Integer Overflow

Integer overflow happens when arithmetic produces a value outside an integer type's range; Rust checks it in debug builds and offers explicit methods for every intended overflow policy.

## What it is
Each integer type has a finite range. For example, `u8` stores `0..=255`, while `i8` stores `-128..=127`. Arithmetic that exceeds the range is overflow.

The Book teaches that debug builds check integer overflow and panic when it occurs. Release builds do not include those checks by default and use two's-complement wrapping for primitive integer operations. Relying on accidental wrapping is considered an error.

Rust gives named arithmetic methods so the overflow policy is visible in code: `checked_*`, `wrapping_*`, `saturating_*`, and `overflowing_*`.

## How it works
`checked_add` and related methods return `Option<T>`, using `None` for overflow. `wrapping_add` wraps modulo the integer range in all build modes. `saturating_add` clamps at the minimum or maximum. `overflowing_add` returns both the wrapped value and a boolean overflow flag.

Choose the method that matches the domain. Counters that must never exceed a maximum may saturate. Cryptographic or hash-style arithmetic may wrap deliberately. User-facing calculations often need checked arithmetic and error handling.

The compile-time range also affects constants: a literal or const expression that cannot fit the annotated type is rejected rather than becoming a surprising runtime value.

## Example
```rust
fn main() {
    let max = u8::MAX;

    assert_eq!(max.checked_add(1), None);
    assert_eq!(max.wrapping_add(1), 0);
    assert_eq!(max.saturating_add(1), u8::MAX);

    let (value, overflowed) = max.overflowing_add(1);
    assert_eq!(value, 0);
    assert!(overflowed);
}
```

## Common errors
Overflow in constants is rejected at compile time:

```rust
// const BAD: u8 = 255 + 1;
```

Typical diagnostic:

```text
error[E0080]: attempt to compute `u8::MAX + 1_u8`, which would overflow
```

Fix by choosing a wider type or spelling the intended policy:

```rust
const WRAPPED: u8 = u8::MAX.wrapping_add(1);
const CLAMPED: u8 = u8::MAX.saturating_add(1);
```

## Best practice
- ✅ Use plain `+`, `-`, and `*` only when overflow would be a bug and tests should catch it.
- ✅ Use `checked_*` when overflow is input-dependent and must be reported or handled.
- ✅ Use `wrapping_*` only when modular arithmetic is the actual algorithm.
- ✅ Use `saturating_*` for counters, scores, capacities, and limits that should clamp.

## Pitfalls
- ⚠️ Depending on debug panics as production validation; release behavior differs unless overflow checks are configured.
- ⚠️ Treating `wrapping_*` as a quick fix instead of documenting why wrapping is correct; see [[Relying on Integer Overflow]].
- ⚠️ Forgetting integer division truncates toward zero.
- ⚠️ Parsing into a smaller integer type without deciding how out-of-range input should fail.

## See also
[[Scalar Types]] · [[Relying on Integer Overflow]] · [[panic!]] · [[Result]] · [[Constants]] · [[Testing]] · [[Type Inference]] · [[Arrays]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "Integer Overflow" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow
- The Rust Reference, "Operator expressions: overflow" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow
