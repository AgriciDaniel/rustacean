---
type: concept
title: "Object-Oriented Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, oop, traits, polymorphism]
domain: "OOP & Trait Objects"
difficulty: basic
related: ["[[Encapsulation in Rust]]", "[[Trait Objects]]", "[[Composition over Inheritance]]", "[[Static vs Dynamic Dispatch]]", "[[Traits]]", "[[Methods]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-00-oop.html", "https://doc.rust-lang.org/book/ch18-01-what-is-oo.html", "https://doc.rust-lang.org/reference/types/trait-object.html"]
rust_version: "edition 2024 / 1.85+"
---

# Object-Oriented Rust

Rust supports several object-oriented design goals without class inheritance: data plus behavior live in structs/enums plus `impl` blocks, encapsulation comes from privacy, and polymorphism comes from generics or trait objects.

## What it is
Object-oriented Rust is not "Rust with classes." It is the use of Rust's own tools to solve problems often solved with OOP elsewhere:

- structs and enums store data;
- `impl` blocks define methods on that data;
- module privacy and `pub` define the public API boundary;
- traits describe shared behavior;
- generics provide compile-time polymorphism;
- `dyn Trait` provides runtime polymorphism when the concrete type is intentionally erased.

The Book points out that there is no single agreed definition of object orientation. Under a "data plus methods" definition, Rust qualifies. Under a "class inheritance is required" definition, Rust does not.

## How it works
Rust separates concerns that class-based languages often bundle together. A `struct` owns fields, an `impl` block owns inherent methods, and a `trait` names behavior that many types can implement. This makes the relationship between data layout, behavior, and abstraction more explicit.

For code reuse, Rust commonly uses trait default methods, free functions, helper types, composition, or generics. For substitutability, it uses trait bounds for static dispatch and trait objects for dynamic dispatch. These choices are deliberate: they avoid forcing every reuse relationship into an inheritance tree.

That means the design question is not "what should this inherit from?" but "what behavior must callers rely on, who owns the data, and should the set of concrete types be known at compile time?"

There is also a visibility dimension that class hierarchies often blur. Rust privacy is module-based, not subclass-based: a type can expose a stable public method surface while keeping fields and helper types private to the module. That privacy boundary is what lets a type preserve invariants without a `protected` escape hatch.

When runtime polymorphism is needed, Rust's trait-object model is narrower than "objects" in many OOP languages. A `dyn Trait` value carries behavior dispatch metadata, but the stored data still belongs to the concrete implementor behind the pointer. You cannot add fields to a trait object; you design the concrete structs first, then erase only the behavior boundary you need.

## Example
```rust
trait Render {
    fn render(&self) -> String;
}

struct Button {
    label: String,
}

impl Button {
    fn new(label: impl Into<String>) -> Self {
        Self {
            label: label.into(),
        }
    }
}

impl Render for Button {
    fn render(&self) -> String {
        format!("[ {} ]", self.label)
    }
}

fn paint(item: &dyn Render) {
    println!("{}", item.render());
}

fn main() {
    let save = Button::new("Save");
    paint(&save);
}
```

## Worked example: open extension point
```rust
trait PaymentProcessor {
    fn charge_cents(&self, cents: u64) -> Result<String, String>;
}

struct Checkout {
    processor: Box<dyn PaymentProcessor>,
}

impl Checkout {
    fn new(processor: Box<dyn PaymentProcessor>) -> Self {
        Self { processor }
    }

    fn checkout(&self, cents: u64) -> Result<String, String> {
        self.processor.charge_cents(cents)
    }
}

struct TestProcessor;

impl PaymentProcessor for TestProcessor {
    fn charge_cents(&self, cents: u64) -> Result<String, String> {
        Ok(format!("test charge for {cents} cents"))
    }
}

fn main() {
    let checkout = Checkout::new(Box::new(TestProcessor));
    assert_eq!(
        checkout.checkout(499).unwrap(),
        "test charge for 499 cents"
    );
}
```

This is an OOP-shaped design, but the Rust boundary is explicit: `Checkout` owns a boxed collaborator, the collaborator's concrete type is erased, and the public method reports failure with `Result` instead of an exception hierarchy.

## Common errors
```text
error[E0277]: the trait bound `String: Render` is not satisfied
```

This usually means a value was passed to a trait-object or generic boundary without implementing the required trait. Fix it by implementing the trait for that type, passing a different type, or changing the boundary to the behavior the caller actually needs.

```text
error[E0038]: the trait `Processor` is not dyn compatible
```

This means the trait was designed for static dispatch but is being used as `dyn Processor`. Move generic, constructor-like, or `Self`-returning methods behind `where Self: Sized`, or use a generic type parameter instead of a trait object.

## Best practice
- ✅ Model data with structs/enums first; add traits when there is real shared behavior.
- ✅ Use [[Encapsulation in Rust]] to keep invariants behind a small public API.
- ✅ Choose [[Static vs Dynamic Dispatch]] explicitly instead of treating `dyn Trait` as the default abstraction.
- ✅ Prefer [[Composition over Inheritance]] when one value should own or delegate to another value.
- ✅ Use enums when the set of variants is closed and your crate owns all the cases; use trait objects when external crates should add new cases.
- ✅ Keep public traits small and behavior-oriented. A broad trait can accidentally become a rigid pseudo-base-class.
- ✅ Use `Result`, `Option`, and state-specific types for control flow instead of recreating exception or nullable-object conventions.

## Pitfalls
- ⚠️ Do not search for a direct class hierarchy translation; Rust designs usually become smaller when expressed with [[Traits]], [[Enums]], and ownership.
- ⚠️ Avoid forcing every variation behind `Box<dyn Trait>`; see [[Overusing Trait Objects]].
- ⚠️ Do not expose fields just because a class in another language would have protected state; that weakens [[Encapsulation in Rust]].
- ⚠️ Avoid "manager" traits that mix construction, mutation, querying, cloning, and formatting. They are harder to make dyn-compatible and harder to implement correctly.
- ⚠️ Do not use inheritance vocabulary to hide ownership. Say whether a value owns, borrows, shares, or delegates.

## See also
[[OOP & Trait Objects]] · [[Encapsulation in Rust]] · [[Trait Objects]] · [[Composition over Inheritance]] · [[Static vs Dynamic Dispatch]] · [[The State Pattern]] · [[Type-State State Machines]] · [[Traits]]
· [[Enums]] · [[Generics]] · [[dyn Compatibility (Object Safety)]] · [[Making Invalid States Unrepresentable]]

## Sources
- The Rust Programming Language, ch. 18 "Object-Oriented Programming Features" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-00-oop.html
- The Rust Programming Language, ch. 18.1 "Characteristics of Object-Oriented Languages" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-01-what-is-oo.html
- The Rust Reference, "Trait object types" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/trait-object.html
