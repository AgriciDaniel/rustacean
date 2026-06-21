---
type: concept
title: "Feature Resolver"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, features, resolver, dependencies]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Feature Flags]]", "[[Dependencies and Version Requirements]]", "[[Cargo.lock]]", "[[Cargo Workspaces]]", "[[Non-Additive Feature Flags]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/resolver.html", "https://doc.rust-lang.org/cargo/reference/features.html#feature-resolver-version-2", "https://doc.rust-lang.org/cargo/reference/manifest.html#the-resolver-field"]
rust_version: "edition 2024 / 1.85+"
---

# Feature Resolver

The Cargo feature resolver decides which dependency versions and feature sets are selected for a build; in edition 2024 the default resolver is `"3"`, which includes resolver v2 feature behavior and changes the default handling of dependencies whose `rust-version` is incompatible.

## What it is
Cargo resolution has two related jobs.
First, it chooses dependency versions that satisfy all version requirements, lockfile constraints, `links` constraints, yanked-version rules, and Rust-version policy.
Second, it determines which features are enabled for each selected package.
The "feature resolver" phrase usually points at the feature-unification behavior controlled by the manifest `resolver` field.
In current Cargo, the resolver version is global for the package or workspace.
Dependency crates cannot force their own resolver behavior on the top-level build.

## How it works
Resolver versions are selected with `resolver = "1"`, `"2"`, or `"3"`.
For a package, the key is under `[package]`.
For a virtual workspace, put it under `[workspace]` because there is no package edition to infer from.

```toml
[workspace]
members = ["crates/app", "crates/lib"]
resolver = "3"
```

Resolver `"1"` is the oldest behavior and unifies features for a package no matter where they are specified.
Resolver `"2"` avoids unifying features in several important cases:
target-specific dependency features are not enabled when that target is not being built;
features on build-dependencies and proc-macros are not unified with normal dependency uses;
features on dev-dependencies are not unified with normal uses unless those dev targets are being built.
Edition 2021 packages default to resolver `"2"`.
Resolver `"3"` is the edition 2024 default and requires Rust 1.84 or newer.
It keeps resolver `"2"` feature behavior and changes the default for `resolver.incompatible-rust-versions` from `allow` to `fallback`.
With `fallback`, Cargo prefers dependency versions whose `rust-version` is compatible with the package's Rust version when such versions satisfy the dependency requirement.

Features are additive.
If one workspace member depends on a crate with feature `serde` and another depends on the same crate with feature `rayon`, a build that selects both members compiles that dependency with both features.
If you need to avoid feature unification across workspace members, build them in separate Cargo invocations.

For lockfile generation, Cargo resolves as if all features of all workspace members are enabled.
Cargo then resolves again for the actual compile based on selected packages, targets, and command-line feature flags.
This design keeps optional dependencies available in `Cargo.lock` as features are toggled.

## Example
```rust
fn dependency_mode(has_std: bool, target_enabled: bool) -> &'static str {
    match (has_std, target_enabled) {
        (true, true) => "std target build",
        (true, false) => "std support available but target feature inactive",
        (false, true) => "target build without std feature",
        (false, false) => "minimal build",
    }
}

fn main() {
    assert_eq!(dependency_mode(true, false), "std support available but target feature inactive");
    println!("{}", dependency_mode(false, false));
}
```

The compile-time behavior is configured in Cargo.
For example, with resolver `"2"` or `"3"`, a Windows-only dependency feature is not enabled on non-Windows builds only because it appears in a target-specific table.

## Best practice
- ✅ Use `resolver = "3"` for edition 2024 workspaces, especially virtual workspaces where Cargo cannot infer the resolver from a root package edition.
- ✅ Keep features additive: enabling a feature should add capability, not remove or change existing APIs.
- ✅ Inspect feature unification with `cargo tree -e features` when a dependency unexpectedly builds with extra capabilities.
- ✅ Build no-std, target-specific, test, and all-target combinations explicitly if feature separation matters.
- ✅ Put resolver selection at the workspace root so every member follows one policy.
- ✅ Use precise dependency requirements that include the minimum version containing the features you require.

## Pitfalls
- ⚠️ Assuming features are selected independently per dependent crate. Features for the same package are usually unified.
- ⚠️ Removing a feature in a SemVer-compatible release. Dependents requiring that feature can get stuck on older versions.
- ⚠️ Depending on resolver `"1"` behavior accidentally in modern workspaces.
- ⚠️ Forgetting that dev-dependency features can still be active for tests, examples, and `--all-targets`.
- ⚠️ Expecting a dependency's own `resolver` field to affect your top-level build.
- ⚠️ Designing mutually exclusive features. Prefer separate crates or runtime configuration; see [[Non-Additive Feature Flags]].

## See also
[[Cargo & Dependencies]] · [[Feature Flags]] · [[Non-Additive Feature Flags]] · [[Dependencies and Version Requirements]] · [[Cargo.lock]] · [[Cargo Workspaces]] · [[Workspace Dependency Inheritance]] · [[Cargo Configuration Hierarchy]] · [[Semantic Versioning]]

## Sources
- The Cargo Book, "Dependency Resolution" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/resolver.html
- The Cargo Book, "Feature resolver version 2" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/features.html#feature-resolver-version-2
- The Cargo Book, "The resolver field" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/manifest.html#the-resolver-field
