---
type: concept
title: "SIMD and target_feature"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, simd, target-feature, codegen]
domain: "Performance & Optimization"
difficulty: advanced
related: ["[[Target Features and CPU Baselines]]", "[[Codegen and Optimization Flags]]", "[[Conditional Compilation (cfg)]]", "[[Unsafe Rust]]", "[[Benchmarking with Criterion]]", "[[Performance & Optimization]]"]
sources: ["[[the-reference]]", "[[rustc-book]]", "[[07-performance-optimization]]"]
source_urls: ["https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute", "https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature", "https://doc.rust-lang.org/std/arch/macro.is_x86_feature_detected.html", "https://doc.rust-lang.org/std/arch/macro.is_aarch64_feature_detected.html", "https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu", "https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature"]
rust_version: "edition 2024 / 1.85+"
---

# SIMD and target_feature

SIMD in Rust is a target-specific optimization: use portable scalar code as the baseline, add feature-specific functions behind `#[target_feature]`, and dispatch only after compile-time or runtime feature checks prove the CPU supports them.

## What it is
SIMD means single instruction, multiple data.
It lets one instruction operate on several lanes of numbers or bytes at once.
Rust exposes target-specific SIMD through `std::arch` and controls instruction availability with crate-wide codegen flags, `#[cfg(target_feature = "...")]`, runtime detection macros, and the `#[target_feature]` function attribute.

The Reference is explicit about the safety boundary.
Calling code compiled for a CPU feature on hardware that does not support that feature is undefined behavior on platforms such as x86 and x86_64.
That is why SIMD code is not just a faster implementation detail.
It is also a deployment and dispatch contract.

Use SIMD after measurement.
LLVM can already auto-vectorize many simple loops when aliases and bounds are clear.
Clear iterator or slice code may compile to vector instructions without explicit intrinsics.
Reach for explicit target features when profiling and assembly or counter inspection show the scalar path remains a real bottleneck.

## How it works
There are three different questions:

1. What is this whole crate allowed to assume?
2. What is this one function allowed to use?
3. What does this running CPU actually support?

`-C target-cpu=...` and `-C target-feature=+foo` answer the first question for the whole crate.
`#[cfg(target_feature = "foo")]` observes crate-wide features during conditional compilation.
It does not become true merely because one function has `#[target_feature(enable = "foo")]`.

`#[target_feature(enable = "...")]` answers the second question for one function.
The function is compiled with that feature enabled.
It is not inlined into a caller that lacks the feature, and `#[inline(always)]` cannot be combined with `#[target_feature]`.
On most native targets, calling it from a context that has not enabled the feature requires an unsafe call because the caller must uphold the runtime CPU guarantee.

Runtime macros such as `is_x86_feature_detected!` answer the third question.
Use them at the dispatch boundary.
Keep the unsafe call small and documented.
Put intrinsics inside the feature-specific function, not scattered throughout ordinary code.

## Example
```rust
fn sum_u32(values: &[u32]) -> u32 {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if std::arch::is_x86_feature_detected!("sse2") {
            // SAFETY: the runtime check above proves SSE2 is available now.
            return unsafe { sum_u32_sse2(values) };
        }
    }

    sum_u32_portable(values)
}

fn sum_u32_portable(values: &[u32]) -> u32 {
    values.iter().copied().sum()
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "sse2")]
unsafe fn sum_u32_sse2(values: &[u32]) -> u32 {
    // Real SSE2 intrinsics would live here.
    // The example keeps the dispatch contract minimal and compilable.
    sum_u32_portable(values)
}

fn main() {
    assert_eq!(sum_u32(&[1, 2, 3, 4]), 10);
}
```

This example demonstrates the shape, not a hand-written intrinsic kernel.
The portable implementation is always present.
The target-specific function is compiled only for x86-family targets.
The unsafe call is guarded by runtime detection and has a local safety comment.

## Choosing the boundary
Prefer one public safe function that dispatches to private implementations.
That keeps callers from needing to reason about CPU features.
Keep the data format and return value identical across implementations.
Use tests to compare portable and accelerated paths on machines where both can run.

For binaries deployed to one known CPU fleet, a crate-wide `-C target-cpu` or target-feature flag may be simpler.
For distributed binaries, do not ship `target-cpu=native` unless every target machine is known to support the same features.
For libraries, avoid raising the CPU baseline unexpectedly.
Offer optional accelerated internals while preserving a portable default.

## Best practice
- ✅ Start with clear portable slice or iterator code and benchmark before adding explicit SIMD.
- ✅ Keep runtime feature detection at one dispatch boundary.
- ✅ Put `#[target_feature]` functions behind target-architecture `cfg` gates.
- ✅ Document the safety reason for each unsafe call into a feature-specific function.
- ✅ Use [[Target Features and CPU Baselines]] to decide whether a feature is a deployment baseline or an optional fast path.
- ✅ Benchmark portable and accelerated paths with [[Benchmarking with Criterion]].
- ✅ Keep feature-specific code private unless the API itself is explicitly unsafe or target-specific.
- ✅ Confirm generated code or counters when the goal is vectorization, not just a source-level rewrite.

## Pitfalls
- ⚠️ Calling a `#[target_feature]` function without proving support can be undefined behavior.
- ⚠️ Assuming `cfg(target_feature)` sees per-function attributes is wrong; it reflects crate-wide features.
- ⚠️ Shipping `-C target-cpu=native` builds to unknown CPUs can crash with illegal instructions.
- ⚠️ Combining `#[inline(always)]` with `#[target_feature]` is not allowed.
- ⚠️ Hand-written intrinsics can lose to auto-vectorized scalar code if they add shuffles, branches, or memory traffic.
- ⚠️ SIMD work that ignores [[Cache-Friendly Data Layout]] may remain memory-bound.
- ⚠️ Adding unsafe SIMD before profiling is [[Speculative Micro-Optimization]].

## See also
[[Target Features and CPU Baselines]] · [[Codegen and Optimization Flags]] · [[Conditional Compilation (cfg)]] · [[Unsafe Rust]] · [[SAFETY Comments]] · [[Benchmarking with Criterion]] · [[Flamegraph and perf Workflow]] · [[Cache-Friendly Data Layout]] · [[Bounds-Check Elimination]] · [[Iterator Performance]] · [[Performance & Optimization]]

## Sources
- The Rust Reference, "`target_feature` attribute" — [[the-reference]],
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-target_feature-attribute
- The Rust Reference, "`target_feature` conditional compilation option" — [[the-reference]],
  https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature
- Rust standard library, `is_x86_feature_detected!`,
  https://doc.rust-lang.org/std/arch/macro.is_x86_feature_detected.html
- Rust standard library, `is_aarch64_feature_detected!`,
  https://doc.rust-lang.org/std/arch/macro.is_aarch64_feature_detected.html
- The rustc Book, codegen options `target-cpu` and `target-feature` — [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu and https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature
- Verified research pack, "Performance & Optimization" — [[07-performance-optimization]]
