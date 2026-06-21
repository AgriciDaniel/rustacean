---
type: concept
title: "Rust WebAssembly Targets"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, webassembly, wasm, targets, cross-compilation]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[wasm-bindgen Basics]]", "[[Target Triples]]", "[[Cargo Cross-Compilation Setup]]", "[[Target Features and CPU Baselines]]", "[[Assuming wasm32 Means Browser]]"]
sources: ["[[rustc-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html", "https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html", "https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip2.html", "https://doc.rust-lang.org/rustc/platform-support/wasm32v1-none.html"]
rust_version: "edition 2024 / 1.85+"
---

# Rust WebAssembly Targets

Rust's WebAssembly targets choose the host contract: browser and JS glue usually use `wasm32-unknown-unknown`, WASI programs use `wasm32-wasip1` or `wasm32-wasip2`, and minimal import-free modules can use `wasm32v1-none`.

## What it is
WebAssembly is a portable instruction format, but a Rust target still needs a precise platform contract.
The target controls which standard-library pieces exist.
It controls which imports the generated module expects.
It controls the target cfg values visible to [[Conditional Compilation (cfg)]].
It controls the baseline WebAssembly proposals that the compiler may emit.
That is why "compile to wasm" is not a complete build decision.

The most common Rust wasm targets are:
- `wasm32-unknown-unknown` for bare wasm modules, often post-processed by [[wasm-bindgen Basics]] for JavaScript.
- `wasm32-wasip1` for core wasm modules using WASI Preview 1 imports.
- `wasm32-wasip2` for WASI Preview 2 components.
- `wasm32v1-none` for `core`/`alloc` modules with no host imports and a WebAssembly 1.0-style baseline.

## How it works
`wasm32-unknown-unknown` is cross-compiled from any host.
It ships `std`, but OS-backed APIs are mostly inert because there is no OS contract.
The rustc book recommends `#[cfg(all(target_family = "wasm", target_os = "unknown"))]` for this target.
That cfg does not prove the module will run in a browser.
It may run in Node, Wasmtime, a plugin host, a blockchain VM, or a custom embedder.

`wasm32-wasip1` imports from `wasi_snapshot_preview1` for OS-like operations.
It is the historical compatibility target after the old `wasm32-wasi` name.
Use `#[cfg(all(target_os = "wasi", target_env = "p1"))]` for WASIp1-specific code.

`wasm32-wasip2` targets the component-model-based WASI Preview 2 world.
The rustc book still describes it as experimental as of January 2024.
Use `#[cfg(all(target_os = "wasi", target_env = "p2"))]` for WASIp2-specific code.

`wasm32v1-none` is closer to [[no_std Crate Design]].
It supports `core` and `alloc`, not `std`.
It imports nothing from the host by default.
It is useful when an embedder wants a small, explicit import surface.

## Example
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WasmHost {
    JavaScriptGlue,
    WasiPreview1,
    WasiPreview2,
    ImportFree,
    NativeOrOther,
}

pub fn wasm_host() -> WasmHost {
    #[cfg(all(target_family = "wasm", target_os = "unknown"))]
    {
        return WasmHost::JavaScriptGlue;
    }

    #[cfg(all(target_os = "wasi", target_env = "p1"))]
    {
        return WasmHost::WasiPreview1;
    }

    #[cfg(all(target_os = "wasi", target_env = "p2"))]
    {
        return WasmHost::WasiPreview2;
    }

    #[cfg(all(target_family = "wasm", target_os = "none"))]
    {
        return WasmHost::ImportFree;
    }

    WasmHost::NativeOrOther
}

fn main() {
    println!("{:?}", wasm_host());
}
```

## Best practice
- ✅ Pick the target from the host API contract, not from the output file extension.
- ✅ Use `wasm32-unknown-unknown` when a JS integration layer such as `wasm-bindgen` owns imports and exports.
- ✅ Use `wasm32-wasip1` when you need a stable WASI Preview 1 deployment path or C interop.
- ✅ Treat `wasm32-wasip2` as a component-model target and verify runtime support.
- ✅ Use `wasm32v1-none` when `core`/`alloc` are enough and no host imports should appear.
- ✅ Keep target setup in [[Cargo Cross-Compilation Setup]] so all developers build the same artifact.

## Pitfalls
- ⚠️ Assuming `target_arch = "wasm32"` means "browser"; see [[Assuming wasm32 Means Browser]].
- ⚠️ Measuring the raw rustc `.wasm` before post-processing with `wasm-bindgen` tools.
- ⚠️ Calling `std::fs`, `std::net`, or `std::process` on `wasm32-unknown-unknown` and expecting host behavior.
- ⚠️ Enabling WebAssembly proposals without checking the deployment engine; see [[Target Features and CPU Baselines]].
- ⚠️ Forgetting that `wasm32-unknown-unknown` is not a C ABI compatibility target.

## See also
[[wasm-bindgen Basics]]
[[Target Triples]]
[[Cargo Cross-Compilation Setup]]
[[Target Features and CPU Baselines]]
[[Target-Specific cfg Boundaries]]
[[Assuming wasm32 Means Browser]]
[[no_std Crate Design]]
[[Using alloc without std]]
[[Panic Strategy Selection]]
[[WebAssembly, no_std & Targets]]

## Sources
- The rustc book, `wasm32-unknown-unknown` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html
- The rustc book, `wasm32-wasip1` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html
- The rustc book, `wasm32-wasip2` and `wasm32v1-none` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip2.html and https://doc.rust-lang.org/rustc/platform-support/wasm32v1-none.html
