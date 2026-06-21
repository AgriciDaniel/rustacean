---
type: concept
title: "Static vs Dynamic Dispatch"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, dispatch, generics, traits]
domain: "OOP & Trait Objects"
difficulty: intermediate
related: ["[[Trait Objects]]", "[[dyn Compatibility (Object Safety)]]", "[[Generics]]", "[[Trait Bounds]]", "[[Zero-Cost Abstractions]]", "[[Overusing Trait Objects]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/book/ch10-01-syntax.html", "https://doc.rust-lang.org/std/keyword.dyn.html"]
rust_version: "edition 2024 / 1.85+"
---

# Static vs Dynamic Dispatch

Static dispatch chooses the concrete method implementation at compile time, while dynamic dispatch chooses it at runtime through a trait object such as `&dyn Trait` or `Box<dyn Trait>`.

## What it is
Dispatch is how Rust decides which function body runs for a method call. With generics and `impl Trait`, Rust usually uses static dispatch: each concrete type gets a specialized version after monomorphization. With `dyn Trait`, Rust uses dynamic dispatch: the call goes through runtime metadata carried by the trait object pointer.

Neither form is universally better. Static dispatch is usually faster and more optimizable. Dynamic dispatch is more flexible at runtime and can reduce code size by avoiding duplicated monomorphized copies.

## How it works
Static dispatch requires the compiler to know the concrete type at the call site. This enables inlining and other optimizations, but a generic function used with many types may produce more generated code.

Dynamic dispatch erases the concrete type behind a trait object. The caller knows only the trait interface, so the compiler emits an indirect call. That indirect call has a small runtime cost and normally prevents inlining across the dynamic boundary, but it lets one collection hold multiple concrete implementors.

For API design, the choice changes the shape of the API. A generic `Screen<T: Draw>` stores one component type per screen. A `Screen` with `Vec<Box<dyn Draw>>` can store buttons, labels, and user-defined widgets together.

Monomorphization is the mechanism behind most static dispatch. The compiler substitutes each concrete type used with a generic function and type-checks one generic definition, then code generation can produce specialized machine code. That often enables inlining and constant propagation, but a widely used generic function can contribute to code size and compile time.

Dynamic dispatch moves that variation to runtime. The compiled caller has one call shape against `dyn Trait`, and the object pointer supplies the vtable for the concrete implementor. This can simplify public APIs and reduce repeated generated code, but the indirect call is less transparent to the optimizer.

## Example
```rust
trait Measure {
    fn measure(&self) -> usize;
}

impl Measure for String {
    fn measure(&self) -> usize {
        self.len()
    }
}

impl Measure for Vec<u8> {
    fn measure(&self) -> usize {
        self.len()
    }
}

fn static_dispatch<T: Measure>(value: &T) -> usize {
    value.measure()
}

fn dynamic_dispatch(value: &dyn Measure) -> usize {
    value.measure()
}

fn main() {
    let text = String::from("rust");
    let bytes = vec![1, 2, 3];

    assert_eq!(static_dispatch(&text), 4);
    assert_eq!(dynamic_dispatch(&bytes), 3);
}
```

## Worked example: same trait, different API shape
```rust
trait Encode {
    fn encode(&self, input: &str) -> String;
}

struct Uppercase;
struct Prefix(&'static str);

impl Encode for Uppercase {
    fn encode(&self, input: &str) -> String {
        input.to_uppercase()
    }
}

impl Encode for Prefix {
    fn encode(&self, input: &str) -> String {
        format!("{}{input}", self.0)
    }
}

fn encode_batch_static<E: Encode>(encoder: &E, inputs: &[&str]) -> Vec<String> {
    inputs.iter().map(|input| encoder.encode(input)).collect()
}

fn encode_pipeline(encoders: &[Box<dyn Encode>], input: &str) -> Vec<String> {
    encoders.iter().map(|encoder| encoder.encode(input)).collect()
}

fn main() {
    assert_eq!(encode_batch_static(&Uppercase, &["a", "b"]), ["A", "B"]);

    let encoders: Vec<Box<dyn Encode>> = vec![Box::new(Uppercase), Box::new(Prefix("#"))];
    assert_eq!(encode_pipeline(&encoders, "id"), ["ID", "#id"]);
}
```

The static function is ideal when one encoder processes many values. The dynamic version is ideal when many different encoders are stored together and applied through one runtime boundary.

## Common errors
```text
error[E0308]: mismatched types
```

This often appears when attempting `vec![Button, Label]` with two concrete types. Use an enum for a closed set, or box/borrow them as `dyn Trait` for an open heterogeneous collection.

```text
error[E0038]: the trait `Encode` is not dyn compatible
```

Static dispatch can use traits that dynamic dispatch cannot. If generic code compiles but `dyn Encode` does not, inspect the trait for generic methods, `Self` returns, associated constants, or `async fn`.

## Best practice
- ✅ Prefer static dispatch for homogeneous data, hot paths, and APIs where callers naturally keep concrete types.
- ✅ Use dynamic dispatch for heterogeneous collections, plugin points, or when hiding the concrete type is part of the design.
- ✅ Measure before optimizing away `dyn`; the cost is often irrelevant outside tight loops.
- ✅ Consider code size and compile time too; generics are not free when widely instantiated.
- ✅ Accept `impl Trait` in arguments when callers should pass any one concrete implementor and you do not need to name the type parameter.
- ✅ Accept `&dyn Trait` when the API boundary is intentionally runtime-polymorphic and does not need ownership.
- ✅ Use `Box<dyn Trait>` or `Arc<dyn Trait + Send + Sync>` when the boundary must own or share erased implementors.

## Pitfalls
- ⚠️ Do not put `Box<dyn Trait>` into a hot inner loop just to avoid writing a type parameter; see [[Overusing Trait Objects]].
- ⚠️ Do not expose unnecessary generic parameters in public APIs when a borrowed trait object would express the boundary more simply.
- ⚠️ Do not forget that `dyn Trait` requires [[dyn Compatibility (Object Safety)]].
- ⚠️ Do not assume static dispatch always produces smaller binaries; many concrete instantiations can duplicate code.
- ⚠️ Do not assume dynamic dispatch implies heap allocation; `&dyn Trait` is a borrowed fat pointer and can point to stack data.

## See also
[[OOP & Trait Objects]] · [[Trait Objects]] · [[dyn Compatibility (Object Safety)]] · [[Generics]] · [[Trait Bounds]] · [[Zero-Cost Abstractions]] · [[Accepting impl Trait vs Generics]] · [[Overusing Trait Objects]]
· [[Dynamically Sized Types]] · [[Enums]] · [[Box]] · [[Arc]]

## Sources
- The Rust Programming Language, ch. 18.2 "Performing Dynamic Dispatch" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
- The Rust Programming Language, ch. 10.1 "Generic Data Types" — [[the-book]],
  https://doc.rust-lang.org/book/ch10-01-syntax.html
- Rust standard library keyword docs, "`dyn`" — https://doc.rust-lang.org/std/keyword.dyn.html
