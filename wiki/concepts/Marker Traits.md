---
type: concept
title: "Marker Traits"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, marker-traits, type-system]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Traits]]", "[[Trait Bounds]]", "[[Blanket Implementations]]", "[[Send and Sync]]", "[[The 'static Lifetime]]", "[[Unsafe Send and Sync Implementations]]"]
sources: ["[[the-reference]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/traits.html", "https://doc.rust-lang.org/std/marker/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Marker Traits

A marker trait carries type-level classification with little or no method surface, allowing bounds to express semantic capabilities.

## What it is
Marker traits often have no required methods.
Their purpose is to tell generic code that a type belongs to a category.
Standard examples include `Send`, `Sync`, `Copy`, `Sized`, and `Unpin`.
Some marker traits are automatically implemented by the compiler, some are ordinary library traits, and unsafe marker traits require extra care.
A marker trait can also combine several bounds under one local name for API clarity.

## How it works
A marker trait is still a trait, so it participates in trait bounds, blanket implementations, coherence, and orphan rules.
An empty trait like `trait CacheKey {}` means nothing by itself unless its documentation defines the semantic contract.
A blanket impl can mark all types satisfying a set of real bounds.
Unsafe marker traits such as `Send` and `Sync` communicate invariants that unsafe code may rely on.
Implementing an unsafe marker trait incorrectly can make otherwise safe code unsound.
Auto traits such as `Send` and `Sync` are implemented structurally by the compiler unless a field prevents it or an explicit negative impl exists in the defining crate.
Ordinary marker traits like `Copy` are still explicit trait contracts with compiler-enforced restrictions.
A local marker trait can improve readability, but it does not add new facts unless it has supertraits or unsafe-code documentation that consumers rely on.
Because marker impls often have empty bodies, review the impl header and documentation as the real implementation.

## Example
```rust
use std::collections::HashMap;
use std::hash::Hash;

trait CacheKey: Eq + Hash + Clone {}

impl<T> CacheKey for T where T: Eq + Hash + Clone {}

fn count_key<K: CacheKey>(map: &mut HashMap<K, usize>, key: K) {
    *map.entry(key).or_insert(0) += 1;
}

fn main() {
    let mut counts = HashMap::new();
    count_key(&mut counts, "rust");
    count_key(&mut counts, "rust");
    assert_eq!(counts["rust"], 2);
}
```

## Common errors
A type containing a non-thread-safe field may fail a bound with:

```text
error[E0277]: `Rc<T>` cannot be sent between threads safely
```

Use `Arc<T>` when shared ownership must cross threads, or keep the value on one thread.
Manual `unsafe impl Send` or `unsafe impl Sync` is not a routine fix; it requires proving the type's aliasing and mutation invariants.
For custom marker traits, forgetting a blanket impl means types satisfying the intended super-bounds still do not implement your marker.
Either write `impl<T> Marker for T where T: Bound1 + Bound2 {}` or implement the marker intentionally per type.

## Best practice
- ✅ Use marker traits when a named semantic category improves signatures or documents a real invariant.
- ✅ Prefer blanket impls when the marker exactly means "implements these other traits."
- ✅ Document the contract because an empty trait body cannot explain it to the compiler.
- ✅ Avoid unsafe marker traits unless unsafe code truly depends on the invariant.
- ✅ Prefer existing standard marker traits when they already describe the capability.

## Pitfalls
- ⚠️ An undocumented empty trait becomes a private club, not a useful abstraction.
- ⚠️ Implementing `Send` or `Sync` manually is unsafe and easy to get wrong; see [[Unsafe Send and Sync Implementations]].
- ⚠️ Marker traits cannot store data or enforce runtime validation.
- ⚠️ A broad blanket marker impl can consume impl space and prevent later exceptions.

## See also
[[Traits]] · [[Trait Bounds]] · [[Blanket Implementations]] · [[Send and Sync]] · [[The 'static Lifetime]] · [[Coherence and the Orphan Rule]] · [[Unsafe Send and Sync Implementations]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Reference, "Traits" and "Unsafe traits" — [[the-reference]], https://doc.rust-lang.org/reference/items/traits.html
- The Rust standard library, `std::marker` — https://doc.rust-lang.org/std/marker/index.html
