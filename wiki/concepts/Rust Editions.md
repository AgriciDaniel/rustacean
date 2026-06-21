---
type: concept
title: "Rust Editions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, editions, compatibility, compiler]
domain: "Editions & Compiler"
difficulty: basic
related: ["[[Edition 2024]]", "[[Migrating Editions]]", "[[The rustc Compiler]]", "[[Lints and Lint Levels]]", "[[Cargo.toml Manifest]]", "[[MSRV Policy]]"]
sources: ["[[edition-guide]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/edition-guide/editions/index.html", "https://doc.rust-lang.org/rustc/command-line-arguments.html#--edition-specify-the-edition-to-use"]
rust_version: "edition 2024 / 1.85+"
---

# Rust Editions

Rust editions are opt-in language compatibility modes for crates; they let Rust evolve syntax and defaults without splitting the ecosystem.

## What it is
An edition is selected per crate, usually with the `edition` key in `Cargo.toml`.
The currently valid edition values are `2015`, `2018`, `2021`, and `2024`.
When Cargo creates a new package on a current stable toolchain, it chooses the newest stable edition.
When no edition is specified, Cargo preserves backwards compatibility by defaulting to Rust 2015.

Editions are not compiler versions.
Rust 1.85 can compile crates from older editions and from the 2024 edition.
The edition changes how source code is parsed and how edition-gated behavior is selected.
It does not create an isolated package ecosystem.

## How it works
Each crate chooses its own edition privately.
A Rust 2024 crate can depend on a Rust 2021 crate, and a Rust 2021 crate can depend on a Rust 2024 crate.
The compiler lowers all editions into the same internal representation, so edition differences are mostly source-level compatibility boundaries.

The compiler also exposes `--edition` for non-Cargo builds.
Cargo normally passes the right edition to `rustc` based on the manifest.
Use `cargo build --verbose` if you need to inspect the `rustc` invocation.

Edition changes are deliberately constrained.
They can reserve new keywords, change parsing rules, adjust prelude contents, and alter carefully chosen semantics.
They should not require the whole ecosystem to migrate at once.
The usual migration path is therefore lint-driven: the old edition compiler mode warns about source that will mean something different in the new edition, then `cargo fix --edition` applies the machine-applicable parts.

Edition is also not a substitute for [[MSRV Policy]].
A crate can set `edition = "2024"` only if its supported compiler is new enough to understand that edition, but raising MSRV and changing edition are separate maintenance decisions.
Dependencies are compiled with their own editions, so a workspace can migrate packages one at a time.

## Example
```rust
fn main() {
    let edition = "2024";
    let crate_name = "demo";
    println!("{crate_name} is written for Rust {edition}");
}
```

In a Cargo package, the matching manifest setting is:

```toml
[package]
name = "demo"
version = "0.1.0"
edition = "2024"
```

A custom build system must pass the edition explicitly because direct `rustc` defaults to Rust 2015:

```bash
rustc --edition=2024 src/main.rs
```

## Common errors
Forgetting the edition in direct compiler invocations usually looks like a parse error for edition-gated syntax or keywords:

```text
error: expected identifier, found keyword `gen`
```

Fix it by passing `--edition=2024` or by letting Cargo read `edition = "2024"` from `Cargo.toml`.
If the code must compile on older editions too, use a raw identifier such as `r#gen` or choose a non-keyword API name.

An invalid manifest value is caught before compilation:

```text
error: failed to parse manifest at `.../Cargo.toml`
```

Use one of the edition strings accepted by the current toolchain: `2015`, `2018`, `2021`, or `2024`.

## Best practice
- ✅ Treat edition changes as a source-compatibility migration, not as a dependency compatibility break.
- ✅ Set `edition = "2024"` explicitly for new crates that target Rust 1.85+.
- ✅ Use `cargo fix --edition` before changing the manifest edition in an existing crate; see [[Migrating Editions]].
- ✅ Keep edition policy separate from [[MSRV Policy]]: the edition says how code is parsed, while MSRV says which compiler version users need.
- ✅ When integrating with a custom build system, pass `--edition=2024` to [[The rustc Compiler]] for 2024 source.
- ✅ In workspaces, migrate leaf packages first when that reduces churn, but run tests at the workspace boundary before landing the edition bump.
- ✅ Keep generated Rust code and doctests in the migration checklist because `cargo fix --edition` does not rewrite every source of Rust text.

## Pitfalls
- ⚠️ Assuming editions split crates into incompatible worlds; they are designed to interoperate.
- ⚠️ Changing `Cargo.toml` first and only then asking why code fails; run migration lints first.
- ⚠️ Treating a new edition as a blanket modernization pass; avoid unrelated rewrites during edition migration.
- ⚠️ Hiding migration warnings with broad `allow` attributes; see [[Silencing Edition Migration Lints]].
- ⚠️ Treating `edition = "2024"` as proof that dependencies also use 2024; dependency crates keep their own manifests.
- ⚠️ Forgetting direct tools, code generators, snippets in docs, and CI scripts that invoke `rustc` without Cargo.

## See also
[[Edition 2024]] · [[Migrating Editions]] · [[The rustc Compiler]] · [[Lints and Lint Levels]] · [[Cargo.toml Manifest]] · [[Cargo Workspaces]] · [[MSRV Policy]] · [[Conditional Compilation (cfg)]] · [[Inspecting rustc Configuration]] · [[Silencing Edition Migration Lints]] · [[Editions & Compiler]]

## Sources
- The Rust Edition Guide, "What are Editions?" — [[edition-guide]],
  https://doc.rust-lang.org/edition-guide/editions/index.html
- The rustc book, "`--edition`: specify the edition to use" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/command-line-arguments.html#--edition-specify-the-edition-to-use
