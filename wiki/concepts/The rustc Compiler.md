---
type: concept
title: "The rustc Compiler"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustc, compiler, cli]
domain: "Editions & Compiler"
difficulty: basic
related: ["[[Rust Editions]]", "[[Lints and Lint Levels]]", "[[Codegen and Optimization Flags]]", "[[Target Triples]]", "[[Conditional Compilation (cfg)]]", "[[Cargo.toml Manifest]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/what-is-rustc.html", "https://doc.rust-lang.org/rustc/command-line-arguments.html"]
rust_version: "edition 2024 / 1.85+"
---

# The rustc Compiler

`rustc` is the Rust compiler: it turns a crate root into a library, executable, metadata, MIR, LLVM IR, object file, or other requested output.

## What it is
Most Rust developers invoke `rustc` through Cargo.
Cargo resolves packages, builds dependencies, chooses targets, reads manifest settings, and then calls `rustc`.
The compiler still performs the actual parsing, type checking, borrow checking, linting, code generation, and linking coordination.

The important unit is the crate root.
You pass `rustc` `main.rs` or `lib.rs`, not every module file.
`mod` declarations tell the compiler which module files belong to the crate.

## How it works
`rustc` accepts command-line flags for edition selection, crate type, crate name, output kinds, lint levels, targets, conditional compilation, and code generation.
Cargo maps manifest and profile settings into those flags.
For debugging, `cargo build --verbose` prints the `rustc` invocations Cargo runs.

Common flags include:
`--edition` for source edition, `--crate-type` for output kind, `--emit` for artifacts, `--target` for cross-compilation, `-A`/`-W`/`-D`/`-F` for lints, `--check-cfg` for cfg checking, and `-C` for codegen options.

When building directly with `rustc`, you must supply details Cargo usually manages for you: extern crates, search paths, target configuration, features, and output directories.
Passing a module file directly creates a different crate instead of adding that module to the original crate.
That is why `rustc src/foo.rs` cannot see the `crate::` items, dependencies, feature cfgs, or crate-level attributes from `src/main.rs` unless you deliberately rebuild all of that context.

The compiler pipeline is roughly: parse and expand macros, resolve names, type check, run lints, build and borrow-check MIR, monomorphize generic code, lower to backend IR, optimize, emit artifacts, and coordinate linking.
Flags such as `--emit=mir` or `--emit=llvm-ir` expose intermediate artifacts for investigation, but they do not replace Cargo's package graph management.

## Example
```rust
mod greeting {
    pub fn message() -> &'static str {
        "hello from the crate root"
    }
}

fn main() {
    println!("{}", greeting::message());
}
```

Compile this crate root directly with:

```bash
rustc --edition=2024 main.rs
```

To inspect compiler output without linking an executable, ask for a specific artifact:

```bash
rustc --edition=2024 --crate-type=lib --emit=metadata,mir lib.rs
```

That command type-checks a library crate and writes metadata plus MIR artifacts for the crate root.

## Common errors
Compiling a module file as if it were a C translation unit often produces missing-module or unresolved-import diagnostics:

```text
error[E0432]: unresolved import `crate::...`
```

Fix the build by compiling the crate root (`main.rs` or `lib.rs`) or by using Cargo.
Do not pass every file under `src/` to `rustc`.

Forgetting dependency metadata in direct invocations commonly appears as:

```text
error[E0463]: can't find crate for `serde`
```

Cargo normally supplies `--extern` and `-L dependency=...` flags.
If you are integrating a custom build system, inspect `cargo build --verbose` and reproduce the required dependency flags deliberately.

Using nightly-only compiler options on stable is rejected:

```text
error: the option `Z` is only accepted on the nightly compiler
```

Stay on stable flags for Rust 1.85+ workflows, or make nightly use an explicit toolchain policy.

## Best practice
- ✅ Use Cargo for normal projects; reach for direct `rustc` when writing build-system integration, experiments, or compiler-facing diagnostics.
- ✅ Pass only the crate root to `rustc`; let modules be discovered from `mod` items.
- ✅ Use `cargo build --verbose` to learn what Cargo is passing before recreating a command manually.
- ✅ Prefer Cargo profile and manifest settings over hand-written `RUSTFLAGS` where the setting belongs to the package.
- ✅ Use [[Inspecting rustc Configuration]] before assuming a target, cfg, sysroot, or CPU feature is active.
- ✅ Use `--emit` to inspect MIR, LLVM IR, assembly, object files, or dependency info when debugging compiler behavior.
- ✅ Keep direct `rustc` commands reproducible in scripts rather than relying on shell history or implicit current-directory state.

## Pitfalls
- ⚠️ Compiling each module like C source files; Rust modules are not separate translation units.
- ⚠️ Forgetting `--edition=2024` in custom build systems and then seeing edition-only syntax fail.
- ⚠️ Passing ad hoc `-C` or lint flags globally without understanding dependency effects.
- ⚠️ Using `-Z` options on stable; unstable compiler options require nightly.
- ⚠️ Assuming `rustc main.rs` and `cargo build` use the same cfgs, features, dependency graph, or output directory.
- ⚠️ Treating compiler output artifacts as stable interfaces; MIR and LLVM IR are diagnostics, not compatibility promises.

## See also
[[Rust Editions]] · [[Edition 2024]] · [[Lints and Lint Levels]] · [[Codegen and Optimization Flags]] · [[Target Triples]] · [[Conditional Compilation (cfg)]] · [[Inspecting rustc Configuration]] · [[Cargo.toml Manifest]] · [[Cargo Workspaces]] · [[Editions & Compiler]]

## Sources
- The rustc book, "What is rustc?" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/what-is-rustc.html
- The rustc book, "Command-line Arguments" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/command-line-arguments.html
