---
type: concept
title: "Macro Diagnostics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, diagnostics, compile-error, procedural-macros]
domain: "Macros"
difficulty: advanced
related: ["[[Procedural Macros]]", "[[syn and quote]]", "[[Testing Macros with trybuild]]", "[[Macro Hygiene]]", "[[Unhygienic Procedural Macro Output]]", "[[Derive Macros]]", "[[Attribute Macros]]"]
sources: ["[[the-reference]]", "Rust core docs compile_error", "docs.rs syn 2.0.118"]
source_urls: ["https://doc.rust-lang.org/reference/procedural-macros.html", "https://doc.rust-lang.org/core/macro.compile_error.html", "https://docs.rs/syn/latest/syn/struct.Error.html"]
rust_version: "edition 2024 / 1.85+"
---

# Macro Diagnostics

Macro diagnostics are the compile-time errors, spans, and messages a macro deliberately emits so callers understand invalid input without reading generated code.

## What it is
Rust macros fail during compilation, so their user experience is the compiler diagnostic.
For simple [[macro_rules!]] macros, diagnostics often come from unmatched arms, explicit fallback arms, or `compile_error!`.
For [[Procedural Macros]], diagnostics come from panics or from generated `compile_error!` tokens.

Good diagnostics name the unsupported input, point at the caller's relevant token, and explain the expected shape.
They avoid exposing internal parser details or producing distant errors in generated code.

The Rust Reference names two stable error-reporting mechanisms for procedural macros:
panic, and emitting a `compile_error!` invocation.
Panic is a last resort for macro bugs.
User-caused errors should become `compile_error!` with a useful span.

With `syn`, parser failures and semantic validation failures are commonly represented as `syn::Error`.
`syn::parse_macro_input!` converts parse failures automatically.
Later validation can return `syn::Result<T>` and use `syn::Error::into_compile_error`.

## How it works
Every procedural macro token has a `Span`.
Spans are opaque source-location handles used primarily for error reporting.
A diagnostic tied to a caller token is easier to fix than a message attached to the macro invocation as a whole.

For `macro_rules!`, the stable tool is `compile_error!` in a deliberately matched arm.
That is useful for catching unsupported syntax before the macro expands into confusing Rust.
For procedural macros, macro output may include `compile_error!("message")`; helper crates such as `syn` generate appropriately spanned invocations.

Diagnostics should be tested as part of the public API.
Changing a macro's accepted grammar or error messages can break users who rely on clear compile failures, especially for teaching-oriented or framework macros.

## Example
```rust
macro_rules! require_nonempty_literal {
    ("") => {
        compile_error!("expected a non-empty string literal")
    };
    ($value:literal) => {
        $value
    };
}

fn main() {
    let name = require_nonempty_literal!("Ferris");
    assert_eq!(name, "Ferris");
}
```

The failing arm is explicit and user-facing.
Calling `require_nonempty_literal!("")` reports the macro's intent instead of letting later code fail mysteriously.

## Procedural macro sketch
```rust
use proc_macro::TokenStream;
use syn::{parse_macro_input, DeriveInput, Error, Result};

#[proc_macro_derive(OnlyStructs)]
pub fn only_structs(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand(input)
        .unwrap_or_else(Error::into_compile_error)
        .into()
}

fn expand(input: DeriveInput) -> Result<proc_macro2::TokenStream> {
    match input.data {
        syn::Data::Struct(_) => Ok(proc_macro2::TokenStream::new()),
        _ => Err(Error::new_spanned(input.ident, "OnlyStructs supports structs only")),
    }
}
```

This sketch belongs in a proc-macro crate.
The public entry point stays small, and validation failures become `compile_error!` tokens instead of panics.

## Best practice
- ✅ Use `compile_error!` for caller mistakes, not `panic!`.
- ✅ Attach errors to the narrowest useful caller span.
- ✅ Return `syn::Result<proc_macro2::TokenStream>` from expansion helpers.
- ✅ Convert parse errors with `parse_macro_input!` and semantic errors with `Error::into_compile_error`.
- ✅ Accumulate independent errors with `syn::Error::combine` when reporting all of them helps the caller.
- ✅ Test compile-fail behavior with [[Testing Macros with trybuild]].
- ✅ Phrase messages in terms of the macro's public contract, not implementation internals.

## Pitfalls
- ⚠️ Panicking for invalid user input produces worse diagnostics and can hide the relevant span.
- ⚠️ Letting malformed generated Rust fail later often points users at code they never wrote.
- ⚠️ Emitting a bare `compile_error!` at call-site span can be too broad when a specific field or attribute is wrong.
- ⚠️ Overly clever parsers can accept invalid combinations and then produce unrelated type errors.
- ⚠️ Do not depend on unstable diagnostic APIs unless the macro explicitly requires nightly.
- ⚠️ Do not snapshot diagnostics without reviewing them; bad snapshots preserve bad messages.

## See also
[[Macros]] · [[Procedural Macros]] · [[syn and quote]] · [[Testing Macros with trybuild]] · [[Derive Macros]] · [[Attribute Macros]] · [[Function-like Macros]] · [[Macro Hygiene]] · [[Unhygienic Procedural Macro Output]] · [[Assertion Macros in Tests]]

## Sources
- The Rust Reference, "Procedural macros / errors" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html
- Rust core docs, `compile_error!`, https://doc.rust-lang.org/core/macro.compile_error.html
- docs.rs, `syn::Error`, latest verified 2026-06-21 as `syn` 2.0.118, https://docs.rs/syn/latest/syn/struct.Error.html
