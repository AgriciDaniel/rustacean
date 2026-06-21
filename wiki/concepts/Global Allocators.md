---
type: concept
title: "Global Allocators"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, allocator, allocation, no-std, wasm]
domain: "WebAssembly, no_std & Targets"
difficulty: advanced
related: ["[[Using alloc without std]]", "[[alloc Collections in no_std]]", "[[no_std Crate Design]]", "[[Allocator Choices]]", "[[Panic Handlers]]", "[[try_reserve and Fallible Allocation]]"]
sources: ["[[the-reference]]", "[[std]]", "[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/runtime.html#the-global_allocator-attribute", "https://doc.rust-lang.org/core/alloc/trait.GlobalAlloc.html", "https://doc.rust-lang.org/std/alloc/fn.handle_alloc_error.html", "https://doc.rust-lang.org/stable/embedded-book/collections/index.html", "https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/template-deep-dive/wee_alloc.html", "https://docs.rs/wee_alloc/latest/wee_alloc/"]
rust_version: "edition 2024 / 1.85+"
---

# Global Allocators

A global allocator is the crate-graph-wide heap implementation selected with `#[global_allocator]`; `alloc` and `std` collection growth route through it, so final binaries choose it and reusable libraries normally do not.

## What it is
Rust heap allocation is centralized behind a global allocation interface.
Types such as [[Box]], [[Vec]], [[String and str]], `Rc`, `Arc`, `VecDeque`, and ordered maps eventually ask the global allocator for memory when they grow or create heap storage.

On hosted `std` targets, the standard library supplies a default global allocator.
A binary may override that default by placing `#[global_allocator]` on one `static` item.
The Rust Reference says that the item must have a type implementing `GlobalAlloc`, and that the attribute may appear only once in the crate graph.

In [[no_std Crate Design]], the distinction is sharper.
`core` has no heap collections.
`alloc` supplies heap-backed types, but the final linked artifact must have an allocator policy.
That policy includes where the heap memory lives, how allocation and deallocation are synchronized, and what happens when memory is exhausted.

For WebAssembly, allocator choice can affect `.wasm` size and runtime behavior.
The RustWasm wasm-pack docs discuss `wee_alloc` as a tiny wasm-focused allocator, but the page is from a legacy docs domain and also notes a speed tradeoff.
The docs.rs latest page should be verified before adopting the crate.
As verified on 2026-06-21, docs.rs reports `wee_alloc` latest as `0.4.5`.

## How it works
`GlobalAlloc` is an unsafe trait because implementations must uphold pointer, layout, alignment, initialization, and deallocation contracts that callers rely on.
The required methods are `alloc` and `dealloc`; provided methods include `alloc_zeroed` and `realloc`.
Allocator methods must not unwind.
The official `GlobalAlloc` docs warn that panicking inside an allocator may lead to memory unsafety.

The `#[global_allocator]` attribute is not a local optimization toggle.
It selects the allocator for the whole final crate graph.
If two dependencies each tried to declare one, the final program could not choose a coherent heap.
That is why general-purpose libraries should expose allocation behavior through APIs and features, while the application crate or final firmware image owns the actual attribute.

Allocation failure is also target policy.
The `GlobalAlloc` API reports failure with a null pointer for allocation methods.
High-level collection APIs may call `handle_alloc_error` when ordinary infallible allocation cannot proceed.
The standard `handle_alloc_error` documentation says it diverges; on `std` binaries the default behavior is to print and abort, while all-`no_std` binaries route through `panic!` and therefore through the configured [[Panic Handlers]].

Do not treat allocation as an observable side channel for correctness.
The `GlobalAlloc` docs explicitly warn that optimizations may remove, stack-promote, or otherwise change allocations.
A custom allocator may be useful for measuring or debugging, but safe program behavior must not depend on a particular call count.

