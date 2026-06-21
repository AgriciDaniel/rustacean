---
type: concept
title: "Procedural Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, procedural-macros, metaprogramming]
domain: "Macros"
difficulty: advanced
related: ["[[Derive Macros]]", "[[Attribute Macros]]", "[[Function-like Macros]]", "[[Macro Hygiene]]", "[[Unhygienic Procedural Macro Output]]", "[[Build Scripts (build.rs)]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/procedural-macros.html"]
rust_version: "edition 2024 / 1.85+"
---

# Procedural Macros

Procedural macros are compile-time Rust functions that consume a `proc_macro::TokenStream` and return generated Rust syntax as another `TokenStream`.

## What it is
Procedural macros are Rust's programmable macro system. Instead of matching token patterns like [[Declarative Macros]], they run Rust code during compilation and operate on token streams.

There are three flavors:

- [[Derive Macros]]: invoked by `#[derive(Name)]` on structs, enums, and unions.
- [[Attribute Macros]]: invoked as custom outer attributes such as `#[route(GET, "/")]`.
- [[Function-like Macros]]: invoked with macro-call syntax such as `sql!(SELECT 1)`.

Procedural macros must be defined in the root of a crate whose library target has `proc-macro = true`. They cannot be used from the same crate that defines them; a consumer crate imports and invokes them.

## How it works
The compiler passes tokens to the macro function. The function returns tokens that either replace the invocation or append generated items, depending on the macro flavor.

The stable interface is token streams, not compiler-internal AST nodes. In real macro crates, authors commonly use `syn` to parse tokens into syntax data structures and `quote` to produce output tokens, but those crates are ecosystem tools rather than language requirements.

Procedural macros run with the compiler's process resources. They can read files and environment variables, print to compiler output, panic, loop forever, or emit `compile_error!`. Treat them with the same trust model as [[Build Scripts (build.rs)]].

Because procedural macro output is unhygienic, generated code must use robust paths and collision-resistant names. See [[Unhygienic Procedural Macro Output]] for the main footgun.

The `proc_macro::TokenStream` API is deliberately token-based rather than a stable compiler AST. A token stream is cheap to clone and consists of token trees such as identifiers, punctuation, literals, and delimited groups. Parsing into `syn` data structures is a library choice, not a compiler requirement.

## Example
```rust
#[derive(Debug, Clone, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let a = Point { x: 3, y: 4 };
    let b = a.clone();

    assert_eq!(a, b);
    assert_eq!(format!("{a:?}"), "Point { x: 3, y: 4 }");
}
```

This example uses built-in derive macros from the language prelude. A custom procedural macro crate exposes the same kind of macro namespace entries, but its definition must live in a separate `proc-macro` crate.

## Implementation sketch
A function-like procedural macro has this public ABI shape in the root of its macro crate:

```rust
use proc_macro::TokenStream;

#[proc_macro]
pub fn passthrough(input: TokenStream) -> TokenStream {
    input
}
```

This snippet is the macro-crate side, not consumer-side code. In a real crate, `Cargo.toml` must contain `[lib] proc-macro = true`, and another crate must import and invoke `passthrough!(...)`.

## Common errors
The most common setup errors are:

```text
error: the `#[proc_macro]` attribute is only usable with crates of the `proc-macro` crate type
error: can't use a procedural macro from the same crate that defines it
```

Fix the first by setting `proc-macro = true` on the library target. Fix the second by adding an integration test, example crate, or separate consumer crate that depends on the macro crate.

## Best practice
- ✅ Use procedural macros when you need to parse nontrivial Rust syntax, inspect item structure, or generate trait impls from annotated items.
- ✅ Keep the public runtime API and the macro implementation in separate crates or re-export the macro from the runtime crate intentionally.
- ✅ Emit `compile_error!` or precise parse errors instead of panicking with vague messages.
- ✅ Use absolute paths in generated code and test under unusual caller imports.
- ✅ Keep macro expansion deterministic and avoid hidden filesystem or network dependencies unless the macro's contract explicitly requires them.
- ✅ Keep parsing, validation, and code generation in separate internal functions so diagnostics remain targeted and testable.
- ✅ Prefer `::core` paths for core language abstractions when generated code should work in `no_std` contexts.

## Pitfalls
- ⚠️ Procedural macros are harder to debug than normal code; prefer functions, traits, or [[Declarative Macros]] when they fit.
- ⚠️ A proc macro crate cannot use its own procedural macros internally.
- ⚠️ Panics become compiler errors, but endless loops can hang compilation.
- ⚠️ Treat third-party procedural macros as code that runs at build time with build-script-like security implications.
- ⚠️ Do not rely on network access, wall-clock time, or undeclared files unless those inputs are part of a documented, reproducible build contract.
- ⚠️ Do not generate names from raw user strings without sanitizing them into valid identifiers and considering collisions.

## See also
[[Macros]] · [[Derive Macros]] · [[Attribute Macros]] · [[Function-like Macros]] · [[Macro Hygiene]] · [[Unhygienic Procedural Macro Output]] · [[Build Scripts (build.rs)]] · [[Cargo.toml Manifest]]

## Sources
- The Rust Programming Language, ch. 20.5 "Procedural Macros for Generating Code from Attributes" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Procedural macros" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html
