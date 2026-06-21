---
type: concept
title: "Using alloc without std"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, no-std, alloc, allocator, heap]
domain: "WebAssembly, no_std & Targets"
difficulty: advanced
related: ["[[no_std Crate Design]]", "[[no_std]]", "[[Panic Strategy Selection]]", "[[Heapless Collections in Embedded Rust]]", "[[Reducing Heap Allocations]]"]
sources: ["[[embedded-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/alloc/", "https://doc.rust-lang.org/core/alloc/trait.GlobalAlloc.html", "https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html"]
rust_version: "edition 2024 / 1.85+"
---

# Using alloc without std

`alloc` gives `no_std` code heap-backed types such as `Vec`, `String`, `Box`, `Rc`, and `Arc`, but the final linked program must provide a global allocator and an allocation-failure policy.

## What it is
`core` has no heap collections.
`alloc` is the Rust library that supplies heap-managed smart pointers and collections without requiring the full `std` operating-system layer.
The official `alloc` docs describe it as the core allocation and collections library.
In ordinary `std` programs, most of its contents are re-exported through `std`.
In [[no_std Crate Design]], you import `alloc` explicitly.

Common `alloc` APIs include:
- `alloc::vec::Vec`
- `alloc::string::String`
- `alloc::boxed::Box`
- `alloc::rc::Rc`
- `alloc::sync::Arc`
- `alloc::format!`
- `alloc::collections::BTreeMap`
- `alloc::collections::VecDeque`

`HashMap` and `HashSet` are not always a portable assumption in constrained environments because secure random seeding can require platform integration.

## How it works
A `no_std` library can usually compile code that mentions `alloc`.
The final binary, cdylib, staticlib, or firmware image must link an allocator if allocation can occur.
The allocator is registered with `#[global_allocator]`.
The allocator implements the unsafe `core::alloc::GlobalAlloc` trait.
The Rust docs warn that allocator methods must not unwind.
They also warn not to rely on allocations actually happening because optimizations may remove or move allocations.

For libraries, the best design is to make allocation explicit.
Offer non-allocating APIs first.
Offer allocating helpers under an `alloc` Cargo feature.
Leave `#[global_allocator]` to the application or final binary.
Document worst-case memory use where it matters.

## Example
```rust
#![no_std]

extern crate alloc;

use alloc::vec::Vec;

pub fn doubled(input: &[u8]) -> Vec<u8> {
    input.iter().flat_map(|byte| [*byte, *byte]).collect()
}

pub fn doubled_into(input: &[u8], out: &mut [u8]) -> usize {
    let mut written = 0;
    for byte in input {
        if written + 2 > out.len() {
            break;
        }
        out[written] = *byte;
        out[written + 1] = *byte;
        written += 2;
    }
    written
}
```

The first function needs `alloc`.
The second function works with only `core`.
That split lets callers choose the allocation policy.

## Edge case
```rust
pub fn needs_capacity(input_len: usize) -> usize {
    input_len.saturating_mul(2)
}

fn main() {
    assert_eq!(needs_capacity(4), 8);
}
```

Pre-computing capacity is useful, but it is not an allocation guarantee.
On constrained systems, the caller may still reject the requested size or use fixed storage.

## Best practice
- ✅ Make the non-allocating API the foundation.
- ✅ Put allocating helpers behind an `alloc` feature when writing reusable crates.
- ✅ Let final binaries choose `#[global_allocator]`.
- ✅ Treat allocation failure as part of target design, not as an afterthought.
- ✅ Prefer [[Heapless Collections in Embedded Rust]] when maximum memory use must be statically bounded.
- ✅ Check allocator crate docs.rs pages and verify the latest version before adopting a crate.

## Pitfalls
- ⚠️ Adding `extern crate alloc` does not by itself provide a heap.
- ⚠️ Implementing `GlobalAlloc` casually is unsafe and easy to get wrong.
- ⚠️ Panicking from allocator methods can lead to memory unsafety.
- ⚠️ Using hidden allocations in APIs that users expect to run in interrupts or tight loops.
- ⚠️ Assuming `Vec` growth behavior is acceptable on every target; see [[Reducing Heap Allocations]].

## See also
[[no_std Crate Design]]
[[no_std]]
[[Heapless Collections in Embedded Rust]]
[[Reducing Heap Allocations]]
[[Panic Strategy Selection]]
[[Target Features and CPU Baselines]]
[[Rust WebAssembly Targets]]
[[Box]]
[[Vec]]
[[WebAssembly, no_std & Targets]]

## Sources
- Rust `alloc` library documentation,
  https://doc.rust-lang.org/alloc/
- Rust `core::alloc::GlobalAlloc` documentation,
  https://doc.rust-lang.org/core/alloc/trait.GlobalAlloc.html
- The Embedded Rust Book, "A no_std Rust Environment" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html
