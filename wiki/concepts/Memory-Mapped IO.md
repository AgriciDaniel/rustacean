---
type: concept
title: "Memory-Mapped IO"
aliases: ["Memory-Mapped I/O"]
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, mmio, volatile]
domain: "Embedded Rust"
difficulty: intermediate
related: ["[[Peripheral Access Crates]]", "[[Embedded Rust Basics]]", "[[Bare-Metal Programming]]", "[[no_std]]", "[[Unsynchronized static mut in Interrupts]]", "[[Unsafe Rust]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/start/registers.html", "https://doc.rust-lang.org/stable/embedded-book/peripherals/borrowck.html", "https://doc.rust-lang.org/core/ptr/fn.read_volatile.html", "https://doc.rust-lang.org/core/ptr/fn.write_volatile.html"]
rust_version: "edition 2024 / 1.85+"
---

# Memory-Mapped IO

Memory-mapped I/O is the embedded technique of controlling hardware by reading and writing special addresses, which Rust code must access through volatile operations and carefully modeled ownership.

## What it is
Many microcontroller peripherals expose registers at fixed memory addresses. Reading one address might return a GPIO input state; writing another might enable a timer, clear an interrupt flag, or start a DMA transfer.

These addresses are not ordinary RAM. The value may change because hardware changed it, a write may have side effects, and repeating or omitting a read or write can change device behavior. That is why MMIO is fundamentally an `unsafe` boundary when accessed directly.

Rust usually hides raw MMIO behind PACs, HALs, and board crates. Those layers still use volatile pointer operations internally, but they provide typed APIs so application code does not need to manipulate addresses and bit masks everywhere.

## How it works
Direct MMIO uses raw pointers and `core::ptr::read_volatile` or `core::ptr::write_volatile`. Volatile tells the compiler that this specific access must happen and must not be optimized away as if it were a normal memory load or store.

Volatile is not a synchronization primitive. It does not make a read-modify-write sequence atomic, does not protect against interrupts, and does not create exclusive access to a register block. It only describes the compiler treatment of the individual memory operation.

The Rust-shaped way to make MMIO safer is to put a small `unsafe` block behind a type whose construction is controlled. If only one `GpioA` value can exist, then `&mut GpioA` can mean exclusive software access to that hardware block, and normal borrow checking becomes useful.

Current Rust documents volatile operations as externally observable events intended for I/O memory. For MMIO outside any Rust allocation, pointer provenance is not the useful safety boundary; the real requirements are that the address and access width are meaningful for the target, properly aligned for the type, do not trap, and do not mutate Rust-owned memory behind the compiler's back.

Rust 2024 also makes unsafe operations inside `unsafe fn` explicit: the function can be unsafe to call, but each volatile read, volatile write, or raw pointer dereference still belongs in a local `unsafe { ... }` block. That keeps the exact hardware operation visible during review.

## Example
```rust
#![no_std]

use core::ptr::{read_volatile, write_volatile};

#[derive(Clone, Copy)]
pub struct Register32 {
    address: *mut u32,
}

impl Register32 {
    pub unsafe fn new(address: usize) -> Self {
        Self { address: address as *mut u32 }
    }

    pub unsafe fn read(self) -> u32 {
        unsafe { read_volatile(self.address) }
    }

    pub unsafe fn write(self, value: u32) {
        unsafe { write_volatile(self.address, value) }
    }
}

pub unsafe fn set_bit(register: Register32, bit: u32) {
    let value = unsafe { register.read() };
    unsafe { register.write(value | (1 << bit)) };
}
```

This compiles without target dependencies, but the safety contract is real: the caller must pass a valid MMIO address for a 32-bit register and must ensure the read-modify-write is appropriate for that register and concurrency context.

## More realistic example
```rust
#![no_std]

use core::ptr::{read_volatile, write_volatile};

pub struct StatusControl {
    status: *const u32,
    control: *mut u32,
}

impl StatusControl {
    pub unsafe fn new(status: usize, control: usize) -> Self {
        Self {
            status: status as *const u32,
            control: control as *mut u32,
        }
    }

    pub fn ready(&self) -> bool {
        let bits = unsafe { read_volatile(self.status) };
        bits & 0b1 != 0
    }

    pub fn start(&mut self) {
        unsafe { write_volatile(self.control, 0b1) };
    }
}
```

The `ready` method can take `&self` because reading a status register does not require exclusive ownership of the wrapper. `start` takes `&mut self` to make command writes explicit and to leave room for future methods that must sequence multiple register accesses.

## Common errors
```text
error[E0133]: call to unsafe function `core::ptr::read_volatile` is unsafe and requires unsafe block
```
Fix it with a small `unsafe` block at the exact access site, and put the safety explanation on the wrapper constructor or method.

```text
warning[E0133]: dereference of raw pointer is unsafe and requires unsafe block
```
In edition 2024, do not rely on an `unsafe fn` body to make operations implicitly unsafe. Keep raw pointer dereferences and volatile calls in explicit `unsafe` blocks.

## Best practice
- ✅ Prefer PAC, HAL, or board-crate APIs over handwritten MMIO in application code.
- ✅ Keep direct volatile operations in tiny functions or types with explicit safety contracts.
- ✅ Read the chip reference manual before using write, modify, write-one-to-clear, or reserved bits.
- ✅ Use critical sections or atomics when the register or backing state is shared with interrupts.
- ✅ Match the access width and alignment to the hardware register; a 32-bit register is not automatically safe to access as bytes or halfwords.
- ✅ Separate status reads, command writes, and read-modify-write helpers so the API reflects the register's documented side effects.
- ✅ Treat DMA-visible memory as a separate contract: volatile register writes can start DMA, but buffer ownership, cache maintenance, and lifetimes need their own design.

## Pitfalls
- ⚠️ Using normal pointer reads and writes for hardware registers; the compiler may optimize them in ways that are valid for RAM but wrong for hardware.
- ⚠️ Believing volatile makes shared state safe; see [[Unsynchronized static mut in Interrupts]].
- ⚠️ Performing read-modify-write on registers where writing back read bits can clear flags or trigger hardware actions.
- ⚠️ Creating multiple owned wrappers for the same register block; use singleton-style acquisition as in [[Peripheral Access Crates]].
- ⚠️ Reading a register just to "inspect" it when reads acknowledge, clear, pop, or advance hardware state.
- ⚠️ Writing reserved bits with arbitrary values. Many manuals require preserving reset values or writing zero to reserved fields.

## See also
[[Peripheral Access Crates]] · [[Embedded Rust Basics]] · [[Bare-Metal Programming]] · [[no_std]] · [[Interrupts and Concurrency (Embedded)]] · [[Critical Sections in Embedded Rust]] · [[Unsynchronized static mut in Interrupts]] · [[Unsafe Rust]] · [[Atomics]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "Memory-mapped Registers" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/registers.html
- The Embedded Rust Book, "The Borrow Checker" for peripherals — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/peripherals/borrowck.html
- `core::ptr::read_volatile`,
  https://doc.rust-lang.org/core/ptr/fn.read_volatile.html
- `core::ptr::write_volatile`,
  https://doc.rust-lang.org/core/ptr/fn.write_volatile.html