## Example
```rust
use std::alloc::System;

#[global_allocator]
static GLOBAL: System = System;

fn collect_lengths(words: &[&str]) -> Vec<usize> {
    let mut lengths = Vec::with_capacity(words.len());
    for word in words {
        lengths.push(word.len());
    }
    lengths
}

fn main() {
    let lengths = collect_lengths(&["wasm", "alloc", "rust"]);
    assert_eq!(lengths, vec![4, 5, 4]);
}
```

This example compiles on a normal `std` target and explicitly selects the system allocator.
It demonstrates where the attribute lives.
It does not imply `System` is best for every platform, nor does it configure a heap for bare-metal `no_std`.

## no_std boundary
```rust
#![no_std]

extern crate alloc;

use alloc::vec::Vec;

pub fn copy_nonzero(input: &[u8]) -> Vec<u8> {
    input.iter().copied().filter(|byte| *byte != 0).collect()
}
```

This library code can name `alloc::vec::Vec`.
The final binary that links it still chooses the allocator.
A firmware image might use a reviewed embedded allocator crate and initialize its heap from linker-provided RAM.
A wasm module might keep the default allocator or select a wasm-specific one after measuring code size and allocation frequency.

## Best practice
- ✅ Put `#[global_allocator]` in the final binary, firmware image, test harness, benchmark, or wasm package root.
- ✅ Prefer maintained allocator crates over hand-written `GlobalAlloc` implementations.
- ✅ Verify docs.rs latest versions and release history before adopting allocator crates.
- ✅ Keep reusable libraries allocator-agnostic; offer non-allocating APIs and optional [[Using alloc without std]] helpers.
- ✅ Use [[try_reserve and Fallible Allocation]] before large growth when allocation failure should be recoverable.
- ✅ Document heap size, placement, synchronization, and OOM behavior for `no_std` targets.
- ✅ Benchmark allocator changes on the real target and workload, especially for wasm code size versus runtime speed.
- ✅ Keep allocator code free of accidental recursive allocation and unwinding.

## Pitfalls
- ⚠️ Declaring a global allocator in a library steals a process-wide decision from downstream applications.
- ⚠️ Multiple `#[global_allocator]` declarations in one crate graph are invalid.
- ⚠️ Implementing `GlobalAlloc` casually is unsafe; wrong layout or pointer handling can make safe collection code unsound.
- ⚠️ Panicking from allocator methods violates the current safety expectations; return null for allocation failure where the trait permits it.
- ⚠️ Assuming `extern crate alloc` creates a heap; it only imports heap-backed APIs.
- ⚠️ Depending on allocator call counts for correctness ignores optimizer freedom.
- ⚠️ Picking a tiny wasm allocator without checking current maintenance and performance can trade away too much runtime behavior.
- ⚠️ Treating allocation failure as impossible on constrained targets hides the actual system limit.

## See also
[[Using alloc without std]]
[[alloc Collections in no_std]]
[[Panic Handlers]]
[[Panic Strategy Selection]]
[[no_std Crate Design]]
[[Rust WebAssembly Targets]]
[[Allocator Choices]]
[[try_reserve and Fallible Allocation]]
[[Heapless Collections in Embedded Rust]]
[[Reducing Heap Allocations]]
[[Capacity and Reallocation]]
[[WebAssembly, no_std & Targets]]

## Sources
- The Rust Reference, "`global_allocator` attribute" - [[the-reference]],
  https://doc.rust-lang.org/reference/runtime.html#the-global_allocator-attribute
- Rust `core::alloc::GlobalAlloc` documentation - [[std]],
  https://doc.rust-lang.org/core/alloc/trait.GlobalAlloc.html
- Rust `std::alloc::handle_alloc_error` documentation - [[std]],
  https://doc.rust-lang.org/std/alloc/fn.handle_alloc_error.html
- The Embedded Rust Book, "Collections" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/collections/index.html
- RustWasm wasm-pack docs, "`wee_alloc`" - verify latest crate version before adopting,
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/template-deep-dive/wee_alloc.html
- `wee_alloc` crate documentation, verify latest version before pinning,
  https://docs.rs/wee_alloc/latest/wee_alloc/
