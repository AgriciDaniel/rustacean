---
type: concept
title: "Variance"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, variance, lifetimes, subtyping, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Lifetimes]]", "[[Borrowing]]", "[[PhantomData]]", "[[UnsafeCell]]", "[[Cell]]", "[[Higher-Ranked Trait Bounds]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/subtyping.html#variance", "https://doc.rust-lang.org/nomicon/subtyping.html"]
rust_version: "edition 2024 / 1.85+"
---

# Variance

Variance explains when subtyping relationships, especially lifetime outlives relationships, pass through generic type constructors.
Most Rust code benefits from variance invisibly; unsafe abstractions and marker fields must design it deliberately.

## What it is
Rust has limited subtyping, mostly through lifetimes.
If `'long: 'short`, then a reference valid for `'long` can often be used where a shorter reference is required.
Variance answers whether that relationship passes through a type constructor such as `&T`, `&mut T`, `Box<T>`, or your own `struct`.
`F<T>` is covariant over `T` if `Sub` being a subtype of `Super` implies `F<Sub>` is a subtype of `F<Super>`.
`F<T>` is contravariant if the direction reverses.
`F<T>` is invariant if no relationship can be derived.
The common intuition is: immutable access tends to be covariant, mutable/interior-mutable access tends to be invariant, and function arguments are contravariant.
Variance is inferred for structs and enums from their fields.
You influence it with field types, including [[PhantomData]] fields.

## How it works
Shared references `&'a T` are covariant in both `'a` and `T`.
Mutable references `&'a mut T` are covariant in `'a` but invariant in `T`.
`UnsafeCell<T>` and types built on it, such as [[Cell]] and [[RefCell]], are invariant in `T`.
Raw `*const T` is covariant in `T`; raw `*mut T` is invariant in `T`.
Function return positions are covariant; function parameter positions are contravariant.
For user-defined types, Rust composes these field positions.
If a parameter appears in both covariant and contravariant positions, or in an invariant position, the resulting type is invariant.
This analysis protects against storing a short-lived reference into a place that promised to hold a longer-lived one.
Unsafe code must match its variance to the aliasing and mutation capabilities it actually exposes.

## Example
```rust
struct Covariant<'a> {
    value: &'a i32,
}

fn accept_short<'short>(input: Covariant<'short>, _anchor: &'short ()) -> &'short i32 {
    input.value
}

fn main() {
    static NUMBER: i32 = 42;
    let long = Covariant { value: &NUMBER };

    let anchor = ();
    let shortened = accept_short(long, &anchor);
    assert_eq!(*shortened, 42);
}
```

## Edge cases
```rust
use std::cell::Cell;
use std::marker::PhantomData;

struct Invariant<'a> {
    _marker: PhantomData<Cell<&'a ()>>,
}

impl<'a> Invariant<'a> {
    fn new() -> Self {
        Self { _marker: PhantomData }
    }
}

fn main() {
    let _value = Invariant::<'static>::new();
    // This marker shape intentionally prevents lifetime shortening through the type.
}
```

## Best practice
- ✅ Let safe Rust infer variance unless you are designing a low-level abstraction.
- ✅ Use `PhantomData<&'a T>` for a covariant borrowed relationship.
- ✅ Use `PhantomData<&'a mut T>` or an `UnsafeCell`-based marker when invariance is required.
- ✅ Review variance whenever a type stores raw pointers but exposes references.
- ✅ Prefer simple lifetime relationships in public APIs; variance should help callers, not become the API.
- ✅ Treat variance as part of the safety argument for unsafe constructors and iterators.

## Pitfalls
- ⚠️ Assuming `&mut T` is covariant in `T`; it is invariant because mutation could otherwise smuggle shorter borrows into longer slots.
- ⚠️ Choosing `PhantomData<T>` without considering whether ownership, covariance, and auto traits are intended.
- ⚠️ Forgetting that interior mutability makes types invariant.
- ⚠️ Depending on contravariance in ordinary application code; it is rare and easiest to encounter through function types.
- ⚠️ Explaining lifetime errors as "the borrow checker being strict" when variance is the real reason.

## See also
[[Advanced Type System]]
[[Lifetimes]]
[[Borrowing]]
[[PhantomData]]
[[Phantom Type Parameters]]
[[UnsafeCell]]
[[Cell]]
[[RefCell]]
[[Higher-Ranked Trait Bounds]]
[[Aliasing and Provenance]]

## Sources
- The Rust Reference, "Subtyping and variance" — [[the-reference]],
  https://doc.rust-lang.org/reference/subtyping.html#variance
- The Rustonomicon, "Subtyping and Variance" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/subtyping.html
