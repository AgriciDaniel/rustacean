---
type: concept
title: "Traits"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, interfaces, polymorphism]
domain: "Generics, Traits & Lifetimes"
difficulty: basic
related: ["[[Generics]]", "[[Trait Bounds]]", "[[Default Implementations]]", "[[Associated Types]]", "[[Supertraits]]", "[[Coherence and the Orphan Rule]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html", "https://doc.rust-lang.org/reference/items/traits.html"]
rust_version: "edition 2024 / 1.85+"
---

# Traits

A trait is Rust's way to name shared behavior: it declares associated functions, methods, types, or constants that implementing types agree to provide.

## What it is
Traits are similar to interfaces, but they are integrated with Rust's generic type system and coherence rules.
A trait declaration creates a name in the type namespace and defines a contract in terms of associated items.
Every trait has an implicit `Self` type representing the implementing type.
Types implement traits in separate `impl Trait for Type` blocks.
Trait methods can be called with method syntax when the trait is in scope and the receiver type implements it.

## How it works
A trait method declaration with a semicolon requires each implementation to provide a body.
A trait method with a body is a [[Default Implementations]] method that implementors may keep or override.
Associated types and associated constants let the trait's contract include type-level and value-level facts.
Traits are used two main ways: as generic bounds such as `T: Summary`, or behind trait objects such as `&dyn Summary` when the trait is dyn-compatible.
The [[Coherence and the Orphan Rule]] limits where trait impls can be written so two crates cannot define competing impls for the same pair.
Method lookup considers inherent methods first, then visible trait methods implemented for the receiver type.
That is why importing a trait can make extension methods appear, even though the implementation was compiled elsewhere.
A trait's associated items are obligations on each implementation, but semantic promises such as "ordering is total" or "hash agrees with equality" still need documentation and tests.
Dyn-compatible traits are represented through a fat pointer containing a data pointer and a vtable pointer; generic trait bounds usually use static dispatch instead.

## Example
```rust
trait Summary {
    fn author(&self) -> &str;

    fn summarize(&self) -> String {
        format!("by {}", self.author())
    }
}

struct Article {
    author: String,
    title: String,
}

impl Summary for Article {
    fn author(&self) -> &str {
        &self.author
    }

    fn summarize(&self) -> String {
        format!("{} ({})", self.title, self.author())
    }
}

fn main() {
    let article = Article { author: "Ferris".into(), title: "Traits".into() };
    assert_eq!(article.summarize(), "Traits (Ferris)");
}
```

## Common errors
Calling a trait method without the trait in scope can produce:

```text
error[E0599]: no method named `summarize` found for struct `Article` in the current scope
help: trait `Summary` which provides `summarize` is implemented but not in scope
```

Import the trait (`use crate::Summary;`) or call with fully qualified syntax.
Trying to use a non-dyn-compatible trait as a trait object reports `error[E0038]: the trait ... is not dyn compatible`.
The fix is usually to add `where Self: Sized` to methods that return `Self` or have generic parameters, or to keep the trait static-dispatch-only.
For `error[E0117]` on a trait impl, check whether both the trait and type are foreign and use a local newtype.

## Best practice
- ✅ Define traits around behavior callers need, not around every type you happen to have.
- ✅ Keep public traits small and focused; adding required methods later is usually breaking unless the trait is sealed or the method has a default.
- ✅ Decide early whether a trait should be used as `dyn Trait`; dyn compatibility affects method signatures.
- ✅ Prefer standard traits such as `Display`, `From`, `TryFrom`, `Iterator`, `Send`, and `Sync` when their contracts fit.
- ✅ Document semantic requirements that the compiler cannot check, especially for marker or unsafe traits.

## Pitfalls
- ⚠️ Treating traits as fields with data is a category error; trait objects carry behavior, not arbitrary extra state.
- ⚠️ Reusing method names across traits can require [[Fully Qualified Syntax]] to disambiguate.
- ⚠️ Making a trait too broad forces implementors to write meaningless methods or prevents dyn use; split it.
- ⚠️ Implementing foreign traits for foreign types is rejected by the [[Coherence and the Orphan Rule]]; use [[Use a Newtype to Implement Foreign Traits]].

## See also
[[Generics]] · [[Trait Bounds]] · [[Default Implementations]] · [[Associated Types]] · [[Supertraits]] · [[Blanket Implementations]] · [[Fully Qualified Syntax]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.2 "Traits: Defining Shared Behavior" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html
- The Rust Reference, "Traits" — [[the-reference]], https://doc.rust-lang.org/reference/items/traits.html
