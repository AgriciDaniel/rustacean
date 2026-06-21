---
type: concept
title: "Patterns"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, patterns, pattern-matching, syntax]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[The match Expression]]", "[[Destructuring]]", "[[Refutable and Irrefutable Patterns]]", "[[Catch-All and Wildcard Patterns]]", "[[Binding with @]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch19-00-patterns.html", "https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Pattern Matching"]
---

# Patterns

Patterns describe the shape of a value so Rust can test, destructure, bind, or ignore parts of that value.

## What it is
A pattern can contain literals, variable bindings, wildcards, ranges, enum variants, struct fields, tuples, slices, and nested combinations of those pieces.
Patterns appear in `match` arms, `let` statements, `if let`, `while let`, `for` loops, function parameters, and closure parameters.

The simplest pattern is a binding such as `x`, which matches anything.
More precise patterns such as `Some(3)`, `1..=10`, or `Point { x: 0, y }` match only certain shapes.

## How it works
Rust compares a value with a pattern in a context that defines what happens on success or failure.
In a `match`, a successful pattern selects an arm.
In a `let`, an irrefutable pattern binds names.
In `if let` and `let else`, a refutable pattern can choose a branch.

Pattern bindings can move or copy values, depending on the value's type and the matched expression.
When you need to keep using a non-`Copy` value, match a reference or use reference patterns.
Use [[Destructuring]] to pull out exactly the pieces the following code needs.

Edition 2024 tightened some match-ergonomics edge cases. Pattern matching still automatically treats
bindings as references when you match a reference with a non-reference pattern, but explicit `ref`,
`ref mut`, and `mut` binding modifiers are only allowed while the default binding mode is still move.
In practice, prefer simple patterns like `if let Some(name) = user.name.as_ref()` when you want a
borrow, and use explicit `ref` only when destructuring an owned value by value but borrowing one field.

Path patterns can refer to constants or enum variants, while bare identifiers bind new variables.
Name resolution decides which one you wrote, which is why ALL_CAPS constants are clearer than lowercase
constants in patterns.

## Example
```rust
fn label(input: (&str, Option<u8>)) -> String {
    match input {
        ("Ferris", Some(points @ 1..=10)) => format!("Ferris scored {points}"),
        (_, Some(0)) => String::from("zero"),
        (name, Some(_)) => format!("{name} scored a lot"),
        (name, None) => format!("{name} did not score"),
    }
}

fn main() {
    assert_eq!(label(("Ferris", Some(7))), "Ferris scored 7");
    assert_eq!(label(("Rust", None)), "Rust did not score");
}
```

## Worked example
```rust
#[derive(Debug, PartialEq)]
struct Request<'a> {
    method: &'a str,
    path: &'a str,
    body: Option<&'a str>,
}

fn route(request: Request<'_>) -> &'static str {
    match request {
        Request { method: "GET", path: "/", body: None } => "home",
        Request { method: "POST", path: "/login", body: Some(_), } => "login",
        Request { method: "GET", path, .. } if path.starts_with("/assets/") => "asset",
        Request { .. } => "not found",
    }
}

fn main() {
    assert_eq!(route(Request { method: "GET", path: "/", body: None }), "home");
    assert_eq!(route(Request { method: "GET", path: "/assets/app.css", body: None }), "asset");
}
```

## Common errors
Tuple, tuple-struct, and variant patterns must match the shape of the value:

```text
error[E0308]: mismatched types
expected a tuple with 3 elements, found one with 2 elements
```

Fix it by adding/removing bindings, or by using `_`/`..` to ignore fields intentionally. If the error
mentions refutability, switch from plain `let` to [[let else]], [[if let]], or [[The match Expression]].

## Best practice
- ✅ Use the narrowest pattern that communicates the case you actually handle.
- ✅ Prefer destructuring in the pattern over indexing into tuples or manually unwrapping enums afterward.
- ✅ Learn [[Refutable and Irrefutable Patterns]] so compiler diagnostics point you to the right construct.
- ✅ Use constants with clear names for reusable value patterns; use guards for runtime comparisons.
- ✅ Keep nested patterns readable by extracting helper functions or matching in stages when necessary.

## Pitfalls
- ⚠️ A name in a pattern binds a new variable; it does not compare to an existing variable. See [[Pattern Variable Shadowing]].
- ⚠️ `_name` still binds and can move a value; `_` does not bind. See [[Catch-All and Wildcard Patterns]].
- ⚠️ Overly nested patterns can be harder to read than a small match plus a named helper.
- ⚠️ Do not put `mut` in a pattern expecting to make the original place mutable; it makes the new binding mutable.
- ⚠️ Be careful with partial moves when mixing by-value and by-reference bindings.

## See also
[[The match Expression]] · [[Destructuring]] · [[Refutable and Irrefutable Patterns]] · [[Catch-All and Wildcard Patterns]] · [[Binding with @]] · [[Match Guards]] · [[if let]] · [[let else]] · [[Pattern Variable Shadowing]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 19 "Patterns and Matching" - [[the-book]], https://doc.rust-lang.org/book/ch19-00-patterns.html
- The Rust Programming Language, ch. 19.3 "Pattern Syntax" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html
