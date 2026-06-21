---
type: concept
title: "dyn Compatibility (Object Safety)"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, dyn, object-safety]
domain: "OOP & Trait Objects"
difficulty: advanced
related: ["[[Trait Objects]]", "[[Static vs Dynamic Dispatch]]", "[[Traits]]", "[[Associated Types]]", "[[Generic Associated Types]]", "[[Non-dyn-Compatible Traits as Trait Objects]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/std/keyword.dyn.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Dyn Compatibility"]
---

# dyn Compatibility (Object Safety)

dyn compatibility, formerly called object safety, is the set of rules that decides whether a trait may be used as the base trait of `dyn Trait`.

## What it is
A trait can be used as a trait object only if Rust can build a coherent dynamic dispatch interface for it. The official Reference term is "dyn compatibility"; "object safety" is the older name and still appears in much Rust discussion.

The rule of thumb: a dyn-compatible trait must not require knowing the erased concrete type at the call site. Methods callable through `dyn Trait` need receivers such as `&self`, `&mut self`, `Box<Self>`, `Rc<Self>`, `Arc<Self>`, or `Pin<P>` around those forms, and they cannot have type parameters.

## How it works
When a value is coerced to `dyn Trait`, Rust erases its concrete type and calls trait methods through a vtable. That vtable cannot contain an infinite family of monomorphized generic methods, and it cannot promise a return type of bare `Self` when the caller no longer knows what `Self` is.

The Reference gives the precise rules. Important design constraints include:

- all supertraits must also be dyn compatible;
- the trait must not require `Self: Sized`;
- associated constants are not allowed on dyn-compatible traits;
- associated types with generics are not allowed;
- dispatchable methods must not have type parameters;
- dispatchable methods must use `Self` only in the receiver type;
- methods that would break these rules can often be marked `where Self: Sized`, making them unavailable on trait objects but still usable on concrete implementors.

A dyn-compatible trait can still contain non-dispatchable methods, but those methods must be explicitly restricted to sized implementors. This is why a trait can offer ergonomic constructors or adapters for concrete types while keeping its `&dyn Trait` surface small and callable.

Associated types are a common edge case. A non-generic associated type can be used with a trait object only when the object type specifies it, such as `&dyn Iterator<Item = u8>`. Generic associated types are not dyn-compatible because the vtable cannot represent all possible instantiations.

## Example
```rust
trait Parser {
    fn name(&self) -> &'static str;
    fn parse(&self, input: &str) -> usize;

    fn boxed(self) -> Box<dyn Parser>
    where
        Self: Sized + 'static,
    {
        Box::new(self)
    }
}

struct WordParser;

impl Parser for WordParser {
    fn name(&self) -> &'static str {
        "words"
    }

    fn parse(&self, input: &str) -> usize {
        input.split_whitespace().count()
    }
}

fn run(parser: &dyn Parser, input: &str) -> usize {
    println!("using {}", parser.name());
    parser.parse(input)
}

fn main() {
    let parser = WordParser.boxed();
    assert_eq!(run(&*parser, "rust likes explicit boundaries"), 4);
}
```

## Worked example: associated type specified on `dyn`
```rust
trait Source {
    type Item;

    fn next_item(&mut self) -> Option<Self::Item>;
}

struct Counter(u8);

impl Source for Counter {
    type Item = u8;

    fn next_item(&mut self) -> Option<Self::Item> {
        let value = self.0;
        self.0 = self.0.checked_add(1)?;
        Some(value)
    }
}

fn take_two(source: &mut dyn Source<Item = u8>) -> Vec<u8> {
    [source.next_item(), source.next_item()]
        .into_iter()
        .flatten()
        .collect()
}

fn main() {
    let mut counter = Counter(7);
    assert_eq!(take_two(&mut counter), vec![7, 8]);
}
```

The object type includes `Item = u8`, so callers know the return type of `next_item` even though they do not know the concrete source type.

## Common errors
```text
error[E0038]: the trait `Factory` is not dyn compatible
```

Typical causes are `fn new() -> Self`, `fn clone_like(&self) -> Self`, `fn convert<T>(&self, value: T)`, an associated constant, or `trait Factory: Sized`. Add `where Self: Sized` to concrete-only methods, split the trait, or use generics.

```text
error: the `next` method cannot be invoked on a trait object
```

This shape appears when the method exists on the trait but has a `Self: Sized` restriction or otherwise is not dispatchable. Call it on a concrete type, or redesign the dyn-facing method.

## Best practice
- ✅ Decide whether a public trait is intended for `dyn` use before stabilizing it.
- ✅ Move constructors, builders, generic helpers, and `Self`-returning convenience methods behind `where Self: Sized`.
- ✅ Keep the dyn-facing trait small; put extension methods in a separate extension trait when useful.
- ✅ Use the current term "dyn compatible" in new docs, with "object safety" as a search synonym.
- ✅ Specify non-generic associated types at the object boundary, for example `dyn Iterator<Item = Event>`.
- ✅ Treat dyn compatibility as part of semver for public traits; adding an associated const or generic method can break downstream `dyn` users.
- ✅ Prefer adapter traits when a rich generic trait also needs a narrow runtime-dispatch surface.

## Pitfalls
- ⚠️ Do not add a generic method to a trait that downstream users already use as `dyn Trait`; that can break their object use.
- ⚠️ Do not add `: Sized` to a trait that is meant to be used as a trait object.
- ⚠️ Do not assume `async fn` in a trait is dyn-compatible by default; use a deliberate boxing or adapter design when dynamic async dispatch is required.
- ⚠️ See [[Non-dyn-Compatible Traits as Trait Objects]] for the common error and alternatives.
- ⚠️ Do not confuse `Self` in a receiver, such as `self: Box<Self>`, with arbitrary `Self` in parameters or return types; receivers have special dyn rules.
- ⚠️ Avoid associated constants on dyn-facing traits; use a method if the value must be queried through the object.

## See also
[[OOP & Trait Objects]] · [[Trait Objects]] · [[Static vs Dynamic Dispatch]] · [[Traits]] · [[Associated Types]] · [[Generic Associated Types]] · [[Async Traits]] · [[Non-dyn-Compatible Traits as Trait Objects]]
· [[Dynamically Sized Types]] · [[Box]] · [[Overusing Trait Objects]] · [[Default Implementations]]

## Sources
- The Rust Reference, "Dyn compatibility" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility
- The Rust Programming Language, ch. 18.2 "Performing Dynamic Dispatch" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
- Rust standard library keyword docs, "`dyn`" — https://doc.rust-lang.org/std/keyword.dyn.html
