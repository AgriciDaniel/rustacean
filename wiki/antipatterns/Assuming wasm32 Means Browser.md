---
type: antipattern
title: "Assuming wasm32 Means Browser"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, wasm, cfg, browser, targets, antipattern]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[Rust WebAssembly Targets]]", "[[wasm-bindgen Basics]]", "[[Target-Specific cfg Boundaries]]", "[[Conditional Compilation (cfg)]]", "[[Target Triples]]"]
sources: ["[[rustc-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html", "https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html", "https://doc.rust-lang.org/reference/conditional-compilation.html"]
rust_version: "edition 2024 / 1.85+"
---

# Assuming wasm32 Means Browser

The mistake is treating `target_arch = "wasm32"` as "running in a browser"; `wasm32` only names the WebAssembly architecture, while the host may be JS glue, WASI, an import-free embedder, or a custom runtime.

## The mistake
This antipattern usually appears as:
- `#[cfg(target_arch = "wasm32")]` around DOM calls
- `#[cfg(target_arch = "wasm32")]` around `wasm-bindgen` imports
- a crate that assumes `web_sys::window()` exists for every wasm build
- a test suite that passes in the browser but fails on WASI
- a library that cannot be used in non-browser wasm hosts

The architecture is not the host.
The rustc book explicitly notes that `wasm32-unknown-unknown` has no cfg that tells you whether code will run on the web.
It also documents separate cfg patterns for `wasm32-unknown-unknown`, `wasm32-wasip1`, `wasm32-wasip2`, and `wasm32v1-none`.

## Why it happens
Most tutorials start with browser wasm.
`wasm-bindgen` examples naturally use `wasm32-unknown-unknown`.
The old mental shortcut becomes "wasm equals web".
Rust target triples make that shortcut tempting because several wasm targets start with `wasm32`.

But `wasm32-wasip1` can print using WASI APIs.
`wasm32-wasip2` produces a component-model target.
`wasm32v1-none` imports nothing by default.
`wasm32-unknown-unknown` might run in browser JS, Node, Wasmtime, a plugin VM, or a bespoke host.
The target can prove a compilation contract.
It cannot prove the embedding context unless the build sets an explicit custom cfg or feature.

## Example
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WasmEnvironment {
    JsGlueCandidate,
    WasiPreview1,
    WasiPreview2,
    ImportFree,
    NotWasm,
}

pub fn classify() -> WasmEnvironment {
    #[cfg(all(target_family = "wasm", target_os = "unknown"))]
    {
        return WasmEnvironment::JsGlueCandidate;
    }

    #[cfg(all(target_os = "wasi", target_env = "p1"))]
    {
        return WasmEnvironment::WasiPreview1;
    }

    #[cfg(all(target_os = "wasi", target_env = "p2"))]
    {
        return WasmEnvironment::WasiPreview2;
    }

    #[cfg(all(target_family = "wasm", target_os = "none"))]
    {
        return WasmEnvironment::ImportFree;
    }

    WasmEnvironment::NotWasm
}

fn main() {
    println!("{:?}", classify());
}
```

This is still not a browser detector.
It only narrows the Rust target contract.

## Best practice
- ✅ Use [[Rust WebAssembly Targets]] to choose the correct wasm target first.
- ✅ Put JS imports behind `all(target_family = "wasm", target_os = "unknown")` plus a crate feature when browser APIs are optional.
- ✅ Keep DOM-specific code in a browser module rather than a generic wasm module.
- ✅ Use explicit Cargo features such as `web` or `browser` for embedding assumptions Cargo cannot infer.
- ✅ Test WASI and browser builds separately if both are supported.
- ✅ Document whether the API needs browser JS, Node JS, WASI, or no imports.

## Pitfalls
- ⚠️ `target_arch = "wasm32"` includes WASI and non-browser wasm targets.
- ⚠️ `wasm32-unknown-unknown` still does not prove browser execution.
- ⚠️ `web_sys::window()` can be absent even in some JS embeddings.
- ⚠️ `wasm-bindgen` imports panic on non-wasm targets if called in native tests.
- ⚠️ Browser-only dependencies can make a portable wasm crate unusable for WASI.

## See also
[[Rust WebAssembly Targets]]
[[wasm-bindgen Basics]]
[[Target-Specific cfg Boundaries]]
[[Conditional Compilation (cfg)]]
[[Target Triples]]
[[Cargo Cross-Compilation Setup]]
[[Target Features and CPU Baselines]]
[[Feature Flags]]
[[Unchecked cfg Names]]
[[WebAssembly, no_std & Targets]]

## Sources
- The rustc book, `wasm32-unknown-unknown` conditional compilation - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html
- The rustc book, `wasm32-wasip1` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html
- The Rust Reference, "Conditional compilation" - [[the-reference]],
  https://doc.rust-lang.org/reference/conditional-compilation.html
