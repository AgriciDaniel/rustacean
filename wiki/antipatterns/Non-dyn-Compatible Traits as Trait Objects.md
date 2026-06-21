---
type: antipattern
title: "Non-dyn-Compatible Traits as Trait Objects"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, antipattern, dyn, object-safety]
domain: "OOP & Trait Objects"
difficulty: advanced
related: ["[[dyn Compatibility (Object Safety)]]", "[[Trait Objects]]", "[[Static vs Dynamic Dispatch]]", "[[Associated Types]]", "[[Async Traits]]", "[[Sealed Traits]]"]
sources: ["[[the-reference]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html"]
rust_version: "edition 2024 / 1.85+"
---

# Non-dyn-Compatible Traits as Trait Objects

Using a non-dyn-compatible trait as `dyn Trait` is a design mismatch: the trait asks for operations that cannot be represented as a runtime trait object interface.

## The mistake
The mistake is designing a trait for generic, concrete-type use and later trying to store it as `Box<dyn Trait>`. Common causes include generic methods, methods that return `Self`, methods that take non-receiver `Self`, associated constants, requiring `Self: Sized`, or async trait methods without a dyn-dispatch strategy.

The compiler rejects this because the vtable for a trait object must have a finite, concrete callable shape. Some trait methods depend on knowing the erased concrete type, so they cannot be called through `dyn Trait`.

This is not a weakness of traits in general. Generic code can use many traits that are not dyn-compatible because monomorphization keeps the concrete type known. The mistake is choosing `dyn Trait` for a trait whose API fundamentally depends on concrete-type knowledge.

## Why it happens
Traits serve two different roles in Rust. A trait can be a generic bound for static dispatch, or it can be a runtime interface for dynamic dispatch. The same trait can sometimes do both, but only if its object-facing methods obey dyn compatibility.

When the trait needs concrete-type operations, keep those operations available only for sized implementors with `where Self: Sized`. That preserves `dyn Trait` for the methods that can be dispatched dynamically.

The vtable has entries for callable trait methods with a fixed signature. A generic method would need a different instantiation for each `T`, an associated constant is not a method call entry, and `Self` in return position would ask the caller to receive an unknown concrete type. Marking those methods `where Self: Sized` removes them from the trait-object call surface.

## Example
```rust
trait CloneBoxed {
    fn describe(&self) -> String;

    fn duplicate(self) -> Self
    where
        Self: Sized;
}

#[derive(Clone)]
struct Token(&'static str);

impl CloneBoxed for Token {
    fn describe(&self) -> String {
        format!("token {}", self.0)
    }

    fn duplicate(self) -> Self {
        self.clone()
    }
}

fn print_description(value: &dyn CloneBoxed) {
    println!("{}", value.describe());
}

fn main() {
    let token = Token("A");
    let duplicate = token.clone().duplicate();
    assert_eq!(duplicate.describe(), "token A");
    print_description(&token);
}
```

Here `duplicate` returns `Self`, so it is explicitly limited to sized concrete implementors. The trait can still be used as `dyn CloneBoxed` for `describe`.

## Better design: split the trait
```rust
trait Describe {
    fn describe(&self) -> String;
}

trait Duplicate: Describe + Sized {
    fn duplicate(&self) -> Self;
}

#[derive(Clone)]
struct Token(&'static str);

impl Describe for Token {
    fn describe(&self) -> String {
        format!("token {}", self.0)
    }
}

impl Duplicate for Token {
    fn duplicate(&self) -> Self {
        self.clone()
    }
}

fn print_description(value: &dyn Describe) -> String {
    value.describe()
}

fn duplicate_concrete<T: Duplicate>(value: &T) -> T {
    value.duplicate()
}

fn main() {
    let token = Token("B");
    assert_eq!(print_description(&token), "token B");
    assert_eq!(duplicate_concrete(&token).describe(), "token B");
}
```

The dyn-facing trait contains only behavior that can be dispatched through a trait object. The concrete helper trait stays available for static dispatch.

## Common errors
```text
error[E0038]: the trait `Clone` is not dyn compatible
```

`Clone::clone` returns `Self`, so `dyn Clone` is not a useful direct object type. Use a crate pattern for `clone_box`, add a dyn-compatible cloning method returning `Box<dyn Trait>`, or keep the concrete type generic.

```text
error[E0038]: the trait `Service` is not dyn compatible
note: method `call` has generic type parameters
```

Generic methods are fine under `T: Service`, but not through `dyn Service`. Move the type parameter to the trait itself, use an associated type specified on the object, or keep the API generic.

## Best practice
- ✅ Split dyn-compatible behavior from concrete-type helpers when the combined trait becomes awkward.
- ✅ Add `where Self: Sized` to methods that construct, consume, clone, or return the concrete implementor.
- ✅ Use associated types carefully: non-generic associated types can work with trait objects when specified, but generic associated types are not dyn-compatible.
- ✅ For async dynamic dispatch, choose a deliberate boxed-future adapter or crate pattern instead of assuming plain `async fn` works on `dyn Trait`.
- ✅ Test public traits both ways when you intend both roles: one generic function and one `&dyn Trait` or `Box<dyn Trait>` use site.
- ✅ Consider a dyn-compatible adapter trait for external traits you do not control.
- ✅ Keep `Self: Sized` helper methods out of examples that are meant to demonstrate calls through a trait object.

## Pitfalls
- ⚠️ Do not add `Self: Sized` as a supertrait if you want `dyn Trait`; that makes the whole trait non-dyn-compatible.
- ⚠️ Do not expose `Box<dyn Trait>` in a public API until the trait's dyn compatibility is part of its design contract.
- ⚠️ Do not confuse "method works with a generic `T: Trait`" with "method works through `dyn Trait`."
- ⚠️ Do not use `dyn` as the first design attempt for async traits; the hidden future type needs an explicit erasure strategy.
- ⚠️ Avoid fixing E0038 by deleting useful generic methods from a trait that was never meant for dynamic dispatch; use static dispatch instead.

## See also
[[OOP & Trait Objects]] · [[dyn Compatibility (Object Safety)]] · [[Trait Objects]] · [[Static vs Dynamic Dispatch]] · [[Associated Types]] · [[Generic Associated Types]] · [[Async Traits]] · [[Sealed Traits]]
· [[Overusing Trait Objects]] · [[Default Implementations]] · [[Box]] · [[Generics]]

## Sources
- The Rust Reference, "Dyn compatibility" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility
- The Rust Programming Language, ch. 18.2 "Performing Dynamic Dispatch" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
