---
type: pattern
title: "Heapless Collections in Embedded Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, no-std, collections]
domain: "Embedded Rust"
difficulty: intermediate
related: ["[[no_std]]", "[[Embedded Rust Basics]]", "[[Bare-Metal Programming]]", "[[Result]]", "[[Unwrap and Expect Overuse]]", "[[Memory-Mapped I/O]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/collections/index.html", "https://doc.rust-lang.org/alloc/", "https://doc.rust-lang.org/core/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Heapless Collections in Embedded Rust

Heapless collections are fixed-capacity data structures used in `no_std` firmware to make memory use and insertion failure explicit instead of depending on a global heap.

## What it is
`core` has no heap-backed `Vec`, `String`, or maps. Firmware can opt into the `alloc` crate with a global allocator, but that creates new questions: where is the heap, how large is it, what happens on out-of-memory, and can allocation happen inside timing-critical code?

A heapless collection chooses its capacity up front. It stores elements inline, in a static buffer, or in another explicitly owned region. Insertions return `Result` when capacity can be exhausted.

This pattern is useful for message queues, small logs, command buffers, sensor windows, protocol frames, and other bounded data where the maximum size is part of the system design.

## How it works
The collection's type or value carries a fixed capacity. Push-like operations check `len < capacity`. If there is room, they insert in predictable time. If not, they return the rejected item or an error.

The tradeoff is explicit. You avoid allocator setup, fragmentation, hidden reallocations, and surprise OOM paths. In exchange, you must choose capacities and handle the full condition locally.

Crates such as `heapless` provide production implementations for common data structures. The exact public API evolves by crate version, so application notes should cite the crate docs for concrete type names. The pattern itself is stable: bounded storage plus explicit insertion failure.

The compiler can often optimize fixed-capacity collections well because their storage layout is known. The cost is that large inline buffers move with their owner unless they are placed behind a static, passed by mutable reference, or pinned in a driver-owned struct. On small MCUs, that stack-versus-static placement is part of the design.

Bounded collections also make backpressure explicit. A full queue is not exceptional in the Rust sense; it is one of the designed states of the system. Good firmware decides whether to reject a command, drop the oldest sample, overwrite a telemetry slot, set an overflow flag, or slow the producer.

## Example
```rust
#![no_std]

pub struct FixedLog {
    len: usize,
    buf: [u16; 8],
}

impl FixedLog {
    pub const fn new() -> Self {
        Self { len: 0, buf: [0; 8] }
    }

    pub fn push(&mut self, value: u16) -> Result<(), u16> {
        if self.len == self.buf.len() {
            return Err(value);
        }

        self.buf[self.len] = value;
        self.len += 1;
        Ok(())
    }

    pub fn as_slice(&self) -> &[u16] {
        &self.buf[..self.len]
    }
}
```

This is the core heapless idea without external dependencies: storage is bounded, `push` can fail, and the caller must decide what to do when capacity is exhausted.

## More realistic example
```rust
#![no_std]

pub struct Ring<const N: usize> {
    head: usize,
    len: usize,
    buf: [u8; N],
}

impl<const N: usize> Ring<N> {
    pub const fn new() -> Self {
        Self { head: 0, len: 0, buf: [0; N] }
    }

    pub fn push_drop_oldest(&mut self, byte: u8) -> bool {
        if N == 0 {
            return false;
        }

        let tail = (self.head + self.len) % N;
        self.buf[tail] = byte;
        if self.len == N {
            self.head = (self.head + 1) % N;
            false
        } else {
            self.len += 1;
            true
        }
    }

    pub fn pop(&mut self) -> Option<u8> {
        if self.len == 0 {
            return None;
        }
        let byte = self.buf[self.head];
        self.head = (self.head + 1) % N;
        self.len -= 1;
        Some(byte)
    }
}
```

This models a common UART or sensor buffer policy: newest data is accepted, the oldest byte is dropped when full, and the boolean return lets the caller count or report overflow.

## Common errors
```text
warning: unused `Result` that must be used
```
Bounded insertion usually returns `Result` because capacity can be exhausted. Fix it by handling `Err`, propagating it, or deliberately documenting a drop policy.

```text
error[E0382]: use of moved value
```
Large fixed buffers and heapless collections are owned values. Passing one by value into a driver moves it; fix by passing `&mut`, returning it from the driver, or making the driver own it for its whole lifetime.

## Best practice
- ✅ Use heapless or fixed-capacity structures for real-time paths where allocation latency or OOM would be unacceptable.
- ✅ Treat capacity as an engineering parameter: derive it from protocol limits, queue depth, sampling windows, or memory budget.
- ✅ Handle insertion failure deliberately with backpressure, dropping policy, error propagation, or telemetry.
- ✅ Keep large fixed buffers in static storage when stack size is tight.
- ✅ Prefer const-generic capacities or type-level capacities when the chosen crate supports them; capacity then appears in signatures and reviews.
- ✅ Place buffers according to lifetime and size: stack for small temporary frames, statics for long-lived queues, driver fields for owned peripheral state.
- ✅ Include overflow counters or status bits when dropping data is acceptable; silent loss is hard to debug in deployed firmware.

## Pitfalls
- ⚠️ Calling `.unwrap()` on every bounded insertion; that turns a designed capacity limit into a panic path.
- ⚠️ Oversizing fixed buffers everywhere "just in case"; static and stack memory are finite on microcontrollers.
- ⚠️ Assuming heapless always means cheaper. Very large inline buffers can be expensive to move and can inflate stack frames.
- ⚠️ Introducing `alloc` casually in firmware without defining allocator behavior and OOM policy.
- ⚠️ Forgetting interrupt access. A foreground consumer and interrupt producer still need atomics, a critical section, or a lock-free queue design.
- ⚠️ Picking a capacity from a happy-path example instead of the protocol maximum plus worst-case scheduling delay.

## See also
[[no_std]] · [[Embedded Rust Basics]] · [[Bare-Metal Programming]] · [[Interrupts and Concurrency (Embedded)]] · [[Critical Sections in Embedded Rust]] · [[Result]] · [[Unwrap and Expect Overuse]] · [[Panic Unwinding and Abort]] · [[Memory-Mapped I/O]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "Collections" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/collections/index.html
- Rust `alloc` crate documentation,
  https://doc.rust-lang.org/alloc/
- `core::result::Result`,
  https://doc.rust-lang.org/core/result/enum.Result.html
