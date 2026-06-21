---
type: pattern
title: "Deriving Traits on Structs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, derive, traits, debug]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Derive Macros]]", "[[Traits]]", "[[Methods]]", "[[Copy and Clone]]", "[[The Debug Trait]]", "[[The Default Trait]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-02-example-structs.html", "https://doc.rust-lang.org/book/appendix-03-derivable-traits.html", "https://doc.rust-lang.org/std/default/trait.Default.html"]
rust_version: "edition 2024 / 1.85+"
---

# Deriving Traits on Structs

Deriving traits asks Rust to generate standard trait implementations for a struct when every field supports the requested behavior.

## What it is
The `#[derive(...)]` attribute is placed before a struct definition.
For common traits, Rust can generate the implementation automatically instead of requiring hand-written code.

The Book introduces this with `Debug`, which enables developer-facing formatting through `{:?}`, `{:#?}`, and tools such as `dbg!`.
Other derivable traits include equality, ordering, copying, cloning, hashing, and defaults, subject to each trait's rules and field support.

## How it works
Derive is an attribute, not a runtime feature.
The compiler expands it into trait implementations during compilation.
For a derived implementation to exist, each relevant field must also implement the trait being derived.

`Debug` is not the same as `Display`.
`Debug` is intended for developers and is usually derivable.
`Display` is intended for end users and often needs a hand-written formatting decision.

For structs, derived behavior is field-based.
Derived `PartialEq` requires all fields to be equal.
Derived ordering compares fields in declaration order.
Derived `Clone` calls `clone` on every field, while derived `Copy` is only allowed when every field is `Copy` and the type has no custom `Drop`.
Derived `Default` calls `Default::default()` for each field, so it is appropriate only when those field defaults form a valid value.

## Example
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let rect = Rectangle {
        width: 30,
        height: 50,
    };
    let copy_for_comparison = rect.clone();

    println!("compact: {rect:?}");
    println!("pretty: {rect:#?}");
    println!("same = {}", rect == copy_for_comparison);
}
```

## Worked example
```rust
#[derive(Debug, Clone, PartialEq, Eq, Default)]
struct SearchOptions {
    query: String,
    limit: usize,
    include_archived: bool,
}

fn main() {
    let options = SearchOptions {
        query: String::from("rust"),
        limit: 20,
        ..SearchOptions::default()
    };

    let backup = options.clone();

    assert_eq!(options, backup);
    println!("{options:#?}");
}
```

This works because `String`, `usize`, and `bool` implement the requested traits.
The derived default is valid here only if an empty query and zero limit make sense for the type; otherwise, write a manual constructor or manual `Default`.

## Common errors
Deriving a trait fails when any field does not implement that trait:

```rust
#[derive(Debug)]
struct Job {
    callback: Box<dyn Fn()>,
}

fn main() {}
```

```console
error[E0277]: `(dyn Fn() + 'static)` doesn't implement `Debug`
```

Fix it by changing the field type, removing the derive, or writing a manual implementation that prints only the safe and meaningful fields.

## Best practice
- ✅ Derive `Debug` on domain structs early; it makes testing and troubleshooting much easier.
- ✅ Derive semantic traits only when the generated behavior matches the meaning of the type.
- ✅ Use `{:#?}` for larger structs when pretty debug output is easier to scan.
- ✅ Use `dbg!(&value)` when you want debug output without moving an owned value into `dbg!`.
- ✅ Derive `Default` for configuration structs only when each field's default combines into a valid configuration.
- ✅ Check declaration order before deriving `PartialOrd` or `Ord`; field order is the comparison order for structs.

## Pitfalls
- ⚠️ `println!("{value}")` requires `Display`, not `Debug`; use `"{value:?}"` or implement `Display`.
- ⚠️ `dbg!(value)` takes ownership of the expression and returns it; pass `&value` when you only want to inspect.
- ⚠️ Derived equality and ordering are field-based; do not derive them when the domain needs different semantics.
- ⚠️ Deriving `Clone` can make expensive duplication look cheap at call sites; prefer borrowing where ownership is not needed.
- ⚠️ Deriving `Copy` on an ID or handle type is convenient, but only do it when duplicate values are semantically harmless.

## See also
[[Structs]] · [[Named Field Structs]] · [[Derive Macros]] · [[Traits]] · [[Methods]] · [[Copy and Clone]] · [[The Debug Trait]] · [[The Display Trait]] · [[The Default Trait]] · [[Struct Update Syntax]]

## Sources
- The Rust Programming Language, ch. 5.2 "Adding Functionality with Derived Traits" — [[the-book]], https://doc.rust-lang.org/book/ch05-02-example-structs.html
- The Rust Programming Language, Appendix C "Derivable Traits" — [[the-book]], https://doc.rust-lang.org/book/appendix-03-derivable-traits.html
- The Rust standard library, `Default` — [[std]], https://doc.rust-lang.org/std/default/trait.Default.html
