---
type: concept
title: "wasm-bindgen Basics"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, webassembly, wasm, wasm-bindgen, javascript]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[Rust WebAssembly Targets]]", "[[Cargo Cross-Compilation Setup]]", "[[Target-Specific cfg Boundaries]]", "[[Assuming wasm32 Means Browser]]", "[[Using alloc without std]]"]
sources: ["[[rustc-book]]"]
source_urls: ["https://rustwasm.github.io/docs/wasm-bindgen/", "https://docs.rs/wasm-bindgen/latest/wasm_bindgen/", "https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html"]
rust_version: "edition 2024 / 1.85+"
---

# wasm-bindgen Basics

`wasm-bindgen` is the Rust-to-JavaScript binding layer for `wasm32-unknown-unknown`: Rust exports are annotated with `#[wasm_bindgen]`, then a CLI post-processing step generates the JavaScript glue and final `.wasm` artifact.

## What it is
Raw WebAssembly has a narrow value interface.
It understands numbers and references, not Rust `String`, JS objects, promises, exceptions, DOM types, or ergonomic classes.
`wasm-bindgen` bridges that gap.
The crate provides the `#[wasm_bindgen]` attribute and runtime types such as `JsValue`.
The command-line tool rewrites the raw compiler output into a pair of files that JavaScript can import.

The official guide says the project is designed around the `wasm32-unknown-unknown` target.
That target is intentionally bare.
Browser APIs normally arrive through generated JS glue plus crates such as `js-sys` and `web-sys`.
For crate versions, cite docs.rs and verify the latest version before writing `Cargo.toml`; docs.rs showed `wasm-bindgen` 0.2.125 when this note was written.

## How it works
A typical library exposes a small Rust API:
- Add `wasm-bindgen` as a dependency.
- Compile with `cargo build --target wasm32-unknown-unknown --release`.
- Run `wasm-bindgen` or a wrapper such as `wasm-pack`.
- Import the generated JS package from browser, bundler, Node, or test harness.

Only exported Rust functions, imported JS functions, and glue they require should be retained.
Do not measure the raw `target/wasm32-unknown-unknown/release/name.wasm` when judging publish size.
The guide calls the post-processed `*_bg.wasm` the artifact that reflects what you ship.

The `wasm-bindgen` crate can appear in code that is also compiled on non-wasm targets.
However, imported JS functions panic on non-wasm targets.
For faster native checks and fewer accidental panics, put wasm-only imports and dependencies behind [[Target-Specific cfg Boundaries]].

## Example
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn add(left: u32, right: u32) -> u32 {
    left + right
}

#[wasm_bindgen]
pub fn greeting(name: &str) -> String {
    format!("Hello, {name}!")
}
```

This is a minimal library example.
It compiles when `wasm-bindgen` is present in `Cargo.toml`.
Build commands are normally outside the Rust source:

```text
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
wasm-bindgen target/wasm32-unknown-unknown/release/your_crate.wasm --out-dir pkg --target web
```

## Edge case
```rust
#[cfg(target_arch = "wasm32")]
pub fn platform() -> &'static str {
    "wasm32"
}

#[cfg(not(target_arch = "wasm32"))]
pub fn platform() -> &'static str {
    "native"
}

fn main() {
    println!("{}", platform());
}
```

Use a native-compatible fallback when you want ordinary `cargo test` to keep working.
Move actual `#[wasm_bindgen] extern "C"` imports behind wasm cfgs.

## Best practice
- ✅ Keep the exported wasm API small, stable, and explicit.
- ✅ Check docs.rs for the current `wasm-bindgen` version before pinning dependencies.
- ✅ Use `web-sys` features narrowly; enable only the browser APIs you call.
- ✅ Test wasm behavior with `wasm-bindgen-test` or `wasm-pack test` when JS behavior matters.
- ✅ Keep pure logic in normal Rust modules so it can be tested natively.
- ✅ Use [[Rust WebAssembly Targets]] to choose `wasm32-unknown-unknown` deliberately.

## Pitfalls
- ⚠️ Assuming `wasm-bindgen` targets WASI; it is mainly for JS glue on `wasm32-unknown-unknown`.
- ⚠️ Calling imported JS functions during native tests; those imports panic off wasm.
- ⚠️ Measuring raw rustc wasm instead of the post-processed `*_bg.wasm`.
- ⚠️ Enabling broad `web-sys` feature sets and inflating compile time or bindings.
- ⚠️ Treating `target_arch = "wasm32"` as a browser test; see [[Assuming wasm32 Means Browser]].

## See also
[[Rust WebAssembly Targets]]
[[Target Triples]]
[[Cargo Cross-Compilation Setup]]
[[Target-Specific cfg Boundaries]]
[[Assuming wasm32 Means Browser]]
[[Target Features and CPU Baselines]]
[[Using alloc without std]]
[[Panic Strategy Selection]]
[[Feature Flags]]
[[WebAssembly, no_std & Targets]]

## Sources
- The `wasm-bindgen` Guide - Rust and WebAssembly,
  https://rustwasm.github.io/docs/wasm-bindgen/
- `wasm-bindgen` crate docs on docs.rs; verify the latest version before use,
  https://docs.rs/wasm-bindgen/latest/wasm_bindgen/
- The rustc book, `wasm32-unknown-unknown` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html
