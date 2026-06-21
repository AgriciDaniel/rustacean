---
type: concept
title: "Boolean Logic"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, bool, boolean, operators, conditions]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Scalar Types]]", "[[Control Flow]]", "[[If Expressions]]", "[[PartialEq]]", "[[Pattern Matching]]", "[[Statements vs Expressions]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html#the-boolean-type", "https://doc.rust-lang.org/reference/types/boolean.html", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#lazy-boolean-operators", "https://doc.rust-lang.org/reference/expressions/if-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Boolean Logic

Boolean logic in Rust is explicit `bool` logic: conditions are `true` or `false`, `!` negates, and lazy `&&`/`||` short-circuit branch decisions.

## What it is
`bool` is Rust's primitive Boolean type.
It has exactly two values: `true` and `false`.
The Book notes that Boolean values are one byte in size and are written with the type name `bool`.
Boolean values are produced directly by literals, comparisons, predicate methods, and logical operators.
Control-flow conditions use `bool`; Rust does not coerce integers or pointers into conditions.
The primary logical operators are `!`, `&&`, and `||`.
`!value` computes logical not for `bool`.
`left && right` computes logical and.
`left || right` computes logical or.
Comparisons such as `==`, `!=`, `<`, and `>=` also produce `bool`.
Use Boolean logic to make program decisions visible to the compiler and to readers.

## How it works
The Reference calls `&&` and `||` lazy Boolean operators.
Both operands must be `bool`.
For `a && b`, the right-hand operand is evaluated only if `a` is `true`.
For `a || b`, the right-hand operand is evaluated only if `a` is `false`.
This short-circuit behavior matters when the right side is expensive, mutates state, borrows data, or might panic.
The `&`, `|`, and `^` operators also work on `bool` as non-lazy logical and, or, and xor.
Prefer `&&` and `||` for conditions because their short-circuit behavior matches ordinary control-flow intent.
Use `&`, `|`, or `^` on `bool` only when evaluating both sides is intentional.
Operator precedence means `!` binds tightly, comparisons produce `bool`, `&&` groups before `||`, and parentheses are often clearer than relying on memory.
In edition 2024 condition chains, `&&` can sequence `let` pattern conditions and Boolean conditions.
If a `let` condition is part of such a chain and a `||` expression is needed, parenthesize the `||` expression.

## Example
```rust
fn can_enter(is_admin: bool, has_badge: bool, is_locked: bool) -> bool {
    (is_admin || has_badge) && !is_locked
}

fn should_not_run() -> bool {
    panic!("short-circuiting should skip this call")
}

fn main() {
    assert!(can_enter(false, true, false));
    assert!(!can_enter(false, true, true));

    let skipped_and = false && should_not_run();
    let skipped_or = true || should_not_run();

    assert!(!skipped_and);
    assert!(skipped_or);
}
```

## Common errors
Rust has no truthiness:

```rust
fn main() {
    let count = 3;
    // if count {
    //     println!("not how Rust tests nonzero values");
    // }
}
```

Typical diagnostic:

```text
error[E0308]: mismatched types
expected `bool`, found integer
```

Fix the condition by stating the predicate:

```rust
fn main() {
    let count = 3;
    if count != 0 {
        println!("nonzero");
    }
}
```

Another common mistake is using bitwise-looking operators where short-circuiting is expected:

```rust
fn main() {
    let ready = false;
    // let ok = ready & expensive_check();
}
```

Use `ready && expensive_check()` if the check should run only when `ready` is true.

## Best practice
- ✅ Write predicates explicitly: `count != 0`, `slice.is_empty()`, `option.is_some()`.
- ✅ Prefer positive, domain-specific predicate names such as `is_ready`, `has_access`, and `can_retry`.
- ✅ Use `&&` and `||` for ordinary branch conditions.
- ✅ Parenthesize mixed `&&`/`||` expressions when it improves readability.
- ✅ Use comparison and equality traits deliberately; `==` depends on [[PartialEq]].
- ✅ Keep Boolean expressions small enough that each term's meaning is obvious.
- ✅ Replace clusters of related booleans with an enum when they represent mutually exclusive states.

## Pitfalls
- ⚠️ Assuming `0`, empty strings, empty vectors, or null-like values are false; they are not conditions in Rust.
- ⚠️ Using `&` or `|` on `bool` and accidentally evaluating the right-hand side.
- ⚠️ Encoding too much state as independent booleans, which can permit impossible combinations.
- ⚠️ Forgetting that floating-point comparisons involving `NaN` can be surprising because `NaN != NaN`.
- ⚠️ Naming negative booleans such as `not_disabled`; double negatives obscure [[Control Flow]].
- ⚠️ Relying on operator precedence in long expressions instead of making grouping explicit.

## See also
[[Scalar Types]] · [[Control Flow]] · [[If Expressions]] · [[PartialEq]] · [[The match Expression]] · [[Pattern Matching]] · [[Iterator predicate search adapters]] · [[Statements vs Expressions]] · [[Type Inference]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "The Boolean Type" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html#the-boolean-type
- The Rust Reference, "Boolean type" — [[the-reference]], https://doc.rust-lang.org/reference/types/boolean.html
- The Rust Reference, "Lazy boolean operators" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#lazy-boolean-operators
- The Rust Reference, "`if` expressions / chains of conditions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/if-expr.html
