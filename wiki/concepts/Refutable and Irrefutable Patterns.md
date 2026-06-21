---
type: concept
title: "Refutable and Irrefutable Patterns"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, patterns, refutability, let-else]
domain: "Enums & Pattern Matching"
difficulty: intermediate
related: ["[[Patterns]]", "[[let else]]", "[[if let]]", "[[The match Expression]]", "[[Destructuring]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch19-02-refutability.html", "https://doc.rust-lang.org/book/ch06-03-if-let.html"]
rust_version: "edition 2024 / 1.85+"
---

# Refutable and Irrefutable Patterns

An irrefutable pattern always matches, while a refutable pattern can fail and therefore needs a construct that handles failure.

## What it is
`let x = value;` uses an irrefutable pattern because `x` matches any value.
`let (a, b) = pair;` is irrefutable when the expression has a two-element tuple type.
`Some(x)` is refutable for `Option<T>` because the value might be `None`.

Rust restricts where each kind of pattern can appear.
Plain `let`, function parameters, closure parameters, and `for` loop patterns require irrefutable patterns.
`match` arms, [[if let]], `while let`, and [[let else]] can use refutable patterns.

## How it works
If a pattern can fail where the program has no failure branch, Rust rejects it.
That is why `let Some(x) = option;` is not valid by itself.
The compiler cannot invent a value for `x` when the option is `None`.

Use `if let` when the success branch is optional.
Use `let else` when failure should exit the current function, loop, or block.
Use `match` when every possible case deserves explicit handling.

Refutability is a property of a pattern in relation to a type. `Some(x)` is refutable for
`Option<T>`, but a tuple pattern `(a, b)` is irrefutable for a known `(A, B)` tuple because every value
of that type has exactly two elements. Range patterns, literal patterns, enum-variant patterns, and
slice length patterns are usually refutable because some values of the same type do not match them.

The compiler uses refutability before runtime. It rejects impossible control flow such as a plain
`let Some(x) = maybe;` because the following statements would have no `x` when `maybe` is `None`.
For [[let else]], the `else` block must diverge so the compiler knows execution cannot continue without
the bindings.

## Example
```rust
fn parse_port(input: &str) -> Option<u16> {
    let Ok(port) = input.parse::<u16>() else {
        return None;
    };

    Some(port)
}

fn main() {
    assert_eq!(parse_port("8080"), Some(8080));
    assert_eq!(parse_port("abc"), None);
}
```

## Worked example
```rust
fn parse_pair(input: &str) -> Option<(u8, u8)> {
    let mut parts = input.split(':');

    let Some(left) = parts.next() else {
        return None;
    };
    let Some(right) = parts.next() else {
        return None;
    };
    let None = parts.next() else {
        return None;
    };

    Some((left.parse().ok()?, right.parse().ok()?))
}

fn main() {
    assert_eq!(parse_pair("10:20"), Some((10, 20)));
    assert_eq!(parse_pair("10:20:30"), None);
}
```

## Common errors
Using a refutable pattern in plain `let` produces:

```text
error[E0005]: refutable pattern in local binding
```

Fix it with `let PATTERN = value else { return ...; };`, an `if let`, or a full `match`.
The reverse mistake is using `let else` with a pattern that cannot fail, which warns that the `else`
clause is useless.

## Best practice
- ✅ Use normal `let` for patterns the type system proves will always match.
- ✅ Use [[let else]] for early-return extraction from `Option` or `Result`.
- ✅ Use [[The match Expression]] when failure is not just an early exit but a meaningful branch.
- ✅ Treat refutability diagnostics as a design hint: decide whether failure should branch, return, or be impossible.
- ✅ Use irrefutable destructuring in `for` loops and function parameters only when every item has that shape.

## Pitfalls
- ⚠️ Do not force a refutable pattern into `let`; switch to `let else`, `if let`, or `match`.
- ⚠️ Do not use `let else` with a pattern that always matches; the `else` block is useless and will warn.
- ⚠️ Do not replace explicit failure handling with `unwrap`; see [[Unwrap and Expect Overuse]].
- ⚠️ Do not confuse "currently always true in my data" with irrefutable; the type must guarantee it.
- ⚠️ Avoid `if let` chains for several meaningful failures when a `match` would document each case.

## See also
[[Patterns]] · [[let else]] · [[if let]] · [[The match Expression]] · [[Option]] · [[Result]] · [[Exhaustiveness]] · [[Destructuring]] · [[Unwrap and Expect Overuse]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 19.2 "Refutability: Whether a Pattern Might Fail to Match" - [[the-book]], https://doc.rust-lang.org/book/ch19-02-refutability.html
- The Rust Programming Language, ch. 6.3 "Concise Control Flow with if let and let...else" - [[the-book]], https://doc.rust-lang.org/book/ch06-03-if-let.html
