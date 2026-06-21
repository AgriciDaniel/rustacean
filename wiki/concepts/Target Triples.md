---
type: concept
title: "Target Triples"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, targets, cross-compilation, compiler]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[The rustc Compiler]]", "[[Conditional Compilation (cfg)]]", "[[Codegen and Optimization Flags]]", "[[Inspecting rustc Configuration]]", "[[Build Scripts (build.rs)]]", "[[Cargo.toml Manifest]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/targets/index.html", "https://doc.rust-lang.org/rustc/platform-support.html"]
rust_version: "edition 2024 / 1.85+"
---

# Target Triples

A target triple is the string that tells `rustc` which architecture, vendor, operating system, ABI, and platform conventions to compile for.

## What it is
Targets describe the platform that the output artifact will run on.
Examples include `x86_64-unknown-linux-gnu`, `aarch64-apple-darwin`, and `wasm32-unknown-unknown`.
The rustc book calls Rust a cross-compiler by default: the compiler can be asked to build for targets other than the host, provided the target support and required libraries are available.

The "triple" name is historical; modern target strings can have more or fewer visible components.
Treat the full string as the target identity instead of parsing it casually.

## How it works
Use `--target` with `rustc` or Cargo to select a target.
`rustc --print target-list` lists built-in targets supported by that compiler.
Most targets need a compiled standard library for that target, and many need a platform linker or SDK.

The selected target controls built-in cfg values such as `target_arch`, `target_os`, `target_env`, `target_vendor`, `target_pointer_width`, `unix`, and `windows`.
It also influences default linker flavor, panic strategy availability, relocation behavior, CPU features, and ABI details.

Custom targets are possible through JSON target specifications, but their properties are unstable.
Pin the compiler version when using custom targets.
The host triple and target triple are different concepts.
The host is where the compiler itself runs; the target is where the produced binary is intended to run.
If no `--target` is supplied, the target defaults to the host.

Target support is tiered.
Some targets have full standard-library and CI guarantees, while others may require building `core`/`alloc`, supplying a linker, or accepting limited test coverage.
Always check the platform support status before treating a target as production-ready.

## Example
```rust
fn main() {
    println!("arch: {}", std::env::consts::ARCH);
    println!("os: {}", std::env::consts::OS);
}
```

Inspect targets and cfgs with:

```bash
rustc --print target-list
rustc --print cfg --target wasm32-unknown-unknown
```

Host and target can be inspected separately:

```bash
rustc --print host-tuple
cargo build --target x86_64-unknown-linux-musl
rustc --print target-libdir --target x86_64-unknown-linux-musl
```

The target library directory tells you whether `rustc` can find standard-library artifacts for that target.

## Common errors
Missing target standard-library artifacts produce an `E0463` diagnostic:

```text
error[E0463]: can't find crate for `std`
  = note: the target may not be installed
```

With rustup-managed toolchains, install the target with `rustup target add <triple>`.
For custom or no-std targets, configure how `core`, `alloc`, or `std` is built.

Linker problems appear later, after Rust code has compiled:

```text
error: linker `cc` not found
```

or:

```text
error: linking with `cc` failed: exit status: 1
```

Fix the platform linker, SDK, C runtime, or Cargo target configuration.
Changing Rust source rarely fixes a missing cross-linker.

## Best practice
- ✅ Use the exact target string accepted by `rustc --print target-list`.
- ✅ Install the target standard library with `rustup target add <triple>` when using rustup-managed targets.
- ✅ Inspect target cfgs rather than guessing from the triple text.
- ✅ Keep linker and SDK configuration in Cargo config or CI setup instead of hard-coding it in source.
- ✅ Pin the compiler when relying on custom target JSON.
- ✅ Distinguish `rustc --print host-tuple` from the selected `--target` in bug reports and CI logs.
- ✅ Check platform support tiers and standard-library availability before promising binary support to users.

## Pitfalls
- ⚠️ Assuming cross-compilation only needs `--target`; the linker, C toolchain, SDK, or standard library may also be required.
- ⚠️ Matching `target_os` when `target_family` is the actual portability boundary.
- ⚠️ Enabling target features globally without proving every deployment CPU supports them.
- ⚠️ Treating a custom target JSON schema as stable across compiler versions.
- ⚠️ Parsing triples with string splits in build scripts; ask `rustc --print cfg --target ...` for semantic cfg values.
- ⚠️ Assuming `wasm32-unknown-unknown` has OS services, threads, files, or sockets just because the crate builds.

## See also
[[The rustc Compiler]] · [[Conditional Compilation (cfg)]] · [[Codegen and Optimization Flags]] · [[Inspecting rustc Configuration]] · [[Build Scripts (build.rs)]] · [[Cargo.toml Manifest]] · [[Profiles and Optimization Settings]] · [[Feature Flags]] · [[Panic Unwinding and Abort]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Targets" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/targets/index.html
- The rustc book, "Platform Support" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support.html
