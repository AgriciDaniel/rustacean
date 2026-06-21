---
type: concept
title: "Publishing to crates.io"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, publishing, crates-io]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Semantic Versioning]]", "[[Cargo.lock]]", "[[cargo-audit and cargo-deny]]"]
sources: ["[[cargo-book]]", "[[dependency-supply-chain-security]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/publishing.html", "https://doc.rust-lang.org/cargo/commands/cargo-publish.html"]
rust_version: "edition 2024 / 1.85+"
---

# Publishing to crates.io

Publishing uploads an immutable crate version to crates.io; once published, the version cannot be overwritten or deleted, only yanked from future resolution.

## What it is
`cargo publish` packages source into a `.crate` archive, verifies it, uploads it to the registry, and lets the registry perform final checks.

crates.io is a permanent archive. If a release is broken, `cargo yank` prevents new lockfiles from choosing it, but existing lockfiles keep working and the uploaded code remains available.

## How it works
Before a first publish, the manifest needs registry metadata: `description`, `license` or `license-file`, and generally `repository`, `readme`, keywords, and categories.

Before every publish, run `cargo publish --dry-run` or `cargo package`. Inspect packaged files with `cargo package --list`, especially when the repository contains large assets, secrets, test fixtures, or generated output.

Version bumps should match [[Semantic Versioning]]. If the crate exposes dependency types in its public API, dependency upgrades can become part of your SemVer surface.

Publishing is a packaging operation, not a git push. Cargo creates an archive from the manifest rules, verifies that the archive builds, and uploads that immutable archive. A later git force-push or repository cleanup does not change the already published crate.

Yanking only affects future resolution. Existing lockfiles can continue using the yanked version, and users can still download the archived crate. That makes pre-publish review more important than post-publish cleanup.

## Example
```rust
/// Returns the crate's greeting.
///
/// This public API is intentionally tiny and stable.
pub fn greeting(name: &str) -> String {
    format!("hello, {name}")
}

fn main() {
    assert_eq!(greeting("crates.io"), "hello, crates.io");
}
```

Publishing makes public API commitments like this available to downstream crates.

## Release checklist example
```text
cargo test --workspace --all-targets
cargo test --workspace --no-default-features
cargo package --list
cargo publish --dry-run
```

Run the checks from the package or workspace state you intend to tag. For a multi-crate release, publish dependency crates first, then update dependent version requirements and publish the crates that depend on them.

## Common errors
```text
error: all packages must have a version
```

Fix: publishable packages need a valid `version` in `[package]`, either written directly or inherited from `[workspace.package]`.

```text
error: failed to prepare local package for uploading
Caused by:
  no matching package named `internal-core` found
```

Fix: crates.io cannot resolve path-only normal dependencies. Publish the dependency first and include a compatible `version`, or mark the package `publish = false`.

```text
error: api errors (status 403 Forbidden): crate version `...` is already uploaded
```

Fix: bump the version. Published versions are immutable and cannot be overwritten.

## Best practice
- ✅ Run `cargo publish --dry-run` and `cargo package --list` before publishing.
- ✅ Review the public API and changelog against [[Semantic Versioning]] before bumping the version.
- ✅ Use `include` or `exclude` for package contents when repository defaults are too broad.
- ✅ Protect publishing credentials; prefer short-lived, scoped publishing flows where available.
- ✅ Tag the exact commit you publish so the registry archive, source repository, and changelog can be correlated later.
- ✅ Use `publish = false` for private workspace members to prevent accidental registry uploads.

## Pitfalls
- ⚠️ Accidentally publishing secrets cannot be fixed by yanking; rotate the secret immediately.
- ⚠️ Publishing a crate with path-only normal dependencies is rejected by crates.io; use publishable versions or multiple locations.
- ⚠️ Rushing a release without inspecting the archive can ship private fixtures or omit required generated files.
- ⚠️ Assuming `Cargo.lock` is shipped as the downstream resolution contract for a library is wrong; consumers resolve from your manifest requirements.
- ⚠️ Publishing generated code without deterministic generation can make registry builds diverge from repository builds.

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Semantic Versioning]] · [[Cargo.lock]] · [[Dependencies and Version Requirements]] · [[cargo-audit and cargo-deny]] · [[MSRV Policy]] · [[Feature Flags]] · [[Cargo Workspaces]]

## Sources
- The Cargo Book, "Publishing on crates.io" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo command reference, `cargo publish` — [[cargo-book]], https://doc.rust-lang.org/cargo/commands/cargo-publish.html
