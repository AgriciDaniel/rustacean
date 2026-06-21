---
type: concept
title: "Derive Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, derive, procedural-macros]
domain: "Macros"
difficulty: intermediate
related: ["[[Procedural Macros]]", "[[Attribute Macros]]", "[[Function-like Macros]]", "[[Macro Hygiene]]", "[[The Drop Trait]]", "[[Copy and Clone]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/procedural-macros.html#the-proc_macro_derive-attribute", "https://doc.rust-lang.org/reference/attributes/derive.html"]
rust_version: "edition 2024 / 1.85+"
---

# Derive Macros

Derive macros generate item-level code from a struct, enum, or union annotated with `#[derive(...)]`, most often trait implementations.

## What it is
The `derive` attribute invokes one or more derive macros. Built-in derives include `Clone`, `Copy`, `Debug`, `Default`, `Eq`, `Hash`, `Ord`, `PartialEq`, and `PartialOrd`. Custom derives are procedural macros defined with `#[proc_macro_derive(Name)]`.

A derive macro receives the token stream of the annotated item and emits zero or more items appended after that item in the same module or block. It does not replace the original struct, enum, or union.

Derive macros may declare helper attributes, such as `#[serde(rename = "...")]` in ecosystem macros. Helper attributes are inert attributes: they are available for the derive macro to read, but they do not transform code by themselves.

## How it works
A custom derive macro definition has this shape in a `proc-macro` crate:

`#[proc_macro_derive(Name, attributes(helper_attr))] pub fn name(input: TokenStream) -> TokenStream`

The function must be public, live in the crate root, use the Rust ABI, and take and return `proc_macro::TokenStream`. The derive name becomes a public macro namespace item.

All derive macros listed in all `derive` attributes on an item are invoked. During expansion, each derive contributes generated items, commonly `impl Trait for Type` blocks with bounds inferred or chosen by the macro author.

For built-in derives, generated implementations are structural and may add trait bounds required by the field-by-field expansion. A manual impl can sometimes express weaker or more domain-specific bounds. Custom derives have their own bound-generation policy, so their trait bounds are part of the macro's semver surface.

## Example
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct User {
    id: u64,
    name: String,
}

fn main() {
    let user = User {
        id: 1,
        name: String::from("Ada"),
    };
    let cloned = user.clone();

    assert_eq!(user, cloned);
    assert_eq!(
        format!("{user:?}"),
        "User { id: 1, name: \"Ada\" }"
    );
}
```

## Worked example: derived semantics are structural
```rust
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Version {
    major: u32,
    minor: u32,
    patch: u32,
}

fn main() {
    let stable = Version {
        major: 1,
        minor: 85,
        patch: 0,
    };
    let next = Version {
        major: 1,
        minor: 86,
        patch: 0,
    };

    assert!(stable < next);
    assert_eq!(format!("{stable:?}"), "Version { major: 1, minor: 85, patch: 0 }");
}
```

The derived ordering compares fields in declaration order. That is perfect for version triples, but it would be wrong for a type whose logical identity ignores a cache field, timestamp, or display-only label.

## Common errors
When a derived trait adds bounds that fields cannot satisfy, rustc reports an unsatisfied trait bound, for example:

```text
error[E0277]: the trait bound `Field: Clone` is not satisfied
```

Fix it by deriving or implementing the trait for the field type, removing the derive, or writing a manual implementation when the field-by-field derived semantics are not what you need.

## Best practice
- ✅ Derive standard traits when the field-by-field behavior is exactly what you want.
- ✅ Prefer a custom derive when users would otherwise write repetitive, structure-driven impls.
- ✅ Document any helper attributes and the generated trait bounds as part of the macro's public API.
- ✅ Keep the runtime trait crate usable without the derive crate when possible, or re-export intentionally.
- ✅ Use `compile_error!` or structured diagnostics for unsupported item shapes.
- ✅ Preserve generics, lifetimes, const generics, and where clauses when generating custom derive impls.
- ✅ Test derives on structs, enums, unit structs, tuple structs, generic types, and visibility combinations the macro claims to support.

## Pitfalls
- ⚠️ Do not derive semantics blindly: derived ordering, hashing, or equality is field-structural and may not match domain meaning.
- ⚠️ Helper attributes introduced by a derive are visible to other macros too; do not treat their presence as private information.
- ⚠️ Avoid relying on deprecated out-of-order helper attribute behavior; put helper attributes where the derive declares them.
- ⚠️ A derive macro can only be applied to structs, enums, and unions; use [[Attribute Macros]] for functions, impls, traits, or modules.
- ⚠️ Do not assume a derive replaces the annotated item; custom derive output is appended after the original item.
- ⚠️ Do not expose undocumented helper attributes as accidental public API; downstream users will start depending on them.

## See also
[[Macros]] · [[Procedural Macros]] · [[Attribute Macros]] · [[Function-like Macros]] · [[Macro Hygiene]] · [[Unhygienic Procedural Macro Output]] · [[Copy and Clone]] · [[The Error Trait]]

## Sources
- The Rust Programming Language, ch. 20.5 "Custom derive Macros" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "`proc_macro_derive` attribute" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html#the-proc_macro_derive-attribute
- The Rust Reference, "`derive` attribute" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/derive.html
