---
type: concept
title: "no_std Crate Design"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, no-std, core, embedded, portability]
domain: "WebAssembly, no_std & Targets"
difficulty: advanced
related: ["[[no_std]]", "[[Using alloc without std]]", "[[Panic Strategy Selection]]", "[[Cargo Cross-Compilation Setup]]", "[[Heapless Collections in Embedded Rust]]"]
sources: ["[[embedded-book]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html", "https://doc.rust-lang.org/core/", "https://doc.rust-lang.org/alloc/"]
rust_version: "edition 2024 / 1.85+"
---

# no_std Crate Design

`no_std` crate design means separating reusable Rust logic from operating-system assumptions: use `core` by default, add `alloc` only behind an explicit allocation policy, and leave runtime, allocator, I/O, and panic choices to the final binary.

## What it is
`#![no_std]` tells a crate to link `core` instead of `std`.
The existing [[no_std]] note covers the embedded basics.
This note is about designing portable libraries and binaries across embedded, wasm, kernels, bootloaders, and constrained targets.

`core` still gives you many Rust fundamentals:
- slices and arrays
- primitive methods
- `Option` and `Result`
- iterators over existing storage
- formatting traits
- pointer and memory utilities
- atomics when the target supports them
- marker traits and many language-facing APIs

What it does not give you is an operating-system contract.
No process startup model.
No filesystem.
No sockets.
No threads.
No environment variables.
No default heap collection story.
No panic runtime chosen by `std`.

## How it works
Use `#![cfg_attr(not(test), no_std)]` in libraries when you want native tests to use `std`.
Keep the library's core algorithms free of host I/O and allocation.
Accept caller-provided buffers, slices, and traits.
Expose optional features for `alloc` or `std` integration.

Final binaries make platform choices:
- a startup/runtime crate for bare metal
- a linker script or target runner when needed
- a global allocator if `alloc` is linked
- exactly one panic handler for `no_std` final artifacts
- target-specific I/O or logging

Avoid using `std` as a hidden default feature in reusable crates.
Cargo features should be additive, so a `std` feature should add host conveniences without changing the meaning of the `core` API.
See [[Feature Flags]] and [[Non-Additive Feature Flags]].

## Example
```rust
#![cfg_attr(not(test), no_std)]

pub fn checksum(bytes: &[u8]) -> u8 {
    bytes
        .iter()
        .copied()
        .fold(0_u8, |acc, byte| acc.wrapping_add(byte))
}

pub fn write_hex(byte: u8, out: &mut [u8; 2]) {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    out[0] = HEX[(byte >> 4) as usize];
    out[1] = HEX[(byte & 0x0f) as usize];
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_hex() {
        let mut out = [0; 2];
        write_hex(0xaf, &mut out);
        assert_eq!(&out, b"af");
        assert_eq!(checksum(&out), b'a'.wrapping_add(b'f'));
    }
}
```

## Best practice
- ✅ Put reusable algorithms in `no_std` libraries when they do not inherently need host services.
- ✅ Accept buffers from callers instead of allocating internally.
- ✅ Gate allocating helpers behind [[Using alloc without std]].
- ✅ Gate host-only conveniences behind a `std` feature.
- ✅ Keep startup, panic handling, logging, and hardware access at the binary edge.
- ✅ Test pure code on the host and cross-check target-specific code in CI.

## Pitfalls
- ⚠️ Adding `std` through a dependency's default features by accident.
- ⚠️ Hiding dynamic allocation in a function that looks target-neutral.
- ⚠️ Putting `#[panic_handler]` in a library used by other final binaries.
- ⚠️ Treating `no_std` as a speed switch rather than a platform contract.
- ⚠️ Using `cfg!(...)` to guard code that does not type-check without `std`; use `#[cfg]`.

## See also
[[no_std]]
[[Using alloc without std]]
[[Rust WebAssembly Targets]]
[[Panic Strategy Selection]]
[[Cargo Cross-Compilation Setup]]
[[Target-Specific cfg Boundaries]]
[[Heapless Collections in Embedded Rust]]
[[Bare-Metal Programming]]
[[Embedded Rust Basics]]
[[WebAssembly, no_std & Targets]]

## Sources
- The Embedded Rust Book, "A no_std Rust Environment" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html
- Rust `core` library documentation,
  https://doc.rust-lang.org/core/
- Rust `alloc` library documentation,
  https://doc.rust-lang.org/alloc/
