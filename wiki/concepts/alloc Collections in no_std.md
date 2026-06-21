---
type: concept
title: "alloc Collections in no_std"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, alloc, collections, no-std, wasm]
domain: "WebAssembly, no_std & Targets"
difficulty: intermediate
related: ["[[Using alloc without std]]", "[[Global Allocators]]", "[[Heapless Collections in Embedded Rust]]", "[[try_reserve and Fallible Allocation]]", "[[Vec]]", "[[BTreeMap and BTreeSet]]"]
sources: ["[[std]]", "[[embedded-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/alloc/", "https://doc.rust-lang.org/alloc/collections/index.html", "https://doc.rust-lang.org/stable/embedded-book/collections/index.html", "https://docs.rs/heapless/latest/heapless/", "https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/template-deep-dive/wee_alloc.html"]
rust_version: "edition 2024 / 1.85+"
---

# alloc Collections in no_std

`alloc` collections are heap-backed Rust collections available without `std`; they work in `no_std` libraries, but final artifacts still need a global allocator and a deliberate out-of-memory policy.

## What it is
`core` contains no heap-backed collections.
`alloc` is the standard Rust crate for heap-managed smart pointers, strings, vectors, and collections without the full operating-system layer of `std`.
The `alloc` crate docs describe it as the core allocation and collections library.

In `no_std` code, you import it explicitly with `extern crate alloc`.
Common imports include `alloc::vec::Vec`, `alloc::string::String`, `alloc::boxed::Box`, `alloc::rc::Rc`, `alloc::collections::BTreeMap`, `alloc::collections::BTreeSet`, `alloc::collections::VecDeque`, `alloc::collections::BinaryHeap`, and `alloc::collections::LinkedList`.
`Arc` is also in `alloc`, but target support depends on pointer-width atomics.

The `alloc::collections` module is not identical to `std::collections`.
It contains ordered and sequence collections such as `BTreeMap`, `BTreeSet`, `VecDeque`, `BinaryHeap`, and `LinkedList`.
It does not provide the standard `HashMap` and `HashSet` API directly.
On constrained targets, hash maps also raise policy questions around hashing, determinism, memory growth, and sometimes randomness.

This note is narrower than [[Using alloc without std]].
That note explains the crate boundary and allocator requirement.
This note focuses on choosing and designing APIs around the heap-backed collections themselves.

## How it works
A `no_std` library may compile code using `alloc` without choosing a heap implementation.
That is useful for portable libraries: they can offer allocating helpers while leaving [[Global Allocators]] to the final program.

The final binary, firmware image, staticlib, cdylib, or wasm module must ensure allocation is available if any `alloc` path is actually linked and used.
On embedded targets, that usually means a global allocator backed by a linker-defined RAM region or allocator crate.
On wasm targets, it means understanding the allocator included in the module and measuring code size if that matters.
The RustWasm wasm-pack allocator page is useful historical context, but it is from a legacy docs domain, so verify current allocator guidance and crate versions before copying its example.

Collection operations can allocate implicitly.
`Vec::push`, `String::push_str`, `BTreeMap::insert`, `VecDeque::push_back`, and `BinaryHeap::push` may request more heap memory.
That request can fail.
Use `try_reserve` or `try_reserve_exact` when capacity planning should be fallible and visible in the API.

The Embedded Rust Book contrasts `alloc` collections with fixed-capacity `heapless` collections.
`alloc` collections can grow and reallocate, which is ergonomic but makes worst-case memory use and worst-case execution time harder to bound.
`heapless` collections require capacity up front and report full conditions locally.
As verified on 2026-06-21, docs.rs reports `heapless` latest as `0.9.3`; verify latest docs.rs before adopting a crate API.

