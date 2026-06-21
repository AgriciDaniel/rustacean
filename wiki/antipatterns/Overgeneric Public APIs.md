---
type: antipattern
title: "Overgeneric Public APIs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, generics, api-design, antipattern]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Generics]]", "[[Trait Bounds]]", "[[Static Dispatch with Generics]]", "[[Traits]]", "[[Dynamically Sized Types]]", "[[Unnecessary Bounds on Data Types]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html#using-traits-as-parameters", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html"]
rust_version: "edition 2024 / 1.85+"
---

# Overgeneric Public APIs

Overgeneric public APIs expose type parameters and bounds where a concrete type or trait object would be simpler, smaller, and easier to use.

## The mistake
Generics are powerful, but they are not free API seasoning.
Every public type parameter becomes part of the caller-visible contract.
Every monomorphized use may add compile-time and code-size cost.
Sometimes `fn log(message: &str)` is better than `fn log<S: AsRef<str>>(message: S)`.
Sometimes `&dyn Write` is better than another generic parameter when performance is irrelevant and heterogeneity is useful.

## Why it happens
Rust makes generic abstractions feel natural because they are checked statically and often optimize well.
That can lead API authors to generalize before there is a demonstrated need.
A public generic parameter asks every user and every error message to carry the abstraction.
The right boundary depends on the workflow: hot homogeneous code favors [[Static Dispatch with Generics]], while plugin-like or cold code may favor dynamic dispatch.
The simplest correct signature is usually the most durable one.
Generics are also viral in public APIs: callers may need turbofish annotations, extra bounds in their own functions, or longer error messages.
`impl Trait` in argument position still creates a generic function, so it has the same monomorphization tradeoff as a named type parameter.
Concrete borrowed parameters often compose better at API edges because Rust already coerces `String` to `&str`, `Vec<T>` to `&[T]`, and `PathBuf` to `&Path`.
Use generic input conversion traits when they remove real caller friction, not as a default style.

## Example
```rust
use std::fmt::Display;

fn render_line(value: &dyn Display) -> String {
    format!("value={value}")
}

fn render_hot<T: Display>(values: &[T]) -> Vec<String> {
    values.iter().map(|v| format!("value={v}")).collect()
}

fn main() {
    assert_eq!(render_line(&42), "value=42");
    assert_eq!(render_hot(&[1, 2]), vec!["value=1", "value=2"]);
}
```

## Common errors
Overgeneralizing can produce inference failures such as:

```text
error[E0283]: type annotations needed
```

This often happens when a public function accepts `impl Into<T>` or several generic conversion traits and the caller's literal could become many types.
Prefer `&str`, `&Path`, `&[u8]`, or another concrete borrowed input when one representation is the real API boundary.
The opposite error is using `Box<dyn Trait>` in a hot homogeneous path and then losing inlining and allocation-free composition.
Choose the dispatch boundary based on the caller workflow and measured cost, not on a blanket preference for either generics or trait objects.

## Best practice
- ✅ Use concrete borrowed types such as `&str`, `&Path`, and `&[T]` when callers already naturally have them.
- ✅ Use generics when type preservation, inlining, or caller-chosen concrete types matter.
- ✅ Use trait objects for heterogeneous collections, plugin registries, and cold abstraction boundaries.
- ✅ Keep public bounds minimal and semantically meaningful.
- ✅ Revisit generic APIs when compile times, binary size, or diagnostics become painful.

## Pitfalls
- ⚠️ `impl AsRef<str>` everywhere can make simple APIs harder to read without practical caller benefit.
- ⚠️ `Box<dyn Trait>` everywhere can be the opposite mistake in hot homogeneous paths.
- ⚠️ Returning `impl Trait` hides a concrete type but still commits the function body to one concrete return type.
- ⚠️ Overgeneric APIs combine badly with [[Unnecessary Bounds on Data Types]].

## See also
[[Generics]] · [[Trait Bounds]] · [[Static Dispatch with Generics]] · [[Traits]] · [[Dynamically Sized Types]] · [[Zero-Cost Abstractions]] · [[Unnecessary Bounds on Data Types]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.2 "Using Traits as Parameters" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html#using-traits-as-parameters
- The Rust Programming Language, ch. 18.2 "Using Trait Objects to Abstract over Shared Behavior" — [[the-book]], https://doc.rust-lang.org/book/ch18-02-trait-objects.html
