---
type: pattern
title: "Phantom Type Parameters"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, phantom-types, marker-types, typestate, pattern]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[PhantomData]]", "[[Zero-Sized Types]]", "[[Type-State Pattern]]", "[[Type-State State Machines]]", "[[Making Invalid States Unrepresentable]]", "[[Variance]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/special-types-and-traits.html#phantomdatat", "https://doc.rust-lang.org/nomicon/phantom-data.html"]
rust_version: "edition 2024 / 1.85+"
---

# Phantom Type Parameters

Phantom type parameters encode distinctions in the type system without storing data for those distinctions at runtime.
Use them to prevent mixing IDs, states, units, or capabilities that share the same representation.

## What it is
A phantom type parameter is a generic parameter used for compile-time meaning rather than runtime storage.
The implementation usually stores a raw value plus a `PhantomData` marker.
For example, `Id<User>` and `Id<Order>` can both wrap `u64` but be incompatible types.
This pattern is related to [[Newtype Pattern]], but the phantom parameter lets one wrapper family cover many domains.
It is also related to [[Type-State Pattern]], where marker types represent states.
The runtime representation stays small because the marker is a [[Zero-Sized Types]] design.
The type checker prevents accidental cross-use.
The pattern is strongest when constructors keep marker choices controlled by the API.

## How it works
Define a generic wrapper with real fields for runtime data.
Add a private `_marker: PhantomData<...>` field so the generic parameter is considered used.
Choose the `PhantomData` shape according to the relationship being modeled.
For pure tagging with no ownership, `PhantomData<fn() -> T>` is often a good marker because it mentions `T` without modeling ownership of a `T`.
For typestate, a simple `PhantomData<State>` is often acceptable when state markers are ZSTs and do not carry lifetimes.
Keep state marker constructors private if users should not forge states.
Expose transitions as methods that consume one state and return another.
This makes invalid states and mixed domains unrepresentable.

## Example
```rust
use std::marker::PhantomData;

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
struct Id<T> {
    raw: u64,
    _kind: PhantomData<fn() -> T>,
}

impl<T> Id<T> {
    fn new(raw: u64) -> Self {
        Self { raw, _kind: PhantomData }
    }

    fn raw(self) -> u64 {
        self.raw
    }
}

struct User;
struct Order;

fn load_user(id: Id<User>) -> String {
    format!("user:{}", id.raw())
}

fn main() {
    let user = Id::<User>::new(1);
    let order = Id::<Order>::new(1);

    assert_eq!(load_user(user), "user:1");
    assert_eq!(order.raw(), 1);
    // load_user(order); // different type, even though both wrap u64
}
```

## Edge cases
```rust
use std::marker::PhantomData;

struct Open;
struct Closed;

struct Door<State> {
    name: String,
    _state: PhantomData<State>,
}

impl Door<Closed> {
    fn open(self) -> Door<Open> {
        Door { name: self.name, _state: PhantomData }
    }
}

fn main() {
    let closed = Door::<Closed> { name: "front".into(), _state: PhantomData };
    let open = closed.open();
    assert_eq!(open.name, "front");
}
```

## Best practice
- ✅ Use phantom type parameters when two values share representation but must not be interchangeable.
- ✅ Keep the marker field private to preserve invariants.
- ✅ Pick `PhantomData<fn() -> T>` for pure output-position tagging when ownership is not intended.
- ✅ Use named marker structs rather than booleans for state or domain distinctions.
- ✅ Provide narrow constructors and consuming transition methods.
- ✅ Document whether the phantom parameter affects variance, drop checking, or auto traits.

## Pitfalls
- ⚠️ Using a type alias instead of a phantom wrapper; aliases do not create distinct types.
- ⚠️ Choosing `PhantomData<T>` casually and accidentally modeling ownership of `T`.
- ⚠️ Making marker types public and constructible when they should be sealed by the API.
- ⚠️ Overusing phantom markers where a normal enum or field would be clearer.
- ⚠️ Letting phantom-heavy public types leak into simple application code without a clear invariant payoff.

## See also
[[Advanced Type System]]
[[PhantomData]]
[[Zero-Sized Types]]
[[Variance]]
[[Type-State Pattern]]
[[Type-State State Machines]]
[[Making Invalid States Unrepresentable]]
[[Newtype Pattern]]
[[Using Type Aliases as Newtypes]]
[[Readable Generic APIs]]

## Sources
- The Rust Reference, "`PhantomData<T>`" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html#phantomdatat
- The Rustonomicon, "`PhantomData`" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/phantom-data.html
