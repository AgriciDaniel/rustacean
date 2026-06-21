---
type: concept
title: "Supertraits"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, supertraits, bounds]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Traits]]", "[[Trait Bounds]]", "[[Default Implementations]]", "[[Marker Traits]]", "[[Sealed Traits]]", "[[Fully Qualified Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-supertraits", "https://doc.rust-lang.org/reference/items/traits.html#supertraits"]
rust_version: "edition 2024 / 1.85+"
---

# Supertraits

A supertrait is a required parent trait: implementing the subtrait also requires implementing the supertrait and makes its associated items available.

## What it is
Write `trait OutlinePrint: Display` to say every `OutlinePrint` implementor must also implement `Display`.
The trait after the colon is the supertrait.
The trait being defined is the subtrait.
Supertraits let default methods use behavior from required parent traits.
They also model semantic refinement: every `Circle` might be a `Shape`, every `CacheKey` might be `Eq + Hash`.

## How it works
The supertrait bound is effectively a bound on `Self`.
Inside the subtrait, methods can call supertrait methods because the bound is guaranteed.
Generic code bounded by the subtrait can also use associated items from the supertrait.
Supertraits can be written after `:` or as `where Self: Parent`.
A trait cannot be its own supertrait, directly or through a cycle.
For trait objects, all supertraits must be dyn-compatible for the subtrait object to be dyn-compatible.
Supertrait obligations are checked when implementing the subtrait, not only when calling a default method.
If `trait JsonValue: Debug + Clone`, an `impl JsonValue for T` is legal only after `T` also implements `Debug` and `Clone`.
Associated items from supertraits may need fully qualified syntax when names collide.
Private supertraits are the mechanism behind the common sealed-trait pattern.

## Example
```rust
use std::fmt;

trait OutlinePrint: fmt::Display {
    fn outline(&self) -> String {
        let text = self.to_string();
        format!("*** {text} ***")
    }
}

struct Point {
    x: i32,
    y: i32,
}

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

impl OutlinePrint for Point {}

fn main() {
    let point = Point { x: 1, y: 3 };
    assert_eq!(point.outline(), "*** (1, 3) ***");
}
```

## Common errors
Implementing only the subtrait usually reports:

```text
error[E0277]: `Point` doesn't implement `std::fmt::Display`
```

Implement the supertrait first, or remove the supertrait if it is not a real semantic requirement.
A cycle such as `trait A: B {}` and `trait B: A {}` is rejected because trait solving could never establish a base obligation.
If `dyn Subtrait` fails with `error[E0038]`, inspect the supertraits too; a non-dyn-compatible parent makes the child non-dyn-compatible.
Adding `Self: Sized` as a supertrait is a common accidental way to rule out trait objects entirely.

## Best practice
- ✅ Use supertraits when the subtrait logically requires the parent behavior.
- ✅ Keep the relationship semantic, not merely convenient for one implementation.
- ✅ Let default methods depend on supertrait methods when that reduces implementor boilerplate.
- ✅ Consider a private supertrait for [[Sealed Traits]] when downstream implementations must be controlled.
- ✅ Check dyn compatibility if users should write `dyn Subtrait`.

## Pitfalls
- ⚠️ Adding a new supertrait to a public trait is a breaking change for implementors.
- ⚠️ A supertrait that is too broad forces unnecessary work on every implementor.
- ⚠️ Supertraits do not inherit implementation bodies from implementors; each trait's contract still matters.
- ⚠️ Requiring `Self: Sized` as a supertrait prevents ordinary trait-object use.

## See also
[[Traits]] · [[Trait Bounds]] · [[Default Implementations]] · [[Marker Traits]] · [[Sealed Traits]] · [[Fully Qualified Syntax]] · [[Dynamically Sized Types]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 20.2 "Using Supertraits" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-supertraits
- The Rust Reference, "Supertraits" — [[the-reference]], https://doc.rust-lang.org/reference/items/traits.html#supertraits
