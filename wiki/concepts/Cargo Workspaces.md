---
type: concept
title: "Cargo Workspaces"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, workspaces, monorepo]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Cargo.lock]]", "[[Dependencies and Version Requirements]]", "[[MSRV Policy]]"]
sources: ["[[cargo-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/workspaces.html", "https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo Workspaces

A Cargo workspace is a set of packages managed together with shared dependency resolution, one root `Cargo.lock`, one target directory, and optional inherited package/dependency/lint settings.

## What it is
Workspaces let related crates live in one repository while still remaining separate packages. They are common for libraries with helper crates, binaries plus libraries, proc-macro companion crates, and monorepos.

A workspace can have a root package or be a virtual workspace. A virtual workspace has `[workspace]` but no `[package]`, so it must set the resolver explicitly.

## How it works
The workspace root lists members and owns the lockfile, output directory, profiles, patches, and replace settings. Member manifests can inherit selected fields from `[workspace.package]`, dependencies from `[workspace.dependencies]`, and lint settings from `[workspace.lints]`.

For edition 2024, prefer `resolver = "3"` in the workspace root. It enables the MSRV-aware resolver behavior that pairs with explicit `rust-version` fields.

Workspace dependencies centralize version requirements. Members opt in with `workspace = true` and can add features, but inherited dependencies cannot override arbitrary keys. For inherited dependencies, `default-features = false` must be declared at the workspace dependency if members need that behavior.

Cargo discovers a workspace by walking up parent directories until it finds a manifest with `[workspace]`, unless a member uses `package.workspace` to point elsewhere. Packages under the workspace directory that are path dependencies are automatically members unless excluded, so `members` and `exclude` need to reflect repository layout.

The workspace root is also the unit for many commands. In a virtual workspace, running `cargo check` at the root checks all default members because there is no root package. In a rooted workspace, `default-members` decides what an unqualified root command means.

## Example
```rust
pub fn workspace_member_name(package: &str) -> String {
    format!("workspace member: {package}")
}

fn main() {
    let label = workspace_member_name("api");
    assert_eq!(label, "workspace member: api");
}
```

The Rust code is ordinary crate code; the workspace value comes from building several packages with shared Cargo configuration.

## More realistic workspace manifest
```toml
[workspace]
members = ["crates/api", "crates/cli", "crates/macros"]
resolver = "3"
default-members = ["crates/api", "crates/cli"]

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"
repository = "https://example.com/project"

[workspace.dependencies]
serde = { version = "1.0.219", features = ["derive"] }
tracing = "0.1.41"
```

A member then writes `edition.workspace = true` and `serde.workspace = true`. It can add member-specific features, but it should not drift to an unrelated version requirement without a reason.

## Common errors
```text
error: current package believes it's in a workspace when it's not
```

Fix: either add the package to the root `members`, add it to `exclude`, or set `package.workspace` to the correct root when it lives outside the normal directory tree.

```text
error: failed to parse manifest at `.../Cargo.toml`
Caused by:
  virtual manifests must be configured with [workspace]
```

Fix: a virtual workspace root has `[workspace]` and no `[package]`; package-only keys belong in member manifests or `[workspace.package]`.

## Best practice
- ✅ Put shared `edition`, `rust-version`, license, repository, and dependency versions at the workspace root.
- ✅ Use `resolver = "3"` for edition 2024 workspaces and especially virtual workspaces.
- ✅ Use `cargo check --workspace` and package selectors (`-p`, `--workspace`) intentionally in CI.
- ✅ Keep `[patch]` and `[profile]` in the root manifest because member copies are ignored.
- ✅ Use `default-members` when root commands should skip slow examples, fuzz crates, or experimental packages by default.
- ✅ Keep public crates publishable independently: avoid path-only normal dependencies unless the target registry can resolve them.

## Pitfalls
- ⚠️ Per-crate dependency version drift can produce duplicate crates and incompatible public types; see [[Dependencies and Version Requirements]].
- ⚠️ Virtual workspaces do not infer a resolver from package edition; forgetting `resolver = "3"` can leave old behavior.
- ⚠️ Different MSRV policies in one workspace complicate dependency resolution; see [[MSRV Policy]].
- ⚠️ Assuming member `[profile]` settings apply is wrong; only the root profile settings control the workspace build.
- ⚠️ A feature enabled by one selected member can affect a shared dependency used by another selected member; test important package selections, not only `--workspace --all-features`.

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Cargo.lock]] · [[Dependencies and Version Requirements]] · [[Feature Flags]] · [[Profiles and Optimization Settings]] · [[MSRV Policy]] · [[Publishing to crates.io]] · [[cargo-audit and cargo-deny]]

## Sources
- The Cargo Book, "Workspaces" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/workspaces.html
- The Rust Programming Language, "Cargo Workspaces" — [[the-book]], https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
