---
type: moc
title: "Editions & Compiler"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, editions, compiler, moc]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Rust Editions]]", "[[Edition 2024]]", "[[The rustc Compiler]]", "[[Lints and Lint Levels]]", "[[Conditional Compilation (cfg)]]", "[[Target Triples]]"]
sources: ["[[edition-guide]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/edition-guide/", "https://doc.rust-lang.org/rustc/"]
rust_version: "edition 2024 / 1.85+"
---

# Editions & Compiler

This map covers Rust edition selection, Rust 2024 migration concerns, `rustc` invocation, lint configuration, cfg checking, compilation targets, and code generation flags.

## Concepts
- [[Rust Editions]] — edition compatibility model and crate-level opt-in behavior.
- [[Edition 2024]] — stabilized Rust 1.85 edition changes and migration hot spots.
- [[The rustc Compiler]] — compiler role, crate roots, and the main CLI surface.
- [[Lints and Lint Levels]] — configurable diagnostics, lint groups, and migration lints.
- [[Conditional Compilation (cfg)]] — compile-time selection by target, feature, and custom cfg.
- [[Target Triples]] — target identities, cross-compilation, and target-derived cfg values.
- [[Codegen and Optimization Flags]] — `-C` backend options for performance, debug info, panic, and linking.

## Patterns
- [[Migrating Editions]] — run compatibility fixes before changing `Cargo.toml`.
- [[Enforcing Expected cfgs]] — use `--check-cfg`, Cargo lint config, or build-script declarations.
- [[Inspecting rustc Configuration]] — print compiler, target, cfg, lint, and codegen state before guessing.

## Antipatterns
- [[Silencing Edition Migration Lints]] — hiding edition warnings instead of reviewing behavior.
- [[Unchecked cfg Names]] — allowing misspelled or stale cfg names to silently disable code.

## Example
```rust
fn main() {
    println!("compile with: rustc --edition=2024 main.rs");
}
```

## Best practice
- ✅ Start with [[Rust Editions]] and [[Edition 2024]] when deciding what an edition changes.
- ✅ Use [[Migrating Editions]] before changing `Cargo.toml` in an existing crate.
- ✅ Pair [[Conditional Compilation (cfg)]] with [[Enforcing Expected cfgs]] for custom cfgs.
- ✅ Use [[Inspecting rustc Configuration]] before tuning [[Codegen and Optimization Flags]].

## Pitfalls
- ⚠️ Treating edition migration as only a manifest edit; review lint-driven changes.
- ⚠️ Guessing target cfg values instead of inspecting the active [[Target Triples]] configuration.
- ⚠️ Hiding warnings that are meant to flag future-incompatible behavior.
- ⚠️ Applying compiler flags globally when a Cargo profile or manifest setting is the better home.

## See also
[[Cargo.toml Manifest]] · [[Cargo Workspaces]] · [[Feature Flags]] · [[Build Scripts (build.rs)]] · [[Profiles and Optimization Settings]] · [[MSRV Policy]] · [[Panic Unwinding and Abort]] · [[Integer Overflow]]

## Sources
- The Rust Edition Guide — [[edition-guide]],
  https://doc.rust-lang.org/edition-guide/
- The rustc book — [[rustc-book]],
  https://doc.rust-lang.org/rustc/
