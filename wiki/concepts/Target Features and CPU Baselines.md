---
type: concept
title: "Target Features and CPU Baselines"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, target-features, codegen, wasm, cpu]
domain: "WebAssembly, no_std & Targets"
difficulty: advanced
related: ["[[Target Triples]]", "[[Rust WebAssembly Targets]]", "[[Cargo Cross-Compilation Setup]]", "[[Target-Specific cfg Boundaries]]", "[[Codegen and Optimization Flags]]"]
sources: ["[[rustc-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature", "https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute", "https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature", "https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html#enabled-webassembly-features"]
rust_version: "edition 2024 / 1.85+"
---

# Target Features and CPU Baselines

Target features are compile-time assumptions about instructions or platform capabilities; enabling them can make faster or smaller code, but it can also raise the minimum CPU or WebAssembly engine required to load and run the artifact.

## What it is
A target triple gives a broad platform.
A target CPU and target features refine what instructions the compiler may use.
`-C target-cpu=...` selects a CPU model.
`-C target-feature=+foo,-bar` enables or disables individual features.
`#[target_feature(enable = "...")]` marks a function with extra requirements.
`#[cfg(target_feature = "...")]` checks whether a feature is enabled for the whole crate.

The rustc book calls target features unsafe at the codegen-option level because mixing crates compiled with different assumptions can be wrong.
The Reference also places restrictions on calling `#[target_feature]` functions.
On native platforms, executing unsupported instructions can be undefined behavior.
On wasm, unsupported instructions fail validation or loading rather than executing as different instructions, but the deployment still breaks.

## How it works
Use these tools to inspect the current compiler:

```text
rustc --print target-cpus --target x86_64-unknown-linux-gnu
rustc --print target-features --target x86_64-unknown-linux-gnu
rustc -Ctarget-feature=help --target wasm32-unknown-unknown
rustc --print cfg --target wasm32-unknown-unknown
```

For WebAssembly, target features are especially visible.
The `wasm32-unknown-unknown` default feature set follows LLVM's generic wasm baseline and can change over time.
The rustc book lists enabled defaults and recommends `wasm32v1-none` when you need a smaller, stable WebAssembly 1.0-style feature baseline with `core` and `alloc`.
For wasm crate authors, prefer `#[cfg(target_feature = "...")]` over forcing `#[target_feature]` when optional code is not required.

## Example
```rust
pub fn acceleration_label() -> &'static str {
    #[cfg(all(target_arch = "wasm32", target_feature = "simd128"))]
    {
        return "wasm simd128";
    }

    #[cfg(all(any(target_arch = "x86", target_arch = "x86_64"), target_feature = "avx2"))]
    {
        return "x86 avx2";
    }

    "portable"
}

fn main() {
    println!("{}", acceleration_label());
}
```

This code compiles everywhere because the feature-specific blocks are removed before type checking on other targets.
It does not enable SIMD by itself.
It only observes what the crate was compiled to assume.

## Edge case
```rust
#[cfg(all(target_arch = "wasm32", target_feature = "simd128"))]
pub fn simd_path_available() -> bool {
    true
}

#[cfg(not(all(target_arch = "wasm32", target_feature = "simd128")))]
pub fn simd_path_available() -> bool {
    false
}

fn main() {
    assert_eq!(simd_path_available(), cfg!(all(target_arch = "wasm32", target_feature = "simd128")));
}
```

Prefer this shape when the optimized path can be fully omitted from unsupported builds.

## Best practice
- ✅ Define the deployment baseline first, then set target features to match it.
- ✅ Keep feature flags in [[Cargo Cross-Compilation Setup]] or CI scripts, not scattered through shell history.
- ✅ Use `#[cfg(target_feature = "...")]` for optional accelerated modules.
- ✅ Rebuild the full dependency graph with consistent features when that is required for correctness.
- ✅ For wasm, check the target engine's supported proposals before shipping.
- ✅ Use `wasm32v1-none` when a stable import-free WebAssembly 1.0-style baseline is the main requirement.

## Pitfalls
- ⚠️ Enabling `-C target-cpu=native` in release artifacts shipped to other machines.
- ⚠️ Assuming a function-level `#[target_feature]` is enough for safe runtime dispatch.
- ⚠️ Forgetting that WebAssembly binaries must not contain instructions the engine cannot validate.
- ⚠️ Relying on `cfg(target_feature)` to observe per-function `#[target_feature]`; it only reflects crate-wide features.
- ⚠️ Mixing dependencies compiled with incompatible codegen assumptions.

## See also
[[Target Triples]]
[[Codegen and Optimization Flags]]
[[Cargo Cross-Compilation Setup]]
[[Rust WebAssembly Targets]]
[[Target-Specific cfg Boundaries]]
[[Conditional Compilation (cfg)]]
[[Inspecting rustc Configuration]]
[[LTO and codegen-units]]
[[Panic Strategy Selection]]
[[WebAssembly, no_std & Targets]]

## Sources
- The rustc book, `-C target-feature` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature
- The Rust Reference, `target_feature` attribute and cfg - [[the-reference]],
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute and https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature
- The rustc book, WebAssembly enabled features - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html#enabled-webassembly-features
