---
type: concept
title: "If Expressions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, if, control-flow, expressions]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Scalar Types]]", "[[Statements vs Expressions]]", "[[Pattern Matching]]", "[[Option vs Result]]", "[[Loop Expressions]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-05-control-flow.html#if-expressions", "https://doc.rust-lang.org/reference/expressions/if-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# If Expressions

An `if` expression selects the first branch whose condition is true, and because it is an expression, it can also produce a value.

## What it is
`if` is Rust's basic conditional control-flow form. It evaluates a condition, runs the associated block if the condition succeeds, and optionally falls through to `else if` or `else`.

The condition must be `bool` or a supported conditional `let` match. Rust has no implicit truthiness for integers, strings, collections, or pointers.

When used for a value, every possible executed branch must produce the same type.

## How it works
The Reference specifies `if` as one or more condition operands followed by a consequent block, optional `else if` blocks, and an optional `else` block. Conditions are evaluated left to right; the first successful branch runs, and the rest are skipped.

In edition 2024, `if` supports condition chains with `&&`, including chained `let` patterns. Pattern bindings introduced by earlier conditions are available to later conditions and to the consequent block.

If no branch is executed and there is no `else`, the expression evaluates to `()`.

## Example
```rust
fn main() {
    let number = 6;

    let label = if number % 4 == 0 {
        "divisible by four"
    } else if number % 3 == 0 {
        "divisible by three"
    } else {
        "something else"
    };

    assert_eq!(label, "divisible by three");
}
```

## Common errors
Using `if` as a value requires compatible arm types:

```rust
fn main() {
    let flag = true;
    // let value = if flag { 1 } else { "one" };
}
```

Typical diagnostic:

```text
error[E0308]: `if` and `else` have incompatible types
```

Fix by returning one type from every branch, or by using an enum when the alternatives are genuinely
different.

## Best practice
- ✅ Write explicit boolean conditions, such as `count != 0` or `name.is_empty()`.
- ✅ Use `if` as an expression when both branches naturally compute the same kind of value.
- ✅ Switch to [[Pattern Matching]] or `match` when many `else if` branches test variants or cases.
- ✅ Parenthesize `||` inside let-chain conditions when needed for clarity and grammar.

## Pitfalls
- ⚠️ `if number { ... }` is invalid; use a comparison.
- ⚠️ `let value = if condition { 5 } else { "six" };` cannot work because the arms have different types.
- ⚠️ Too many `else if` branches can hide exhaustiveness problems that `match` would expose.
- ⚠️ An `if` without `else` used for effects has type `()`, not the type of its body.

## See also
[[Scalar Types]] · [[Statements vs Expressions]] · [[Pattern Matching]] · [[Option vs Result]] · [[Loop Expressions]] · [[Control Flow]] · [[Type Inference]] · [[Result]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.5 "`if` Expressions" — [[the-book]], https://doc.rust-lang.org/book/ch03-05-control-flow.html#if-expressions
- The Rust Reference, "`if` expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/if-expr.html
