---
type: concept
title: "Type Inference"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, type-inference, types, annotations]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Scalar Types]]", "[[Functions]]", "[[Statements vs Expressions]]", "[[Readable Generic APIs]]", "[[Iterators]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html", "https://doc.rust-lang.org/reference/types/inferred.html"]
rust_version: "edition 2024 / 1.85+"
---

# Type Inference

Rust infers most types from usage via Hindley–Milner-style local inference; annotations are needed where context is ambiguous.

## What it is
Type inference is the compiler's ability to fill in omitted local types from constraints in the
surrounding code. It lets you write `let count = 0;` or `let names = vec!["Ada"];` without spelling
every type.

Inference is intentionally local and conservative. Public function signatures, constants, statics,
and many trait boundaries still need explicit types because those types are part of the program's
contract.

The goal is not to hide types completely; it is to avoid repetition where the compiler and reader have
enough context.

## How it works
The compiler creates type variables for unknowns, then unifies them with constraints from literals,
method calls, function signatures, trait bounds, assignments, and return positions.

Integer literals default to `i32` and floating literals default to `f64` only when no stronger
constraint exists. Collection builders such as `collect()` often need a target type because many
collection types can be built from the same iterator.

Inference does not cross API boundaries in a way that would make public contracts implicit. Function
parameters require annotations, and return-position `impl Trait` hides a concrete type from callers
while still requiring the function body to produce one concrete type.

## Example
```rust
fn main() {
    let numbers = [1, 2, 3];
    let doubled: Vec<_> = numbers.iter().map(|n| n * 2).collect();

    assert_eq!(doubled, vec![2, 4, 6]);

    let port = "8080".parse::<u16>().expect("valid port");
    assert_eq!(port, 8080);
}
```

The `Vec<_>` annotation chooses the collection, while `_` lets the element type come from the
iterator.

## Edge cases
Method-call context can infer types after the initializer:

```rust
fn main() {
    let mut queue = Vec::new();
    queue.push(String::from("first"));

    let item = queue.pop().expect("one item");
    assert_eq!(item, "first");
}
```

Without the later `push`, `Vec::new()` would be ambiguous because `Vec<T>` needs an element type.

## Common errors
Ambiguous inference often appears as E0282:

```rust
fn main() {
    // let values = Vec::new();
}
```

Typical diagnostic:

```text
error[E0282]: type annotations needed for `Vec<_>`
```

Fix it by giving the compiler one useful constraint:

```rust
fn main() {
    let values: Vec<String> = Vec::new();
    assert!(values.is_empty());
}
```

## Best practice
- ✅ Annotate public APIs, constants, statics, and ambiguous parses.
- ✅ Use turbofish syntax such as `parse::<u16>()` when it keeps the receiving variable cleaner.
- ✅ Use `Vec<_>` and similar partial annotations when only the outer type is ambiguous.
- ✅ Add local annotations at semantic boundaries, not on every obvious binding.
- ✅ Treat inference failures as design feedback: the code may be asking readers to infer too much too.

## Pitfalls
- ⚠️ Assuming function parameter types can be inferred; Rust requires them in signatures.
- ⚠️ Calling `collect()` without telling Rust which collection to build.
- ⚠️ Depending on numeric defaults when the domain requires a specific width.
- ⚠️ Overusing `_` in complex generic code can make compiler errors less localized.
- ⚠️ Returning different concrete types from `-> impl Trait` branches is not allowed.

## See also
[[Scalar Types]] · [[Functions]] · [[Statements vs Expressions]] · [[Readable Generic APIs]] · [[Iterator Method Trio]] · [[The Display Trait]] · [[The Debug Trait]] · [[Variables and Mutability]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "Data Types" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html
- The Rust Reference, "Inferred type" — [[the-reference]], https://doc.rust-lang.org/reference/types/inferred.html
