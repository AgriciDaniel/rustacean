---
type: antipattern
title: "Overbroad Version Requirements"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, dependencies, semver]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Dependencies and Version Requirements]]", "[[Semantic Versioning]]", "[[Cargo.lock]]", "[[cargo-audit and cargo-deny]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#version-requirement-syntax", "https://doc.rust-lang.org/cargo/reference/resolver.html#recommendations"]
rust_version: "edition 2024 / 1.85+"
---

# Overbroad Version Requirements

Overbroad version requirements such as `*`, `>=1`, or unconstrained upper bounds invite future SemVer-incompatible releases into normal resolution.

## The mistake
The mistake is writing dependency requirements that are much wider than the API compatibility you have tested or intend to support.

Examples include `crate = "*"`, `crate = ">=1.0"`, `crate = "1.*"` when a normal caret requirement is enough, or `crate = ">=0.6,<2"` for a public dependency without a strong reason.

## Why it happens
Broad requirements look flexible, but they transfer risk to downstream users. Cargo generally prefers the highest matching version. If the requirement admits a future major version, a routine update can select it.

Broad ranges also make duplicate versions more likely. If one crate asks for `rand = "0.7"` and another asks for `rand = ">=0.6"`, Cargo may select both `0.7` and a newer incompatible line for the broad requirement.

The correct alternative is usually the default caret form with the minimum version your code actually needs, such as `serde = "1.0.219"`.

The resolver does not know which APIs your code actually calls. It can only compare version requirements and package metadata. A broad range says "any of these versions are acceptable," so Cargo is allowed to pick a future release you never tested.

This is especially risky when a dependency's types appear in your public API. If your crate accepts `time::OffsetDateTime`, then accidentally allowing a future incompatible `time` major line can split downstream type identity.

## Example
```rust
mod v1 {
    pub struct Id(pub u64);
}

mod v2 {
    pub struct Id(pub u64);
}

fn takes_v1(id: v1::Id) -> u64 {
    id.0
}

fn main() {
    let id = v1::Id(7);
    assert_eq!(takes_v1(id), 7);
    let _other_major_is_a_different_type = v2::Id(7);
}
```

Two SemVer-incompatible crate versions behave like these modules: same names do not make their types interchangeable.

## Bad and good manifest examples
```toml
# Bad: admits future breaking releases.
[dependencies]
serde = ">=1"
regex = "*"
time = ">=0.3, <1"

# Good: state the minimum compatible version you tested.
[dependencies]
serde = "1.0.219"
regex = "1.11.1"
time = "0.3.41"
```

The "good" lines are still flexible: Cargo may choose newer compatible releases, and [[Cargo.lock]] records the exact chosen versions for an application build.

## Common errors
```text
error: failed to select a version for `some-crate`
  previously selected package `dep v2.0.0`
  ... which satisfies dependency `dep = ">=1"` ...
```

Fix: narrow the broad requirement to the compatible major version your code supports, such as `dep = "1.4.2"`.

```text
error[E0308]: mismatched types
  expected `dep::Id`, found a different `dep::Id`
```

Fix: inspect `cargo tree -d`. Duplicate incompatible versions can produce same-named but distinct public types.

## Best practice
- ✅ Use default caret requirements with all three components for normal dependencies.
- ✅ Update the minimum version when you begin using newer dependency APIs.
- ✅ Use exact requirements only for tightly coupled packages, such as a parent crate and companion proc macro.
- ✅ Let [[Cargo.lock]] pin application builds instead of encoding pins into library manifests.
- ✅ Treat public dependency types as part of your own SemVer surface and keep their ranges conservative.
- ✅ Use `cargo update -p name --precise version` for temporary application triage rather than publishing broad or exact library requirements.

## Pitfalls
- ⚠️ Bare `*` is not allowed on crates.io and is still risky in unpublished packages.
- ⚠️ `>=1.0` can admit `2.0`, `3.0`, or later breaking releases.
- ⚠️ Overly narrow ranges can be bad too; `~1.3` may conflict with another crate that correctly accepts `1.4`.
- ⚠️ Combining broad lower bounds with no upper compatibility boundary can make a previously valid lockfile update fail months later.
- ⚠️ Broad dev-dependency ranges can still break CI, examples, benches, and publish dry runs.

## See also
[[Cargo & Dependencies]] · [[Dependencies and Version Requirements]] · [[Semantic Versioning]] · [[Cargo.lock]] · [[cargo-audit and cargo-deny]] · [[Minimizing Dependencies]] · [[Cargo Workspaces]] · [[Feature Flags]] · [[Publishing to crates.io]]

## Sources
- The Cargo Book, "Version requirement syntax" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#version-requirement-syntax
- The Cargo Book, "Dependency Resolution: Recommendations" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html#recommendations
