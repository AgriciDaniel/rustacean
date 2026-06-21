---
type: pattern
title: "Target-Specific cfg Boundaries"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cfg, targets, portability, conditional-compilation]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[Conditional Compilation (cfg)]]", "[[Unchecked cfg Names]]", "[[Enforcing Expected cfgs]]", "[[Rust WebAssembly Targets]]", "[[Cargo Cross-Compilation Setup]]"]
sources: ["[[rustc-book]]", "[[the-reference]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/conditional-compilation.html", "https://doc.rust-lang.org/rustc/check-cfg.html", "https://doc.rust-lang.org/cargo/reference/config.html"]
rust_version: "edition 2024 / 1.85+"
---

# Target-Specific cfg Boundaries

Target-specific cfg boundaries keep platform code behind small, named functions or modules selected with `#[cfg]`, so unsupported code is removed before type checking and portable code remains readable.

## What it is
Rust has two common cfg mechanisms:
- `#[cfg(...)]`, which includes or removes items and blocks before type checking
- `cfg!(...)`, which evaluates to a boolean while both surrounding branches must still be valid Rust

Target-specific code usually needs `#[cfg]`.
That is especially true for wasm imports, embedded register access, Unix file descriptors, Windows handles, and `std` APIs absent from `no_std`.
The existing [[Conditional Compilation (cfg)]] note covers the mechanism.
This pattern covers where to put the boundary.

The goal is simple:
- portable logic sees one function or trait
- platform modules own platform-specific imports
- cfg expressions are few and easy to audit
- each target has a fallback or compile error by design

## How it works
Choose cfgs from compiler facts, not from guessed string parsing.
Inspect them with `rustc --print cfg --target <triple>`.
For wasm, use the target combinations documented by the rustc book:
- `all(target_family = "wasm", target_os = "unknown")`
- `all(target_os = "wasi", target_env = "p1")`
- `all(target_os = "wasi", target_env = "p2")`
- `all(target_family = "wasm", target_os = "none")`

Use Cargo's `unexpected_cfgs` checking for custom cfgs.
Use [[Enforcing Expected cfgs]] when a build script or rustflags set names such as `has_board_rev_b`.
Avoid large inline cfg thickets in business logic.

## Example
```rust
pub fn platform_id() -> &'static str {
    platform_id_impl()
}

#[cfg(all(target_family = "wasm", target_os = "unknown"))]
fn platform_id_impl() -> &'static str {
    "wasm-unknown"
}

#[cfg(all(target_os = "wasi", target_env = "p1"))]
fn platform_id_impl() -> &'static str {
    "wasi-preview1"
}

#[cfg(all(target_os = "wasi", target_env = "p2"))]
fn platform_id_impl() -> &'static str {
    "wasi-preview2"
}

#[cfg(not(any(
    all(target_family = "wasm", target_os = "unknown"),
    all(target_os = "wasi", target_env = "p1"),
    all(target_os = "wasi", target_env = "p2")
)))]
fn platform_id_impl() -> &'static str {
    "other"
}

fn main() {
    println!("{}", platform_id());
}
```

## Edge case
```rust
pub fn is_wasm_compile() -> bool {
    cfg!(target_family = "wasm")
}

fn main() {
    println!("{}", is_wasm_compile());
}
```

This is fine for a boolean label.
It is not enough to protect code that imports a wasm-only crate or uses a missing API.

## Best practice
- ✅ Put cfgs at module or function boundaries.
- ✅ Prefer positive target cfgs documented by rustc over fragile negative lists.
- ✅ Provide a fallback implementation or an intentional `compile_error!`.
- ✅ Use `#[cfg]` to remove unsupported code before type checking.
- ✅ Use [[Enforcing Expected cfgs]] for custom cfg names and values.
- ✅ Keep cfg expressions in sync with [[Cargo Cross-Compilation Setup]] and CI.

## Pitfalls
- ⚠️ Using `cfg!(...)` around code that does not compile on every target.
- ⚠️ Matching only `target_arch = "wasm32"` and accidentally including WASI or non-browser hosts.
- ⚠️ Letting platform modules leak target-specific types into portable APIs.
- ⚠️ Misspelling cfg names and silently dropping code; see [[Unchecked cfg Names]].
- ⚠️ Making Cargo features mutually exclusive instead of additive; see [[Non-Additive Feature Flags]].

## See also
[[Conditional Compilation (cfg)]]
[[Enforcing Expected cfgs]]
[[Unchecked cfg Names]]
[[Rust WebAssembly Targets]]
[[Assuming wasm32 Means Browser]]
[[Cargo Cross-Compilation Setup]]
[[Target Features and CPU Baselines]]
[[Feature Flags]]
[[Non-Additive Feature Flags]]
[[WebAssembly, no_std & Targets]]

## Sources
- The Rust Reference, "Conditional compilation" - [[the-reference]],
  https://doc.rust-lang.org/reference/conditional-compilation.html
- The rustc book, "Checking conditional configurations" - [[rustc-book]],
  https://doc.rust-lang.org/rustc/check-cfg.html
- The Cargo Book, target configuration - [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/config.html
