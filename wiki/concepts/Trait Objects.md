---
type: concept
title: "Trait Objects"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, trait-objects, dyn]
domain: "OOP & Trait Objects"
difficulty: intermediate
related: ["[[dyn Compatibility (Object Safety)]]", "[[Static vs Dynamic Dispatch]]", "[[Dynamically Sized Types]]", "[[Traits]]", "[[Box]]", "[[Composition over Inheritance]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/reference/types/trait-object.html", "https://doc.rust-lang.org/std/keyword.dyn.html"]
rust_version: "edition 2024 / 1.85+"
---

# Trait Objects

A trait object, written through a pointer such as `&dyn Trait` or `Box<dyn Trait>`, erases a concrete type while preserving calls to a dyn-compatible trait through runtime dispatch.

## What it is
Trait objects are Rust's main tool for runtime polymorphism. They let one API accept values of many concrete types as long as each type implements the same trait. This is useful when the concrete set is open-ended or only known at runtime: plugin registries, GUI widget trees, heterogeneous job queues, and similar designs.

The trait object type starts with `dyn` to make the dynamic dispatch boundary visible. Common forms include `&dyn Draw`, `&mut dyn Draw`, `Box<dyn Draw>`, `Arc<dyn Draw + Send + Sync>`, and `Box<dyn Error + Send + Sync>`.

## How it works
A pointer to a trait object is a fat pointer: it carries a data pointer plus metadata used to find the implementation of trait methods for the erased concrete type. Calling a trait method through `dyn Trait` performs dynamic dispatch through that metadata.

The object itself is dynamically sized, so it must live behind a pointer. Use `&dyn Trait` when borrowing an existing value, `Box<dyn Trait>` when the trait object should own one heap-allocated value, and `Arc<dyn Trait + Send + Sync>` when shared ownership across threads is required.

Only dyn-compatible traits can be used this way. Methods that mention bare `Self` in the wrong places, generic methods, async functions, associated constants, and some other features can prevent a trait from becoming a trait object.

The bounds on a trait object are part of its type. `Box<dyn Draw>` is not the same public contract as `Box<dyn Draw + Send + Sync>`, and `Box<dyn Draw>` defaults to a lifetime bound when no lifetime is written. If an owned trait object stores borrowed data, write the lifetime explicitly, such as `Box<dyn Draw + 'a>`, instead of accidentally requiring `'static`.

Trait-object coercions happen at pointer boundaries. `Box<Button>` can coerce to `Box<dyn Draw>`, and `&Button` can coerce to `&dyn Draw`, but a bare local variable cannot have type `dyn Draw` because the unsized value itself has no compile-time size.

## Example
```rust
trait Draw {
    fn draw(&self) -> String;
}

struct Button {
    label: String,
}

impl Draw for Button {
    fn draw(&self) -> String {
        format!("button: {}", self.label)
    }
}

struct Label(&'static str);

impl Draw for Label {
    fn draw(&self) -> String {
        format!("label: {}", self.0)
    }
}

struct Screen {
    components: Vec<Box<dyn Draw>>,
}

impl Screen {
    fn render(&self) -> Vec<String> {
        self.components.iter().map(|component| component.draw()).collect()
    }
}

fn main() {
    let screen = Screen {
        components: vec![
            Box::new(Button { label: "OK".into() }),
            Box::new(Label("Status")),
        ],
    };
    assert_eq!(
        screen.render(),
        vec![String::from("button: OK"), String::from("label: Status")]
    );
}
```

## Worked example: borrowed trait objects
```rust
trait Formatter {
    fn format(&self, value: i32) -> String;
}

struct Hex;
struct Binary;

impl Formatter for Hex {
    fn format(&self, value: i32) -> String {
        format!("{value:x}")
    }
}

impl Formatter for Binary {
    fn format(&self, value: i32) -> String {
        format!("{value:b}")
    }
}

fn render_all(formatters: &[&dyn Formatter], value: i32) -> Vec<String> {
    formatters.iter().map(|formatter| formatter.format(value)).collect()
}

fn main() {
    let hex = Hex;
    let binary = Binary;
    let formatters: [&dyn Formatter; 2] = [&hex, &binary];
    let output = render_all(&formatters, 10);
    assert_eq!(output, vec![String::from("a"), String::from("1010")]);
}
```

No allocation is needed here because the function only borrows existing values. Reach for `Box<dyn Trait>` when the collection or API must own the erased values, not merely because dynamic dispatch is involved.

## Common errors
```text
error[E0277]: the trait bound `String: Draw` is not satisfied
```

This appears when Rust tries to coerce `Box<String>` or `&String` into a trait object whose base trait `String` does not implement. Implement the trait, pass a different value, or use an enum if the value does not share the behavior.

```text
error[E0038]: the trait `Draw` is not dyn compatible
```

The trait cannot be turned into a vtable-shaped runtime interface. See [[dyn Compatibility (Object Safety)]] and either adjust the trait or use static dispatch.

## Best practice
- ✅ Use trait objects when you need a heterogeneous collection or an extension point whose implementors are not all known to your crate.
- ✅ Put only the methods needed at the dynamic boundary into the trait.
- ✅ Add auto-trait bounds such as `Send` and `Sync` to the trait object type when the object crosses threads.
- ✅ Prefer `&dyn Trait` for temporary polymorphic borrowing; use `Box<dyn Trait>` when ownership and type erasure are both needed.
- ✅ Write object lifetimes explicitly when storing borrowed implementors: `Box<dyn Handler + 'a>` communicates a different promise than `Box<dyn Handler + 'static>`.
- ✅ Prefer `Arc<dyn Trait + Send + Sync>` for shared plugin registries that are read from multiple threads.
- ✅ Keep construction and downcasting outside the main trait-object interface unless runtime type recovery is a real requirement.

## Pitfalls
- ⚠️ A trait object is not a place to store extra fields; store data in concrete types and expose behavior through the trait.
- ⚠️ Avoid using `dyn Trait` as a vague substitute for a well-modeled enum when the set of variants is closed.
- ⚠️ Check [[dyn Compatibility (Object Safety)]] before designing a public trait intended for `dyn` use.
- ⚠️ See [[Overusing Trait Objects]] when dynamic dispatch gives no real flexibility benefit.
- ⚠️ Do not assume `Box<dyn Trait>` is cloneable just because concrete implementors are cloneable; `Clone` itself is not dyn-compatible as a direct trait-object API.
- ⚠️ Avoid adding auto-trait bounds later to public aliases such as `type Handler = Box<dyn Trait>`; callers may already store non-`Send` implementors.

## See also
[[OOP & Trait Objects]] · [[dyn Compatibility (Object Safety)]] · [[Static vs Dynamic Dispatch]] · [[Dynamically Sized Types]] · [[Traits]] · [[Box]] · [[Composition over Inheritance]] · [[The State Pattern]]
· [[Overusing Trait Objects]] · [[Non-dyn-Compatible Traits as Trait Objects]] · [[Generics]] · [[Arc]]

## Sources
- The Rust Programming Language, ch. 18.2 "Using Trait Objects to Abstract over Shared Behavior" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
- The Rust Reference, "Trait object types" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/trait-object.html
- Rust standard library keyword docs, "`dyn`" — https://doc.rust-lang.org/std/keyword.dyn.html
