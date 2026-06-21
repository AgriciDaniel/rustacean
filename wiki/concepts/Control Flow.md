---
type: concept
title: "Control Flow"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, control-flow, syntax, expressions]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[If Expressions]]", "[[Loop Expressions]]", "[[While and For Loops]]", "[[Pattern Matching]]", "[[Boolean Logic]]", "[[Statements vs Expressions]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-05-control-flow.html", "https://doc.rust-lang.org/book/ch06-02-match.html", "https://doc.rust-lang.org/book/ch06-03-if-let.html", "https://doc.rust-lang.org/reference/expressions/if-expr.html", "https://doc.rust-lang.org/reference/expressions/loop-expr.html", "https://doc.rust-lang.org/reference/expressions/match-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Control Flow

Control flow is how Rust chooses which block runs next: `if`, `match`, `loop`, `while`, `for`, `break`, `continue`, and pattern-based forms select or repeat code while preserving static type checking.

## What it is
Rust's core control-flow forms are expressions, not just statements.
That means many of them can produce values as well as direct execution.
Use `if` when a `bool` condition chooses between branches.
Use `match` when a value should be compared against patterns and all cases should be handled.
Use `loop` when repetition exits from inside the body, possibly with `break value`.
Use `while` when a predicate controls repetition.
Use `for` when iterating over something that implements `IntoIterator`.
Use `if let`, `let else`, and `while let` when a single refutable pattern is the point of the branch.
The common thread is that conditions and patterns are checked before the body runs.
Rust does not use implicit truthiness for numbers, strings, pointers, or collections.

## How it works
`if` conditions must be `bool` expressions or conditional `let` matches.
An `if` expression evaluates to the value of the executed block, or to `()` when no branch runs.
When `if` is used as a value, all possible branches must have compatible types.
`match` evaluates its scrutinee, tests arms in order, and returns the selected arm expression.
`match` is exhaustive, so the compiler rejects missing cases unless a catch-all pattern covers them.
`loop` repeats until `break`, `return`, panic, or another diverging operation exits it.
A plain `break` from `loop` is equivalent to `break ()`.
A `break value` can make the whole `loop` evaluate to that value.
`while` re-evaluates its condition before each iteration and evaluates to `()`.
`for` desugars through the standard `IntoIterator`, `Iterator`, and `Option` machinery.
`break` exits the targeted loop; `continue` skips the rest of the current iteration.
Loop labels such as `'outer:` let nested loops name the target for `break` and `continue`.
Pattern-based control flow composes with [[Pattern Matching]], [[Option]], and [[Result]].
In edition 2024, condition chains can mix `let` patterns and `bool` expressions with `&&`.

## Example
```rust
fn first_large_even(values: &[i32]) -> Option<i32> {
    for &value in values {
        if value <= 10 {
            continue;
        }

        match value % 2 {
            0 => return Some(value),
            _ => {}
        }
    }

    None
}

fn attempts_until(limit: u8) -> u8 {
    let mut attempts = 0;

    loop {
        attempts += 1;

        if attempts == limit {
            break attempts;
        }
    }
}

fn main() {
    let values = [3, 11, 13, 18, 21];

    assert_eq!(first_large_even(&values), Some(18));
    assert_eq!(attempts_until(3), 3);
}
```

## Common errors
Using a non-`bool` value as a condition fails:

```rust
fn main() {
    let count = 3;
    // if count {
    //     println!("not valid Rust");
    // }
}
```

Typical diagnostic:

```text
error[E0308]: mismatched types
expected `bool`, found integer
```

Fix it by writing the predicate explicitly, such as `count != 0`, `items.is_empty()`, or `path.exists()`.
Another common error is returning different types from different branches:

```rust
fn main() {
    let flag = true;
    // let value = if flag { 1 } else { "one" };
}
```

Use one type, an enum, or separate statements when the branches have different results.

## Best practice
- ✅ Use the smallest control-flow form that expresses the decision clearly.
- ✅ Prefer `match` for enum cases where exhaustiveness is valuable.
- ✅ Prefer `for` over manual indexing for collection traversal.
- ✅ Use `loop { ... break value; }` when retry logic naturally computes a final value.
- ✅ Keep branch result types explicit and boring; reach for enums when branches represent different states.
- ✅ Use labels only when nested loops need a named target.
- ✅ Use pattern-specific forms (`if let`, `let else`, `while let`) when one successful pattern is the whole point.

## Pitfalls
- ⚠️ Treating integers, strings, collections, or pointers as truthy; Rust conditions require [[Boolean Logic]].
- ⚠️ Replacing an exhaustive `match` with a long `else if` ladder and losing compiler coverage checks.
- ⚠️ Forgetting that `for item in collection` can move the collection; borrow with `for item in &collection` when needed.
- ⚠️ Mixing incompatible branch or `break` value types and expecting runtime choice to decide the type.
- ⚠️ Hiding important early exits in deeply nested branches; consider `let else`, `?`, or small helper functions.
- ⚠️ Using `_` too early in a `match` and accidentally making later arms unreachable.

## See also
[[If Expressions]] · [[Loop Expressions]] · [[While and For Loops]] · [[Boolean Logic]] · [[Pattern Matching]] · [[The match Expression]] · [[if let]] · [[Refutable and Irrefutable Patterns]] · [[Statements vs Expressions]] · [[The Question Mark Operator]] · [[Option]] · [[Result]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.5 "Control Flow" — [[the-book]], https://doc.rust-lang.org/book/ch03-05-control-flow.html
- The Rust Programming Language, ch. 6.2 "The `match` Control Flow Construct" — [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html
- The Rust Programming Language, ch. 6.3 "Concise Control Flow with `if let` and `let...else`" — [[the-book]], https://doc.rust-lang.org/book/ch06-03-if-let.html
- The Rust Reference, "`if` expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/if-expr.html
- The Rust Reference, "Loops and other breakable expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/loop-expr.html
- The Rust Reference, "`match` expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/match-expr.html
