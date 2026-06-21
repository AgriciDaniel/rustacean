---
type: concept
title: "Generics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, generics, types, abstraction]
domain: "Generics, Traits & Lifetimes"
difficulty: basic
related: ["[[Traits]]", "[[Trait Bounds]]", "[[Where Clauses]]", "[[Lifetimes]]", "[[Associated Types]]", "[[Overgeneric Public APIs]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-01-syntax.html", "https://doc.rust-lang.org/reference/items/generics.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Generic Parameters", "Generic Functions"]
---

# Generics

Generics let one item work over many concrete types, lifetimes, or constant values while Rust still checks the fully concrete program at compile time.

## What it is
Generic parameters are placeholders declared on functions, structs, enums, traits, type aliases, and `impl` blocks.
The common type parameter is `T`, but Rust also supports lifetime parameters such as `'a` and const parameters such as `const N: usize`.
Use generics when duplicated code differs only by type shape or by a compile-time constant.
The standard library's `Option<T>`, `Result<T, E>`, `Vec<T>`, arrays `[T; N]`, and iterators are everyday examples.
Generics are not dynamic typing: every use is checked against concrete types and required bounds.

## How it works
Declare generic parameters in angle brackets, then use them in the item signature or body.
For `impl` blocks, parameters appear after `impl`, because an implementation has no item name.
A generic struct like `Point<T>` means all fields using `T` have the same concrete type for a given `Point<T>` value.
If two fields should allow different types, use distinct parameters such as `Point<T, U>`.
Generic functions are usually monomorphized: the compiler generates specialized machine code for concrete instantiations.
That gives static dispatch and optimization, but broad public generics can increase compile time and binary size.
Generic parameters are chosen per item use, not per value at runtime.
For example, one `Pair<&str, i32>` value and one `Pair<String, usize>` value are different concrete instantiations of the same generic definition.
Bounds are checked from the generic body's point of view, so the compiler rejects operations that are not promised for every possible `T`.
Const generics are also part of the type identity: `[u8; 16]` and `[u8; 32]` are different types.

## Example
```rust
fn largest<T: PartialOrd>(items: &[T]) -> &T {
    let mut best = &items[0];
    for item in &items[1..] {
        if item > best {
            best = item;
        }
    }
    best
}

#[derive(Debug, PartialEq)]
struct Pair<T, U> {
    left: T,
    right: U,
}

fn main() {
    let numbers = [3, 9, 4];
    let chars = ['a', 'z', 'm'];
    assert_eq!(*largest(&numbers), 9);
    assert_eq!(*largest(&chars), 'z');

    let pair = Pair { left: "id", right: 42 };
    assert_eq!(pair.right, 42);
}
```

## Common errors
The first error after extracting a generic function is often:

```text
error[E0369]: binary operation `>` cannot be applied to type `&T`
help: consider restricting type parameter `T` with trait `PartialOrd`
```

The fix is not to make `T` concrete again, but to add the smallest required bound:
`fn largest<T: PartialOrd>(items: &[T]) -> &T`.
Another common error is `error[E0308]: mismatched types` when a single `T` is used for two fields that callers try to fill with different concrete types.
Use `Point<T, U>` when the fields are independent.
If a method exists only for `impl Point<f32>`, `Point<i32>` will not have that method; move the method to `impl<T>` only if the body works for every `T`.

## Best practice
- ✅ Start with concrete code, extract duplication, then introduce a generic parameter where it buys real reuse.
- ✅ Put only the bounds the body actually needs on the generic parameter; see [[Trait Bounds]] and [[Where Clauses]].
- ✅ Use conventional short names (`T`, `U`, `E`) for local generics and descriptive names for public traits when meaning matters.
- ✅ Consider `impl Trait` for simple argument positions and named type parameters when two arguments must be the same type.
- ✅ Keep const generics for sizes and compile-time values that are truly part of the type, such as `[T; N]`.

## Pitfalls
- ⚠️ Using a single `T` for fields that are allowed to differ forces them to be the same concrete type.
- ⚠️ Adding bounds to a struct definition just because derived impls need them needlessly restricts all uses; see [[Unnecessary Bounds on Data Types]].
- ⚠️ Making every public function generic can leak implementation choices into callers and increase code size; see [[Overgeneric Public APIs]].
- ⚠️ Assuming generic `T` excludes references is wrong: `T` can be `&str`, `&mut Foo`, or an owned type.

## See also
[[Traits]] · [[Trait Bounds]] · [[Where Clauses]] · [[Lifetimes]] · [[Associated Types]] · [[Blanket Implementations]] · [[Static Dispatch with Generics]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.1 "Generic Data Types" — [[the-book]], https://doc.rust-lang.org/book/ch10-01-syntax.html
- The Rust Reference, "Generic parameters" — [[the-reference]], https://doc.rust-lang.org/reference/items/generics.html
