---
type: concept
title: "Dependencies and Version Requirements"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, dependencies, versions]
domain: "Cargo & Dependencies"
difficulty: basic
related: ["[[Cargo.toml Manifest]]", "[[Semantic Versioning]]", "[[Cargo.lock]]", "[[Overbroad Version Requirements]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html", "https://doc.rust-lang.org/cargo/reference/resolver.html"]
rust_version: "edition 2024 / 1.85+"
---

# Dependencies and Version Requirements

Cargo dependency declarations name a package source and a version requirement; the requirement describes an allowed range, while `Cargo.lock` records the exact resolved version.

## What it is
A dependency line like `serde = "1.0.219"` is not an exact pin. It is Cargo's default caret requirement, equivalent to `>=1.0.219, <2.0.0`.

Dependencies can come from crates.io, another registry, a git repository, or a local path. They can be normal dependencies, dev-dependencies for tests/examples/benches, build-dependencies for `build.rs`, or target-specific dependencies.

## How it works
Cargo prefers the newest version that satisfies every active requirement while trying to unify compatible versions. For `1.2.3`, Cargo can use any `1.x.y` version at least `1.2.3`. For pre-1.0 crates, Cargo uses the left-most non-zero component: `0.2.3` means `>=0.2.3, <0.3.0`.

Use the default requirement form for most crates. Tilde (`~1.2`) and exact (`=1.2.3`) requirements are narrower and can make the graph impossible to resolve when another crate needs a newer compatible version.

Path and git dependencies are useful during development, but crates.io packages cannot depend on unpublished local or external git code except in limited dev-dependency cases. For local development plus publishable fallback, combine `path` or `git` with `version`.

Cargo's resolver works over package IDs: name, version, and source. `serde 1.0.219` from crates.io and a local path package named `serde` are different sources, even if their package names match. This is why `[patch]` is source-specific and why a lockfile records registry checksums.

Resolver 3, the edition 2024 default, also considers `rust-version` compatibility as a fallback preference. It does not magically rewrite an impossible requirement, but it can prefer an older compatible dependency release when the newest release requires a newer compiler than your declared [[MSRV Policy]].

## Example
```rust
pub trait Encoder {
    fn encode(&self, input: &str) -> String;
}

pub struct Plain;

impl Encoder for Plain {
    fn encode(&self, input: &str) -> String {
        input.to_owned()
    }
}

fn main() {
    let encoder = Plain;
    assert_eq!(encoder.encode("cargo"), "cargo");
}
```

This compiles without external crates; in a real package, the trait might be implemented by optional dependency-backed encoders chosen through the manifest.

## More realistic manifest example
```toml
[dependencies]
serde = { version = "1.0.219", features = ["derive"] }
tracing = { version = "0.1.41", default-features = false, features = ["std"] }

[target.'cfg(unix)'.dependencies]
rustix = "1.0.7"

[dev-dependencies]
assert_matches = "1.5.0"

[build-dependencies]
cc = "1.2.27"
```

This keeps dependency purpose visible: `serde` is part of normal code, `assert_matches` is test-only, `cc` is available only to `build.rs`, and `rustix` is only resolved for Unix targets that need it.

## Common errors
```text
error: failed to select a version for `serde`
  ... required by package `app v0.1.0`
versions that meet the requirements `=1.0.0` are: 1.0.0
```

Fix: avoid exact pins in libraries unless the crates are tightly coupled. Use a caret requirement such as `serde = "1.0.219"` and let [[Cargo.lock]] record the exact application build.

```text
error: no matching package named `local-helper` found
location searched: registry `crates-io`
```

Fix: add `path = "../local-helper"` for local development, or publish the dependency and use a registry `version` requirement for crates.io-compatible packages.

## Best practice
- ✅ Use default caret requirements with all three components, such as `regex = "1.10.6"`.
- ✅ Update the minimum requirement when your code starts using APIs introduced in a newer dependency release.
- ✅ Use `[dev-dependencies]` for test-only crates and `[build-dependencies]` for build scripts so dependency purpose stays clear.
- ✅ Inspect resolution with `cargo tree`, especially when a dependency appears unexpectedly.
- ✅ Prefer `path` plus `version` for in-repo crates that will also be publishable, so local development and registry users agree on the intended compatible version.
- ✅ Put platform-specific dependencies under target-specific tables instead of relying on runtime `cfg` to hide unused imports.

## Pitfalls
- ⚠️ `*`, `>=1`, and broad upper bounds can admit future SemVer-breaking releases; see [[Overbroad Version Requirements]].
- ⚠️ Exact pins in libraries can conflict with downstream users; prefer pinning exact versions through [[Cargo.lock]] for applications.
- ⚠️ A dependency's default features may pull in substantial transitive code; pair this note with [[Feature Flags]] and [[Minimizing Dependencies]].
- ⚠️ Git dependencies are not a substitute for a release process; they bypass normal registry indexing, checksums, and SemVer expectations.
- ⚠️ Public APIs that expose dependency types make that dependency's version line part of your compatibility story. See [[Semantic Versioning]].

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Semantic Versioning]] · [[Cargo.lock]] · [[Feature Flags]] · [[Cargo Workspaces]] · [[Overbroad Version Requirements]] · [[Minimizing Dependencies]] · [[MSRV Policy]] · [[cargo-audit and cargo-deny]]

## Sources
- The Cargo Book, "Specifying Dependencies" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- The Cargo Book, "Dependency Resolution" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html
