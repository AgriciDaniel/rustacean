---
type: pattern
title: "Enforcing Expected cfgs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cfg, lints, check-cfg]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Conditional Compilation (cfg)]]", "[[Unchecked cfg Names]]", "[[Lints and Lint Levels]]", "[[Feature Flags]]", "[[Build Scripts (build.rs)]]", "[[Target Triples]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/check-cfg.html", "https://doc.rust-lang.org/rustc/check-cfg/cargo-specifics.html"]
rust_version: "edition 2024 / 1.85+"
---

# Enforcing Expected cfgs

Declare custom cfg names and values with `--check-cfg`, Cargo lint configuration, or `cargo::rustc-check-cfg` so misspelled conditional compilation paths warn instead of disappearing silently.

## What it is
`--check-cfg` configures the compiler to check reachable `#[cfg]`, `#[cfg_attr]`, `#[link(..., cfg(...))]`, and `cfg!(...)` conditions against expected names and values.
Unexpected conditions trigger the `unexpected_cfgs` lint, which warns by default.

Cargo automatically declares feature cfgs from the `[features]` table.
For custom cfgs, you should declare the expected cfg contract yourself.

## How it works
For direct `rustc`, pass `--check-cfg 'cfg(name)'` for a bare cfg or `--check-cfg 'cfg(name, values("a", "b"))'` for key-value cfgs.
At least one `--check-cfg` argument also brings in rustc's well-known cfg names and values.

For Cargo projects with static custom cfgs, use the `[lints.rust]` table.
For build-script-produced cfgs, print both `cargo::rustc-check-cfg=...` and, conditionally, `cargo::rustc-cfg=...`.
The check declaration should be unconditional so all expected names are known even when the cfg is not active.
The `unexpected_cfgs` lint checks reachable cfg expressions in the local package.
Cargo automatically supplies expected cfgs for declared features, but it cannot infer arbitrary names a build script may print later unless the build script declares them.
For key-value cfgs, prefer listing the accepted values instead of `values(any())` so stale values are caught.

## Example
```rust
#[cfg(has_fast_mode)]
fn mode() -> &'static str {
    "fast"
}

#[cfg(not(has_fast_mode))]
fn mode() -> &'static str {
    "portable"
}

fn main() {
    println!("{}", mode());
}
```

Cargo static configuration:

```toml
[lints.rust]
unexpected_cfgs = { level = "warn", check-cfg = ['cfg(has_fast_mode)'] }
```

Build-script-produced cfgs should declare the contract unconditionally:

```rust
fn main() {
    println!("cargo::rustc-check-cfg=cfg(storage_backend, values(\"sqlite\", \"memory\"))");

    if std::env::var_os("CARGO_FEATURE_SQLITE").is_some() {
        println!("cargo::rustc-cfg=storage_backend=\"sqlite\"");
    } else {
        println!("cargo::rustc-cfg=storage_backend=\"memory\"");
    }
}
```

Then source can rely on checked values:

```rust
#[cfg(storage_backend = "sqlite")]
fn backend_name() -> &'static str {
    "sqlite"
}

#[cfg(storage_backend = "memory")]
fn backend_name() -> &'static str {
    "memory"
}
```

## Common errors
Enabling a cfg is not the same as declaring it expected:

```text
warning: unexpected `cfg` condition name: `has_fast_mode`
  = note: `#[warn(unexpected_cfgs)]` on by default
```

Fix it by adding `--check-cfg 'cfg(has_fast_mode)'`, `[lints.rust]` configuration, or `cargo::rustc-check-cfg=cfg(has_fast_mode)`.

A misspelled expected value is reported when values are checked:

```text
warning: unexpected `cfg` condition value: `sqltie`
```

Fix the spelling in the source or the build script.
Avoid `values(any())` unless arbitrary values are genuinely part of the contract.

## Best practice
- ✅ Declare every custom cfg your crate intentionally uses.
- ✅ Put static cfg expectations in `Cargo.toml` under `[lints.rust]`.
- ✅ In `build.rs`, always print `cargo::rustc-check-cfg` next to any possible `cargo::rustc-cfg`.
- ✅ Use named cfgs sparingly; Cargo features and target cfgs are easier for users to discover.
- ✅ Consider raising `unexpected_cfgs` to `deny` in CI once the project is clean.
- ✅ Declare expected values for key-value cfgs, not only the cfg name.
- ✅ Keep build-script cfg names stable and documented because downstream users may see them in diagnostics.
- ✅ Pair expected-cfg enforcement with CI jobs that compile important feature and target combinations.

## Pitfalls
- ⚠️ Passing `--cfg foo` and assuming that also declares `foo` as expected; it does not.
- ⚠️ Emitting `cargo::rustc-check-cfg` only inside the branch that enables the cfg.
- ⚠️ Allowing `values(any())` when the real value set is known.
- ⚠️ Letting misspellings compile as disabled code; see [[Unchecked cfg Names]].
- ⚠️ Declaring a cfg in `Cargo.toml` and then spelling a different cfg from `build.rs`.
- ⚠️ Treating `unexpected_cfgs` as a substitute for compiling inactive branches; it checks names and values, not type correctness.

## See also
[[Conditional Compilation (cfg)]] · [[Unchecked cfg Names]] · [[Lints and Lint Levels]] · [[Feature Flags]] · [[Build Scripts (build.rs)]] · [[Target Triples]] · [[The rustc Compiler]] · [[Inspecting rustc Configuration]] · [[Cargo.toml Manifest]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Checking conditional configurations" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/check-cfg.html
- The rustc book, "Cargo Specifics - Checking Conditional Configurations" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/check-cfg/cargo-specifics.html
