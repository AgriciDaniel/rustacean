---
type: concept
title: "Statements vs Expressions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, expressions, statements, blocks]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Functions]]", "[[If Expressions]]", "[[Loop Expressions]]", "[[Tuples]]", "[[Variables and Mutability]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-03-how-functions-work.html#statements-and-expressions", "https://doc.rust-lang.org/reference/statements.html", "https://doc.rust-lang.org/reference/expressions/block-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Statements vs Expressions

Rust is expression-oriented: statements sequence actions, while expressions evaluate to values that can be returned, assigned, matched, or nested.

## What it is
Statements perform an action and do not produce a value for surrounding expressions. `let y = 6;` is a statement, as are item declarations.

Expressions evaluate to a value. Literals, arithmetic, function calls, macro calls, blocks, `if`, `match`, and loops are all expressions in Rust.

The distinction matters because semicolons can intentionally discard expression results, and function return values usually come from tail expressions.

## How it works
A block is itself an expression. It executes its statements in order, then evaluates its final operand if one is present. If there is no final operand and the block does not diverge, the block has unit type `()`.

The tail expression is the last expression in a block without a semicolon. Adding a semicolon turns it into an expression statement and discards the value.

Expression statements are mainly for effects, such as printing, pushing into a vector, or calling a function whose return value is intentionally ignored.

## Example
```rust
fn plus_one(n: i32) -> i32 {
    n + 1
}

fn main() {
    let y = {
        let x = 3;
        x + 1
    };

    assert_eq!(y, 4);
    assert_eq!(plus_one(y), 5);
}
```

## Common errors
Trying to use a statement where an expression is required fails because `let` does not produce a value:

```rust
fn main() {
    // let value = (let x = 3);
}
```

Typical diagnostic:

```text
error: expected expression, found `let` statement
```

Fix by separating the statement from the expression or by using a block with a tail expression.

## Best practice
- ✅ Use tail expressions for simple function and block results.
- ✅ Add semicolons when you intentionally discard a value for its side effects.
- ✅ Keep block expressions small when they are used inside `let` initializers.
- ✅ Read compiler `expected T, found ()` errors as a likely semicolon or missing-tail-expression problem.

## Pitfalls
- ⚠️ Writing `x + 1;` at the end of `fn plus_one(...) -> i32` makes the function return `()`, not `i32`.
- ⚠️ Trying to assign a `let` statement to a variable; `let` is not a value-producing expression.
- ⚠️ Forgetting that `if` arms used as values must have compatible types; see [[If Expressions]].
- ⚠️ Ignoring return values accidentally can hide logic bugs, even when the code compiles.

## See also
[[Functions]] · [[If Expressions]] · [[Loop Expressions]] · [[Tuples]] · [[Variables and Mutability]] · [[Pattern Matching]] · [[Type Inference]] · [[Scalar Types]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.3 "Statements and Expressions" — [[the-book]], https://doc.rust-lang.org/book/ch03-03-how-functions-work.html#statements-and-expressions
- The Rust Reference, "Statements" — [[the-reference]], https://doc.rust-lang.org/reference/statements.html
- The Rust Reference, "Block expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/block-expr.html
