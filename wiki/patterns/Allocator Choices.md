---
type: pattern
title: "Allocator Choices"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, allocation, allocator]
domain: "Performance & Optimization"
difficulty: advanced
related: ["[[Reducing Heap Allocations]]", "[[Profiling Rust Programs]]", "[[Arena Allocation]]", "[[SmallVec for Inline Storage]]", "[[LTO and codegen-units]]", "[[Performance & Optimization]]"]
sources: ["[[07-performance-optimization]]", "[[rust-performance-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://nnethercote.github.io/perf-book/build-configuration.html", "https://doc.rust-lang.org/reference/runtime.html#the-global_allocator-attribute", "https://doc.rust-lang.org/std/alloc/index.html", "https://doc.rust-lang.org/core/alloc/trait.GlobalAlloc.html", "https://docs.rs/tikv-jemallocator/latest/tikv_jemallocator/", "https://docs.rs/mimalloc/latest/mimalloc/"]
rust_version: "edition 2024 / 1.85+"
---

# Allocator Choices

Allocator choice is a measured build-level optimization: change the global allocator only when profiling shows allocation behavior is hot and the workload benefits from a different allocation strategy.

## What it is
Rust programs using `std` have a global allocator for heap allocations made by `Box`, `Vec`, `String`, `Arc`, most collections, and many library abstractions.
By default, Rust uses the platform's default allocator through the standard library.
The `#[global_allocator]` attribute lets a crate select a different allocator for the final crate graph.

This note is about choosing an allocator for an application or binary.
It is not a replacement for reducing allocation count.
If a hot loop allocates thousands of short-lived `String`s, changing the allocator might help, but [[Reducing Heap Allocations]] may remove the cost entirely.
If objects share a phase lifetime, [[Arena Allocation]] might fit better.
If values are usually tiny vectors, [[SmallVec for Inline Storage]] might avoid the heap on the common path.

Alternative allocators such as jemalloc-family crates or mimalloc can improve speed or memory footprint for some workloads.
They are external dependencies, so cite docs.rs, verify the latest version before pinning, and benchmark against the default allocator in the target deployment environment.

## How it works
The Reference defines `#[global_allocator]` as a runtime attribute applied to one `static` item whose type implements `GlobalAlloc`.
The attribute can be used only once in the crate graph.
That means allocator selection is effectively a final-binary decision, not something each library should impose on downstream users.

The `GlobalAlloc` trait is unsafe to implement because allocation and deallocation must obey strict layout, alignment, and pointer rules.
Most applications should not implement it manually.
Use a maintained allocator crate when a different allocator is justified, or use `std::alloc::System` when the platform allocator must be selected explicitly.

Allocator choice interacts with measurement.
CPU profiles may show allocator functions as hot.
Allocation profilers can show which call paths allocate most.
RSS, peak memory, fragmentation, tail latency, and throughput can move in different directions.
Measure the outcome you actually care about.

## Example
```rust
use std::alloc::System;

#[global_allocator]
static GLOBAL: System = System;

fn collect_words(input: &str) -> Vec<String> {
    input.split_whitespace().map(str::to_owned).collect()
}

fn main() {
    let words = collect_words("measure before changing allocators");
    assert_eq!(words.len(), 4);
}
```

This example compiles with only the standard library and explicitly selects the system allocator.
It is not claiming `System` is faster than the default on every target.
It demonstrates where allocator selection lives and why it is a crate-graph-wide choice.

## Choosing deliberately
Start by proving allocation is relevant.
Use [[Flamegraph and perf Workflow]] for CPU hot paths and allocation-specific tooling when allocator routines dominate.
Then compare candidates under the same profile, input, target, and feature set.
Measure wall-clock time, CPU time, memory footprint, and tail behavior if latency matters.

Keep allocator configuration close to the application root.
Libraries should usually optimize allocation count and data layout, not force a global allocator.
If a library needs specialized allocation internally, prefer local structures such as arenas or reusable buffers over a global process-wide decision.

For third-party allocator crates, the exact dependency line belongs in the project manifest, not in a reusable note.
Check the crate's current docs, supported targets, license, feature flags, and MSRV before adoption.
Do not assume an allocator that helped a Linux service will help a Windows desktop app, a WebAssembly target, or a short-lived CLI.

## Best practice
- ✅ Treat allocator choice as a benchmarked experiment, not a default tweak.
- ✅ Prefer removing allocations before changing the allocator.
- ✅ Put `#[global_allocator]` in the final binary or application crate, not in general-purpose libraries.
- ✅ Compare memory footprint as well as runtime; faster allocation can still increase retained memory.
- ✅ Test under production-like concurrency, input sizes, and target operating systems.
- ✅ Verify the latest docs.rs version and release notes before pinning allocator crates.
- ✅ Keep one baseline run with the default allocator for future regressions.
- ✅ Use local strategies such as [[Arena Allocation]] or scratch-buffer reuse when only one subsystem has allocation pressure.

## Pitfalls
- ⚠️ Multiple `#[global_allocator]` declarations in the crate graph are not allowed.
- ⚠️ Manually implementing `GlobalAlloc` is unsafe and easy to get wrong; prefer maintained allocators.
- ⚠️ Switching allocators to hide excessive `clone`, `format!`, or `collect` calls misses the simpler fix.
- ⚠️ Judging only average throughput can hide worse peak memory or latency.
- ⚠️ Libraries that set a global allocator take control away from applications.
- ⚠️ Allocator wins can be target-specific; avoid assuming the same result across OSes or CPU families.
- ⚠️ Changing allocator and `lto` together makes the result hard to attribute.
- ⚠️ Treating an allocator swap as a substitute for [[Cache-Friendly Data Layout]] can leave cache misses untouched.

## See also
[[Reducing Heap Allocations]] · [[Profiling Rust Programs]] · [[Flamegraph and perf Workflow]] · [[Arena Allocation]] · [[SmallVec for Inline Storage]] · [[LTO and codegen-units]] · [[Profiles and Optimization Settings]] · [[Capacity and Reallocation]] · [[Needless Clone]] · [[Unnecessary Collect]] · [[Cache-Friendly Data Layout]] · [[Performance & Optimization]]

## Sources
- Rust Performance Book, "Build Configuration" — [[rust-performance-book]],
  https://nnethercote.github.io/perf-book/build-configuration.html
- The Rust Reference, "`global_allocator` attribute" — [[the-reference]],
  https://doc.rust-lang.org/reference/runtime.html#the-global_allocator-attribute
- Rust standard library, `std::alloc` — [[std]],
  https://doc.rust-lang.org/std/alloc/index.html
- Rust standard library, `GlobalAlloc` — [[std]],
  https://doc.rust-lang.org/core/alloc/trait.GlobalAlloc.html
- `tikv-jemallocator` crate documentation, verify latest version before pinning,
  https://docs.rs/tikv-jemallocator/latest/tikv_jemallocator/
- `mimalloc` crate documentation, verify latest version before pinning,
  https://docs.rs/mimalloc/latest/mimalloc/
- Verified research pack, "Performance & Optimization" — [[07-performance-optimization]]
