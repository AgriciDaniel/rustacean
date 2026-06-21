---
type: pattern
title: "LTO and codegen-units"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, cargo, lto, codegen]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Profiles and Optimization Settings]]", "[[Codegen and Optimization Flags]]", "[[The inline Attribute]]", "[[Profiling Rust Programs]]", "[[Benchmarking with Criterion]]", "[[Avoiding Premature Optimization]]", "[[Performance & Optimization]]"]
sources: ["[[cargo-book]]", "[[rustc-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/profiles.html#lto", "https://doc.rust-lang.org/cargo/reference/profiles.html#codegen-units", "https://doc.rust-lang.org/rustc/codegen-options/index.html#lto", "https://doc.rust-lang.org/book/ch14-01-release-profiles.html"]
rust_version: "edition 2024 / 1.85+"
---

# LTO and codegen-units

LTO and `codegen-units` are Cargo profile knobs that trade compile time for more whole-program optimization, especially cross-crate inlining and optimization visibility.

## What it is
Link-time optimization, or LTO, lets optimization happen across crate and object boundaries at link time.
`codegen-units` controls how many separate chunks a crate is split into for code generation.
More units can compile in parallel faster.
Fewer units give the optimizer a larger view of the crate.

The default release profile already optimizes.
These knobs are for workloads where build time can be spent to chase runtime speed or binary size.
They are not guaranteed wins.
`thin` LTO is a common middle ground.
`fat` LTO is more aggressive and usually slower to compile.
`codegen-units = 1` maximizes within-crate optimization opportunity but reduces parallel code generation.

## How it works
Rust compiles crates separately, and Cargo profiles choose optimization settings.
Without LTO, each crate boundary can limit cross-crate optimization.
With LTO, LLVM can see more bodies at link time and may inline, remove dead code, or simplify generic instantiations across boundaries.
Reducing codegen units has a similar "larger optimization window" effect inside one crate.
Cargo's `lto = false` is not exactly "no LLVM LTO of any kind" in every optimized build: Cargo documents thin local LTO across codegen units for the local crate when applicable.
`lto = "off"` disables LTO more explicitly.
That distinction matters when comparing profiles because `codegen-units = 1` also changes the local-LTO story.

These settings interact with `#[inline]`.
Small public functions can use `#[inline]` to expose bodies across crates, but LTO attacks the problem globally.
For applications, trying LTO is often cleaner than adding inline attributes throughout the code.
For libraries, the library author still may mark tiny public wrappers `#[inline]` because downstream crates choose their own LTO settings.
The tradeoff is mostly build-time and code-size pressure.
More optimization visibility can reduce calls and dead code, but it can also duplicate hot helpers into many call sites.
Instruction-cache effects and linker time are workload-dependent, so keep LTO changes behind benchmark evidence and release-process tolerance.

## Example
```rust
pub fn parse_flag(input: &str) -> bool {
    matches!(input.trim(), "1" | "true" | "yes" | "on")
}

fn main() {
    assert!(parse_flag(" yes "));
    assert!(!parse_flag("off"));
}
```

The Rust code does not change when you evaluate LTO.
The experiment belongs in `Cargo.toml`:

```toml
[profile.release]
lto = "thin"
codegen-units = 1
```

Benchmark this as a build-configuration experiment.
If it helps, keep it with a comment explaining the measured tradeoff.
If it does not help, remove it and keep faster release builds.

## Worked example: separate profiling and shipping profiles
```toml
[profile.release]
lto = "thin"
codegen-units = 1

[profile.profiling]
inherits = "release"
debug = true
strip = false
```

The release profile is tuned for the shipped binary.
The profiling profile keeps the same optimization choices but preserves enough symbol information for [[Profiling Rust Programs]].
If the profiling profile changes `lto` or `codegen-units`, the profile may stop representing the shipped code.

## Common errors
Profile settings are read from the workspace root manifest.
Putting this in a dependency crate's manifest will not tune the final binary:

```text
warning: profiles for the non root package will be ignored, specify profiles at the workspace root
```

Move `[profile.release]` or custom `[profile.name]` settings to the root `Cargo.toml`.
Another common mistake is using a custom profile with an invalid or missing inheritance chain:

```text
error: profile `release-lto` is missing an `inherits` directive
```

Custom profiles should normally inherit from `release` or another built-in/profile-specific base so only the intended knobs change.

## Best practice
- ✅ Change one profile setting at a time and measure with [[Benchmarking with Criterion]] or an application benchmark.
- ✅ Try `lto = "thin"` before `lto = "fat"` for a common speed/build-time compromise.
- ✅ Use `codegen-units = 1` when runtime speed or binary size matters more than release build time.
- ✅ Keep a release-like profiling build with debug symbols when inspecting optimized code.
- ✅ Prefer profile-level optimization for applications before adding many `#[inline]` attributes.
- ✅ Use `lto = "off"` when the experiment specifically needs LTO disabled, not merely Cargo's default `false` behavior.
- ✅ Track binary size and release build time alongside runtime numbers; LTO can move costs into CI and deployment.
- ✅ Re-evaluate profile settings after major compiler or dependency upgrades because optimizer behavior changes.

## Pitfalls
- ⚠️ Assuming LTO always improves runtime is wrong; some programs regress or only change binary size.
- ⚠️ Turning on all knobs at once hides which setting mattered.
- ⚠️ Forgetting compile-time cost can make CI and release workflows painful.
- ⚠️ Using `target-cpu=native` for distributed binaries can produce executables that fail on older CPUs.
- ⚠️ Replacing algorithmic work with build flags is [[Speculative Micro-Optimization]] when the bottleneck is elsewhere.
- ⚠️ Comparing a stripped release binary against a debug-symbol profiling binary can confuse size and profiling conclusions.
- ⚠️ Library crates cannot force downstream applications to use their preferred LTO profile; design public APIs accordingly.

## See also
[[Profiles and Optimization Settings]] · [[Codegen and Optimization Flags]] · [[The inline Attribute]] · [[Profiling Rust Programs]] · [[Benchmarking with Criterion]] · [[Avoiding Premature Optimization]] · [[Speculative Micro-Optimization]] · [[Zero-Cost Abstractions]] · [[Performance & Optimization]]

## Sources
- The Cargo Book, "Profiles: lto" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html#lto
- The Cargo Book, "Profiles: codegen-units" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html#codegen-units
- The rustc Book, "Codegen options: lto" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html#lto
- The Rust Programming Language, ch. 14.1 "Customizing Builds with Release Profiles" — [[the-book]],
  https://doc.rust-lang.org/book/ch14-01-release-profiles.html
