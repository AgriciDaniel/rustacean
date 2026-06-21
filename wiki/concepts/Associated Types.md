---
type: concept
title: "Associated Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, associated-types, generics]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Traits]]", "[[Trait Bounds]]", "[[Generic Associated Types]]", "[[Associated Constants]]", "[[Fully Qualified Syntax]]", "[[The Iterator Trait]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#associated-types", "https://doc.rust-lang.org/reference/items/associated-items.html#associated-types"]
rust_version: "edition 2024 / 1.85+"
---

# Associated Types

An associated type is a type placeholder owned by a trait implementation, letting a trait name a related type without making callers choose it at every use site.

## What it is
Associated types are type aliases declared in traits and defined in trait implementations.
The classic example is `Iterator::Item`: each iterator implementation chooses exactly what item type it yields.
Associated types are part of the trait contract, so implementors must provide concrete definitions.
They differ from trait generic parameters because a trait with an associated type is normally implemented once for a given type.
That "one choice per impl" removes repeated type annotations at call sites.

## How it works
Declare an associated type with `type Name;` or with bounds such as `type Name: Debug;`.
Use it in trait methods as `Self::Name`.
Define it in an impl with `type Name = ConcreteType;`.
Refer to a specific associated type with a projection such as `<Counter as Iterator>::Item`.
Associated types have an implicit `Sized` bound unless relaxed with `?Sized`.
Plain associated type defaults in traits are not stable; the implementation supplies the concrete type.
Projection equality is part of trait solving: `I: Iterator<Item = String>` means the compiler must prove `<I as Iterator>::Item` is exactly `String`.
Because the associated type is selected by the impl, callers do not pass it as an extra generic argument at every use site.
This is why `Iterator` is written as `Iterator<Item = T>` in bounds rather than `Iterator<T>`.
Use fully qualified projections when several traits expose the same associated type name or diagnostics mention an ambiguous `Self::Item`.

## Example
```rust
trait Container {
    type Item;

    fn push_item(&mut self, item: Self::Item);
    fn len(&self) -> usize;
}

impl<T> Container for Vec<T> {
    type Item = T;

    fn push_item(&mut self, item: T) {
        self.push(item);
    }

    fn len(&self) -> usize {
        Vec::len(self)
    }
}

fn main() {
    let mut values = Vec::new();
    values.push_item(10);
    values.push_item(20);
    assert_eq!(Container::len(&values), 2);
}
```

## Common errors
Forgetting to define an associated type in an impl reports:

```text
error[E0046]: not all trait items implemented, missing: `Item`
```

Add `type Item = ...;` in the `impl` block and make every method signature line up with that concrete choice.
Using an associated type where the caller needs to choose the type can lead to conflicting impl attempts; switch to a generic trait parameter when multiple impls per type are intentional.
Ambiguous projections can produce `error[E0223]: ambiguous associated type`.
Use `<Type as Trait>::Assoc` or add a trait bound such as `I: Iterator<Item = u8>` so the compiler knows which trait's associated type is meant.

## Best practice
- ✅ Use associated types when the output or related type is intrinsic to the implementor, like an iterator's `Item`.
- ✅ Use trait generic parameters when the same type should be allowed to implement the trait multiple times for different parameters.
- ✅ Name associated types semantically (`Item`, `Error`, `Output`, `Target`) and document their contract.
- ✅ Put bounds on associated types when users of the trait need guaranteed behavior from the associated type.
- ✅ Use [[Fully Qualified Syntax]] when projections are ambiguous or when reading compiler diagnostics.

## Pitfalls
- ⚠️ Choosing generics instead of an associated type can force noisy annotations and permit multiple impls you did not intend.
- ⚠️ Choosing an associated type when callers should choose the type per use can make the trait too rigid.
- ⚠️ Forgetting associated type bounds moves errors from the trait definition into distant generic call sites.
- ⚠️ GAT syntax has extra where-clause rules; see [[Generic Associated Types]] before designing lending APIs.

## See also
[[Traits]] · [[Trait Bounds]] · [[Generic Associated Types]] · [[Associated Constants]] · [[Fully Qualified Syntax]] · [[The Iterator Trait]] · [[Operator Overloading]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 20.2 "Defining Traits with Associated Types" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#associated-types
- The Rust Reference, "Associated types" — [[the-reference]], https://doc.rust-lang.org/reference/items/associated-items.html#associated-types
