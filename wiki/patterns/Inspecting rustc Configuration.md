---
type: pattern
title: "Inspecting rustc Configuration"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustc, diagnostics, targets]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[The rustc Compiler]]", "[[Target Triples]]", "[[Conditional Compilation (cfg)]]", "[[Codegen and Optimization Flags]]", "[[Lints and Lint Levels]]", "[[Cargo.toml Manifest]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/print.html#print-options", "https://doc.rust-lang.org/rustc/command-line-arguments.html#--print-print-compiler-information"]
rust_version: "edition 2024 / 1.85+"
---

# Inspecting rustc Configuration

Use `rustc --print ...`, `rustc -C help`, `rustc -W help`, and verbose Cargo builds to inspect the compiler, target, cfg, lint, and codegen settings before guessing.

## What it is
`rustc` can print its view of the compilation environment.
This is often the fastest way to answer questions about active cfgs, known targets, sysroot paths, target CPU names, target features, relocation models, and lint names.

Inspection commands are read-only diagnostics.
They help debug cross-compilation, feature gates, unexpected cfg behavior, linker failures, and build-system integrations.

## How it works
`--print` accepts named print options such as `cfg`, `target-list`, `sysroot`, `target-libdir`, `host-tuple`, `target-cpus`, and `target-features`.
Adding `--target <triple>` changes target-sensitive output.

`rustc -C help` lists codegen options for the exact compiler.
`rustc -W help` lists lints and lint groups.
`cargo build --verbose` shows the actual `rustc` commands Cargo executes.

This avoids relying on stale documentation snippets or assumptions about the host platform.
Inspection commands are target-sensitive when they involve cfgs, libraries, CPU features, or linker behavior.
Always include `--target` when debugging a non-host build.
For Cargo, inspect both the high-level manifest/profile settings and the final verbose `rustc` line because environment variables such as `RUSTFLAGS` can still affect the invocation.

## Example
```rust
fn main() {
    println!("arch={} os={}", std::env::consts::ARCH, std::env::consts::OS);
}
```

Useful inspection commands:

```bash
rustc --print cfg
rustc --print cfg --target wasm32-unknown-unknown
rustc --print target-list
rustc -C help
rustc -W help
cargo build --verbose
```

For cross-compilation or codegen work, capture the target-specific view:

```bash
rustc --print host-tuple
rustc --print target-libdir --target aarch64-unknown-linux-gnu
rustc --print target-cpus --target x86_64-unknown-linux-gnu
rustc --print target-features --target x86_64-unknown-linux-gnu
cargo build --target aarch64-unknown-linux-gnu --verbose
```

These commands separate "what machine am I on?" from "what machine am I building for?"

## Common errors
Using the host cfg output for a cross-target bug leads to false conclusions.
The symptom is usually source that appears correct locally but is removed or included in CI:

```text
warning: unexpected `cfg` condition name: `target_oss`
```

Run `rustc --print cfg --target <triple>` and fix the cfg spelling or target assumption.

An unavailable target library directory usually precedes an `E0463` compile failure:

```text
error[E0463]: can't find crate for `std`
```

Check `rustc --print target-libdir --target <triple>`.
If the directory is missing standard-library artifacts, install or build the target before debugging application code.

Unknown codegen choices should be verified against the exact compiler:

```text
error: incorrect value `native-ish` for codegen option `target-cpu`
```

Use `rustc --print target-cpus --target <triple>` or `rustc -C help` instead of copying values from another toolchain.

## Best practice
- ✅ Inspect `cfg` output for the selected target before writing target-specific conditions.
- ✅ Use `rustc --print target-list` to validate target names in CI matrices.
- ✅ Use `rustc -W help` when enabling migration lints manually.
- ✅ Use `rustc -C help` before relying on a codegen option in custom build scripts.
- ✅ Record important target and linker assumptions in project build documentation.
- ✅ Include the toolchain version, host tuple, target tuple, and active cfg output in difficult compiler bug reports.
- ✅ Check verbose Cargo output when `RUSTFLAGS`, `.cargo/config.toml`, profiles, or workspace lint settings may be involved.

## Pitfalls
- ⚠️ Reading host `cfg` output while debugging a cross target.
- ⚠️ Assuming Cargo and direct `rustc` invocations use the same flags without checking verbose output.
- ⚠️ Copying `-C target-feature` values from another architecture.
- ⚠️ Forgetting that nightly-only `-Z` inspection is not available on stable.
- ⚠️ Trusting cached CI logs after changing toolchains; rerun inspection after the toolchain or target changes.
- ⚠️ Treating `rustc -W help` lint names as source attribute syntax without converting hyphens to underscores where attributes require it.

## See also
[[The rustc Compiler]] · [[Target Triples]] · [[Conditional Compilation (cfg)]] · [[Codegen and Optimization Flags]] · [[Lints and Lint Levels]] · [[Enforcing Expected cfgs]] · [[Unchecked cfg Names]] · [[Cargo.toml Manifest]] · [[Profiles and Optimization Settings]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Print Options" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/print.html#print-options
- The rustc book, "`--print`: print compiler information" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/command-line-arguments.html#--print-print-compiler-information
