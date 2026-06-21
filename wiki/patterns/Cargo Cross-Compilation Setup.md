---
type: pattern
title: "Cargo Cross-Compilation Setup"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, cross-compilation, targets, tooling]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[Target Triples]]", "[[Rust WebAssembly Targets]]", "[[Target-Specific cfg Boundaries]]", "[[Target Features and CPU Baselines]]", "[[Cargo Build Run Check Test]]"]
sources: ["[[embedded-book]]", "[[rustc-book]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/start/qemu.html#cross-compiling", "https://doc.rust-lang.org/cargo/reference/config.html", "https://doc.rust-lang.org/rustc/targets/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo Cross-Compilation Setup

Use `.cargo/config.toml` to make cross-compilation reproducible: pin the target, linker, runner, and target-specific rustflags outside source code, then build with `cargo build --target <triple>` or a configured default.

## What it is
Cross-compilation builds code for a target different from the host running Cargo.
Rust supports this directly through [[Target Triples]].
Cargo adds project-level configuration for target-specific build behavior.
The Embedded Rust Book demonstrates this with a default ARM target in `.cargo/config.toml`.
The Cargo Book documents `[target.<triple>]` and `[target.'cfg(...)']` tables for linkers, runners, rustflags, and rustdocflags.

This pattern keeps build policy out of Rust modules.
It makes CI, local development, and release builds agree.
It also prevents accidental host builds when a project is intended to produce firmware or wasm artifacts.

## How it works
The moving parts are:
- install the Rust target with `rustup target add <triple>` when rustup ships it
- set `[build] target = "<triple>"` only when the repository has one dominant target
- set `[target.<triple>] linker = "..."`
- set `[target.<triple>] runner = "..."`
- set `[target.<triple>] rustflags = [...]` for target-specific codegen details
- prefer `[target.'cfg(...)']` when a whole family shares a runner or flags

Cargo only passes target rustflags to the target side when `--target` or `build.target` is used.
That matters because build scripts and proc macros are compiled for the host.
It avoids poisoning host tools with flags meant for embedded or wasm code.

## Example
```rust
pub fn target_label() -> &'static str {
    if cfg!(all(target_family = "wasm", target_os = "unknown")) {
        "wasm32-unknown-unknown"
    } else if cfg!(all(target_os = "none", target_arch = "arm")) {
        "bare-metal arm"
    } else {
        "host or other target"
    }
}

fn main() {
    println!("{}", target_label());
}
```

Example `.cargo/config.toml`:

```toml
[build]
target = "wasm32-unknown-unknown"

[target.wasm32-unknown-unknown]
runner = "wasm-bindgen-test-runner"

[target.'cfg(all(target_arch = "arm", target_os = "none"))']
runner = "probe-rs run --chip STM32F303VCTx"
rustflags = ["-C", "link-arg=-Tlink.x"]
```

## Best practice
- ✅ Commit project-specific target configuration when the target is part of the project contract.
- ✅ Keep personal paths and secrets out of committed config; use environment variables for those.
- ✅ Use exact triples from `rustc --print target-list`.
- ✅ Use `rustc --print cfg --target <triple>` when designing cfg gates.
- ✅ Keep linker scripts, memory maps, and runners documented next to target setup.
- ✅ Build all supported targets in CI, even if some tests only run on the host.

## Pitfalls
- ⚠️ Assuming `cargo build --target` installs the target; use `rustup target add` first.
- ⚠️ Forgetting the C linker, SDK, or runtime needed by targets with native dependencies.
- ⚠️ Using global `RUSTFLAGS` for project policy and accidentally affecting build scripts.
- ⚠️ Setting one default target in a workspace that contains host-only tools.
- ⚠️ Using `cfg!(...)` in source when `#[cfg]` item selection is needed.

## See also
[[Target Triples]]
[[Rust WebAssembly Targets]]
[[Target-Specific cfg Boundaries]]
[[Target Features and CPU Baselines]]
[[Cargo Build Run Check Test]]
[[Cargo.toml Manifest]]
[[Build Scripts (build.rs)]]
[[Inspecting rustc Configuration]]
[[Profiles and Optimization Settings]]
[[WebAssembly, no_std & Targets]]

## Sources
- The Embedded Rust Book, "Cross compiling" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/qemu.html#cross-compiling
- The Cargo Book, "Configuration" - [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/config.html
- The rustc book, "Targets" - [[rustc-book]],
  https://doc.rust-lang.org/rustc/targets/index.html
