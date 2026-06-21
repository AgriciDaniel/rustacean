---
type: concept
title: "Generic Associated Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, associated-types, gat, lifetimes]
domain: "Generics, Traits & Lifetimes"
difficulty: advanced
related: ["[[Associated Types]]", "[[Traits]]", "[[Lifetimes]]", "[[Where Clauses]]", "[[Trait Bounds]]", "[[Lifetime Elision]]"]
sources: ["[[the-reference]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/associated-items.html#associated-types", "https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#associated-types"]
rust_version: "edition 2024 / 1.85+"
---

# Generic Associated Types

Generic associated types, or GATs, are associated types with their own lifetime, type, or const parameters, commonly used to express outputs that borrow from `self`.

## What it is
A normal associated type chooses one concrete type per implementation.
A GAT chooses a family of related types, indexed by parameters such as a borrow lifetime.
The important use case is a "lending" API where the returned type can borrow from the receiver.
For example, a trait can say "for every borrow lifetime `'a`, my view type is `Self::View<'a>`."
This fills a gap that plain `Iterator<Item = T>` cannot express for iterators yielding references tied to each `next` borrow.

## How it works
Declare the associated type with parameters: `type View<'a> where Self: 'a;`.
Use it in methods as `Self::View<'a>` or `<T as Trait>::View<'a>`.
The `where Self: 'a` clause is often required when the GAT appears in a method taking `&'a self`.
Implementation definitions repeat the generic parameters and usually repeat the where clause after the type alias value.
GATs are stable, but their syntax is intentionally explicit because the borrow relationship is part of the trait contract.
A GAT is not one type; it is a type constructor family attached to each implementation.
For a lending API, the compiler must know that `Self::Ref<'short>` may borrow from `self` for exactly the method call's borrow.
That is the relationship plain `Iterator` cannot express, because `Iterator::Item` has no lifetime parameter tied to `&mut self`.
The required `where Self: 'a` clause prevents implementations from promising views for lifetimes longer than the receiver can support.

## Example
```rust
trait View {
    type Ref<'a>
    where
        Self: 'a;

    fn view<'a>(&'a self) -> Self::Ref<'a>;
}

struct Name(String);

impl View for Name {
    type Ref<'a> = &'a str where Self: 'a;

    fn view<'a>(&'a self) -> Self::Ref<'a> {
        &self.0
    }
}

fn main() {
    let name = Name("Ferris".to_string());
    let borrowed = name.view();
    assert_eq!(borrowed, "Ferris");
}
```

## Common errors
The most common diagnostic is a required-clause error near the GAT declaration:

```text
error: missing required bound on `Ref`
help: add the required where clause: `where Self: 'a`
```

Put the clause on the associated type in the trait, and repeat it in the impl when defining the concrete projection.
Another common failure is trying to make `dyn Trait` from a trait with a GAT, which usually reports `error[E0038]: the trait ... is not dyn compatible`.
Use static dispatch, split out an object-safe facade trait, or return owned data if dynamic dispatch is the real requirement.
If a borrowed output does not actually need to vary by lifetime, use a plain associated type instead.

## Best practice
- ✅ Reach for GATs when an associated output must borrow from `self` or from another lifetime parameter.
- ✅ Keep the trait small; GAT-heavy APIs can be powerful but difficult to read.
- ✅ Write required `where Self: 'a` clauses exactly where the compiler asks, then verify they express the intended borrow relationship.
- ✅ Prefer a simpler associated type when the output does not vary by lifetime or parameter.
- ✅ Use examples in docs because GAT projections can be hard to infer from the signature alone.

## Pitfalls
- ⚠️ Treating a GAT as "just a nested generic type alias" misses that it is part of trait coherence and method obligations.
- ⚠️ Omitting required where clauses can prevent implementations that should be legal.
- ⚠️ Using GATs where an owned return type would be simpler can overfit the API to borrowing.
- ⚠️ GATs with generic associated types are not dyn-compatible in trait objects; consider [[Static Dispatch with Generics]] or a simpler object-safe trait.

## See also
[[Associated Types]] · [[Traits]] · [[Lifetimes]] · [[Lifetime Elision]] · [[Where Clauses]] · [[Trait Bounds]] · [[Dynamically Sized Types]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Reference, "Associated types" and "Generic associated types" — [[the-reference]], https://doc.rust-lang.org/reference/items/associated-items.html#associated-types
- The Rust Programming Language, ch. 20.2 "Associated Types" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#associated-types
