---
type: concept
title: "Profiles and Optimization Settings"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, profiles, optimization]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Cargo Workspaces]]", "[[Build Scripts (build.rs)]]", "[[Minimizing Dependencies]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/profiles.html", "https://doc.rust-lang.org/rustc/codegen-options/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Profiles and Optimization Settings

Cargo profiles are named compiler-setting bundles that control optimization, debug info, overflow checks, LTO, panic behavior, incremental compilation, and codegen units.

## What it is
Cargo has built-in `dev`, `release`, `test`, and `bench` profiles. Commands choose a profile by default: `cargo build` uses `dev`, `cargo test` uses `test`, and `cargo build --release` uses `release`.

Profiles are configured with `[profile.*]` tables in the root manifest of the package or workspace.

## How it works
Profile settings map to rustc codegen behavior. `opt-level` changes optimization; `debug` controls debuginfo; `overflow-checks` controls integer overflow panics; `lto` enables link-time optimization; `panic` selects unwind or abort where supported.

Workspace profile settings are root-only. Settings in dependency manifests are ignored so dependencies cannot force downstream users into surprising optimization modes.

Cargo also supports custom profiles with `inherits`, package-specific overrides, dependency-wide overrides with `package."*"`, and build-script/proc-macro overrides with `build-override`.

Profiles affect compilation units, not source semantics in isolation. `debug_assert!`, integer overflow behavior, inlining, monomorphization, and link-time decisions can differ by profile. That means a performance bug or overflow panic can appear only in the profile a user actually runs.

Profile settings for dependencies are chosen by the final package being built. A library cannot publish a manifest that forces all downstream builds to use its preferred `opt-level`; downstream applications decide their profile policy.

## Example
```rust
fn checked_add(a: u32, b: u32) -> u32 {
    debug_assert!(a < 1_000_000);
    a.saturating_add(b)
}

fn main() {
    assert_eq!(checked_add(2, 3), 5);
    println!("debug assertions: {}", cfg!(debug_assertions));
}
```

The same code compiles under every profile, but debug assertions and optimization behavior differ by profile.

## Manifest example
```toml
[profile.release]
opt-level = 3
debug = "line-tables-only"
lto = "thin"
codegen-units = 1
panic = "abort"

[profile.release.package."*"]
opt-level = 2

[profile.dev.package."*"]
opt-level = 1
```

This keeps the final crate highly optimized while avoiding the assumption that every dependency benefits from the same setting. The dev override can speed up debug runs for dependency-heavy applications, but it should be measured.

## Common errors
```text
warning: profiles for the non root package will be ignored, specify profiles at the workspace root
```

Fix: move `[profile.*]` tables to the root `Cargo.toml` of the package or workspace that invokes the build.

```text
error: profile `release-lto` is missing an `inherits` directive
```

Fix: custom profiles need `inherits = "release"` or another built-in/custom profile so Cargo knows the base settings.

## Best practice
- ✅ Tune profiles after measuring; `opt-level = 3` is not always faster or smaller than `2`, `"s"`, or `"z"`.
- ✅ Put workspace-wide profile settings in the root manifest.
- ✅ Use custom profiles for named workflows such as `release-lto` instead of overloading `release`.
- ✅ Keep build dependency optimization low unless profiling shows build scripts or proc macros are the bottleneck.
- ✅ Preserve useful debug info in release artifacts when production crash triage matters.
- ✅ Test the profile you ship; `cargo test` does not automatically exercise the exact `release` binary behavior.

## Pitfalls
- ⚠️ Disabling overflow checks in `dev` removes useful bug detection during normal development.
- ⚠️ Assuming dependency package profile settings apply downstream is wrong; Cargo ignores dependency-defined profiles.
- ⚠️ Profile overrides on generic-heavy crates can disappoint because monomorphized code may be generated in the local crate.
- ⚠️ `panic = "abort"` reduces binary/runtime overhead but removes unwinding behavior that some embedding or test scenarios expect.
- ⚠️ LTO and single codegen units can improve runtime performance while increasing build time enough to hurt iteration speed.

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Cargo Workspaces]] · [[Build Scripts (build.rs)]] · [[Feature Flags]] · [[Minimizing Dependencies]] · [[Cargo.lock]] · [[MSRV Policy]] · [[Publishing to crates.io]]

## Sources
- The Cargo Book, "Profiles" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/profiles.html
- The rustc Book, "Codegen options" — [[rustc-book]], https://doc.rust-lang.org/rustc/codegen-options/index.html
