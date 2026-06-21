---
type: antipattern
title: "Overusing Trait Objects"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, antipattern, trait-objects, performance]
domain: "OOP & Trait Objects"
difficulty: intermediate
related: ["[[Trait Objects]]", "[[Static vs Dynamic Dispatch]]", "[[Generics]]", "[[Enums]]", "[[Zero-Cost Abstractions]]", "[[Composition over Inheritance]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/std/keyword.dyn.html"]
rust_version: "edition 2024 / 1.85+"
---

# Overusing Trait Objects

Overusing trait objects means reaching for `Box<dyn Trait>` before you actually need runtime type erasure, paying indirection and losing type information without buying useful flexibility.

## The mistake
The mistake is treating `dyn Trait` as the standard way to abstract in Rust. It often appears as boxed trait objects in homogeneous collections, hot loops, or APIs where the caller and callee both know the concrete type.

This can make code harder to optimize, harder to reason about, and harder to extend with concrete-type-specific operations. It also introduces allocation when `Box<dyn Trait>` is used solely to erase a type.

Another symptom is a public API that returns `Box<dyn Trait>` even though the implementation always returns one concrete type. That prevents callers from using concrete methods, may force heap allocation, and turns a local implementation detail into a dynamic-dispatch contract.

## Why it happens
Developers coming from class-based OOP often map "interface" directly to "trait object." In Rust, a trait is not automatically a runtime interface. A trait bound such as `T: Draw` usually means static dispatch, while `dyn Draw` means dynamic dispatch.

The Book notes that generics are preferable for homogeneous collections because monomorphization can specialize calls at compile time. Trait objects shine when one value must hold multiple concrete implementors or when the concrete type is deliberately unknown until runtime.

The confusion is amplified because Rust traits serve both roles. `T: Cost` and `dyn Cost` use the same trait name but different dispatch models. A trait bound keeps the concrete type in the type system; a trait object erases it behind pointer metadata.

## Example
```rust
trait Cost {
    fn cost(&self) -> u32;
}

struct Item(u32);

impl Cost for Item {
    fn cost(&self) -> u32 {
        self.0
    }
}

fn total_static<T: Cost>(items: &[T]) -> u32 {
    items.iter().map(Cost::cost).sum()
}

fn total_dynamic(items: &[Box<dyn Cost>]) -> u32 {
    items.iter().map(|item| item.cost()).sum()
}

fn main() {
    let items = vec![Item(2), Item(3), Item(5)];
    assert_eq!(total_static(&items), 10);

    let erased: Vec<Box<dyn Cost>> = vec![Box::new(Item(2)), Box::new(Item(3))];
    assert_eq!(total_dynamic(&erased), 5);
}
```

The static version is the better fit for a `Vec<Item>`. The dynamic version is justified only when different concrete `Cost` implementors need to share one collection or boundary.

## Better alternatives
```rust
trait Command {
    fn run(&self) -> String;
}

struct Print(&'static str);

impl Command for Print {
    fn run(&self) -> String {
        self.0.to_owned()
    }
}

fn run_one(command: &impl Command) -> String {
    command.run()
}

fn run_many<C: Command>(commands: &[C]) -> Vec<String> {
    commands.iter().map(Command::run).collect()
}

fn run_pipeline(commands: &[Box<dyn Command>]) -> Vec<String> {
    commands.iter().map(|command| command.run()).collect()
}

fn main() {
    let command = Print("hello");
    assert_eq!(run_one(&command), "hello");
    assert_eq!(run_many(&[Print("a"), Print("b")]), ["a", "b"]);

    let mixed: Vec<Box<dyn Command>> = vec![Box::new(Print("dynamic"))];
    assert_eq!(run_pipeline(&mixed), ["dynamic"]);
}
```

Use the narrowest abstraction that matches the data shape: `impl Trait` for one borrowed value, generics for homogeneous slices, and trait objects for heterogeneous runtime collections.

## Common errors
```text
error[E0599]: no method named `specific_method` found for struct `Box<dyn Trait>`
```

After type erasure, only methods on the trait are available. Keep the concrete type, add the required behavior to the trait, or model the closed set with an enum and match on variants.

```text
error[E0277]: `dyn Handler` cannot be sent between threads safely
```

A bare `dyn Handler` does not imply `Send` or `Sync`. If crossing thread boundaries is part of the design, spell it in the object type up front: `Arc<dyn Handler + Send + Sync>`.

## Best practice
- ✅ Use generics, `impl Trait`, or concrete types when data is homogeneous.
- ✅ Use enums for a closed set of alternatives that your crate owns.
- ✅ Use [[Trait Objects]] for open-ended extension points and heterogeneous collections.
- ✅ Make the dispatch choice part of API design; see [[Static vs Dynamic Dispatch]].
- ✅ Prefer `&dyn Trait` over `Box<dyn Trait>` when the callee only needs a temporary borrow.
- ✅ Keep concrete return types when the caller benefits from the concrete API and the type is not part of an abstraction boundary.
- ✅ Use benchmarks or profiling before changing a clean generic design into dynamic dispatch for performance guesses.

## Pitfalls
- ⚠️ `Box<dyn Trait>` adds allocation when a borrow, generic parameter, or enum would work.
- ⚠️ Dynamic dispatch can block inlining and some optimization across the call boundary.
- ⚠️ Type erasure removes access to concrete-type methods unless you add them to the trait or use a different design.
- ⚠️ Adding `Send` or `Sync` later to public trait object types can be a breaking API change.
- ⚠️ Avoid `Vec<Box<dyn Trait>>` for a list that always contains one concrete type; it adds indirection without heterogeneity.
- ⚠️ Do not use downcasting as a routine escape hatch from an over-erased design.

## See also
[[OOP & Trait Objects]] · [[Trait Objects]] · [[Static vs Dynamic Dispatch]] · [[Generics]] · [[Enums]] · [[Zero-Cost Abstractions]] · [[Composition over Inheritance]] · [[Accepting impl Trait vs Generics]]
· [[dyn Compatibility (Object Safety)]] · [[Dynamically Sized Types]] · [[Box]] · [[Arc]]

## Sources
- The Rust Programming Language, ch. 18.2 "Using Trait Objects to Abstract over Shared Behavior" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
- Rust standard library keyword docs, "`dyn`" — https://doc.rust-lang.org/std/keyword.dyn.html
