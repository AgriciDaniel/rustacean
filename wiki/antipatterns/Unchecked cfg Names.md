---
type: antipattern
title: "Unchecked cfg Names"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cfg, lints, footgun]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Conditional Compilation (cfg)]]", "[[Enforcing Expected cfgs]]", "[[Lints and Lint Levels]]", "[[Target Triples]]", "[[Feature Flags]]", "[[Build Scripts (build.rs)]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/check-cfg.html", "https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#unexpected-cfgs"]
rust_version: "edition 2024 / 1.85+"
---

# Unchecked cfg Names

Unchecked cfg names turn typos and stale platform assumptions into silently disabled code; declare expected cfgs so `unexpected_cfgs` catches mistakes.

## The mistake
Writing custom or platform cfgs without `--check-cfg` allows misspellings to compile.
For example, `#[cfg(widnows)]` is just a cfg name that is not set.
Without checking, the compiler treats that condition as false and removes the code.

This is dangerous because the broken branch may be exactly the platform-specific branch you cannot test locally.
It is also common in feature-heavy crates where optional code is only built in some CI jobs.

## Why it happens
Conditional compilation happens before normal type checking of removed items.
That is useful for platform-specific APIs, but it means wrong cfg names can hide code entirely.
Historically, custom cfgs were often passed with `--cfg` or emitted by build scripts without a parallel declaration of the expected names.

Rust now has `--check-cfg` and the `unexpected_cfgs` lint to make cfg contracts explicit.
Cargo also has specific support for static cfg declarations in `[lints.rust]` and dynamic build-script declarations.
The compiler only type-checks code that survives conditional compilation for the current configuration.
That means unchecked cfg names create two separate risks: a misspelled condition may disable the intended code, and an inactive branch may keep compiling in nobody's CI until a user selects that target or feature.
Checked cfgs solve the first risk; target and feature CI still solve the second.

## Example
```rust
#[cfg(has_widget)]
fn widget_status() -> &'static str {
    "enabled"
}

#[cfg(not(has_widget))]
fn widget_status() -> &'static str {
    "disabled"
}

fn main() {
    println!("{}", widget_status());
}
```

Correct Cargo lint configuration:

```toml
[lints.rust]
unexpected_cfgs = { level = "warn", check-cfg = ['cfg(has_widget)'] }
```

Misspelled platform cfgs are the same class of bug:

```rust
#[cfg(target_os = "linux")]
fn socket_backend() -> &'static str {
    "epoll"
}

#[cfg(target_oss = "linux")]
fn typo_backend() -> &'static str {
    "this branch is never selected"
}
```

With cfg checking enabled, `target_oss` warns instead of silently acting like a custom cfg that is not set.

## Common errors
The checked-cfg diagnostic names the unexpected condition:

```text
warning: unexpected `cfg` condition name: `target_oss`
  = help: there is a config with a similar name and value
```

Fix the spelling to `target_os` or remove the stale branch.

For custom cfgs, the warning often means the build script enabled a cfg but did not declare it:

```text
warning: unexpected `cfg` condition name: `has_widget`
```

Add a matching `cargo::rustc-check-cfg=cfg(has_widget)` line or static `[lints.rust]` declaration.

For key-value cfgs, unexpected values should be fixed at the producer:

```text
warning: unexpected `cfg` condition value: `prodution`
```

Correct the emitted value or widen the declared value list only if the new value is intentional.

## Best practice
- ✅ Use [[Enforcing Expected cfgs]] for every custom cfg.
- ✅ Prefer Cargo features for user-facing optional compilation.
- ✅ Run CI with important feature and target combinations.
- ✅ Inspect target cfgs with [[Inspecting rustc Configuration]] before writing platform conditions.
- ✅ Raise `unexpected_cfgs` to `deny` once the project has declared all intentional cfgs.
- ✅ Use value-checked declarations for custom modes like `backend = "sqlite"` rather than accepting arbitrary strings.
- ✅ Keep cfg declarations near their producers: static custom cfgs in `Cargo.toml`, dynamic ones in `build.rs`.
- ✅ Combine checked cfgs with CI coverage for important inactive branches.

## Pitfalls
- ⚠️ Assuming `--cfg has_widget` is enough; it enables the cfg but does not declare the expected cfg contract.
- ⚠️ Trusting untested `#[cfg]` branches to compile.
- ⚠️ Using `cfg!(...)` where `#[cfg(...)]` is needed to remove invalid platform code.
- ⚠️ Creating cfg names that overlap confusingly with Cargo feature names.
- ⚠️ Silencing `unexpected_cfgs` after the first warning instead of declaring the cfg contract.
- ⚠️ Using unchecked custom cfgs for public crate features that should be visible in the `[features]` table.

## See also
[[Conditional Compilation (cfg)]] · [[Enforcing Expected cfgs]] · [[Lints and Lint Levels]] · [[Target Triples]] · [[Feature Flags]] · [[Build Scripts (build.rs)]] · [[Non-Additive Feature Flags]] · [[Inspecting rustc Configuration]] · [[Silencing Edition Migration Lints]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Checking conditional configurations" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/check-cfg.html
- The rustc lint listing, "`unexpected_cfgs`" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#unexpected-cfgs
