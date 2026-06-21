---
type: antipattern
title: "Non-Additive Feature Flags"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, features, semver]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Feature Flags]]", "[[Semantic Versioning]]", "[[Dependencies and Version Requirements]]", "[[Minimizing Dependencies]]"]
sources: ["[[cargo-book]]", "[[tooling-project-hygiene]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/features.html#feature-unification", "https://doc.rust-lang.org/cargo/reference/features.html#mutually-exclusive-features"]
rust_version: "edition 2024 / 1.85+"
---

# Non-Additive Feature Flags

Non-additive features are Cargo feature flags that disable, replace, or make incompatible behavior when enabled; they fight Cargo's feature unification model.

## The mistake
The common mistake is modeling features as mutually exclusive modes: `std` versus `no_std`, `backend-a` versus `backend-b`, or `fast` versus `safe`.

Because Cargo unifies features with a union, a transitive dependency can enable a feature you did not select directly. If enabling one feature disables another code path, a graph that compiles for one user can fail for another.

## Why it happens
Feature flags feel like build settings, but Cargo treats them as additive capabilities on a package. There is no global solver that lets each dependent choose a separate feature set for the same dependency in the same build.

The right model is usually: defaults provide the common capability, opt-out removes defaults with `default-features = false`, and named features add extra APIs or implementations.

If features truly cannot coexist, split packages, make the runtime choice explicit, or add a clear `compile_error!` so the failure is immediate and diagnosable.

Feature unification means the failure may be caused by another crate several edges away. Your direct manifest may enable only `backend_a`, but another dependency can enable `backend_b` on the same package, and Cargo will build one package instance with both features.

Resolver 2 and resolver 3 reduce some accidental unification across target, build, and dev contexts, but they do not change the core rule for a selected package: active features are a union. Design as if every feature combination you publish can be selected by someone.

## Example
```rust
#[cfg(all(feature = "backend_a", feature = "backend_b"))]
compile_error!("features backend_a and backend_b cannot be enabled together");

#[cfg(feature = "backend_a")]
fn backend_name() -> &'static str { "a" }

#[cfg(all(not(feature = "backend_a"), feature = "backend_b"))]
fn backend_name() -> &'static str { "b" }

#[cfg(not(any(feature = "backend_a", feature = "backend_b")))]
fn backend_name() -> &'static str { "default" }

fn main() {
    assert!(!backend_name().is_empty());
}
```

The example compiles by default and fails clearly only if the mutually exclusive features are both enabled.

## Better design example
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Backend {
    Default,
    A,
    B,
}

fn connect(backend: Backend) -> &'static str {
    match backend {
        Backend::Default => "default",
        Backend::A => "a",
        Backend::B => "b",
    }
}

fn main() {
    assert_eq!(connect(Backend::A), "a");
}
```

When both backends can be compiled into the same binary, make backend choice a runtime configuration value. Reserve Cargo features for adding backend implementations or dependencies.

## Common errors
```text
error: features `backend_a` and `backend_b` cannot be enabled together
```

Fix: if exclusivity is unavoidable, keep the `compile_error!` clear and document which dependency enables each feature. Prefer separate crates or runtime selection for widely used libraries.

```text
error[E0428]: the name `connect` is defined multiple times
```

Fix: avoid defining the same item in separate feature blocks that can both be active. Use additive modules, trait implementations, or a single function that dispatches based on available capabilities.

## Best practice
- ✅ Prefer additive features that only add APIs, dependencies, implementations, or faster code paths.
- ✅ Model `std` support as a `std` feature enabled by default, not as a `no_std` feature.
- ✅ Document every public feature and test the feature combinations users are likely to build.
- ✅ Use runtime configuration or separate crates when users need exclusive backends.
- ✅ Hide internal optional dependency names with `dep:name` so the public feature set reflects capabilities, not implementation details.
- ✅ Test `--no-default-features`, each important feature, and representative combinations in CI, not only `--all-features`.

## Pitfalls
- ⚠️ Removing a feature from the default list can be SemVer-breaking; see [[Semantic Versioning]].
- ⚠️ Moving existing public items behind a new feature breaks users who did not have to enable it before.
- ⚠️ `--all-features` may trigger combinations that require explicit compile errors or architectural changes.
- ⚠️ A feature named `no_std` is usually backwards: enabling it removes capability instead of adding one.
- ⚠️ Depending on feature activation order is impossible; Cargo features are an unordered set.

## See also
[[Cargo & Dependencies]] · [[Feature Flags]] · [[Semantic Versioning]] · [[Dependencies and Version Requirements]] · [[Minimizing Dependencies]] · [[Cargo Workspaces]] · [[Overbroad Version Requirements]] · [[Cargo.toml Manifest]] · [[MSRV Policy]]

## Sources
- The Cargo Book, "Feature unification" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/features.html#feature-unification
- The Cargo Book, "Mutually exclusive features" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/features.html#mutually-exclusive-features
