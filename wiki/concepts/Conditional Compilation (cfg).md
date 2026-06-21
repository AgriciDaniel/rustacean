---
type: concept
title: "Conditional Compilation (cfg)"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cfg, conditional-compilation, compiler]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Target Triples]]", "[[Enforcing Expected cfgs]]", "[[Unchecked cfg Names]]", "[[Feature Flags]]", "[[The rustc Compiler]]", "[[Lints and Lint Levels]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/check-cfg.html", "https://doc.rust-lang.org/reference/conditional-compilation.html"]
rust_version: "edition 2024 / 1.85+"
---

# Conditional Compilation (cfg)

Conditional compilation selects Rust items, expressions, and attributes at compile time using `#[cfg(...)]`, `cfg!(...)`, Cargo features, target facts, and custom compiler configuration values.

## What it is
`cfg` is Rust's compile-time configuration mechanism.
It is commonly used for platform-specific code, optional features, test-only code, documentation-only code, and target capabilities.
The compiler knows many target cfgs such as `target_os`, `target_arch`, `target_family`, `target_pointer_width`, `unix`, and `windows`.

`#[cfg(...)]` removes or keeps code before normal compilation of that code.
`cfg!(...)` evaluates to a boolean constant but both branches of surrounding Rust code must still be syntactically and type-correct.

## How it works
`rustc --cfg name` activates a bare cfg like `#[cfg(name)]`.
`rustc --cfg 'feature="serde"'` activates a key-value cfg like `#[cfg(feature = "serde")]`.
Cargo sets `feature = "..."` cfgs for enabled Cargo features.

Use `--check-cfg` or Cargo's lint configuration to declare expected custom cfg names and values.
Without checking, a typo like `#[cfg(widnows)]` silently evaluates to false, which can hide entire code paths.

Target cfgs are derived from the selected [[Target Triples]] and compiler target specification.
Inspect active cfg values with `rustc --print cfg` or `rustc --print cfg --target <triple>`.
The condition language supports names, key-value pairs, `all(...)`, `any(...)`, and `not(...)`.
A cfg option is either set or not set; key-value cfgs can have multiple values set at once, such as multiple `target_feature` values.

`#[cfg_attr(condition, attr)]` conditionally applies attributes.
This is useful for target-specific `path`, lint, link, or documentation attributes without duplicating the item.
Remember that all tokens still need to parse far enough for attributes and macro expansion, but code removed by `#[cfg]` is not type-checked for the inactive configuration.

## Example
```rust
fn platform_name() -> &'static str {
    if cfg!(target_os = "windows") {
        "windows"
    } else if cfg!(target_family = "unix") {
        "unix-like"
    } else {
        "other"
    }
}

fn main() {
    println!("{}", platform_name());
}
```

Use `#[cfg]` when a branch imports platform-only APIs:

```rust
#[cfg(windows)]
fn path_separator() -> char {
    '\\'
}

#[cfg(not(windows))]
fn path_separator() -> char {
    '/'
}

fn main() {
    println!("{}", path_separator());
}
```

The inactive function is removed before type checking, so each implementation can use APIs that only exist on that platform.

## Common errors
Using `cfg!` to guard code that does not type-check everywhere still fails:

```text
error[E0433]: failed to resolve: could not find `windows` in `os`
```

Fix it by moving platform-specific imports and items behind `#[cfg(...)]`.
Use `cfg!(...)` only when both sides are valid Rust for every target being compiled.

With cfg checking enabled, misspellings become lint diagnostics:

```text
warning: unexpected `cfg` condition name: `widnows`
  = note: `#[warn(unexpected_cfgs)]` on by default
```

Fix the spelling or declare the custom cfg through [[Enforcing Expected cfgs]].
Do not silence the warning unless the cfg contract is intentionally broader than the checker knows.

## Best practice
- ✅ Keep platform-specific code behind small, named functions instead of scattering large `#[cfg]` blocks through business logic.
- ✅ Use Cargo features for additive optional behavior; see [[Feature Flags]].
- ✅ Declare custom cfgs with [[Enforcing Expected cfgs]] so typos become `unexpected_cfgs` warnings.
- ✅ Use `cfg!(...)` only when both paths are valid for all configurations; use `#[cfg]` to remove invalid platform code.
- ✅ Inspect active cfg values with [[Inspecting rustc Configuration]] when cross-compiling.
- ✅ Prefer `target_family = "unix"` or `windows` when the boundary is a platform family, not one specific OS.
- ✅ Keep `cfg_attr` small and local; if the attributes get complex, split the item into named cfg-specific modules.

## Pitfalls
- ⚠️ Misspelling a cfg name and silently compiling the wrong code; see [[Unchecked cfg Names]].
- ⚠️ Using `cfg!(...)` to guard code that only type-checks on one platform.
- ⚠️ Creating mutually exclusive feature cfgs when Cargo features should be additive; see [[Non-Additive Feature Flags]].
- ⚠️ Assuming a target triple component maps exactly to a cfg value without checking `rustc --print cfg`.
- ⚠️ Treating custom cfgs as user-facing feature flags; Cargo features are usually more discoverable for crate consumers.
- ⚠️ Forgetting that inactive cfg branches can rot unless CI builds the relevant targets and feature combinations.

## See also
[[Target Triples]] · [[Enforcing Expected cfgs]] · [[Unchecked cfg Names]] · [[Feature Flags]] · [[Non-Additive Feature Flags]] · [[The rustc Compiler]] · [[Lints and Lint Levels]] · [[Inspecting rustc Configuration]] · [[Build Scripts (build.rs)]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Checking conditional configurations" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/check-cfg.html
- The Rust Reference, "Conditional compilation" — [[the-reference]],
  https://doc.rust-lang.org/reference/conditional-compilation.html