## Example
```rust
#![no_std]

extern crate alloc;

use alloc::collections::BTreeMap;
use alloc::vec::Vec;

pub fn byte_positions(input: &[u8]) -> BTreeMap<u8, Vec<usize>> {
    let mut positions = BTreeMap::new();

    for (index, byte) in input.iter().copied().enumerate() {
        positions.entry(byte).or_insert_with(Vec::new).push(index);
    }

    positions
}
```

This compiles as `no_std` library code using `alloc`.
A final artifact that calls it must provide a working global allocator.
The map is ordered by byte value, so iteration order is deterministic.

## Fallible capacity planning
```rust
extern crate alloc;

use alloc::collections::TryReserveError;
use alloc::vec::Vec;

pub fn copy_with_budget(input: &[u8]) -> Result<Vec<u8>, TryReserveError> {
    let mut out = Vec::new();
    out.try_reserve(input.len())?;
    out.extend_from_slice(input);
    Ok(out)
}

fn main() -> Result<(), TryReserveError> {
    let copied = copy_with_budget(b"alloc")?;
    assert_eq!(copied, b"alloc");
    Ok(())
}
```

This second snippet uses a `std` test harness shape for easy execution, but the core function uses `alloc` APIs.
The important pattern is making the capacity request part of the function's `Result`.

## Best practice
- ✅ Offer allocation-free APIs first when a caller can provide a slice, array, or mutable output buffer.
- ✅ Put allocating conveniences behind an `alloc` Cargo feature in reusable crates.
- ✅ Use `extern crate alloc` and import collection types from `alloc::...`, not `std::...`, in `no_std` code.
- ✅ Choose ordered `BTreeMap` or `BTreeSet` when deterministic iteration matters.
- ✅ Use `try_reserve` before large or input-sized growth when memory failure should be reported.
- ✅ Prefer [[Heapless Collections in Embedded Rust]] for interrupt paths, hard real-time paths, and fixed memory budgets.
- ✅ Document collection growth behavior in APIs that may run on embedded, wasm, plugin, or kernel targets.
- ✅ Verify docs.rs latest versions before adopting external no-alloc or allocator-related crates.

## Pitfalls
- ⚠️ Assuming `alloc` gives every `std::collections` type; standard `HashMap` and `HashSet` are not in `alloc::collections`.
- ⚠️ Forgetting that `Vec::push` and `BTreeMap::insert` may allocate far away from the original capacity decision.
- ⚠️ Hiding unbounded allocation behind a function that appears safe for real-time or interrupt context.
- ⚠️ Calling `.unwrap()` on `try_reserve` in code that promised recoverable memory pressure.
- ⚠️ Treating deterministic `BTreeMap` ordering as a substitute for analyzing memory growth.
- ⚠️ Pulling in `std` through dependency default features while trying to keep a `no_std` collection path.
- ⚠️ Choosing `alloc` collections when a fixed protocol maximum would make a heapless buffer simpler.
- ⚠️ Measuring wasm size before considering how collection use pulls allocator support into the module.

## See also
[[Using alloc without std]]
[[Global Allocators]]
[[Panic Handlers]]
[[no_std Crate Design]]
[[Heapless Collections in Embedded Rust]]
[[try_reserve and Fallible Allocation]]
[[Vec]]
[[VecDeque]]
[[BinaryHeap Priority Queues]]
[[BTreeMap and BTreeSet]]
[[Capacity and Reallocation]]
[[Rust WebAssembly Targets]]
[[WebAssembly, no_std & Targets]]

## Sources
- Rust `alloc` crate documentation - [[std]],
  https://doc.rust-lang.org/alloc/
- Rust `alloc::collections` documentation - [[std]],
  https://doc.rust-lang.org/alloc/collections/index.html
- The Embedded Rust Book, "Collections" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/collections/index.html
- `heapless` crate documentation, verify latest version before pinning,
  https://docs.rs/heapless/latest/heapless/
- RustWasm wasm-pack docs, "`wee_alloc`" - verify latest allocator guidance before copying,
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/template-deep-dive/wee_alloc.html
