---
type: concept
title: "Return-Position impl Trait in Traits"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, impl-trait, associated-types, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Traits]]", "[[Associated Types]]", "[[Generic Associated Types]]", "[[Trait Objects]]", "[[dyn Compatibility (Object Safety)]]", "[[Return Iterators Instead of Collecting]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/types/impl-trait.html#return-position-impl-trait-in-traits-and-trait-implementations", "https://doc.rust-lang.org/reference/types/impl-trait.html#capturing"]
rust_version: "edition 2024 / 1.85+"
---

# Return-Position impl Trait in Traits

Return-position `impl Trait` in a trait method lets each implementation choose one hidden concrete return type while the trait exposes only bounds.
In traits, this syntax behaves like an anonymous associated type, not like dynamic dispatch.

## What it is
`impl Trait` in return position means "the function chooses a concrete type that implements these bounds."
When used in a trait method, every implementation supplies the hidden concrete type through its method body.
The Reference describes this as desugaring to an anonymous associated type.
This is the stable way to write many iterator-returning or future-returning trait methods without naming long adapter types.
It is different from an explicit associated type because callers usually cannot name or constrain the hidden type directly.
It is also different from `Box<dyn Trait>` because it uses static dispatch and has no required heap allocation.
The feature is often called RPITIT: return-position `impl Trait` in traits.
It is closely related to [[Associated Types]], [[Generic Associated Types]], and [[Static Dispatch with Generics]].

## How it works
Each implementation must return a single concrete type for each `impl Trait` return position.
Different impls may choose different hidden types.
Within one function body, all return paths must resolve to the same concrete type.
The hidden type captures generic parameters according to return-position `impl Trait` capture rules.
In edition 2024, return-position `impl Trait` automatically captures all in-scope generic parameters, including lifetimes.
Use bounds such as `use<..>` can precisely control captures where allowed.
Trait methods returning `impl Trait` are not automatically usable through `dyn Trait`.
If object safety is required, use an associated type, a boxed trait object, or a separate object-safe trait.

## Example
```rust
trait Words {
    fn words(&self) -> impl Iterator<Item = &str>;
}

struct Line(String);

impl Words for Line {
    fn words(&self) -> impl Iterator<Item = &str> {
        self.0.split_whitespace()
    }
}

fn count_words(source: &impl Words) -> usize {
    source.words().count()
}

fn main() {
    let line = Line(String::from("rust types carry invariants"));
    assert_eq!(count_words(&line), 4);
}
```

## Edge cases
```rust
trait MakeNumber {
    fn number(&self) -> impl Copy + Into<i32>;
}

struct One;

impl MakeNumber for One {
    fn number(&self) -> impl Copy + Into<i32> {
        1_i32
    }
}

fn main() {
    let one = One;
    let n: i32 = one.number().into();
    assert_eq!(n, 1);
}
```

## Best practice
- ✅ Use RPITIT when callers only need the returned trait behavior and should not depend on the concrete type.
- ✅ Prefer an explicit associated type when downstream code must name, constrain, or compose the returned type.
- ✅ Prefer `Box<dyn Trait>` only when heterogeneous runtime dispatch or object safety is required.
- ✅ Keep public return bounds tight; every listed bound is part of the API contract.
- ✅ Test trait implementations through generic functions so capture and lifetime behavior is exercised.
- ✅ Document whether the hidden type borrows from `self`, because that shapes caller ergonomics.

## Pitfalls
- ⚠️ Assuming `fn f(&self) -> impl Trait` is object-safe; check [[dyn Compatibility (Object Safety)]].
- ⚠️ Returning different concrete iterator adapter types from different branches; use an enum, `Either`, or `Box<dyn Iterator>` when needed.
- ⚠️ Exposing too few bounds, then discovering callers need `Clone`, `ExactSizeIterator`, or `Send`.
- ⚠️ Treating direct `type Assoc = impl Trait` as the same feature; type-alias `impl Trait` positions have their own stability rules.
- ⚠️ Forgetting edition 2024 capture changes when comparing older examples.

## See also
[[Advanced Type System]]
[[Traits]]
[[Associated Types]]
[[Generic Associated Types]]
[[Trait Objects]]
[[dyn Compatibility (Object Safety)]]
[[Static Dispatch with Generics]]
[[Return Iterators Instead of Collecting]]
[[Async Traits]]
[[Boxed Closure Returns]]

## Sources
- The Rust Reference, "`impl Trait`" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/impl-trait.html
- The Rust Reference, "Return-position `impl Trait` in traits and trait implementations" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/impl-trait.html#return-position-impl-trait-in-traits-and-trait-implementations
