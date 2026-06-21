---
type: concept
title: "syn and quote"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, procedural-macros, syn, quote]
domain: "Macros"
difficulty: advanced
related: ["[[Procedural Macros]]", "[[Procedural Macro Crate Structure]]", "[[Macro Diagnostics]]", "[[Testing Macros with trybuild]]", "[[Derive Macros]]", "[[Attribute Macros]]", "[[Unhygienic Procedural Macro Output]]"]
sources: ["[[the-reference]]", "docs.rs syn 2.0.118", "docs.rs quote 1.0.45"]
source_urls: ["https://doc.rust-lang.org/reference/procedural-macros.html", "https://docs.rs/syn/latest/syn/", "https://docs.rs/quote/latest/quote/", "https://docs.rs/quote/latest/quote/macro.quote.html"]
rust_version: "edition 2024 / 1.85+"
---

# syn and quote

`syn` parses Rust token streams into structured syntax, and `quote` turns syntax-shaped Rust fragments back into token streams for procedural macro output.

## What it is
`syn` and `quote` are ecosystem crates, not language features.
They are the standard practical toolkit for writing nontrivial [[Procedural Macros]] on stable Rust.

`syn` provides Rust syntax tree data structures and parsing APIs.
For example, a derive macro commonly parses input as `syn::DeriveInput`, while an attribute macro may parse an annotated function as `syn::ItemFn`.
The crate is feature-gated so macro authors can enable only the syntax categories they need.

`quote` provides the `quote!` macro and related traits for producing tokens.
The quoted body looks like Rust code, but it is data that becomes a `proc_macro2::TokenStream`.
Interpolation with `#name` inserts identifiers, syntax nodes, or token streams that implement `quote::ToTokens`.

Together they provide the parse-transform-print loop used by many [[Derive Macros]], [[Attribute Macros]], and [[Function-like Macros]].

## How it works
Rust exposes procedural macros through `proc_macro::TokenStream`.
Most helper crates use `proc_macro2::TokenStream` internally because it is available outside proc-macro crates and works in unit tests.
Entry points convert at the boundary:

- parse `proc_macro::TokenStream` with `syn::parse_macro_input!` or `syn::parse`.
- validate the parsed syntax and collect errors with `syn::Error`.
- generate `proc_macro2::TokenStream` with `quote!` or `quote_spanned!`.
- convert generated tokens with `.into()` for the final `proc_macro::TokenStream`.

Use `syn` when the macro needs Rust-aware parsing.
Use raw token manipulation only for very small token shuffles where a syntax tree would be unnecessary.
Use `quote` when the output is mostly Rust-shaped code with interpolated pieces.
For mechanical token construction, direct `proc_macro2` building can sometimes be clearer.

As of 2026-06-21, docs.rs shows `syn` 2.0.118 and `quote` 1.0.45.
Verify the docs.rs latest pages before updating dependency versions because macro ecosystem crates release independently from Rust.

## Example
```rust
use quote::{format_ident, quote};

fn main() {
    let ident = format_ident!("Generated{}", 1);
    let tokens = quote! {
        struct #ident {
            value: u32,
        }
    };

    let text = tokens.to_string();
    assert!(text.contains("Generated1"));
    assert!(text.contains("value"));
}
```

This example is ordinary Rust code with the `quote` crate as a dependency.
It demonstrates that `quote!` builds tokens, not a string API, even though `to_string()` is useful for tests and debugging.

## Derive macro sketch
```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = input.ident;

    quote! {
        impl ::my_crate::Describe for #name {
            fn describe(&self) -> ::std::string::String {
                ::std::string::String::from(stringify!(#name))
            }
        }
    }
    .into()
}
```

This sketch belongs in a `proc-macro` crate and depends on the runtime crate exposing `::my_crate::Describe`.
Real derives also preserve generics and where clauses.

## Best practice
- ✅ Use `syn::parse_macro_input!` at public macro entry points for parser errors that become `compile_error!`.
- ✅ Keep `proc_macro2::TokenStream` inside expansion helpers so they can be unit-tested outside rustc.
- ✅ Use `quote_spanned!` or spanned `syn::Error` when generated errors should point at caller input.
- ✅ Enable only needed `syn` features such as `derive`, `full`, `parsing`, or `printing`.
- ✅ Preserve generics, lifetimes, const generics, visibility, and where clauses from parsed syntax.
- ✅ Treat generated paths as caller-context code; use absolute paths to avoid [[Unhygienic Procedural Macro Output]].
- ✅ Re-check docs.rs latest versions before changing dependency pins in macro crates.

## Pitfalls
- ⚠️ Do not parse Rust syntax with ad hoc strings when `syn` has the right syntax node.
- ⚠️ Do not use `quote!` output strings as a stable formatting contract; token display is for debugging.
- ⚠️ Do not forget to interpolate repetitions with the correct `#(...)*` or `#(...),*` form.
- ⚠️ Do not generate unqualified `Option`, `Result`, or `Vec` paths and hope the caller's prelude is normal.
- ⚠️ Do not panic on unsupported input when `syn::Error::into_compile_error` can report a targeted diagnostic.
- ⚠️ Do not enable `syn = { features = ["full"] }` by habit if the macro only needs derive input.

## See also
[[Macros]] · [[Procedural Macros]] · [[Procedural Macro Crate Structure]] · [[Macro Diagnostics]] · [[Testing Macros with trybuild]] · [[Derive Macros]] · [[Attribute Macros]] · [[Function-like Macros]] · [[Unhygienic Procedural Macro Output]] · [[Cargo.toml Manifest]]

## Sources
- The Rust Reference, "Procedural macros" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html
- docs.rs, `syn` crate docs, latest verified 2026-06-21 as 2.0.118, https://docs.rs/syn/latest/syn/
- docs.rs, `quote` crate docs and `quote!` macro, latest verified 2026-06-21 as 1.0.45, https://docs.rs/quote/latest/quote/
