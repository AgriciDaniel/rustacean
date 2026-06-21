---
type: concept
title: "Loop Expressions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, loop, control-flow, break]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[While and For Loops]]", "[[Statements vs Expressions]]", "[[If Expressions]]", "[[Never Type]]", "[[Result]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-05-control-flow.html#repetition-with-loops", "https://doc.rust-lang.org/reference/expressions/loop-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Loop Expressions

The `loop` expression repeats a block until control flow exits it, and it can return a value with `break value`.

## What it is
`loop { ... }` is Rust's explicit infinite-loop construct. It runs the body repeatedly until `break`, `return`, panic, or another diverging operation exits.

Unlike `while` and `for`, a `loop` can evaluate to a non-unit value by using `break expression`. This makes it useful for retry-until-success logic that computes a result.

`continue` skips the rest of the current iteration and starts the next one.

## How it works
The Reference classifies `loop`, `while`, `for`, and labeled blocks as breakable expressions. A `loop` without an associated `break` expression is diverging and has the never type `!`.

If a `loop` has `break` expressions with values, those values must have compatible types because they define the type of the whole loop expression.

Loop labels such as `'outer: loop { ... }` let `break 'outer` or `continue 'outer` target an outer loop instead of the innermost one.

## Example
```rust
fn main() {
    let mut counter = 0;

    let answer = 'search: loop {
        counter += 1;

        if counter < 3 {
            continue;
        }

        break 'search counter * 10;
    };

    assert_eq!(answer, 30);
}
```

## Common errors
Different `break` values make the loop expression ill-typed:

```rust
fn main() {
    // let value = loop {
    //     if true { break 1; }
    //     break "done";
    // };
}
```

Typical diagnostic:

```text
error[E0308]: mismatched types
```

Fix by choosing one result type or returning an enum/`Result`.

## Best practice
- ✅ Use `loop` when the exit condition is naturally inside the body.
- ✅ Use `break value` for retry or polling code that must produce one final result.
- ✅ Label nested loops when a `break` or `continue` targets anything other than the innermost loop.
- ✅ Prefer [[While and For Loops]] when a condition or iterator clearly describes repetition.

## Pitfalls
- ⚠️ Writing `loop` without a reachable exit can hang a program unless divergence is intentional.
- ⚠️ Mixing different `break` value types makes the loop expression ill-typed.
- ⚠️ Assuming `break` exits a function; it exits the targeted loop. Use `return` to exit the function.
- ⚠️ Using labels casually can make control flow harder to follow; reserve them for nested-loop clarity.

## See also
[[While and For Loops]] · [[Statements vs Expressions]] · [[If Expressions]] · [[Never Type]] · [[Result]] · [[panic!]] · [[Type Inference]] · [[Iterator Method Trio]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.5 "Repeating Code with `loop`" — [[the-book]], https://doc.rust-lang.org/book/ch03-05-control-flow.html#repeating-code-with-loop
- The Rust Reference, "Loops and other breakable expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/loop-expr.html
