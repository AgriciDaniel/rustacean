---
type: pattern
title: "Workspace Dependency Inheritance"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, workspace, dependencies, manifests]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo Workspaces]]", "[[Cargo.toml Manifest]]", "[[Dependencies and Version Requirements]]", "[[Feature Resolver]]", "[[Cargo.lock]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/workspaces.html#the-dependencies-table", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#inheriting-a-dependency-from-a-workspace"]
rust_version: "edition 2024 / 1.85+"
---

# Workspace Dependency Inheritance

Workspace dependency inheritance centralizes shared dependency declarations in `[workspace.dependencies]` and lets member crates opt in with `workspace = true`, reducing version drift while keeping per-member feature choices explicit.

## What it is
In a Cargo workspace, the root manifest can define shared dependency specifications under `[workspace.dependencies]`.
Member packages then inherit those dependencies in `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, or target-specific dependency tables.
This is a pattern for keeping versions, registry choices, git sources, path sources, and default feature policy aligned across many crates.
It is not automatic.
Each member still chooses which inherited dependency it actually uses.

## How it works
The workspace root defines shared dependencies:

```toml
[workspace]
members = ["crates/api", "crates/cli"]
resolver = "3"

[workspace.dependencies]
cc = "1.0.73"
rand = "0.8.5"
regex = { version = "1.6.0", default-features = false, features = ["std"] }
```

A member inherits a dependency with `workspace = true`:

```toml
[package]
name = "api"
version = "0.2.0"
edition = "2024"

[dependencies]
regex = { workspace = true, features = ["unicode"] }

[build-dependencies]
cc.workspace = true

[dev-dependencies]
rand.workspace = true
```

The inherited dependency uses the definition from `[workspace.dependencies]`.
The member may add `features`, and those features are additive with the workspace-level features.
The member may add `optional = true`.
Other dependency keys, such as `version`, `default-features`, `path`, or `registry`, are not allowed on the inherited member entry because those belong in the workspace definition.
The workspace-level dependency itself cannot be declared `optional`.

This distinction is useful.
The workspace says "this is the version and source policy for `regex`."
The member says "this crate uses `regex`, and it also needs the `unicode` feature."
Cargo still resolves one dependency graph and one workspace `Cargo.lock`.
Feature unification still follows the [[Feature Resolver]] rules.

## Example
```rust
fn normalize_name(input: &str) -> String {
    input
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
        .to_ascii_lowercase()
}

fn main() {
    assert_eq!(normalize_name("  Cargo   Workspace  "), "cargo workspace");
    println!("{}", normalize_name("Shared Dependencies"));
}
```

In a real member crate, this function might use an inherited `regex` dependency.
The inheritance is expressed in the member's `Cargo.toml`; the Rust code imports the crate normally.

## Best practice
- ✅ Put common third-party dependency versions in `[workspace.dependencies]`.
- ✅ Keep member manifests explicit by inheriting only dependencies that the member actually uses.
- ✅ Put shared feature baseline, such as disabling default features or enabling `std`, in the workspace definition.
- ✅ Add member-specific features at the member entry so local requirements are reviewable.
- ✅ Use `resolver = "3"` at the workspace root for edition 2024 workspaces.
- ✅ Review `cargo tree -e features` after adding inherited features to understand workspace-wide unification.

## Pitfalls
- ⚠️ Trying to put `optional = true` in `[workspace.dependencies]`; Cargo does not allow optional workspace dependency definitions.
- ⚠️ Repeating `version` or `default-features` beside `workspace = true` in a member dependency.
- ⚠️ Assuming inheritance prevents feature unification. Features are still additive across selected packages.
- ⚠️ Centralizing every possible dependency even when only one crate uses it; that can make the root manifest noisy.
- ⚠️ Forgetting that target-specific dependency tables can also inherit workspace dependencies.
- ⚠️ Publishing a member without checking package contents and dependency specifications; see [[cargo publish, yank and owners]].

## See also
[[Cargo & Dependencies]] · [[Cargo Workspaces]] · [[Cargo.toml Manifest]] · [[Dependencies and Version Requirements]] · [[Feature Resolver]] · [[Feature Flags]] · [[Cargo.lock]] · [[Semantic Versioning]] · [[Minimizing Dependencies]]

## Sources
- The Cargo Book, "Workspaces: The dependencies table" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/workspaces.html#the-dependencies-table
- The Cargo Book, "Inheriting a dependency from a workspace" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#inheriting-a-dependency-from-a-workspace
