---
type: concept
title: "Arithmetic Operator Traits Add and Mul"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, operators, add, mul]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[Operator Overloading]]", "[[Index and IndexMut Traits]]", "[[Clone Semantics in std]]", "[[Trait Bounds]]"]
sources: ["[[std]]", "[[the-reference]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/std/ops/index.html", "https://doc.rust-lang.org/std/ops/trait.Add.html", "https://doc.rust-lang.org/std/ops/trait.Mul.html"]
rust_version: "edition 2024 / 1.85+"
---

# Arithmetic Operator Traits Add and Mul

`Add`, `Mul`, and their assignment variants let user-defined types participate in arithmetic operator syntax when the operator has the expected meaning.

## What it is
Rust overloads a fixed set of operators through traits in `std::ops`.
`Add` backs `+`.
`Mul` backs `*`.
`AddAssign` backs `+=`.
`MulAssign` backs `*=`.

You cannot create new operators.
You cannot overload assignment itself.
You cannot overload `&&` or `||` through these traits because their short-circuiting behavior needs a different design.

The existing note [[Operator Overloading]] covers the general language feature.
This note focuses on arithmetic operator trait design.

## How it works
`Add<Rhs = Self>` has an associated `Output` type.
The method takes `self` by value and a right-hand side by value.
That means `a + b` may consume both operands for non-`Copy` types.

The default right-hand side is `Self`, but you can implement mixed operations.
For example, a duration-like type could add seconds.
Keep mixed implementations unsurprising.

For expensive non-`Copy` values, consider implementing operators for references too.
Generic code may otherwise need clones just to reuse inputs.
The std module docs explicitly call out `T`, `&T`, and mixed RHS implementations as a way to reduce unnecessary cloning.

Operator traits should match domain expectations.
If `*` does something unrelated to multiplication, a named method is clearer.

## Example
```rust
use std::ops::{Add, Mul};

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
struct Pixels(u32);

impl Add for Pixels {
    type Output = Self;

    fn add(self, rhs: Self) -> Self::Output {
        Self(self.0 + rhs.0)
    }
}

impl Mul<u32> for Pixels {
    type Output = Self;

    fn mul(self, rhs: u32) -> Self::Output {
        Self(self.0 * rhs)
    }
}

fn main() {
    assert_eq!(Pixels(10) + Pixels(5), Pixels(15));
    assert_eq!(Pixels(6) * 3, Pixels(18));
}
```

## Best practice
- ✅ Implement arithmetic operators only when they preserve the operator's ordinary meaning for the type.
- ✅ Choose `Output` deliberately; it does not have to be `Self`.
- ✅ Add reference-based implementations when cloning large values would otherwise be common.
- ✅ Implement assignment variants when in-place mutation is natural and efficient.
- ✅ Prefer named methods for operations with policy, side effects, or surprising units.

## Pitfalls
- ⚠️ Do not overload operators for clever DSL syntax that obscures ordinary Rust expectations.
- ⚠️ Remember by-value operands can move non-`Copy` values.
- ⚠️ Do not use arithmetic traits to hide fallible operations; return `Result` from a named method instead.
- ⚠️ Be careful with overflow semantics when wrapping primitive integers.

## See also
[[std: Core Trait Catalog]] · [[Operator Overloading]] · [[Index and IndexMut Traits]] · [[Clone Semantics in std]] · [[Trait Bounds]] · [[Generics]] · [[Integer Overflow]] · [[Relying on Integer Overflow]] · [[Newtype Pattern]] · [[Methods]]

## Sources
- Rust standard library, `std::ops` - [[std]], https://doc.rust-lang.org/std/ops/index.html
- Rust standard library, `std::ops::Add` - [[std]], https://doc.rust-lang.org/std/ops/trait.Add.html
- Rust standard library, `std::ops::Mul` - [[std]], https://doc.rust-lang.org/std/ops/trait.Mul.html
