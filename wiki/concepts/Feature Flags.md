---
type: concept
title: "Feature Flags"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, features, cfg]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Dependencies and Version Requirements]]", "[[Semantic Versioning]]", "[[Non-Additive Feature Flags]]", "[[Minimizing Dependencies]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/features.html", "https://doc.rust-lang.org/cargo/reference/resolver.html#features"]
rust_version: "edition 2024 / 1.85+"
---

# Feature Flags

Cargo features are named compile-time switches declared in `Cargo.toml`; features unify across the dependency graph, so they must add capability rather than remove or reinterpret behavior.

## What it is
A feature is a named flag in a package's `[features]` table. It can enable conditional Rust code, other features, or optional dependencies.

Features are selected by dependency declarations and command-line flags such as `--features`, `--all-features`, and `--no-default-features`.

## How it works
Cargo builds each package with the union of all features requested for that package by all users in the selected graph. If one dependency enables `serde` support and another enables `rayon` support on the same crate, Cargo builds that crate with both.

Optional dependencies implicitly create same-named features unless the `[features]` table uses `dep:name` to hide the implementation detail behind a better public feature name.

Edition 2024 uses resolver 3 by default, inheriting resolver 2 feature behavior and MSRV-aware resolution. Resolver 2 and later avoid unifying some target-specific, build-dependency, and dev-dependency features in cases where resolver 1 over-unified them.

Features are not key-value settings and they are not selected separately for each dependent. Cargo computes one feature set per package instance in the selected graph. That model is why features must be additive and why mutually exclusive feature pairs are a design smell.

The manifest controls the public feature surface. An optional dependency named `native-tls` becomes a public feature named `native-tls` unless you refer to it as `dep:native-tls` from a more intentional feature such as `tls-native`.

## Example
```rust
#[cfg(feature = "json")]
fn render(value: &str) -> String {
    format!("{{\"value\":\"{value}\"}}")
}

#[cfg(not(feature = "json"))]
fn render(value: &str) -> String {
    value.to_owned()
}

fn main() {
    let rendered = render("cargo");
    assert!(rendered.contains("cargo"));
}
```

This compiles with or without a `json` feature. The feature adds a representation; it does not make the default path invalid.

## Manifest example
```toml
[dependencies]
serde = { version = "1.0.219", optional = true, features = ["derive"] }
serde_json = { version = "1.0.140", optional = true }

[features]
default = ["std"]
std = []
json = ["dep:serde", "dep:serde_json"]
```

Here `json` is the public feature. The `dep:` syntax prevents `serde` and `serde_json` from becoming accidental public feature names that users may rely on forever.

## Common errors
```text
error: none of the selected packages contains this feature: json
```

Fix: run the command for the package that defines the feature, or use package-qualified feature syntax in a workspace command, such as `cargo test -p api-client --features json`.

```text
error[E0425]: cannot find function `to_json` in this scope
```

Fix: build with the feature that exposes the API, or keep the API available and feature-gate only the implementation details. Moving existing API behind a feature is usually a [[Semantic Versioning]] break.

## Best practice
- ✅ Make features additive: enabling a feature should not disable existing APIs or break other feature combinations.
- ✅ Use `default-features = false` only after checking which defaults you are opting out of.
- ✅ Use `dep:crate_name` to avoid exposing internal optional dependencies as public features.
- ✅ Test default, no-default, all-features, and important individual feature combinations.
- ✅ Prefer capability names (`json`, `tls-native`, `compression`) over dependency names unless the dependency itself is intentionally public.
- ✅ Keep `std` as an additive default feature for `no_std`-capable libraries; do not create a `no_std` feature that disables `std`.

## Pitfalls
- ⚠️ Mutually exclusive features require the whole graph to coordinate perfectly; see [[Non-Additive Feature Flags]].
- ⚠️ Removing a feature, optional dependency, or default feature can be SemVer-breaking; see [[Semantic Versioning]].
- ⚠️ `--all-features` alone can hide broken individual combinations because feature unification makes the graph more permissive than some real users' builds.
- ⚠️ Feature-gating tests only through `--all-features` misses the common `--no-default-features --features alloc` style build.
- ⚠️ Using features for runtime choices can force downstream dependency graphs into compile-time conflicts; prefer configuration values when both modes can exist.

## See also
[[Cargo & Dependencies]] · [[Dependencies and Version Requirements]] · [[Semantic Versioning]] · [[Cargo Workspaces]] · [[Minimizing Dependencies]] · [[Non-Additive Feature Flags]] · [[Profiles and Optimization Settings]] · [[Cargo.toml Manifest]] · [[Overbroad Version Requirements]]

## Sources
- The Cargo Book, "Features" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/features.html
- The Cargo Book, "Dependency Resolution: Features" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html#features
