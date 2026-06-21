---
type: antipattern
title: "Uncovered Type Parameters in Foreign Impl"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, coherence, orphan-rule, traits, antipattern]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Trait Coherence and Covered Implementations]]", "[[Coherence and the Orphan Rule]]", "[[Blanket Implementations]]", "[[Newtype Pattern]]", "[[Use a Newtype to Implement Foreign Traits]]", "[[Using Type Aliases as Newtypes]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules", "https://doc.rust-lang.org/reference/glossary.html#uncovered-type"]
rust_version: "edition 2024 / 1.85+"
---

# Uncovered Type Parameters in Foreign Impl

An uncovered type parameter in a foreign-trait impl is a coherence violation because it claims impl space before any local type anchors the implementation.
Fix it by making the trait local, making the self type local, or wrapping the foreign type in a newtype.

## The mistake
The mistake is trying to implement a foreign trait for a foreign type while placing a generic parameter before the first local type in the impl header.
The compiler rejects this under the orphan rules.
The simple version is trying to implement `Display for Vec<T>`.
The deeper version appears when there is a local type somewhere in the trait arguments, but an uncovered generic parameter appears first.
This feels surprising because a local type is present.
Coherence cares about where the local type appears and whether earlier generic parameters are covered.
The rule prevents a crate from claiming broad implementation territory around types it does not own.
It is a common trap in generic adapter and conversion APIs.

## Why it happens
Rust must guarantee that trait lookup finds at most one implementation across all crates.
If crates could write broad impls involving foreign traits and foreign self types, independent dependencies could conflict.
For `impl<P1..=Pn> Trait<T1..=Tn> for T0`, an impl is allowed if the trait is local.
Otherwise, a local type must appear in `T0..=Tn`.
Let `Ti` be the first local type.
No uncovered type parameter may appear in `T0..Ti`, excluding `Ti`.
The order matters because earlier uncovered parameters make the impl apply too broadly before local ownership appears.
A type alias does not help because it is not a new local nominal type.
The [[Newtype Pattern]] does help because it creates a local type.

## Example
```rust
use std::fmt::{self, Display};

struct LocalVec<T>(Vec<T>);

impl<T: Display> Display for LocalVec<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let mut first = true;
        for item in &self.0 {
            if !first {
                write!(f, ",")?;
            }
            first = false;
            write!(f, "{item}")?;
        }
        Ok(())
    }
}

fn main() {
    let values = LocalVec(vec![1, 2, 3]);
    assert_eq!(values.to_string(), "1,2,3");

    // This would be rejected: both `Display` and `Vec` are foreign.
    // impl<T: Display> Display for Vec<T> { /* ... */ }
}
```

## Edge cases
```rust
use std::ops::Deref;

struct Local<T>(T);

impl<T> Deref for Local<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

fn main() {
    let local = Local(String::from("owned"));
    assert_eq!(local.len(), 5);
}
```

## Best practice
- ✅ Make either the trait or the self type local before writing an impl.
- ✅ Reach for [[Use a Newtype to Implement Foreign Traits]] when both sides are foreign.
- ✅ Prefer local extension traits for behavior that does not need a standard trait.
- ✅ Avoid type aliases as orphan-rule workarounds; they do not create local nominal types.
- ✅ Check broad generic impls for overlap and covered-parameter issues before publishing.
- ✅ Keep impl headers simple when possible; coherence errors get harder to reason about as generic arguments multiply.

## Pitfalls
- ⚠️ Assuming a local type anywhere in the impl header is enough.
- ⚠️ Assuming a type alias makes `Vec<T>` local to your crate.
- ⚠️ Trying to outsmart coherence with blanket impls; overlap checks still apply.
- ⚠️ Adding a local marker type in an argument position that comes too late to cover earlier parameters.
- ⚠️ Treating the orphan rule as only a nuisance instead of a semver guarantee for crate composition.

## See also
[[Advanced Type System]]
[[Trait Coherence and Covered Implementations]]
[[Coherence and the Orphan Rule]]
[[Blanket Implementations]]
[[Newtype Pattern]]
[[Use a Newtype to Implement Foreign Traits]]
[[Using Type Aliases as Newtypes]]
[[Overgeneric Public APIs]]
[[Sealed Traits]]
[[Traits]]

## Sources
- The Rust Reference, "Orphan rules" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules
- The Rust Reference, glossary, "Uncovered type" — [[the-reference]],
  https://doc.rust-lang.org/reference/glossary.html#uncovered-type
