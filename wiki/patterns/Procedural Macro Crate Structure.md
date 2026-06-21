---
type: pattern
title: "Procedural Macro Crate Structure"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, procedural-macros, cargo, crate-structure]
domain: "Macros"
difficulty: advanced
related: ["[[Procedural Macros]]", "[[syn and quote]]", "[[Macro Diagnostics]]", "[[Testing Macros with trybuild]]", "[[Derive Macros]]", "[[Attribute Macros]]", "[[Function-like Macros]]"]
sources: ["[[the-reference]]", "docs.rs syn 2.0.118", "docs.rs quote 1.0.45"]
source_urls: ["https://doc.rust-lang.org/reference/procedural-macros.html", "https://docs.rs/syn/latest/syn/", "https://docs.rs/quote/latest/quote/"]
rust_version: "edition 2024 / 1.85+"
---

# Procedural Macro Crate Structure

Put procedural macro entry points in a dedicated `proc-macro` crate, keep reusable runtime APIs in a normal crate, and test the macro from a separate caller crate or integration test.

## What it is
A procedural macro crate is a library target whose manifest sets `[lib] proc-macro = true`.
That crate exports macro namespace items such as `#[derive(MyTrait)]`, `#[my_attr]`, or `my_macro!(...)`.
The Rust Reference requires procedural macro functions to live in the root of the proc-macro crate.

This shape is different from normal library organization.
A proc-macro crate is compiled as a compiler plugin-like dynamic library and is run by rustc during compilation of downstream crates.
It cannot use its own procedural macros from inside the same crate.
Its public exports are the macro entry points, not arbitrary runtime helpers.

The usual production layout is therefore split:

- `my_crate` contains traits, runtime support types, and ordinary APIs.
- `my_crate_macros` contains `#[proc_macro]`, `#[proc_macro_derive]`, or `#[proc_macro_attribute]` entry points.
- `my_crate` may optionally re-export macros from `my_crate_macros` behind a feature.
- Integration tests or examples use the macro the way a downstream crate would.

This keeps [[Procedural Macros]] isolated from ordinary runtime code and makes the semver surface explicit.

## How it works
Cargo enables the crate type with:

```toml
[lib]
proc-macro = true
```

The proc-macro crate typically depends on `proc-macro2`, `syn`, and `quote`.
Use the unversioned docs.rs `/latest/` URLs to verify the latest compatible versions before pinning exact versions.
As of 2026-06-21, docs.rs shows `syn` 2.0.118 and `quote` 1.0.45.

Inside `src/lib.rs`, keep only thin public macro functions at the root.
Move parsing, validation, and generation into private modules.
That style gives each entry point a predictable shape:

1. Convert `proc_macro::TokenStream` into parsed data.
2. Validate input and build an internal model.
3. Generate `proc_macro2::TokenStream`.
4. Convert errors into `compile_error!` tokens.
5. Return `proc_macro::TokenStream` to rustc.

The runtime crate should not depend on the proc-macro crate unless it is only re-exporting macros as an optional convenience.
The proc-macro crate may depend on the runtime crate to generate paths such as `::my_crate::TraitName`, but that can create version-coupling if not designed deliberately.

## Example
```rust
pub trait Describe {
    fn describe(&self) -> String;
}

pub struct User {
    pub name: String,
}

impl Describe for User {
    fn describe(&self) -> String {
        format!("User({})", self.name)
    }
}

fn main() {
    let user = User {
        name: String::from("Ada"),
    };
    assert_eq!(user.describe(), "User(Ada)");
}
```

This is the ordinary runtime API that a derive macro would target.
The generated impl should call public paths such as `::my_crate::Describe` rather than private helpers in the macro crate.

## Layout sketch
```text
my_crate/
  Cargo.toml
  src/lib.rs              # trait, runtime helpers, optional macro re-export
  tests/derive.rs         # downstream-style integration test
my_crate_macros/
  Cargo.toml              # [lib] proc-macro = true
  src/lib.rs              # public macro entry points only
  src/derive_describe.rs  # parsing, validation, expansion
  tests/ui.rs             # trybuild harness
  tests/ui/*.rs           # pass and compile-fail cases
```

This sketch is not a language requirement, but it matches how complex macro crates stay reviewable.

## Best practice
- ✅ Keep the `#[proc_macro*]` functions in `src/lib.rs` small and rooted in the proc-macro crate.
- ✅ Put reusable traits and runtime helpers in a normal library crate, not in the proc-macro crate.
- ✅ Generate paths to public runtime APIs, usually with absolute paths such as `::my_crate::Trait`.
- ✅ Use internal modules for parsing, semantic validation, expansion, and [[Macro Diagnostics]].
- ✅ Exercise public macros from integration tests, examples, or [[Testing Macros with trybuild]] cases.
- ✅ Re-export macros from the runtime crate only when it improves the public API intentionally.
- ✅ Keep macro implementation dependencies out of runtime users' dependency graph when possible.

## Pitfalls
- ⚠️ A proc-macro crate cannot use its own procedural macros internally; test through another crate boundary.
- ⚠️ Do not make the macro crate the home of runtime traits that generated code needs to name.
- ⚠️ Do not expose private helper functions through generated output; callers cannot access them cross-crate.
- ⚠️ Do not let `src/lib.rs` become a large parser and code generator; diagnostics degrade quickly.
- ⚠️ Do not assume `syn`, `quote`, or `trybuild` latest versions stay fixed; verify docs.rs before updating pins.
- ⚠️ Do not forget that procedural macros run at build time with build-script-like trust concerns.

## See also
[[Macros]] · [[Procedural Macros]] · [[Derive Macros]] · [[Attribute Macros]] · [[Function-like Macros]] · [[syn and quote]] · [[Macro Diagnostics]] · [[Testing Macros with trybuild]] · [[Unhygienic Procedural Macro Output]] · [[Cargo.toml Manifest]]

## Sources
- The Rust Reference, "Procedural macros" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html
- docs.rs, `syn` crate docs, latest verified 2026-06-21 as 2.0.118, https://docs.rs/syn/latest/syn/
- docs.rs, `quote` crate docs, latest verified 2026-06-21 as 1.0.45, https://docs.rs/quote/latest/quote/
