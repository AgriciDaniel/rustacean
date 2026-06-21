---
type: concept
title: "Generic Functions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, generics, functions, trait-bounds, syntax]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Functions]]", "[[Readable Generic APIs]]", "[[Generics]]", "[[Trait Bounds]]", "[[Where Clauses]]", "[[Type Inference]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-01-syntax.html#in-function-definitions", "https://doc.rust-lang.org/reference/items/functions.html", "https://doc.rust-lang.org/reference/items/generics.html", "https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html"]
rust_version: "edition 2024 / 1.85+"
---

# Generic Functions

Generic functions are `fn` items or methods with type, lifetime, or const parameters in their signature, letting one checked implementation work for many concrete types.

## What it is
A generic function declares placeholders before its parameter list, such as `fn identity<T>(value: T) -> T`.
Those placeholders can appear in argument types, return types, bounds, and `where` clauses.
The most common placeholder is a type parameter like `T`.
Functions can also be generic over lifetimes and const parameters.
Generic functions remove duplication when the same algorithm works for more than one concrete type.
They are still statically typed: the function body must be valid for every type allowed by its bounds.
If the body compares values, the signature must require a comparison trait.
If the body formats values, the signature must require a formatting trait.
If the body clones values, the signature must require `Clone`.
The signature is the contract that lets Rust check callers and the implementation separately.

## How it works
Type parameters are declared in angle brackets after the function name and before the ordinary parameter list.
For example, `fn first<T>(items: &[T]) -> Option<&T>` is generic over `T`.
The compiler infers concrete type arguments from the call site when it can.
When inference cannot choose, callers can use turbofish syntax such as `parse::<u32>()`.
Bounds restrict which concrete types may instantiate the function.
Inline bounds use `fn largest<T: PartialOrd>(items: &[T]) -> &T`.
`where` clauses move larger bounds after the signature, which keeps public APIs readable.
`impl Trait` in argument position is anonymous generic syntax.
Use named type parameters when two positions must be the same concrete type.
Generic functions are commonly monomorphized, so Rust generates concrete code for the types actually used.
That gives static dispatch and optimization without a runtime type lookup.
The tradeoff is that very broad generic APIs can increase compile time and binary size.
Lifetimes in generic functions describe relationships between borrowed inputs and outputs.
They do not make references live longer; they document and check what must already be true.

## Example
```rust
fn largest<T: PartialOrd>(items: &[T]) -> Option<&T> {
    let mut iter = items.iter();
    let mut best = iter.next()?;

    for item in iter {
        if item > best {
            best = item;
        }
    }

    Some(best)
}

fn same_type<T: PartialEq>(left: T, right: T) -> bool {
    left == right
}

fn main() {
    let numbers = [34, 50, 25, 100, 65];
    let chars = ['y', 'm', 'a', 'q'];

    assert_eq!(largest(&numbers), Some(&100));
    assert_eq!(largest(&chars), Some(&'y'));
    assert!(same_type(10u8, 10u8));
}
```

## Common errors
After extracting a concrete function into a generic one, operations in the body may no longer be guaranteed:

```rust
fn main() {
    // fn largest<T>(items: &[T]) -> &T {
    //     let mut best = &items[0];
    //     for item in items {
    //         if item > best {
    //             best = item;
    //         }
    //     }
    //     best
    // }
}
```

Typical diagnostic:

```text
error[E0369]: binary operation `>` cannot be applied to type `&T`
help: consider restricting type parameter `T` with trait `PartialOrd`
```

Fix by adding the smallest bound the body needs:

```rust
fn largest_ref<T: PartialOrd>(items: &[T]) -> &T {
    let mut best = &items[0];
    for item in &items[1..] {
        if item > best {
            best = item;
        }
    }
    best
}
```

Another common error is using one `T` when two inputs are allowed to differ.
`fn pair<T>(left: T, right: T)` requires both arguments to have the same concrete type.
Use `fn pair<T, U>(left: T, right: U)` when the types are independent.

## Best practice
- ✅ Start concrete, extract duplication, then introduce a generic parameter where the algorithm is truly shared.
- ✅ Put only the bounds the function body needs in the signature.
- ✅ Use named generics when two or more positions must share exactly one concrete type.
- ✅ Use `impl Trait` for simple input positions where the concrete type does not need a name.
- ✅ Prefer `where` clauses once bounds get long or involve associated types.
- ✅ Borrow inputs (`&[T]`, `&T`, `&str`) when the generic function only needs to inspect data.
- ✅ Return `Option` or `Result` instead of panicking when a generic helper cannot satisfy its precondition for all inputs.

## Pitfalls
- ⚠️ Adding `Clone` or `Copy` just to silence ownership errors; borrowing may be the correct API.
- ⚠️ Assuming a generic `T` supports `>`, `==`, formatting, or cloning without declaring the relevant bound.
- ⚠️ Using `impl Trait` twice when both arguments must be the same type; two anonymous generics may differ.
- ⚠️ Overgeneric public functions can be harder to read and slower to compile; see [[Readable Generic APIs]].
- ⚠️ Returning references from generic functions without tying them to an input lifetime.
- ⚠️ Making an empty-slice helper return `&T`; there is no element to borrow, so return `Option<&T>`.

## See also
[[Functions]] · [[Readable Generic APIs]] · [[Generics]] · [[Trait Bounds]] · [[Where Clauses]] · [[Type Inference]] · [[PartialEq]] · [[The Display Trait]] · [[The Debug Trait]] · [[Ownership]] · [[Borrowing]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 10.1 "Generic Data Types / In Function Definitions" — [[the-book]], https://doc.rust-lang.org/book/ch10-01-syntax.html#in-function-definitions
- The Rust Reference, "Functions" — [[the-reference]], https://doc.rust-lang.org/reference/items/functions.html
- The Rust Reference, "Generic parameters" — [[the-reference]], https://doc.rust-lang.org/reference/items/generics.html
- Standard library, `std::cmp::PartialOrd` — https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html
