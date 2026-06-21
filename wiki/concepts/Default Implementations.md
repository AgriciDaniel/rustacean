---
type: concept
title: "Default Implementations"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, defaults, api-design]
domain: "Generics, Traits & Lifetimes"
difficulty: basic
related: ["[[Traits]]", "[[Trait Bounds]]", "[[Supertraits]]", "[[Associated Types]]", "[[Sealed Traits]]", "[[Overgeneric Public APIs]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html#default-implementations", "https://doc.rust-lang.org/reference/items/traits.html"]
rust_version: "edition 2024 / 1.85+"
---

# Default Implementations

A default implementation is a trait method body supplied by the trait itself, so implementors can inherit behavior or override it.

## What it is
Trait functions may either end with `;`, meaning every impl must define them, or include a body, meaning that body is the default.
Defaults reduce boilerplate when many implementors share behavior.
They are especially useful when one small required method can support several convenience methods.
A default can call other trait methods, including required methods that each implementor must provide.
Overriding a default uses the same syntax as implementing any required trait method.

## How it works
When a type implements the trait and omits the defaulted method, method calls dispatch to the trait's default body.
If the impl provides its own method body, that body replaces the default.
Rust does not provide a stable "call the overridden default implementation" mechanism from inside the override.
Adding a new required method to a public trait is breaking; adding a new defaulted method is often compatible, though method-name conflicts can still matter.
Associated constants may also have defaults, but associated types cannot currently have default definitions in stable traits.
Defaults are type-checked once against the trait's declared requirements, not against a particular implementor's private fields.
That means a default method can only use `Self`, associated items, supertrait methods, and other trait methods that the contract exposes.
Default methods may include `where Self: Sized` to keep object-safe parts of a trait usable through `dyn Trait` while reserving builder-style helpers for concrete types.
An override completely replaces the default body for that implementation.

## Example
```rust
trait Summary {
    fn author(&self) -> &str;

    fn summarize(&self) -> String {
        format!("read more from {}", self.author())
    }
}

struct Post {
    user: String,
}

impl Summary for Post {
    fn author(&self) -> &str {
        &self.user
    }
}

fn main() {
    let post = Post { user: "@rustacean".into() };
    assert_eq!(post.summarize(), "read more from @rustacean");
}
```

## Common errors
Calling a helper from a default method without making it part of the trait contract usually fails with:

```text
error[E0599]: no method named `helper` found for reference `&Self` in the current scope
```

Add the helper as a required or default trait method, move the logic to a free function with suitable bounds, or avoid assuming implementor-specific inherent methods.
Another common mistake is trying to call the original default from an override as if Rust had `super::method`.
There is no stable syntax for that; factor the shared behavior into a differently named default method if an override needs to reuse it.
If a default method returns `Self`, add `where Self: Sized` when the rest of the trait should remain dyn-compatible.

## Best practice
- ✅ Put reusable behavior in defaults and keep the required surface as small as the true contract allows.
- ✅ Use a required primitive method plus default convenience methods when implementors can provide the primitive efficiently.
- ✅ Document whether implementors are expected to override defaults for performance or semantics.
- ✅ Prefer defaulted additions over required additions when evolving a public trait.
- ✅ Consider [[Sealed Traits]] when you need stronger control over future trait evolution.

## Pitfalls
- ⚠️ You cannot call the default body from an overriding implementation as a "super" method.
- ⚠️ A default that assumes more than the required methods promise can encode hidden semantic requirements.
- ⚠️ Adding a default method can still conflict with downstream inherent or trait method names in some call sites.
- ⚠️ Using defaults to create a large "kitchen sink" trait often signals the trait should be split; see [[Overgeneric Public APIs]].

## See also
[[Traits]] · [[Trait Bounds]] · [[Supertraits]] · [[Associated Types]] · [[Sealed Traits]] · [[Blanket Implementations]] · [[The Iterator Trait]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.2 "Default Implementations" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html#default-implementations
- The Rust Reference, "Traits" — [[the-reference]], https://doc.rust-lang.org/reference/items/traits.html
