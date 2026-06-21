---
type: pattern
title: "Migrating Editions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, editions, migration, cargo-fix]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Rust Editions]]", "[[Edition 2024]]", "[[Lints and Lint Levels]]", "[[Conditional Compilation (cfg)]]", "[[Cargo Workspaces]]", "[[Silencing Edition Migration Lints]]"]
sources: ["[[edition-guide]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html", "https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html"]
rust_version: "edition 2024 / 1.85+"
---

# Migrating Editions

Migrate a Rust crate by applying compatibility lints with `cargo fix --edition` before changing `Cargo.toml`, then test on the new edition and review any semantic hot spots manually.

## What it is
Edition migration is the workflow for moving an existing crate to a newer Rust edition.
It is intentionally incremental.
The migration tool rewrites code so it stays compatible with the current edition and the next edition where possible.

For Rust 2024, the key lint group is `rust-2024-compatibility`.
Cargo enables the relevant lints during `cargo fix --edition`.

## How it works
The basic order is:
run `cargo update`, run `cargo fix --edition`, edit `Cargo.toml`, run `cargo build` or `cargo test`, then run `cargo fmt`.
Large workspaces can migrate one package at a time because edition is package-local.

`cargo fix --edition` runs checks, applies machine-applicable suggestions, and reruns checks.
It may need multiple passes.
It only sees one configuration at a time, so feature-gated and target-gated code may need separate runs with `--all-features`, `--features`, or `--target`.

Some areas require manual work: macros, generated code, doctests, unsafe audits, and cases where lints report a problem but cannot preserve semantics automatically.
For Rust 2024, also plan for semantic review of RPIT lifetime capture, `if let` and tail-expression temporary scopes, match ergonomics reservations, unsafe extern blocks, unsafe attributes, `unsafe_op_in_unsafe_fn`, `static mut` references, the `gen` keyword, macro fragment changes, and prelude additions.
The migration tool can preserve older behavior for many cases, but it cannot decide whether older behavior is still the right behavior.

## Example
```rust
fn r#gen() -> &'static str {
    "compatible with the 2024 keyword reservation"
}

fn main() {
    println!("{}", r#gen());
}
```

Typical commands:

```bash
cargo update
cargo fix --edition
cargo test
cargo fmt
```

A more realistic workspace pass checks features and a cross target:

```bash
cargo fix --edition --workspace --all-features
cargo fix --edition --package cli --target x86_64-unknown-linux-musl
cargo test --workspace --all-features
cargo test --doc --workspace
```

Only after those passes are reviewed should you edit manifests to `edition = "2024"`.
Then rerun tests on the new edition.

## Common errors
Running the migration after editing the manifest can produce hard errors instead of compatibility suggestions:

```text
error: extern blocks must be unsafe
```

Restore the old edition, run `cargo fix --edition`, review the diff, then reapply `edition = "2024"`.

Generated code and doctests may still fail because automatic migration does not rewrite every Rust source:

```text
error: expected identifier, found reserved keyword `gen`
```

Fix the generator, proc macro, or doctest source so it emits edition-compatible Rust.
Do not patch only the generated file if it will be overwritten on the next build.

Feature-gated code can stay unmigrated if it was not compiled:

```text
warning: `impl Trait` will capture more lifetimes than possibly intended in edition 2024
```

Rerun with `--all-features`, important `--features ...` sets, and relevant `--target ...` values.

## Best practice
- ✅ Commit dependency updates separately before applying edition rewrites.
- ✅ Run `cargo fix --edition --all-features` when feature-gated code exists.
- ✅ Run target-specific migrations for important `#[cfg(target_...)]` paths.
- ✅ Review macros, doctests, build-script generated code, and unsafe changes by hand.
- ✅ After changing `edition = "2024"`, run tests and consider a plain `cargo fix` for fresh warnings.
- ✅ Review `if let` to `match` rewrites specifically for lock guards, `RefCell` borrows, and other types with meaningful `Drop`.
- ✅ Keep a checklist of cfg combinations that matter to users, then migrate those combinations explicitly.
- ✅ Land the edition bump separately from style cleanup so regressions can be traced to migration decisions.

## Pitfalls
- ⚠️ Editing `edition = "2024"` first and treating the resulting errors as the migration plan.
- ⚠️ Running migration only for the host target when the crate supports multiple platforms.
- ⚠️ Trusting automatic unsafe rewrites without checking safety requirements.
- ⚠️ Suppressing compatibility lints to speed up the migration; see [[Silencing Edition Migration Lints]].
- ⚠️ Assuming `cargo fix --edition` rewrites proc macro output, generated source, or markdown code blocks.
- ⚠️ Migrating all workspace packages in one huge diff when package-local migration would make review clearer.

## See also
[[Rust Editions]] · [[Edition 2024]] · [[Lints and Lint Levels]] · [[Conditional Compilation (cfg)]] · [[Cargo Workspaces]] · [[Feature Flags]] · [[Silencing Edition Migration Lints]] · [[Unchecked cfg Names]] · [[The rustc Compiler]] · [[Editions & Compiler]]

## Sources
- The Rust Edition Guide, "Transitioning an existing project to a new edition" — [[edition-guide]],
  https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
- The Rust Edition Guide, "Advanced migration strategies" — [[edition-guide]],
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
