---
type: concept
title: "Build-Time Code Execution"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, build-scripts, supply-chain]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Documentation Comments]]", "[[Name Resolution]]", "[[Static Items]]", "[[Readable Generic APIs]]", "[[Supply Chain Security]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[cargo-book]]", "[[dependency-supply-chain-security]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/build-scripts.html"]
rust_version: "edition 2024 / 1.85+"
---

# Build-Time Code Execution

`build.rs` build scripts run at compile time to generate code, probe the environment, or link native libs — a trust and reproducibility surface.

## What it is
Build-time code execution is any Rust project behavior that runs code while compiling rather than
while the final program runs. The most common form is Cargo's `build.rs` build script.

Build scripts are useful for compiling bundled C code, discovering native libraries, generating Rust
source into `OUT_DIR`, or emitting target-specific `cfg` flags.

They are also a supply-chain and reproducibility concern: dependencies' build scripts execute on the
developer or CI machine during builds.

## How it works
When a package has a `build.rs` file, Cargo compiles it and runs it before compiling the package. The
script's current directory is the package root, and Cargo passes inputs through environment variables.

The script communicates with Cargo by printing lines beginning with `cargo::` to stdout. Common
instructions include `cargo::rerun-if-changed=PATH`, `cargo::rerun-if-env-changed=VAR`,
`cargo::rustc-link-lib=LIB`, `cargo::rustc-link-search=PATH`, `cargo::rustc-cfg=KEY`, and
`cargo::rustc-check-cfg=...`.

Generated files should be written under the `OUT_DIR` environment variable. Cargo does not guarantee
that `OUT_DIR` is empty between builds, so scripts must manage their own generated filenames and stale
artifacts.

## Example
```rust
// build.rs
use std::{env, fs, path::PathBuf};

fn main() {
    println!("cargo::rerun-if-changed=schema.txt");

    let out_dir = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR set by Cargo"));
    let generated = out_dir.join("schema.rs");

    fs::write(&generated, "pub const FIELD_COUNT: usize = 3;\n")
        .expect("write generated schema");
}
```

Application code can include the generated file:

```rust
include!(concat!(env!("OUT_DIR"), "/schema.rs"));

fn main() {
    assert_eq!(FIELD_COUNT, 3);
}
```

## Edge cases
When emitting custom `cfg` values, register them with `rustc-check-cfg` so typo checking remains useful:

```rust
// build.rs
fn main() {
    println!("cargo::rustc-check-cfg=cfg(has_fast_path)");

    if std::env::var_os("ENABLE_FAST_PATH").is_some() {
        println!("cargo::rustc-cfg=has_fast_path");
    }

    println!("cargo::rerun-if-env-changed=ENABLE_FAST_PATH");
}
```

For cross-compilation, use Cargo's target environment variables such as `CARGO_CFG_TARGET_OS` rather
than `cfg!`, which describes the host running the build script.

## Common errors
Forgetting rerun directives makes Cargo rerun a build script whenever any package file changes:

```rust
// build.rs
fn main() {
    // probes or generates, but prints no rerun-if-* directive
}
```

The symptom is not usually a compiler error; it is slow or unstable rebuilds. Fix it by declaring the
actual inputs:

```rust
fn main() {
    println!("cargo::rerun-if-changed=build.rs");
    println!("cargo::rerun-if-changed=schema.txt");
}
```

Another common failure is writing generated files into `src/`, which dirties the working tree and can
create rebuild loops. Write to `OUT_DIR` instead.

## Best practice
- ✅ Avoid build scripts unless Cargo features, declarative configuration, or checked-in generated code are insufficient.
- ✅ Print precise `rerun-if-changed` and `rerun-if-env-changed` directives.
- ✅ Write generated artifacts only under `OUT_DIR`.
- ✅ Register custom cfgs with `cargo::rustc-check-cfg` near the matching `cargo::rustc-cfg`.
- ✅ Audit dependencies with build scripts as executable code, not passive metadata.

## Pitfalls
- ⚠️ Build scripts run on the host machine, which may differ from the target when cross-compiling.
- ⚠️ Reading the network, current time, or broad filesystem state makes builds hard to reproduce.
- ⚠️ `cargo::` instruction order can affect linker argument order.
- ⚠️ `OUT_DIR` may contain stale files from earlier builds.
- ⚠️ A build script in a dependency can affect trust even if your own crate has no `build.rs`.

## See also
[[Documentation Comments]] · [[Name Resolution]] · [[Static Items]] · [[Readable Generic APIs]] · [[Supply Chain Security]] · [[Testing]] · [[Cargo]] · [[Basic Concepts & Syntax]]

## Sources
- The Cargo Book, "Build Scripts" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Supply chain security research — [[dependency-supply-chain-security]]
