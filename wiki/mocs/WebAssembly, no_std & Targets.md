---
type: moc
title: "WebAssembly, no_std & Targets"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, webassembly, no-std, targets]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[Rust WebAssembly Targets]]", "[[no_std Crate Design]]", "[[Cargo Cross-Compilation Setup]]", "[[Target-Specific cfg Boundaries]]", "[[Panic Strategy Selection]]"]
sources: ["[[rustc-book]]", "[[embedded-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/rustc/platform-support.html", "https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html", "https://doc.rust-lang.org/reference/conditional-compilation.html"]
rust_version: "edition 2024 / 1.85+"
---

# WebAssembly, no_std & Targets

This MOC links the Rust notes for building outside the default host process: WebAssembly modules, `no_std` crates, cross-compilation, target features, panic policy, and target-specific cfg design.

## Core route
Start with [[Rust WebAssembly Targets]] when the output is `.wasm`.
Start with [[no_std Crate Design]] when the code must avoid `std`.
Start with [[Cargo Cross-Compilation Setup]] when the build must produce artifacts for a non-host target.
Start with [[Target-Specific cfg Boundaries]] when the same crate supports several targets.
Start with [[Panic Strategy Selection]] when the target does not have ordinary `std` panic behavior.

## WebAssembly notes
[[Rust WebAssembly Targets]] explains target choice.
It separates `wasm32-unknown-unknown`, `wasm32-wasip1`, `wasm32-wasip2`, and `wasm32v1-none`.
It links target cfgs to host contracts.
It warns that target architecture is not a browser detector.

[[wasm-bindgen Basics]] explains the JS binding path.
It covers `#[wasm_bindgen]`, generated glue, docs.rs version checks, and wasm-specific testing.
It belongs with `wasm32-unknown-unknown`.
It should not be confused with WASI.

[[Assuming wasm32 Means Browser]] is the main wasm antipattern.
It catches accidental DOM assumptions.
It explains why `target_arch = "wasm32"` is too broad.
It recommends explicit cfg and Cargo feature boundaries.

## no_std notes
[[no_std Crate Design]] is the deep design note.
It separates `core`, `alloc`, and `std`.
It explains why libraries should avoid choosing runtime, allocator, and panic policy.
It links back to the existing [[no_std]] note for embedded basics.

[[Using alloc without std]] covers heap-backed collections in `no_std`.
It explains `extern crate alloc`.
It keeps `#[global_allocator]` in final binaries.
It warns that `GlobalAlloc` is unsafe and allocation behavior is not a portable side channel.

[[Global Allocators]] explains the crate-graph-wide heap selection point.
It covers `#[global_allocator]`, `GlobalAlloc`, OOM behavior, wasm allocator tradeoffs, and why allocator choice belongs in final artifacts.

[[alloc Collections in no_std]] narrows the `alloc` story to collection APIs.
It covers `Vec`, `String`, `BTreeMap`, `BTreeSet`, `VecDeque`, `BinaryHeap`, `try_reserve`, and when fixed-capacity collections are a better fit.

Existing related notes:
[[Heapless Collections in Embedded Rust]]
[[Bare-Metal Programming]]
[[Embedded Rust Basics]]
[[Memory-Mapped I/O]]
[[Peripheral Access Crates]]

## Target and build notes
[[Cargo Cross-Compilation Setup]] is the build pattern.
It covers `.cargo/config.toml`.
It covers target-specific `runner`, `linker`, and `rustflags`.
It explains why `--target` matters for separating host build scripts from target artifacts.

[[Target Features and CPU Baselines]] covers `-C target-cpu`, `-C target-feature`, `#[target_feature]`, and `cfg(target_feature)`.
It is especially important for wasm because unsupported instructions can make a module fail validation.
It also matters for native release artifacts shipped to machines unlike the build host.

Existing related notes:
[[Target Triples]]
[[Codegen and Optimization Flags]]
[[Inspecting rustc Configuration]]
[[Profiles and Optimization Settings]]
[[Build Scripts (build.rs)]]

## cfg and policy notes
[[Target-Specific cfg Boundaries]] is the portability pattern.
It keeps target-specific imports behind small functions or modules.
It clarifies when to use `#[cfg]` instead of `cfg!(...)`.
It links to cfg checking so misspellings do not silently remove code.

[[Panic Strategy Selection]] covers abort, unwind, wasm defaults, and `no_std` panic handlers.
It complements [[Panic Unwinding and Abort]].
It reminds library authors not to impose panic handlers on downstream final artifacts.

[[Panic Handlers]] explains the exact `#[panic_handler]` item.
It covers the single-handler rule, `PanicInfo`, `std` panic hooks versus `no_std` panic handlers, and wasm console diagnostics.

Existing related notes:
[[Conditional Compilation (cfg)]]
[[Enforcing Expected cfgs]]
[[Unchecked cfg Names]]
[[Feature Flags]]
[[Non-Additive Feature Flags]]

## Decision checklist
Choose a target triple.
Install the target with rustup when available.
Inspect cfg values for the target.
Decide whether `std`, `alloc`, or only `core` is available.
Decide whether a global allocator exists.
Decide whether panic abort, unwind, halt, or target reporting is required.
Decide whether target features raise the deployment baseline.
Put build policy in Cargo configuration.
Put platform code behind cfg boundaries.
Test at least one host path and every supported target path.

## Created notes in this domain
[[Rust WebAssembly Targets]]
[[wasm-bindgen Basics]]
[[no_std Crate Design]]
[[Using alloc without std]]
[[Global Allocators]]
[[Panic Handlers]]
[[alloc Collections in no_std]]
[[Cargo Cross-Compilation Setup]]
[[Target Features and CPU Baselines]]
[[Panic Strategy Selection]]
[[Target-Specific cfg Boundaries]]
[[Assuming wasm32 Means Browser]]

## Sources
- The rustc book, "Platform Support" and WebAssembly target pages - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support.html
- The Embedded Rust Book, "A no_std Rust Environment" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html
- The Rust Reference, "Conditional compilation" and "Panic" - [[the-reference]],
  https://doc.rust-lang.org/reference/conditional-compilation.html and https://doc.rust-lang.org/reference/panic.html
