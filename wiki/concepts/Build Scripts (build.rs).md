---
type: concept
title: "Build Scripts (build.rs)"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, build-scripts, ffi]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Build-Time Code Execution]]", "[[Minimizing Dependencies]]", "[[cargo-audit and cargo-deny]]"]
sources: ["[[cargo-book]]", "[[dependency-supply-chain-security]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/build-scripts.html", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#build-dependencies"]
rust_version: "edition 2024 / 1.85+"
---

# Build Scripts (build.rs)

`build.rs` is a Cargo build script: a Rust program compiled and run before the package, used for native linking, code generation, and build-time configuration.

## What it is
If a package root contains `build.rs`, Cargo compiles and runs it before compiling the package. The manifest can rename or disable this with the `package.build` key.

Build scripts communicate with Cargo by printing `cargo::...` instructions to stdout. They can set link flags, emit custom cfgs, expose compile-time environment variables, and tell Cargo when to rerun.

## How it works
The script runs on the host machine with the privileges of the build process. It receives target information through environment variables such as `TARGET` and `CARGO_CFG_TARGET_OS`, and it should write generated artifacts only under `OUT_DIR`.

Build scripts have their own `[build-dependencies]`. They cannot use normal dependencies unless those crates are also listed as build dependencies, because the script is compiled separately and before the package.

Cargo reruns a build script conservatively if no change-detection instructions are emitted. Good scripts print `cargo::rerun-if-changed=...` and `cargo::rerun-if-env-changed=...` for their actual inputs.

The build script is compiled for the host, not the target. In cross-compilation, `cfg!(target_os = "...")` inside `build.rs` describes the machine running the script; `CARGO_CFG_TARGET_OS` describes the crate being built. Mixing those up is a common source of incorrect link flags.

Cargo interprets stdout lines beginning with `cargo::` as instructions. The double-colon form is current for Rust 1.77+; the older `cargo:` form remains relevant only if you intentionally support older toolchains. Instruction order can matter for link arguments, so print dependent link flags in the order the native linker expects.

## Example
```rust
use std::env;
use std::fs;
use std::path::PathBuf;

fn main() {
    let out_dir = PathBuf::from(env::var_os("OUT_DIR").unwrap_or_default());
    if !out_dir.as_os_str().is_empty() {
        let generated = out_dir.join("generated.rs");
        fs::write(generated, "pub const BUILD_MESSAGE: &str = \"generated\";\n").unwrap();
    }
    println!("cargo::rerun-if-changed=build.rs");
}
```

This compiles as a build script. It writes only under `OUT_DIR` and narrows rerun detection to the script itself.

## Target-aware example
```rust
use std::env;

fn main() {
    let target_os = env::var("CARGO_CFG_TARGET_OS").unwrap_or_default();

    println!("cargo::rerun-if-env-changed=MYLIB_DIR");
    println!("cargo::rustc-check-cfg=cfg(has_mylib)");

    if env::var_os("MYLIB_DIR").is_some() {
        println!("cargo::rustc-cfg=has_mylib");
    }

    if target_os == "windows" {
        println!("cargo::rustc-link-lib=userenv");
    }
}
```

The custom `has_mylib` cfg is registered before use, which keeps the `unexpected_cfgs` lint useful instead of silencing it globally.

## Common errors
```text
error[E0433]: failed to resolve: use of unresolved crate `cc`
```

Fix: put crates used by `build.rs` under `[build-dependencies]`, not only under `[dependencies]`.

```text
warning: unexpected `cfg` condition name: `has_mylib`
```

Fix: print `cargo::rustc-check-cfg=cfg(has_mylib)` from the build script near the matching `cargo::rustc-cfg=has_mylib` instruction.

## Best practice
- ✅ Keep build scripts deterministic, small, and explicit about rerun inputs.
- ✅ Read target information from Cargo-provided environment variables, not from `cfg!`, which describes the host build-script process.
- ✅ Use `cargo::rustc-check-cfg` next to custom `cargo::rustc-cfg` values so typos are caught.
- ✅ Treat dependencies with build scripts as higher supply-chain risk and review them accordingly.
- ✅ Write generated Rust to `OUT_DIR` and include it with `include!(concat!(env!("OUT_DIR"), "/file.rs"))` from crate code when needed.
- ✅ Prefer well-maintained `-sys` crates for common native libraries instead of duplicating fragile platform probing.

## Pitfalls
- ⚠️ Writing into `src/` or the package root from `build.rs` breaks registry immutability expectations; generated files belong in `OUT_DIR`.
- ⚠️ Missing `rerun-if-*` lines can cause needless rebuilds whenever any package file changes.
- ⚠️ Running untrusted dependencies with build scripts can execute arbitrary code during `cargo build`; see [[cargo-audit and cargo-deny]].
- ⚠️ Reading arbitrary environment variables without `rerun-if-env-changed` can leave stale builds when the environment changes.
- ⚠️ Emitting host link flags during cross-compilation can produce binaries that link locally but fail for the target platform.

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Dependencies and Version Requirements]] · [[Feature Flags]] · [[Minimizing Dependencies]] · [[cargo-audit and cargo-deny]] · [[Profiles and Optimization Settings]] · [[Cargo Workspaces]] · [[MSRV Policy]]

## Sources
- The Cargo Book, "Build Scripts" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/build-scripts.html
- The Cargo Book, "Build dependencies" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#build-dependencies
