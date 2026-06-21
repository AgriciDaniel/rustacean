---
type: pattern
title: "Sealed Traits"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, sealed-traits, api-design]
domain: "Generics, Traits & Lifetimes"
difficulty: advanced
related: ["[[Traits]]", "[[Supertraits]]", "[[Coherence and the Orphan Rule]]", "[[Default Implementations]]", "[[Marker Traits]]", "[[Overgeneric Public APIs]]"]
sources: ["[[the-reference]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/traits.html#supertraits", "https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-supertraits"]
rust_version: "edition 2024 / 1.85+"
---

# Sealed Traits

A sealed trait is a public trait that downstream crates can use but cannot implement, usually enforced by requiring a private supertrait.

## What it is
Rust has no `sealed` keyword for traits.
The common pattern is to make the public trait extend a private trait from a private module.
External crates cannot name or implement the private supertrait, so they cannot implement the public trait.
Sealing is an API design tool for closed sets, forward compatibility, and invariants.
It is not appropriate for extension-point traits that users are expected to implement.

## How it works
Define `pub trait Public: private::Sealed`.
Define `mod private { pub trait Sealed {} }` without exporting the module.
Implement `private::Sealed` only for the types you choose.
Then implement the public trait for those same types.
Callers can call public trait methods because the public trait is exported.
They cannot implement the trait for their own types because the private supertrait is unnameable outside the crate.
This is an intentional coherence boundary, not a privacy trick for hiding methods from callers.
The public trait's methods remain callable anywhere the trait is in scope.
Only the implementation obligation is blocked, because implementing the public trait also requires implementing the private supertrait.
Sealing is especially useful when a trait's set of implementors corresponds to enum-like cases owned by the crate but the API wants trait syntax.

## Example
```rust
pub trait Token: private::Sealed {
    fn text(&self) -> &str;
}

pub struct Keyword(String);

impl Token for Keyword {
    fn text(&self) -> &str {
        &self.0
    }
}

mod private {
    pub trait Sealed {}
}

impl private::Sealed for Keyword {}

fn main() {
    let kw = Keyword("fn".to_string());
    assert_eq!(kw.text(), "fn");
}
```

## Common errors
A downstream crate trying to implement a sealed trait usually sees a private-bound error similar to:

```text
error[E0277]: the trait bound `MyType: private::Sealed` is not satisfied
```

That is the point of the pattern; users can consume the trait but cannot add impls.
If users are meant to extend the system, expose an unsealed extension trait or accept callbacks instead.
A crate author can accidentally weaken sealing by making the sealing module public or by exporting the sealing trait under another path.
Keep the module private and document the trait as sealed in rustdoc.

## Best practice
- ✅ Seal traits meant to be consumed by users but implemented only by your crate.
- ✅ Use sealing when adding future methods would otherwise break unknown downstream impls.
- ✅ Keep the private supertrait truly private; the public trait should expose the usable behavior.
- ✅ Document that the trait is sealed so users understand why their impl does not compile.
- ✅ Leave extension traits unsealed when downstream implementations are the point of the API.

## Pitfalls
- ⚠️ Sealing a plugin trait blocks users from extending your system.
- ⚠️ A sealed trait still needs a coherent, documented contract for its users.
- ⚠️ Accidentally exporting the sealing module weakens the pattern.
- ⚠️ Sealing does not replace the [[Coherence and the Orphan Rule]]; it is an additional API choice.

## See also
[[Traits]] · [[Supertraits]] · [[Coherence and the Orphan Rule]] · [[Default Implementations]] · [[Marker Traits]] · [[Static Dispatch with Generics]] · [[Overgeneric Public APIs]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Reference, "Supertraits" — [[the-reference]], https://doc.rust-lang.org/reference/items/traits.html#supertraits
- The Rust Programming Language, ch. 20.2 "Using Supertraits" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-supertraits
