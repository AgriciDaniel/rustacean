---
type: pattern
title: "Static Dispatch with Generics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, generics, traits, dispatch]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Generics]]", "[[Trait Bounds]]", "[[Traits]]", "[[Overgeneric Public APIs]]", "[[Dynamically Sized Types]]", "[[Zero-Cost Abstractions]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html#using-traits-as-parameters", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html"]
rust_version: "edition 2024 / 1.85+"
---

# Static Dispatch with Generics

Use generic parameters and trait bounds when callers provide one concrete type and you want compile-time dispatch, inlining, and type-specific optimization.

## What it is
Static dispatch means the compiler knows the concrete type being called at compile time.
In Rust, generic functions with trait bounds are the usual static-dispatch tool.
The compiler can monomorphize the generic function for concrete types and optimize through the trait calls.
This is the natural choice for homogeneous collections, hot loops, and APIs where the concrete type is chosen by the caller.
The contrast is dynamic dispatch through `dyn Trait`, which chooses the implementation through a vtable at runtime.

## How it works
Write a named generic parameter such as `T: Trait` or use argument-position `impl Trait`.
Inside the function, call only methods guaranteed by the bound.
Each concrete instantiation gets checked independently.
Use named generic parameters when multiple arguments must be the same type.
Use `impl Trait` when parameters are independent and the signature should stay compact.
Use `dyn Trait` instead when values of different concrete types must live in one collection or when code size matters more than inlining.
Static dispatch lets LLVM see the concrete callee after monomorphization, which can enable inlining and constant propagation.
The tradeoff is that each concrete instantiation may produce separate machine code.
For library APIs, static dispatch also pushes more type information into error messages and public signatures.
For internal hot paths, that explicitness is often worth it.

## Example
```rust
trait Score {
    fn score(&self) -> i32;
}

struct User(i32);

impl Score for User {
    fn score(&self) -> i32 {
        self.0
    }
}

fn total<T: Score>(items: &[T]) -> i32 {
    items.iter().map(Score::score).sum()
}

fn main() {
    let users = [User(3), User(5), User(8)];
    assert_eq!(total(&users), 16);
}
```

## Common errors
Two `impl Trait` parameters do not mean "same type":

```rust
fn pair(left: impl Score, right: impl Score) {
    let _ = left.score() + right.score();
}
```

Use `fn pair<T: Score>(left: T, right: T)` when the concrete type must match.
Returning different concrete iterator adapters behind `impl Iterator` produces `error[E0308]: if and else have incompatible types`.
Use the same adapter shape, an enum, or `Box<dyn Iterator<Item = T>>`.
If a generic function causes code-size growth in many call sites, measure whether a `dyn Trait` boundary is a better cold-path API.

## Best practice
- ✅ Prefer static dispatch for performance-sensitive generic code and homogeneous data.
- ✅ Use `impl Trait` in argument position for one-off simple bounds.
- ✅ Use named `T` when relationships between parameters matter.
- ✅ Keep bounds minimal so callers are not forced to implement unrelated traits.
- ✅ Consider `&dyn Trait` or `Box<dyn Trait>` when you need heterogeneity or want to reduce monomorphization.

## Pitfalls
- ⚠️ Static dispatch is not always smaller; many concrete instantiations can increase binary size.
- ⚠️ `impl Trait` for two parameters allows two different concrete types; use `T` if they must match.
- ⚠️ Public generic APIs expose more type detail to callers than a simple trait object parameter.
- ⚠️ Returning `impl Trait` still means one hidden concrete type per function, not any implementor.

## See also
[[Generics]] · [[Trait Bounds]] · [[Traits]] · [[Overgeneric Public APIs]] · [[Dynamically Sized Types]] · [[Zero-Cost Abstractions]] · [[The Iterator Trait]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.2 "Using Traits as Parameters" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html#using-traits-as-parameters
- The Rust Programming Language, ch. 18.2 "Using Trait Objects to Abstract over Shared Behavior" — [[the-book]], https://doc.rust-lang.org/book/ch18-02-trait-objects.html
