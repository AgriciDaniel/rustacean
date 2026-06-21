---
type: concept
title: "Trait Coherence and Covered Implementations"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, coherence, orphan-rule, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Coherence and the Orphan Rule]]", "[[Traits]]", "[[Blanket Implementations]]", "[[Newtype Pattern]]", "[[Use a Newtype to Implement Foreign Traits]]", "[[Sealed Traits]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence", "https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules"]
rust_version: "edition 2024 / 1.85+"
---

# Trait Coherence and Covered Implementations

Trait coherence is Rust's guarantee that trait lookup has one unambiguous implementation for a type.
The orphan rule and overlap checks preserve that guarantee across independently compiled crates.

## What it is
A trait implementation is coherent only if it passes two checks.
First, it must satisfy the orphan rules.
Second, it must not overlap with another implementation that could apply to the same type.
The basic orphan-rule intuition is simple: you can implement your trait for any type, or any trait for your type, but not a foreign trait for a foreign type.
The full rule is more precise for generic impls.
For `impl<P1..=Pn> Trait<T1..=Tn> for T0`, either the trait must be local, or a local type must appear among `T0..=Tn`.
Before the first local type, uncovered generic type parameters may not appear.
This "covered" parameter rule prevents crates from reserving broad impl space around types they do not own.
It is why [[Newtype Pattern]] is the standard escape hatch.

## How it works
An impl overlaps when two impls can be instantiated for the same trait and self type.
For example, `impl<T> MyTrait for T` overlaps with `impl MyTrait for String`.
Blanket impls are powerful because they reserve a wide part of the impl space.
A downstream crate cannot write an impl that conflicts with an upstream blanket impl.
The orphan rule is also semver protection.
It lets a crate author add impls for their own trait or their own type without arbitrary downstream crates having already claimed the same pair.
Fundamental type constructors such as references and `Box` receive special treatment in coherence.
For example, `Box<LocalType>` can count as local, but the parameter inside `Box<T>` is not considered covered merely by being inside `Box`.
The details matter most for library authors designing extension traits and blanket implementations.

## Example
```rust
use std::fmt::Display;

trait Label {
    fn label(&self) -> String;
}

struct Local<T>(T);

impl<T: Display> Label for Local<T> {
    fn label(&self) -> String {
        format!("local({})", self.0)
    }
}

impl Label for Vec<i32> {
    fn label(&self) -> String {
        format!("{} integers", self.len())
    }
}

fn main() {
    assert_eq!(Local("id").label(), "local(id)");
    assert_eq!(vec![1, 2, 3].label(), "3 integers");
}
```

## Edge cases
```rust
use std::fmt::{self, Display};

struct UserId(u64);

impl Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "user:{}", self.0)
    }
}

fn main() {
    assert_eq!(UserId(7).to_string(), "user:7");
}
```

## Best practice
- ✅ Implement local traits for foreign types when you need extension behavior.
- ✅ Use [[Newtype Pattern]] or [[Use a Newtype to Implement Foreign Traits]] when both the desired trait and type are foreign.
- ✅ Be conservative with blanket impls in public crates; they claim future impl space.
- ✅ Use [[Sealed Traits]] when you need to reserve implementation control for a public trait.
- ✅ Check overlap mentally before publishing a generic impl.
- ✅ Document blanket impl intent because removing or narrowing it can be breaking.

## Pitfalls
- ⚠️ Trying to implement `Display for Vec<T>` in your crate; both the trait and type are foreign.
- ⚠️ Publishing `impl<T> Trait for T` casually; it prevents more specific downstream impls.
- ⚠️ Assuming a generic parameter is covered just because it appears somewhere syntactically.
- ⚠️ Using a type alias as a workaround; aliases do not create a local nominal type. See [[Using Type Aliases as Newtypes]].
- ⚠️ Treating coherence errors as arbitrary compiler limitations; they are what let crates compose predictably.

## See also
[[Advanced Type System]]
[[Coherence and the Orphan Rule]]
[[Traits]]
[[Blanket Implementations]]
[[Newtype Pattern]]
[[Use a Newtype to Implement Foreign Traits]]
[[Sealed Traits]]
[[Overgeneric Public APIs]]
[[Using Type Aliases as Newtypes]]
[[Uncovered Type Parameters in Foreign Impl]]

## Sources
- The Rust Reference, "Trait implementation coherence" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence
- The Rust Reference, "Orphan rules" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules
