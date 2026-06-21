---
type: concept
title: "MSRV Policy"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, msrv, rust-version]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Cargo Workspaces]]", "[[Semantic Versioning]]", "[[Dependencies and Version Requirements]]"]
sources: ["[[cargo-book]]", "[[edition-guide]]", "[[tooling-project-hygiene]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/rust-version.html", "https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html"]
rust_version: "edition 2024 / 1.85+"
---

# MSRV Policy

An MSRV policy states the Minimum Supported Rust Version for a crate and how that version is chosen, tested, and raised over time.

## What it is
Cargo's `rust-version` package field declares the oldest Rust toolchain a package supports. If a user builds with an older toolchain, Cargo reports a clear error.

For this vault's target, new edition 2024 notes assume `rust-version = "1.85"` unless a package deliberately supports older Rust.

## How it works
The `rust-version` value is a bare Rust version such as `1.85`; it is not a SemVer range. It applies to all targets in the package.

Edition 2024 defaults to resolver 3, which changes the default `resolver.incompatible-rust-versions` behavior to `fallback`. That means dependency resolution prefers versions compatible with the package's declared `rust-version` when possible.

Declaring an MSRV is a commitment. The Cargo Book expects supported versions to be complete, verified, patchable, and supported by at least one compatible dependency version for each dependency requirement.

`rust-version` is checked before rustc tries to compile the crate. That gives users a direct Cargo error instead of a confusing parse error from using a newer edition, feature, or standard-library API on an older compiler.

MSRV interacts with dependencies in two directions. Your code may accidentally use a newer dependency API than your minimum requirement guarantees, and your dependency graph may select a dependency release whose own `rust-version` is higher than yours unless resolver policy and testing catch it.

## Example
```rust
pub fn first_word(input: &str) -> Option<&str> {
    input.split_whitespace().next()
}

fn main() {
    assert_eq!(first_word("rust cargo"), Some("rust"));
}
```

This deliberately uses long-stable standard-library APIs; an MSRV test would catch accidental use of newer APIs.

## CI example
```text
cargo +1.85.0 check --workspace --all-targets --locked
cargo +stable test --workspace --all-targets
```

The MSRV job proves the declared lower bound. The stable job proves the project still works on the current compiler and catches new warnings or behavior changes earlier.

## Common errors
```text
error: package `api-client v0.3.0` cannot be built because it requires rustc 1.85 or newer
```

Fix: build with a supported toolchain, or lower `rust-version` only after verifying the crate and its dependencies truly build on that older compiler.

```text
error[E0658]: use of unstable library feature ...
```

Fix: do not treat nightly-only features as part of a stable MSRV. Replace the API, raise the policy when the feature is stable, or gate experimental code outside the stable release path.

## Policy choices
A latest-stable-only policy is simple for maintainers but costly for conservative users. An N-2 or annual MSRV policy gives users predictability but requires discipline when adopting language and std APIs.

For libraries, raising MSRV should be documented in the changelog and reflected in the version bump policy. For applications, the MSRV may simply be the pinned toolchain used to build and deploy the binary.

## Best practice
- ✅ Declare `rust-version` in every publishable package.
- ✅ Write down the policy: latest stable only, N-2, annual window, or another explicit rule.
- ✅ Test the declared MSRV in CI, not just stable.
- ✅ Use resolver 3 for edition 2024 workspaces and understand how it interacts with dependency selection.
- ✅ Keep dependency minimum versions aligned with APIs actually used by your code.
- ✅ Test representative feature combinations on MSRV because optional dependencies can raise the effective compiler requirement.

## Pitfalls
- ⚠️ Claiming an MSRV without testing it lets newer standard-library APIs slip in unnoticed.
- ⚠️ A workspace with multiple MSRV policies can resolve lower dependency versions for newer members or too-new versions for older members.
- ⚠️ Raising MSRV is commonly treated as a minor compatibility change, but it can still block users; document it in release notes.
- ⚠️ Setting `rust-version` lower than the crate's edition permits is invalid; edition 2024 itself requires a sufficiently new compiler.
- ⚠️ Depending on a crate's newest release can silently raise your practical MSRV if you never test with the declared compiler.

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Cargo Workspaces]] · [[Dependencies and Version Requirements]] · [[Semantic Versioning]] · [[Feature Flags]] · [[Profiles and Optimization Settings]] · [[Cargo.lock]] · [[Publishing to crates.io]]

## Sources
- The Cargo Book, "Rust Version" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/rust-version.html
- The Rust Edition Guide, "Rust-version aware resolver" — [[edition-guide]], https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
