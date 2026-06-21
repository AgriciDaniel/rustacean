---
type: concept
title: "Codegen and Optimization Flags"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, codegen, optimization, compiler]
domain: "Editions & Compiler"
difficulty: advanced
related: ["[[The rustc Compiler]]", "[[Target Triples]]", "[[Profiles and Optimization Settings]]", "[[Integer Overflow]]", "[[Panic Unwinding and Abort]]", "[[Inspecting rustc Configuration]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/codegen-options/index.html", "https://doc.rust-lang.org/rustc/command-line-arguments.html#-c--codegen-code-generation-options"]
rust_version: "edition 2024 / 1.85+"
---

# Codegen and Optimization Flags

`rustc -C` flags control backend code generation: optimization level, debuginfo, codegen units, LTO, panic strategy, overflow checks, CPU features, linker behavior, and related artifact choices.

## What it is
Codegen flags are passed with `-C` or `--codegen`.
They affect the generated machine code, emitted debug information, link behavior, and compile-time tradeoffs.
The rustc book recommends checking `rustc -C help` for the options supported by the exact compiler in use.

Common options include `opt-level`, `debuginfo`, `debug-assertions`, `overflow-checks`, `codegen-units`, `lto`, `panic`, `target-cpu`, `target-feature`, `linker`, and `link-arg`.
Cargo profile settings are usually the right interface for application crates.

## How it works
`-O` is shorthand for `-C opt-level=3`.
`-g` is shorthand for `-C debuginfo=2`.
`opt-level=0` is the default and enables `cfg(debug_assertions)`.
Higher optimization levels can improve runtime performance but increase compile time and may reduce debuggability.

`codegen-units` trades compile parallelism against optimization opportunity.
More units can compile faster; `codegen-units=1` can improve generated code at the cost of compile time.
`lto` enables link-time optimization across crate boundaries.
`overflow-checks` controls runtime integer overflow checks; if unspecified, it follows debug assertions.

Some flags are target-sensitive.
`target-feature` is explicitly risky because enabling CPU features can make the binary invalid on CPUs that lack those instructions.
Flags can also interact.
For example, LTO needs compatible bitcode availability, panic strategy must match how libraries are linked in some contexts, and linker arguments depend on the target linker flavor.
Cargo profiles encode the common, repeatable choices, while direct `-C` flags are best for experiments or non-Cargo build systems.

The compiler only promises that a codegen option is accepted by the exact compiler and target you are using.
Check `rustc -C help`, `rustc --print target-cpus`, and `rustc --print target-features` rather than copying values from another platform.

## Example
```rust
fn sum_squares(values: &[u64]) -> u64 {
    values.iter().map(|value| value * value).sum()
}

fn main() {
    let values = [1, 2, 3, 4];
    println!("{}", sum_squares(&values));
}
```

Example direct compile commands:

```bash
rustc --edition=2024 -C opt-level=3 main.rs
rustc --edition=2024 -C debuginfo=2 -C overflow-checks=yes main.rs
```

The Cargo-profile equivalent is more reproducible for projects:

```toml
[profile.release]
opt-level = 3
codegen-units = 1
lto = "thin"
debug = "line-tables-only"
panic = "abort"
```

Use a profile when the setting is part of the crate's supported build mode; use direct `-C` flags when inspecting or integrating with another build system.

## Common errors
Some combinations are rejected before code generation:

```text
error: options `-C embed-bitcode=no` and `-C lto` are incompatible
```

Fix it by removing one of the flags or letting Cargo choose compatible defaults for the selected profile.

Invalid CPU or feature names are target-specific:

```text
error: incorrect value `native-ish` for codegen option `target-cpu`
```

or:

```text
warning: unknown and unstable feature specified for `-Ctarget-feature`
```

Check the exact compiler with `rustc --print target-features --target <triple>` and avoid enabling features unless every deployment CPU supports them.

Linker arguments often fail outside Rust:

```text
error: linking with `cc` failed: exit status: 1
```

Read the linker output, confirm the target linker flavor, and prefer Cargo target configuration for persistent linker choices.

## Best practice
- ✅ Prefer Cargo profiles for repeatable project optimization settings; see [[Profiles and Optimization Settings]].
- ✅ Use direct `-C` flags for experiments, build-system integration, or one-off investigation.
- ✅ Measure before and after changing `opt-level`, `codegen-units`, or `lto`.
- ✅ Keep `debuginfo` and frame-pointer choices aligned with observability and profiling needs.
- ✅ Treat `target-cpu` and `target-feature` as deployment contracts.
- ✅ Prefer `lto = "thin"` as a first release-build experiment before paying the full compile-time cost of fat LTO.
- ✅ Keep overflow checks enabled in test and debug builds; decide release behavior deliberately instead of inheriting assumptions.
- ✅ Record non-default panic, linker, relocation, or CPU settings in release documentation.

## Pitfalls
- ⚠️ Assuming `-O` is always best; size, compile time, startup time, and debuggability may matter more.
- ⚠️ Turning off overflow checks to hide bugs; see [[Integer Overflow]] and [[Relying on Integer Overflow]].
- ⚠️ Combining `-C embed-bitcode=no` with LTO in direct rustc usage; that combination is invalid.
- ⚠️ Passing linker flags without understanding target linker flavor.
- ⚠️ Applying `RUSTFLAGS` globally and accidentally changing dependencies, tests, build scripts, or proc macros.
- ⚠️ Benchmarking one `target-cpu=native` binary and shipping it to machines with different CPU features.
- ⚠️ Stripping symbols so aggressively that production crash reports and profilers become much less useful.

## See also
[[The rustc Compiler]] · [[Target Triples]] · [[Profiles and Optimization Settings]] · [[Integer Overflow]] · [[Panic Unwinding and Abort]] · [[Relying on Integer Overflow]] · [[Inspecting rustc Configuration]] · [[Cargo.toml Manifest]] · [[MSRV Policy]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Codegen Options" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html
- The rustc book, "`-C`/`--codegen`" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/command-line-arguments.html#-c--codegen-code-generation-options
