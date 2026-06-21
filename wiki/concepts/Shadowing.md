---
type: concept
title: "Shadowing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, shadowing, variables, scope]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Variables and Mutability]]", "[[Statements vs Expressions]]", "[[Ownership]]", "[[Pattern Matching]]", "[[Constants]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html#shadowing", "https://doc.rust-lang.org/reference/statements.html#let-statements"]
rust_version: "edition 2024 / 1.85+"
---

# Shadowing

Shadowing creates a new binding with the same name as an earlier binding, making the newer binding the one that name resolves to until its scope ends or it is shadowed again.

## What it is
Shadowing happens when a `let` statement introduces a name that is already visible. The older binding is not reassigned; a new binding is introduced, and name lookup now finds the newer one.

This is useful for short transformation pipelines where the concept stays the same but the representation changes, such as raw text becoming a parsed number.

Shadowing differs from [[Variables and Mutability]] because it works through a new declaration, not assignment. That means the resulting binding can be immutable even after several transformations.

## How it works
Bindings introduced by `let` are visible from the declaration until the end of the enclosing block, except when another declaration shadows them. Inner scopes can shadow an outer name and then reveal the outer binding again when the inner scope ends.

Because shadowing creates a new variable, the new binding may have a different type. That is why `let spaces = "   "; let spaces = spaces.len();` works, while assigning `spaces = spaces.len();` to a mutable `&str` binding does not.

For non-`Copy` values, shadowing can also move from the old binding into the new one. After the move, the old binding is no longer usable even aside from name shadowing.

## Example
```rust
fn main() {
    let input = " 42 ";
    let input = input.trim();
    let input: u32 = input.parse().expect("valid integer");

    {
        let input = input + 1;
        assert_eq!(input, 43);
    }

    assert_eq!(input, 42);
}
```

## Common errors
Expecting `mut` assignment to change a binding's type fails with E0308:

```rust
fn main() {
    let mut spaces = "   ";
    // spaces = spaces.len();
}
```

Typical diagnostic:

```text
error[E0308]: mismatched types
```

Fix it with shadowing: `let spaces = spaces.len();`.

## Best practice
- ✅ Use shadowing for linear normalization steps where one name remains clearer than `raw_input`, `trimmed_input`, and `parsed_input`.
- ✅ Keep shadowing local; if a name changes meaning across a long block, use more specific names.
- ✅ Prefer shadowing over `mut` when the final value should be immutable.
- ✅ Add an explicit type annotation at the shadowing point when inference would be unclear.
- ✅ Use block scopes when a temporary shadow should disappear before later code.

## Pitfalls
- ⚠️ Shadowing can hide an outer binding in nested scopes; keep scopes short enough that this remains obvious.
- ⚠️ Do not use shadowing to disguise unrelated meanings under one name.
- ⚠️ Remember that shadowing a moved value does not preserve the old value for later use; see [[Ownership]] and [[Move Semantics]].
- ⚠️ Shadowing constants or imports with local names is legal in many positions but usually makes code harder to scan.

## See also
[[Variables and Mutability]] · [[Constants]] · [[Statements vs Expressions]] · [[Ownership]] · [[Move Semantics]] · [[Pattern Matching]] · [[Name Resolution]] · [[Type Inference]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.1 "Shadowing" — [[the-book]], https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html#shadowing
- The Rust Reference, "let statements" — [[the-reference]], https://doc.rust-lang.org/reference/statements.html#let-statements
