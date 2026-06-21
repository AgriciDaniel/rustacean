---
type: concept
title: "Coherence and the Orphan Rule"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, coherence, orphan-rule]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Traits]]", "[[Blanket Implementations]]", "[[Use a Newtype to Implement Foreign Traits]]", "[[Newtype Pattern]]", "[[Trait Bounds]]", "[[Fully Qualified Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html#implementing-a-trait-on-a-type", "https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules"]
rust_version: "edition 2024 / 1.85+"
---

# Coherence and the Orphan Rule

Coherence guarantees there is one applicable trait implementation, and the orphan rule is the key restriction that prevents crates from adding conflicting foreign-trait-for-foreign-type impls.

## What it is
An implementation is allowed when the trait is local to your crate or at least one relevant implemented type is local to your crate.
An orphan impl is an impl of a foreign trait for a foreign type.
Rust rejects orphan impls because two independent crates could otherwise define incompatible impls for the same trait and type.
Coherence is what makes trait method lookup deterministic across the dependency graph.
The rule also lets library authors add impls for their own traits or types without being broken by downstream crates.

## How it works
For ordinary code, remember the practical rule: own the trait or own the type.
You may implement a standard trait like `Display` for your local `UserId`.
You may implement your local trait for `Vec<T>`.
You may not implement `Display` for `Vec<T>` directly because both are foreign.
Use a local wrapper type when you need that behavior.
Blanket impls and generic parameters have extra uncovered-parameter rules in the Reference, but the same coherence goal applies.
Fundamental wrappers such as references and `Box<T>` have special coherence treatment, but the practical design rule remains: make a local type or local trait the anchor of the impl.
Coherence is crate-graph global, so Rust rejects impls that would be ambiguous if another crate added a plausible type or impl later.
This conservative rule is what lets upstream crates add impls for their own traits and types without silently changing downstream method resolution.
Newtype wrappers are the usual explicit boundary when you need behavior the orphan rule intentionally blocks.

## Example
```rust
use std::fmt;

struct DisplayVec(Vec<String>);

impl fmt::Display for DisplayVec {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}

trait WordCount {
    fn word_count(&self) -> usize;
}

impl WordCount for Vec<String> {
    fn word_count(&self) -> usize {
        self.iter().map(|s| s.split_whitespace().count()).sum()
    }
}

fn main() {
    let words = DisplayVec(vec!["hello".into(), "rust".into()]);
    assert_eq!(words.to_string(), "[hello, rust]");
}
```

## Common errors
The classic orphan violation reports:

```text
error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate
```

Own the trait, own the type, or introduce a local newtype wrapper.
Overlapping local impls report `error[E0119]: conflicting implementations`, even if one impl seems "more specific" to a human reader.
Stable Rust does not have general specialization, so redesign the impl set instead of expecting priority rules.
For generic impls, uncovered type parameters before the first local type can also violate the Reference's orphan rules; move the local type into the implementing position or use a wrapper.

## Best practice
- ✅ Design trait impls around ownership: implement local traits for foreign types or foreign traits for local types.
- ✅ Use [[Use a Newtype to Implement Foreign Traits]] when both the desired trait and type are foreign.
- ✅ Treat public blanket impls as API commitments because they reserve impl space.
- ✅ Read coherence errors as dependency-graph protection, not arbitrary compiler strictness.
- ✅ Prefer explicit wrapper types when a foreign type needs domain-specific formatting or behavior.

## Pitfalls
- ⚠️ `impl Display for Vec<String>` is illegal in your crate because both `Display` and `Vec` are foreign.
- ⚠️ Newtype wrappers do not automatically expose all inner methods; forward deliberately.
- ⚠️ Broad blanket impls can conflict with future specific impls.
- ⚠️ Fully qualified syntax can disambiguate names, but it cannot fix an illegal impl.

## See also
[[Traits]] · [[Blanket Implementations]] · [[Use a Newtype to Implement Foreign Traits]] · [[Newtype Pattern]] · [[Trait Bounds]] · [[Fully Qualified Syntax]] · [[Default Implementations]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.2 "Implementing a Trait on a Type" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html#implementing-a-trait-on-a-type
- The Rust Reference, "Orphan rules" — [[the-reference]], https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules
