---
type: concept
title: "no_std"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, no-std, core]
domain: "Embedded Rust"
difficulty: basic
related: ["[[Embedded Rust Basics]]", "[[Bare-Metal Programming]]", "[[Memory-Mapped I/O]]", "[[Heapless Collections in Embedded Rust]]", "[[Panic Unwinding and Abort]]", "[[The Never Type]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html", "https://doc.rust-lang.org/core/"]
rust_version: "edition 2024 / 1.85+"
---

# no_std

`no_std` is the crate-level mode for Rust programs that link `core` instead of `std`, which is the default for bare-metal firmware, bootloaders, kernels, and other targets without an operating-system runtime.

## What it is
`#![no_std]` tells the compiler that the crate must not depend on the standard library. The crate still has Rust's language primitives, traits, slices, formatting machinery, atomics when the target supports them, and many other platform-independent APIs through `core`.

The important boundary is platform integration. `std` assumes some system services exist: process startup, threads, file descriptors, networking, environment variables, stack overflow handling, and a heap-backed collection story. A microcontroller usually offers none of those by default. Firmware starts from reset code, talks to hardware registers, and decides explicitly what to do on panic or allocation failure.

`no_std` is not "less Rust"; it is Rust without the host operating-system layer. Most ownership, borrowing, traits, generics, enums, pattern matching, iterators over fixed storage, and zero-cost abstractions work the same way.

## How it works
A `no_std` crate imports `core` automatically, just as a `std` crate imports `std` automatically. You can use `core::fmt`, `core::mem`, `core::ptr`, `core::cell`, `core::sync::atomic`, and many primitive methods without linking an OS runtime.

What disappears is anything that requires a host contract. `Vec`, `String`, and `Box` are not in `core`; they live in `alloc`, and `alloc` requires a global allocator. `println!` is not available unless a target-specific logging path provides something similar. `std::thread`, `std::fs`, and `std::net` are absent because bare-metal code has no standard process or kernel interface to call.

Application firmware normally combines `#![no_std]` with `#![no_main]`, a target runtime such as `cortex-m-rt`, and exactly one panic handler crate or local `#[panic_handler]`. Library crates can often support both `std` and `no_std` by avoiding `std` in their default core logic and adding optional features for allocation or host integration.

At compile time, `#![no_std]` changes name resolution and linking: the crate gets the `core` prelude, not the `std` prelude, and the final binary must supply any missing language items through runtime and panic crates. It does not change ownership, monomorphization, trait dispatch, or optimization; a `no_std` generic function is still normal Rust code after the platform boundary has been removed.

For reusable crates, the common shape is `#![cfg_attr(not(feature = "std"), no_std)]`. Keep the default path allocation-free, expose optional `alloc` support only behind a feature, and put host-only conveniences such as file loading, environment variables, or `std::error::Error` integration behind a separate `std` feature.

## Example
```rust
#![no_std]

pub fn ticks_from_millis(ms: u32, core_hz: u32) -> u32 {
    ms.saturating_mul(core_hz / 1_000)
}

pub fn checksum(bytes: &[u8]) -> u8 {
    bytes.iter().fold(0, |acc, byte| acc.wrapping_add(*byte))
}
```

This compiles as a `no_std` library because it uses only `core` facilities: integer arithmetic, slices, iterators, and pure functions. A firmware binary would add target startup, panic behavior, and hardware access around code like this.

## More realistic example
```rust
#![no_std]

use core::fmt::{self, Write};

pub struct LineBuffer<const N: usize> {
    len: usize,
    bytes: [u8; N],
}

impl<const N: usize> LineBuffer<N> {
    pub const fn new() -> Self {
        Self { len: 0, bytes: [0; N] }
    }

    pub fn as_str(&self) -> &str {
        // Safety: write_str only appends UTF-8 input.
        unsafe { core::str::from_utf8_unchecked(&self.bytes[..self.len]) }
    }
}

impl<const N: usize> Write for LineBuffer<N> {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        let next = self.len.checked_add(s.len()).ok_or(fmt::Error)?;
        if next > N {
            return Err(fmt::Error);
        }
        self.bytes[self.len..next].copy_from_slice(s.as_bytes());
        self.len = next;
        Ok(())
    }
}

pub fn render_voltage(millivolts: u16) -> LineBuffer<16> {
    let mut out = LineBuffer::new();
    let _ = write!(&mut out, "{} mV", millivolts);
    out
}
```

This uses `core::fmt` without `String` or heap allocation. In production firmware the same `Write` idea can target a fixed buffer, UART logger, ITM port, RTT channel, or display driver.

## Common errors
```text
error[E0433]: failed to resolve: use of unresolved module or unlinked crate `std`
```
Fix it by replacing `std::...` imports with `core::...` when the API is platform-independent, or by gating that code behind a `std` feature.

```text
error: `#[panic_handler]` function required, but not found
```
Fix it in a final `no_std` binary by linking exactly one panic handler crate, such as `panic-halt`, or by defining one local `#[panic_handler]`. A library crate should usually not choose panic behavior for the final program.

## Best practice
- ✅ Put reusable embedded logic in `no_std` libraries when it does not inherently need host services.
- ✅ Add `alloc` only when dynamic allocation is a deliberate design choice with a configured allocator and OOM policy.
- ✅ Keep target-specific runtime glue at the binary edge; let drivers and algorithms depend on `core` where possible.
- ✅ Choose and document one panic behavior for the final firmware image, such as halt, abort, semihosting, or target-specific logging.
- ✅ Audit dependency features: many crates are `no_std` only when `default-features = false` or when a `std` feature is left disabled.
- ✅ Use `core::fmt::Write`, slices, arrays, const generics, and iterator adapters over fixed storage before reaching for `alloc`.
- ✅ Test pure `no_std` libraries on the host with a `std` dev harness when possible; the library can stay `no_std` while tests use host tooling.

## Pitfalls
- ⚠️ Assuming `no_std` forbids all dynamic allocation. It forbids `std`; allocation is possible through `alloc`, but it must be configured explicitly and analyzed for failure.
- ⚠️ Pulling in a dependency whose default features require `std`; disable default features or select crates that advertise `no_std` support.
- ⚠️ Treating `no_std` as a performance switch for desktop code. It is a platform-contract switch, not a general optimization setting.
- ⚠️ Forgetting that a `no_std` binary still needs startup and panic behavior; see [[Bare-Metal Programming]] and [[Panic Unwinding and Abort]].
- ⚠️ Letting a reusable crate depend directly on a board HAL. Keep algorithms and protocol code generic over traits or plain buffers so they remain portable.
- ⚠️ Assuming `HashMap` is a normal `alloc` choice in firmware. Hashing needs policy decisions around memory, determinism, and randomness; fixed maps or sorted arrays are often clearer.

## See also
[[Embedded Rust Basics]] · [[Bare-Metal Programming]] · [[Memory-Mapped I/O]] · [[Peripheral Access Crates]] · [[Heapless Collections in Embedded Rust]] · [[Critical Sections in Embedded Rust]] · [[Panic Unwinding and Abort]] · [[The Never Type]] · [[Result]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "A no_std Rust Environment" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html
- Rust `core` library documentation,
  https://doc.rust-lang.org/core/
