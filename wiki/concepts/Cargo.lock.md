---
type: concept
title: "Cargo.lock"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, lockfile, reproducibility]
domain: "Cargo & Dependencies"
difficulty: basic
related: ["[[Cargo.toml Manifest]]", "[[Dependencies and Version Requirements]]", "[[Cargo Workspaces]]", "[[Publishing to crates.io]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html", "https://doc.rust-lang.org/cargo/reference/resolver.html#lock-file"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo.lock

`Cargo.lock` records the exact resolved dependency versions for a package or workspace, turning broad manifest requirements into reproducible builds.

## What it is
`Cargo.toml` says "any compatible version in this range is acceptable." `Cargo.lock` says "this build used exactly these package versions and checksums."

Cargo creates or updates the lockfile when it resolves dependencies. In a workspace, the lockfile lives at the workspace root and covers all members.

## How it works
When possible, Cargo keeps using versions already recorded in `Cargo.lock`, even if newer compatible versions have been published. If the manifest requirement changes so a locked version no longer matches, Cargo resolves a new version and updates the lockfile.

`cargo update` refreshes lockfile entries. Without options it updates the whole graph; with `-p` it targets a package. `--locked` and `--frozen` make Cargo error instead of silently changing the lockfile.

For applications, binaries, and CI, commit `Cargo.lock`. For libraries, modern practice is also often to commit it so CI and audits are reproducible, even though downstream users resolve their own lockfiles.

The lockfile records package name, version, source, checksum, and dependency edges. It does not replace version requirements in `Cargo.toml`; it is an output of resolving those requirements for this package or workspace at a point in time.

Cargo uses the lockfile as a preference, not as permission to violate the manifest. If `Cargo.toml` changes from `regex = "1.10"` to `regex = "1.11"` and the locked version is too old, Cargo must resolve a newer compatible version and update the lockfile unless `--locked` prevents the write.

## Example
```rust
fn checksum_input(packages: &[&str]) -> String {
    packages.join("\n")
}

fn main() {
    let locked = checksum_input(&["serde 1.0.219", "itoa 1.0.15"]);
    assert!(locked.contains("serde"));
}
```

This models the lockfile's job: record exact package identities so repeated builds know what to use.

## Focused update example
```text
cargo update -p tracing
cargo tree -p tracing
cargo test --workspace --locked
```

This workflow updates one package line, inspects the resulting dependency edges, and then verifies the workspace without allowing another silent lockfile rewrite.

## Common errors
```text
error: the lock file ... needs to be updated but --locked was passed to prevent this
```

Fix: either commit the lockfile change produced by normal Cargo resolution, or revert the manifest change that made the existing lockfile stale.

```text
error: failed to select a version for the requirement `crate = "^1.2"`
```

Fix: the lockfile cannot solve incompatible requirements. Inspect the constraints with `cargo tree -i crate` and adjust the manifest ranges or dependency versions.

## Applications vs libraries
Applications and deployable binaries use `Cargo.lock` as part of release reproducibility. A production rebuild, container image, or CI job should not silently pick a newer transitive dependency than the one tested.

Libraries can commit a lockfile for their own CI, examples, and security scans, but downstream users do not inherit that exact graph. A library's real compatibility promise remains the manifest requirements plus [[Semantic Versioning]].

## Best practice
- ✅ Commit `Cargo.lock` for binaries, applications, workspaces, and CI-tested libraries.
- ✅ Use `cargo update -p crate_name` for focused upgrades instead of refreshing the whole graph casually.
- ✅ Run security tools against the lockfile because it reflects the actual resolved graph.
- ✅ Use `--locked` in CI, release packaging, and `cargo install` guidance when exact dependency reproduction matters.
- ✅ Review lockfile diffs by package source as well as version; a source change can be more important than a numeric bump.
- ✅ Pair lockfile updates with `cargo tree --duplicates` when dependency churn looks larger than expected.

## Pitfalls
- ⚠️ Deleting `Cargo.lock` to "fix" dependency problems hides the real resolver constraint; inspect with `cargo tree`.
- ⚠️ Assuming a library's committed lockfile controls downstream users is wrong; dependents resolve their own graph.
- ⚠️ Ignoring lockfile diffs in review can smuggle transitive dependency changes into unrelated commits.
- ⚠️ Running security checks only on `Cargo.toml` misses the actual selected versions; use the resolved lockfile.
- ⚠️ Using `cargo update` without a package selector during a hotfix can introduce unrelated transitive changes.

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Dependencies and Version Requirements]] · [[Cargo Workspaces]] · [[cargo-audit and cargo-deny]] · [[Publishing to crates.io]] · [[Overbroad Version Requirements]] · [[Semantic Versioning]] · [[MSRV Policy]]

## Sources
- The Cargo Book, "Cargo.toml vs Cargo.lock" — [[cargo-book]], https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
- The Cargo Book, "Dependency Resolution: Lock file" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html#lock-file
