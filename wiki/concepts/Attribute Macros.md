---
type: concept
title: "Attribute Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, attributes, procedural-macros]
domain: "Macros"
difficulty: advanced
related: ["[[Procedural Macros]]", "[[Derive Macros]]", "[[Function-like Macros]]", "[[Macro Hygiene]]", "[[Unhygienic Procedural Macro Output]]", "[[Documentation Comments]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/procedural-macros.html#the-proc_macro_attribute-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Attribute Macros

Attribute macros are procedural macros invoked as custom outer attributes that receive both the attribute input and the item they annotate.

## What it is
An attribute macro looks like `#[custom(...)]`, `#[custom]`, or `#[custom { ... }]` on an item. Frameworks often use this shape for routes, tests, embedded entry points, tracing instrumentation, and code generation around functions or modules.

Unlike [[Derive Macros]], attribute macros can be used on more kinds of items: items, items in extern blocks, inherent and trait implementations, and trait definitions. Unlike inert attributes, they are active: they transform the annotated item by replacing it with the macro's returned tokens.

An attribute macro is defined in a `proc-macro` crate with `#[proc_macro_attribute]`.

## How it works
The macro function has this shape:

`pub fn name(attr: TokenStream, item: TokenStream) -> TokenStream`

The first token stream is the contents after the attribute name, not including the outer delimiters. For `#[route(GET, "/")]`, that stream is `GET, "/"`. For `#[route]`, it is empty.

The second token stream is the annotated item, including its other attributes. The returned token stream replaces that item with zero or more items. That makes attribute macros powerful and risky: they can preserve the item, wrap it, add items around it, or remove it entirely.

Expansion order matters. Active attributes such as `cfg`, `cfg_attr`, and procedural attribute macros participate in attribute processing, while most other attributes are inert metadata. If an attribute macro preserves an item, it must decide which inert attributes to keep, consume, or reject.

## Example
```rust
#[must_use]
fn build_message(name: &str) -> String {
    format!("hello, {name}")
}

fn main() {
    let message = build_message("Ada");
    assert_eq!(message, "hello, Ada");
}
```

This is a minimal compilable example of outer-attribute syntax on an item. A user-defined attribute macro uses the same surface position, but its implementation must live in a separate `proc-macro` crate.

## Edge cases
Attribute macros should be designed around the exact item shapes they support:

- Functions may have `async`, `const`, `unsafe`, `extern`, generics, lifetimes, where clauses, and visibility.
- Modules may be inline (`mod m { ... }`) or file-backed (`mod m;`), which gives the macro different token content.
- Attributes may be stacked, so the item stream can contain doc comments, `#[cfg]`, lint attributes, and other tool attributes.
- Trait and impl items may carry generic parameters and associated items that must not be dropped during transformation.

If the macro only supports a subset, reject unsupported shapes early with a clear `compile_error!` instead of emitting malformed Rust.

## Common errors
The setup diagnostic mirrors other procedural macros:

```text
error: the `#[proc_macro_attribute]` attribute is only usable with crates of the `proc-macro` crate type
```

At the call site, a poorly written attribute macro often produces confusing errors about missing generics, private items, or duplicate names. Those are usually signs that the macro failed to preserve the annotated item faithfully or generated caller-visible helper names without collision control.

## Best practice
- ✅ Preserve caller attributes and visibility intentionally when transforming an item.
- ✅ Make the attribute input grammar small and documented; parse errors should point at the bad token.
- ✅ Return the original item unchanged when the macro is meant to augment rather than replace it.
- ✅ Use absolute paths and collision-resistant helper names in generated code.
- ✅ Test attribute stacking with other attributes, because the annotated item stream includes neighboring attributes.
- ✅ Treat doc comments as attributes that must be preserved unless the macro explicitly consumes documentation.
- ✅ Keep generated wrapper behavior visible in docs or examples; attribute macros can otherwise hide important control flow.

## Pitfalls
- ⚠️ Do not silently drop doc comments, cfg attributes, visibility, generics, or where clauses from the annotated item.
- ⚠️ Do not assume `attr` includes delimiter tokens; the compiler passes only the tokens inside the attribute delimiters.
- ⚠️ Do not make hidden runtime behavior surprising; attribute macros can obscure control flow and generated items.
- ⚠️ Generated unqualified names are subject to caller scope; see [[Unhygienic Procedural Macro Output]].
- ⚠️ Do not leave private inert helper attributes in the returned item if rustc or downstream tools will reject or warn about them.
- ⚠️ Do not assume an attribute macro is equivalent to `derive`; it replaces the item, while derive appends generated items after it.

## See also
[[Macros]] · [[Procedural Macros]] · [[Derive Macros]] · [[Function-like Macros]] · [[Macro Hygiene]] · [[Unhygienic Procedural Macro Output]] · [[Documentation Comments]] · [[Conditional Compilation (cfg)]]

## Sources
- The Rust Programming Language, ch. 20.5 "Attribute-like Macros" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "`proc_macro_attribute` attribute" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html#the-proc_macro_attribute-attribute
