---
type: concept
title: "Cargo.toml Manifest"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, manifest, metadata]
domain: "Cargo & Dependencies"
difficulty: basic
related: ["[[Dependencies and Version Requirements]]", "[[Cargo Workspaces]]", "[[Publishing to crates.io]]", "[[MSRV Policy]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/manifest.html", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo.toml Manifest

`Cargo.toml` is the package manifest: the TOML file where Cargo learns what the package is, which Rust edition and MSRV it targets, which targets it builds, and which dependencies it resolves.

## What it is
Every Cargo package has a manifest at its package root. The required field is `package.name`; publishable packages also need version and registry metadata such as description and license.

The manifest is not just documentation. Cargo reads it to select the edition, resolver, targets, profiles, dependencies, features, lints, packaging rules, and workspace membership.

For edition 2024 packages, write the edition explicitly:

```toml
[package]
name = "parse-demo"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"
description = "Small parsing utilities."

[dependencies]
```

## How it works
Cargo treats `Cargo.toml` as structured input, not as a script. Known tables have defined meaning, unknown ordinary keys produce warnings, and tool-specific data belongs under `package.metadata` or `workspace.metadata`.

The `[package]` table controls identity and package-level defaults. Dependency tables (`[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, and target-specific tables) control the resolver graph. Target tables such as `[lib]` and `[[bin]]` override Cargo's source-file auto-discovery when needed.

In a workspace, some settings only matter at the workspace root: `[patch]`, `[replace]`, and `[profile.*]` are ignored in member manifests. Use [[Cargo Workspaces]] inheritance for shared package metadata and dependency declarations.

Edition selection is per package, not per workspace. A workspace can share `edition.workspace = true`, but Cargo ultimately compiles each package with the edition recorded for that package. If `edition` is missing, Cargo falls back to the historical 2015 default, so modern manifests should be explicit even when `cargo new` currently writes `edition = "2024"`.

The `rust-version` field is also package metadata with resolver consequences. With edition 2024's resolver 3 behavior, Cargo prefers dependency versions compatible with the package's declared MSRV when a compatible version exists. That makes `rust-version = "1.85"` both documentation and resolver input for this vault's target.

## Example
```rust
fn main() {
    let package = option_env!("CARGO_PKG_NAME").unwrap_or("standalone");
    let version = option_env!("CARGO_PKG_VERSION").unwrap_or("0.0.0");
    println!("{package} {version}");
}
```

The example compiles as ordinary Rust. When Cargo builds it, the manifest's package fields become compile-time environment variables.

## More realistic manifest slice
```toml
[package]
name = "api-client"
version = "0.3.0"
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"
description = "Client library for an internal JSON API."
repository = "https://example.com/api-client"
publish = false

[dependencies]
serde = { version = "1.0.219", features = ["derive"] }
serde_json = "1.0.140"

[dev-dependencies]
pretty_assertions = "1.4.1"

[lints.rust]
unsafe_code = "forbid"
```

`publish = false` is a strong guard for internal crates. Public crates would remove that line and make sure the registry-required metadata and packaged files are correct before [[Publishing to crates.io]].

## Common errors
```text
error: failed to parse manifest at `.../Cargo.toml`
Caused by:
  no targets specified in the manifest
```

Fix: add `src/lib.rs`, `src/main.rs`, a `[[bin]]` target with a valid `path`, or another supported target table. Cargo needs at least one target to build.

```text
warning: unused manifest key: package.licence
```

Fix: Cargo recognized neither the misspelled key nor the intent. Use `license`, `license-file`, or put tool-owned keys under `package.metadata.*`.

## Best practice
- ✅ Set `edition = "2024"` and `rust-version = "1.85"` explicitly so tooling and users do not infer old defaults.
- ✅ Keep publish metadata complete: `description`, `license` or `license-file`, `repository`, and `readme`.
- ✅ Put tool-specific configuration under `package.metadata.*` or `workspace.metadata.*`, not in ad hoc top-level keys.
- ✅ Use `include` or `exclude` deliberately for crates that contain large fixtures, generated assets, or private files.
- ✅ In workspaces, centralize repeatable metadata with `[workspace.package]` and opt in from members with `field.workspace = true`.
- ✅ Keep normal, dev, build, and target-specific dependencies in their correct tables so Cargo builds the smallest correct graph for each command.

## Pitfalls
- ⚠️ Omitting `edition` falls back to 2015 for old manifests; that is rarely what a new project wants. See [[MSRV Policy]].
- ⚠️ Putting `[profile]` or `[patch]` in a workspace member has no effect; root-only Cargo settings belong at the workspace root.
- ⚠️ Treating `Cargo.toml` as a lockfile leads to surprise updates; exact resolved versions belong to [[Cargo.lock]].
- ⚠️ Relying on `package.metadata` for Cargo behavior is a category error; Cargo reserves it for external tools.
- ⚠️ Publishing with broad `include` defaults can ship secrets or omit generated sources; inspect the package archive before release.

## See also
[[Cargo & Dependencies]] · [[Dependencies and Version Requirements]] · [[Cargo.lock]] · [[Cargo Workspaces]] · [[Feature Flags]] · [[Publishing to crates.io]] · [[MSRV Policy]] · [[Profiles and Optimization Settings]] · [[Build Scripts (build.rs)]] · [[Overbroad Version Requirements]]

## Sources
- The Cargo Book, "The Manifest Format" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/manifest.html
- The Cargo Book, "Specifying Dependencies" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
