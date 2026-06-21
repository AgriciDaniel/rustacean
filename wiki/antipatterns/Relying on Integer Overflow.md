---
type: antipattern
title: "Relying on Integer Overflow"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, antipattern, integers, overflow]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Integer Overflow]]", "[[Scalar Types]]", "[[panic!]]", "[[Result]]", "[[Testing]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow"]
rust_version: "edition 2024 / 1.85+"
---

# Relying on Integer Overflow

Relying on accidental integer overflow is a footgun because debug builds may panic while release builds may wrap, so the correct alternative is to choose an explicit overflow method.

## The mistake
The mistake is writing arithmetic that only behaves correctly if overflow wraps, then leaving that policy implicit in ordinary `+`, `-`, or `*` operators.

This often slips in through counters, byte arithmetic, small integer types, or tests that only run in one build profile.

Rust's Book calls relying on wrapping overflow behavior an error. If wrapping, checking, saturation, or overflow reporting is intended, the code should say so.

## Why it happens
Many languages define fixed-width integer overflow as wrapping, and many CPUs naturally wrap. Rust instead uses debug overflow checks to catch arithmetic bugs early.

In release builds, primitive integer overflow can wrap when checks are not enabled. That difference means code can appear safe in one profile and behave differently in another.

The standard library gives explicit method families so the code documents the intended policy and behaves consistently across build profiles.

## Example
```rust
fn next_byte_id(current: u8) -> u8 {
    current.wrapping_add(1)
}

fn add_score(score: u8, points: u8) -> u8 {
    score.saturating_add(points)
}

fn main() {
    assert_eq!(next_byte_id(255), 0);
    assert_eq!(add_score(250, 20), 255);
    assert_eq!(250u8.checked_add(20), None);
}
```

## Common errors
The same plain arithmetic can fail loudly in debug tests but appear to work in optimized builds:

```rust
fn main() {
    let max = u8::MAX;
    // let wrapped = max + 1;
}
```

Typical debug behavior:

```text
thread 'main' panicked at attempt to add with overflow
```

Fix by writing the policy in the operation name: `max.wrapping_add(1)`, `max.checked_add(1)`,
or `max.saturating_add(1)`.

## Best practice
- ✅ Use `checked_*` when overflow should become `None` or a domain error.
- ✅ Use `wrapping_*` when modulo arithmetic is the actual algorithm.
- ✅ Use `saturating_*` when values should clamp at the numeric bounds.
- ✅ Test arithmetic near minimum and maximum values, not only typical inputs.

## Pitfalls
- ⚠️ Do not assume debug and release profiles handle overflow identically.
- ⚠️ Do not silence a panic by switching blindly to `wrapping_*`; first decide the domain policy.
- ⚠️ Do not narrow integer types for storage without validating arithmetic ranges.
- ⚠️ Do not hide overflow behavior behind vague helper names; name the policy.

## See also
[[Integer Overflow]] · [[Scalar Types]] · [[panic!]] · [[Result]] · [[Testing]] · [[Constants]] · [[Type Inference]] · [[Arrays]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "Integer Overflow" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow
- The Rust Reference, "Operator expressions: overflow" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow
