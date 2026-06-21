---
type: antipattern
title: "Integer Overflow Assumptions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, integers, overflow, arithmetic, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Integer Types]]", "[[Panic Unwinding and Abort]]", "[[Result]]", "[[Option vs Result]]", "[[Unwrap and Expect Overuse]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow", "https://doc.rust-lang.org/std/primitive.u32.html"]
rust_version: "edition 2024 / 1.85+"
---

# Integer Overflow Assumptions

Integer overflow assumptions are relying on `+`, `-`, or `*` to have one universal overflow behavior instead of choosing checked, saturating, overflowing, or wrapping arithmetic explicitly.

## The mistake
Rust integer operators can panic on overflow when checks are enabled, and optimized builds may wrap unless overflow checks are configured. Code that assumes "Rust always panics" or "Rust always wraps" is brittle.

The bug is not only performance-related. Overflow in counters, sizes, balances, timestamps, or offsets can become incorrect authorization, allocation, or indexing logic.

## Why it happens
Many languages define one default overflow behavior. Rust exposes multiple arithmetic families because different domains need different semantics.

Use `checked_*` when overflow is invalid, `saturating_*` when clamping is the intended result, `overflowing_*` when the overflow flag is part of the algorithm, and `wrapping_*` or `Wrapping<T>` for deliberate modular arithmetic.

For primitive integer operators, overflow checks are enabled in debug builds by default and can be configured for release profiles. When checks are disabled, two's-complement wrapping occurs for ordinary arithmetic. That profile sensitivity is why relying on `a + b` for overflow semantics is the footgun.

Casts are a separate issue: `as` conversions can truncate or reinterpret within Rust's defined casting rules. Use `try_from`/`try_into` when narrowing should fail instead of silently losing information.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
enum AddError {
    Overflow,
}

fn add_bytes(used: u32, incoming: u32) -> Result<u32, AddError> {
    used.checked_add(incoming).ok_or(AddError::Overflow)
}

fn main() {
    let total = add_bytes(20, 22).unwrap();
    println!("total = {total}");

    let clamped = u8::MAX.saturating_add(1);
    println!("clamped = {clamped}");

    let wrapped = 255_u8.wrapping_add(1);
    println!("wrapped = {wrapped}");
}
```

## Second example: bounds and arithmetic belong together
```rust
#[derive(Debug, PartialEq, Eq)]
enum WindowError {
    Overflow,
    OutOfBounds,
}

fn window_at<T>(items: &[T], start: usize, len: usize) -> Result<&[T], WindowError> {
    let end = start.checked_add(len).ok_or(WindowError::Overflow)?;
    items.get(start..end).ok_or(WindowError::OutOfBounds)
}

fn main() {
    let values = [10, 20, 30, 40];

    println!("{:?}", window_at(&values, 1, 2));
    println!("{:?}", window_at(&values, usize::MAX, 2));
    println!("{:?}", window_at(&values, 2, 9));
}
```

`checked_add` handles arithmetic validity; `get(start..end)` handles slice bounds. Keeping them separate produces better errors than computing `end` with `+` and indexing.

## Common errors
Debug overflow panic:

```text
thread 'main' panicked at 'attempt to add with overflow'
```

Fix it by choosing explicit arithmetic. If overflow is invalid input, use `checked_add` and return `Result`; if wraparound is the algorithm, use `wrapping_add` so debug and release agree.

Narrowing conversion error with the safe API:

```text
error[E0277]: the trait bound `u8: From<u32>` is not satisfied
```

Use `u8::try_from(value)` when the conversion can fail, then handle the `Result`. Avoid replacing it with `as u8` unless truncation is intentional and documented.

## Best practice
- ✅ Treat overflow behavior as part of the domain model.
- ✅ Use `checked_*` and return `Option` or `Result` for untrusted sizes, money, limits, and offsets.
- ✅ Use `saturating_*` for counters or UI quantities where reaching a bound is acceptable.
- ✅ Use `wrapping_*` only when modular arithmetic is the intended algorithm.
- ✅ Enable `overflow-checks = true` in release profiles when the application values detection over the small performance cost.
- ✅ Pair index arithmetic with slice APIs like `.get(range)` so overflow and bounds failures stay explicit.

## Pitfalls
- ⚠️ Tests run in one profile may not expose overflow behavior in another profile.
- ⚠️ Casting to a smaller integer can truncate; validate ranges before narrowing.
- ⚠️ Index arithmetic that overflows can lead to panics later; see [[Index Panics vs get]].
- ⚠️ Calling `.unwrap()` on `checked_*` just moves the panic; return a real error when overflow is input-driven.
- ⚠️ `overflowing_*` reports overflow but still returns a wrapped value; ignoring the flag is usually a bug.
- ⚠️ Floating-point overflow and integer overflow have different semantics; do not transfer assumptions between them.

## See also
[[Integer Types]] · [[Panic Unwinding and Abort]] · [[Result]] · [[Option vs Result]] · [[Index Panics vs get]] · [[Unwrap and Expect Overuse]] · [[Stringly-Typed Code]] · [[Sentinel Values]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 3.2 "Data Types" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html
- The Rust Reference, operator expressions and overflow — [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow
- Standard library, primitive integer methods such as `u32::checked_add` — [[the-reference]], https://doc.rust-lang.org/std/primitive.u32.html
