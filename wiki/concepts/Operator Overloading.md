---
type: concept
title: "Operator Overloading"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, operators, std-ops]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[Associated Constants]]", "[[Fully Qualified Syntax]]", "[[Newtype Pattern]]", "[[Type Aliases]]", "[[Traits]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-default-generic-parameters-and-operator-overloading", "https://doc.rust-lang.org/std/ops/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Operator Overloading

Operator overloading in Rust means implementing the standard traits in `std::ops` to define how existing operators behave for your types.

## What it is
Rust does not let you invent new operators or overload arbitrary syntax.
Instead, operators such as `+`, `-`, `*`, indexing, dereferencing, and call-like behavior are tied to specific traits.

For `+`, the trait is `std::ops::Add`.
`Add` has a default right-hand-side type parameter of `Self` and an associated type named `Output`.
That default makes the common case concise while still allowing mixed-type operations such as adding `Meters` to `Millimeters`.

Operator overloading should make domain code clearer.
It should not surprise readers by making `+` perform unrelated effects, hidden I/O, or lossy transformations that the operator does not naturally suggest.

## How it works
Implement the relevant `std::ops` trait for a local type.
The orphan rules still apply: you can implement a foreign trait for your local type, or a local trait for a foreign type, but not a foreign trait for a foreign type.
Use [[Newtype Pattern]] when you need to define operator behavior for a type you do not own.

The trait method usually consumes `self`, though many operator traits can be implemented for references when avoiding moves is important.
The `Output` associated type controls the result type.

The operator syntax is just surface syntax for a trait method call.
`a + b` uses `std::ops::Add::add(a, b)`, `a[index]` uses `Index` or `IndexMut`, unary `-a` uses `Neg`, and `*a` uses `Deref`.
Not every operator is overloadable: assignment itself and short-circuiting `&&` and `||` do not have ordinary overload traits.

Default generic parameters matter here.
`Add<Rhs = Self>` makes `impl Add for Point` mean `Point + Point`, while `impl Add<Meters> for Millimeters` customizes only the right-hand side.
For non-`Copy` types, consider implementations for references so generic code can avoid clones and accidental moves.

## Example
```rust
use std::ops::Add;

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
struct Millimeters(u32);

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
struct Meters(u32);

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, rhs: Meters) -> Self::Output {
        Millimeters(self.0 + rhs.0 * 1_000)
    }
}

fn main() {
    assert_eq!(Millimeters(500) + Meters(2), Millimeters(2_500));
}
```

## More realistic example
```rust
use std::ops::Add;

#[derive(Debug, PartialEq, Eq)]
struct PathParts(Vec<String>);

impl PathParts {
    fn new(parts: &[&str]) -> Self {
        Self(parts.iter().map(|part| (*part).to_owned()).collect())
    }
}

impl<'a> Add<&'a str> for PathParts {
    type Output = PathParts;

    fn add(mut self, rhs: &'a str) -> Self::Output {
        self.0.push(rhs.to_owned());
        self
    }
}

impl<'a> Add<&'a str> for &PathParts {
    type Output = PathParts;

    fn add(self, rhs: &'a str) -> Self::Output {
        let mut cloned = PathParts(self.0.clone());
        cloned.0.push(rhs.to_owned());
        cloned
    }
}

fn main() {
    let base = PathParts::new(&["api", "v1"]);
    let users = &base + "users";
    let health = base + "health";

    assert_eq!(users.0, vec![String::from("api"), String::from("v1"), String::from("users")]);
    assert_eq!(health.0, vec![String::from("api"), String::from("v1"), String::from("health")]);
}
```

This shows the API choice: consuming `PathParts` is cheap when the caller is done with it, while `&PathParts + &str` preserves the original at the cost of cloning.

## Common errors
```rust
// impl std::ops::Add for Vec<String> {
//     type Output = Vec<String>;
//     fn add(self, rhs: Vec<String>) -> Self::Output { self }
// }
// error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate
```

`Add` and `Vec` are both foreign, so the orphan rules reject the impl.
Fix it by wrapping the vector in a local [[Newtype Pattern]] and implementing `Add` for that wrapper.

```rust
use std::ops::Add;

struct Name(String);

impl Add for Name {
    type Output = Name;

    fn add(self, rhs: Self) -> Self::Output {
        Name(format!("{}{}", self.0, rhs.0))
    }
}

fn main() {
    let first = Name(String::from("Ferris"));
    let full = first + Name(String::from(" Jr."));
    // println!("{}", first.0);
    // error[E0382]: borrow of moved value: `first`
    assert_eq!(full.0, "Ferris Jr.");
}
```

The default `Add` impl consumes `self`.
If callers need to reuse values, implement the operator for references or provide an explicit method such as `joined`.

## Best practice
- ✅ Implement operator traits only when the operator has the conventional meaning for your type.
- ✅ Use the `Output` associated type deliberately; mixed-unit arithmetic often benefits from returning one canonical unit.
- ✅ Use [[Newtype Pattern]] for unit types, domain quantities, and foreign types that need local operator behavior.
- ✅ Document non-obvious units, rounding, overflow behavior, and allocation behavior.
- ✅ Implement reference forms (`&T + &T`, `&T + U`) when ownership cost is visible and callers often need to keep operands.
- ✅ Mirror symmetric operations only when both directions are meaningful and unambiguous.

## Pitfalls
- ⚠️ Do not overload operators for surprising side effects; method names are clearer for domain-specific actions.
- ⚠️ Do not use [[Type Aliases]] when you need distinct operator behavior; aliases cannot get separate trait impls from the underlying type.
- ⚠️ Avoid implementing only one direction of a symmetric operation when users naturally expect both `A + B` and `B + A`.
- ⚠️ Do not assume `+` is non-mutating for your type if your impl consumes and reuses allocation internally; document ownership behavior.
- ⚠️ Avoid panicking in operator impls for ordinary invalid input; prefer checked methods when failure is expected.

## See also
[[Newtype Pattern]] · [[Type Aliases]] · [[Using Type Aliases as Newtypes]] · [[Fully Qualified Syntax]] · [[Associated Constants]] · [[Traits]] · [[Copy and Clone]] · [[Move Semantics]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.2 "Using Default Generic Parameters and Operator Overloading" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-default-generic-parameters-and-operator-overloading
- Standard library module `std::ops` — https://doc.rust-lang.org/std/ops/index.html
