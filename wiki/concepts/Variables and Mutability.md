---
type: concept
title: "Variables and Mutability"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, variables, mutability, bindings]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Shadowing]]", "[[Constants]]", "[[Ownership]]", "[[Borrowing]]", "[[Statements vs Expressions]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html", "https://doc.rust-lang.org/reference/statements.html#let-statements"]
rust_version: "edition 2024 / 1.85+"
---

# Variables and Mutability

Rust variables are immutable bindings by default; add `mut` only when the same binding must be reassigned.

## What it is
A variable binding connects a name to a value introduced by a `let` statement. In Rust, `let x = 5;` creates an immutable binding: the value can be read, moved, copied, or borrowed according to its type, but the binding cannot be assigned a new value.

Mutability is explicit at the binding site with `let mut`. This is a local promise to readers and to the compiler that later assignments to that binding are intentional.

Immutability is about the binding, not necessarily the whole reachable object graph. A binding to a type with interior mutability can still permit mutation through its API; that belongs with [[Interior Mutability]], not the basic `mut` rule.

## How it works
The Reference defines `let` as a declaration statement that introduces variables from a pattern. Variables are visible from their declaration until the end of the enclosing block, unless a later binding shadows them.

Without `mut`, assigning again to the same binding is a compile-time error. With `mut`, the new assigned value must still have the same type as the binding. If you need to change type while keeping the same name, use [[Shadowing]] instead of mutability.

`mut` also appears in other binding positions, such as function parameters and pattern bindings. It says the local binding may be reassigned; it does not make a borrowed value mutable unless the type is a mutable reference such as `&mut T`.

## Example
```rust
fn main() {
    let language = "Rust";
    println!("{language} is immutable by default");

    let mut attempts = 0;
    attempts += 1;
    attempts += 1;

    assert_eq!(attempts, 2);
}
```

## Common errors
Reassigning an immutable binding produces E0384:

```rust
fn main() {
    let count = 0;
    // count += 1;
}
```

Typical diagnostic:

```text
error[E0384]: cannot assign twice to immutable variable `count`
```

Fix it with `let mut count = 0;` when reassignment is the point, or use [[Shadowing]] when a later
value is a new stage of computation.

## Best practice
- ✅ Start with immutable `let`; add `mut` only after a real reassignment appears.
- ✅ Keep mutable bindings in the smallest useful scope so later code can rely on stable values.
- ✅ Prefer [[Shadowing]] for staged transformations that produce a final immutable value.
- ✅ Use `&mut T` only when a function needs to mutate a caller-owned value; see [[Borrowing]].
- ✅ Prefer a fresh immutable binding after validation or parsing so the checked value cannot be
  accidentally overwritten later.

## Pitfalls
- ⚠️ Treating `mut` as a default style loses one of Rust's clearest local signals.
- ⚠️ Expecting `mut` to permit type changes; reassignment keeps one static type, while [[Shadowing]] creates a new binding.
- ⚠️ Confusing a mutable binding with shared mutable ownership; that topic belongs to [[Ownership]], [[Borrowing]], and [[Interior Mutability]].
- ⚠️ Reusing one large mutable variable across many steps can hide invariants that smaller immutable bindings would make obvious.

## See also
[[Shadowing]] · [[Constants]] · [[Statements vs Expressions]] · [[Ownership]] · [[Borrowing]] · [[Interior Mutability]] · [[Type Inference]] · [[Static Items]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.1 "Variables and Mutability" — [[the-book]], https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html
- The Rust Reference, "let statements" — [[the-reference]], https://doc.rust-lang.org/reference/statements.html#let-statements
