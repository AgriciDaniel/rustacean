---
type: concept
title: "Semantic Versioning"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, semver, api]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Dependencies and Version Requirements]]", "[[Publishing to crates.io]]", "[[Feature Flags]]", "[[MSRV Policy]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/semver.html", "https://doc.rust-lang.org/cargo/reference/resolver.html#semver-compatibility"]
rust_version: "edition 2024 / 1.85+"
---

# Semantic Versioning

Semantic Versioning is the compatibility contract Cargo assumes when it decides which dependency updates are safe to select automatically.

## What it is
Rust crates use versions shaped like `MAJOR.MINOR.PATCH`. Cargo assumes that releases within the same compatible range do not break existing users.

For `1.2.3`, compatible updates are `>=1.2.3, <2.0.0`. For `0.2.3`, compatible updates are `>=0.2.3, <0.3.0`; Cargo treats the left-most non-zero component as the compatibility boundary.

The Cargo SemVer reference classifies API, trait, type, feature, dependency, platform, and MSRV changes as major, minor, or possibly breaking.

## How it works
SemVer is enforced socially, but Cargo's resolver relies on it mechanically. If a crate publishes a breaking change as a patch or minor release, users can receive it through a normal `cargo update`.

Public API shape matters: removing public items, adding variants to a non-`#[non_exhaustive]` enum, adding a non-defaulted trait method, or tightening a generic bound can break downstream builds.

Cargo features are part of the compatibility surface. Adding a feature is usually minor; removing one, moving existing public API behind a feature, or removing a feature from the default set can be breaking.

Compatibility is checked from the downstream user's point of view, not only from the crate's own test suite. Adding a blanket trait impl, changing auto-trait behavior by adding `Rc` or `UnsafeCell` to a public type, or changing a dependency type exposed in function signatures can break code that compiled before.

Cargo treats all `1.x` releases of the same crate source as candidates for one compatible version line, but it can compile multiple incompatible major versions in the same graph. Those versions are distinct crates to the type system; `foo::Id` from `foo 1` and `foo::Id` from `foo 2` are unrelated types even if their source looks identical.

## Example
```rust
#[non_exhaustive]
pub enum ParseMode {
    Strict,
    Lenient,
}

pub fn parse_mode_name(mode: ParseMode) -> &'static str {
    match mode {
        ParseMode::Strict => "strict",
        ParseMode::Lenient => "lenient",
    }
}

fn main() {
    assert_eq!(parse_mode_name(ParseMode::Strict), "strict");
}
```

Starting with `#[non_exhaustive]` preserves room to add variants later without forcing downstream exhaustive matches.

## Edge case example
```rust
pub trait Store {
    fn get(&self, key: &str) -> Option<String>;

    fn contains(&self, key: &str) -> bool {
        self.get(key).is_some()
    }
}

struct MemoryStore;

impl Store for MemoryStore {
    fn get(&self, key: &str) -> Option<String> {
        (key == "answer").then(|| "42".to_owned())
    }
}

fn main() {
    let store = MemoryStore;
    assert!(store.contains("answer"));
}
```

Adding `contains` with a default body is usually compatible. Adding the same required method without a default would force every downstream `impl Store` to change and is a breaking API change.

## Common errors
```text
error[E0046]: not all trait items implemented, missing: `contains`
```

Fix: if you maintain the trait, add a default method body when possible and release it as a minor change. If a default is impossible, plan a major version bump.

```text
error[E0004]: non-exhaustive patterns: `_` not covered
```

Fix: downstream users should add a wildcard arm when matching non-exhaustive types. Maintainers should mark public enums `#[non_exhaustive]` before they need that extension point.

## Best practice
- ✅ Design public enums and structs for growth with `#[non_exhaustive]` or private fields where appropriate.
- ✅ Add default implementations to new trait methods when compatibility permits.
- ✅ Treat feature removal, public API removal, and MSRV raises as release-policy decisions, not incidental edits.
- ✅ Run SemVer checks before publishing when a crate has downstream users.
- ✅ Consider dependency upgrades SemVer-relevant when dependency types appear in your public API.
- ✅ Document compatibility policy for pre-1.0 crates because Cargo treats `0.x` compatibility more narrowly than `1.x`.

## Pitfalls
- ⚠️ Assuming "it still compiles here" means the release is SemVer-compatible; downstream generic bounds, glob imports, and trait impls may see different breakage.
- ⚠️ Publishing a breaking patch release forces users to pin or wait for a yank; see [[Cargo.lock]] for how applications contain the damage.
- ⚠️ Removing optional dependencies can be breaking because optional dependencies create implicit features; see [[Feature Flags]].
- ⚠️ Adding trait impls can break downstream code through method ambiguity or coherence conflicts, even though it feels purely additive.
- ⚠️ Raising `rust-version` may be allowed by your policy, but users experience it as a build compatibility change. See [[MSRV Policy]].

## See also
[[Cargo & Dependencies]] · [[Dependencies and Version Requirements]] · [[Publishing to crates.io]] · [[Feature Flags]] · [[Cargo.lock]] · [[MSRV Policy]] · [[Non-Additive Feature Flags]] · [[Overbroad Version Requirements]] · [[Cargo.toml Manifest]]

## Sources
- The Cargo Book, "SemVer Compatibility" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/semver.html
- The Cargo Book, "Dependency Resolution: SemVer compatibility" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html#semver-compatibility
