---
type: pattern
title: "Minimizing Dependencies"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, dependencies, supply-chain]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Dependencies and Version Requirements]]", "[[Feature Flags]]", "[[cargo-audit and cargo-deny]]", "[[Build Scripts (build.rs)]]"]
sources: ["[[cargo-book]]", "[[dependency-supply-chain-security]]", "[[tooling-project-hygiene]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/features.html", "https://doc.rust-lang.org/cargo/reference/resolver.html#troubleshooting"]
rust_version: "edition 2024 / 1.85+"
---

# Minimizing Dependencies

Minimizing dependencies means keeping the resolved graph as small and intentional as practical, reducing compile time, binary size, review burden, and supply-chain exposure.

## What it is
Every dependency brings code, maintainers, licenses, features, transitive dependencies, and sometimes build scripts or proc macros. Rust memory safety does not make those choices free.

The goal is not "zero dependencies"; it is "no accidental dependencies." A well-maintained crate can be the right choice, but unused, duplicate, overfeatured, or heavyweight crates should be removed.

## How it works
Cargo features often control dependency surface. `default-features = false` plus explicit feature selection can avoid pulling in TLS backends, async runtimes, derive proc macros, native libraries, or Unicode tables you do not use.

Use `cargo tree` to inspect why a crate is present and which features enabled it. The Cargo Book recommends `cargo tree --duplicates` for duplicate versions and feature-edge views to explain why features were activated.

Third-party hygiene tools such as unused-dependency scanners can help, but their results need review because proc macros, build scripts, and feature-only uses can fool simple scans.

Dependency cost is not only runtime size. A tiny normal dependency may be acceptable while a derive macro adds a proc-macro build, a `-sys` crate adds native probing, or a default TLS feature adds platform-specific build requirements. The resolved graph is the unit to evaluate.

Minimization is also an API design issue. If your public API exposes a dependency type, removing or upgrading that dependency becomes a compatibility decision. Keeping dependency types behind your own small types can preserve freedom to change internals later.

## Example
```rust
fn normalize_slug(input: &str) -> String {
    input
        .chars()
        .filter(|ch| ch.is_ascii_alphanumeric() || *ch == '-')
        .flat_map(char::to_lowercase)
        .collect()
}

fn main() {
    assert_eq!(normalize_slug("Cargo_2024!"), "cargo2024");
}
```

This small utility does not need a general-purpose text-processing dependency unless requirements grow beyond the standard library.

## Manifest example
```toml
[dependencies]
reqwest = { version = "0.12.20", default-features = false, features = ["json", "rustls-tls"] }
serde = { version = "1.0.219", features = ["derive"] }

[dev-dependencies]
insta = { version = "1.43.1", default-features = false }
```

This explicitly chooses a TLS backend and keeps snapshot-testing helpers out of the normal dependency graph. The exact feature set should be justified by the crate's real requirements.

## Common errors
```text
error[E0432]: unresolved import `serde::Serialize`
```

Fix: if you disabled default features or optional derive support, enable the required feature explicitly, for example `serde = { version = "1.0.219", features = ["derive"] }`.

```text
error: failed to run custom build command for `openssl-sys`
```

Fix: inspect which dependency feature pulled in the native library. You may need system packages, a different feature set, or a pure-Rust backend.

## Review workflow
Use `cargo tree -e features` to answer "why is this crate here?" and `cargo tree -d` to find duplicate version lines. Review dependency additions in the same change as the code that uses them; a manifest-only addition should be unusual.

## Best practice
- ✅ Prefer the standard library for small, stable needs.
- ✅ Disable default features and enable only the features you actually need when a crate supports it.
- ✅ Review `cargo tree --workspace --target all --all-features` periodically.
- ✅ Pay extra attention to dependencies with `build.rs` or proc macros because they execute code during builds.
- ✅ Wrap external types at API boundaries when the dependency is an implementation detail.
- ✅ Keep dev-only tooling in `[dev-dependencies]` so normal consumers do not inherit it.

## Pitfalls
- ⚠️ Copy-pasting dependency snippets with default features can pull in large transitive graphs.
- ⚠️ Removing a dependency feature can be a behavior change; test important feature combinations. See [[Feature Flags]].
- ⚠️ Duplicate major versions can create distinct incompatible types at API boundaries; see [[Semantic Versioning]].
- ⚠️ Reimplementing complex security, parsing, crypto, or protocol logic just to avoid a dependency can be worse than choosing a reputable crate.
- ⚠️ Optional dependencies still become part of your public feature and SemVer surface unless hidden behind deliberate feature names.

## See also
[[Cargo & Dependencies]] · [[Dependencies and Version Requirements]] · [[Feature Flags]] · [[cargo-audit and cargo-deny]] · [[Build Scripts (build.rs)]] · [[Cargo.lock]] · [[Overbroad Version Requirements]] · [[Semantic Versioning]] · [[MSRV Policy]]

## Sources
- The Cargo Book, "Features" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/features.html
- The Cargo Book, "Dependency Resolution: Troubleshooting" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html#troubleshooting
