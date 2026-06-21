---
type: pattern
title: "Critical Sections in Embedded Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, interrupts, synchronization]
domain: "Embedded Rust"
difficulty: intermediate
related: ["[[Interrupts and Concurrency (Embedded)]]", "[[Unsynchronized static mut in Interrupts]]", "[[Memory-Mapped I/O]]", "[[Peripheral Access Crates]]", "[[The Drop Trait]]", "[[Interior Mutability]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/concurrency/index.html", "https://doc.rust-lang.org/core/cell/struct.Cell.html", "https://doc.rust-lang.org/core/cell/struct.RefCell.html"]
rust_version: "edition 2024 / 1.85+"
---

# Critical Sections in Embedded Rust

A critical section is the embedded Rust pattern of temporarily preventing interrupt preemption while accessing shared state, ideally represented by a token so safe APIs can require proof that the section is active.

## What it is
On a single-core microcontroller, disabling interrupts creates a short region where the foreground code cannot be interrupted by normal interrupt handlers. That can make a non-atomic read-modify-write sequence safe with respect to those handlers.

Rust embedded libraries commonly expose this as a closure API. On Cortex-M, `cortex_m::interrupt::free` runs a closure with interrupts disabled and passes a `CriticalSection` token. Types can require that token before exposing access to shared state.

The token is the important Rust idea. Instead of scattering `unsafe` blocks across application code, the synchronization requirement becomes part of the function signature.

## How it works
The critical-section function saves interrupt state, disables interrupts, calls the closure, then restores the previous state. The closure cannot keep the token beyond the call unless the API deliberately allows that, so access remains scoped.

For simple `Copy` data, an interrupt-aware mutex around `Cell<T>` can work. For non-`Copy` peripherals, the common shape is `Mutex<RefCell<Option<T>>>`: `Mutex` ties access to a critical section, `RefCell` checks borrows at runtime, and `Option` permits late initialization after `Peripherals::take()`.

Critical sections are not free. They increase interrupt latency and jitter, and they do not protect against another CPU core. Use them narrowly and prefer atomics for simple counters or flags when supported.

The token is a proof object. It does not need runtime data; its value is that safe constructors are private and only the interrupt-free function can produce one. APIs that require `&CriticalSection` can then expose interior mutability without making every caller write `unsafe`.

Correct implementations restore the previous interrupt mask rather than blindly enabling interrupts at the end. That matters for nesting: if code enters a critical section while interrupts are already disabled, exiting the inner section must not accidentally enable them.

## Example
```rust
#![no_std]

pub struct CriticalSection {
    _private: (),
}

pub fn interrupt_free<R>(f: impl FnOnce(&CriticalSection) -> R) -> R {
    let token = CriticalSection { _private: () };
    f(&token)
}

pub struct SharedCounter {
    value: u32,
}

impl SharedCounter {
    pub const fn new() -> Self {
        Self { value: 0 }
    }

    pub fn increment(&mut self, _cs: &CriticalSection) {
        self.value = self.value.wrapping_add(1);
    }

    pub fn reset(&mut self, _cs: &CriticalSection) {
        self.value = 0;
    }
}
```

This is a compilable token sketch. On real hardware, `interrupt_free` must be supplied by the target support crate so it actually masks interrupts and restores the prior interrupt state.

## More realistic example
```rust
#![no_std]

use core::cell::Cell;

pub struct CriticalSection {
    _private: (),
}

pub struct CsCell<T: Copy> {
    value: Cell<T>,
}

impl<T: Copy> CsCell<T> {
    pub const fn new(value: T) -> Self {
        Self { value: Cell::new(value) }
    }

    pub fn get(&self, _cs: &CriticalSection) -> T {
        self.value.get()
    }

    pub fn set(&self, _cs: &CriticalSection, value: T) {
        self.value.set(value);
    }
}
```

This mirrors the safe API idea used by interrupt-aware mutexes: `Cell` provides interior mutability, but the public methods require proof that the caller is inside the critical section.

## Common errors
```text
error[E0596]: cannot borrow data in a `&` reference as mutable
```
A shared global protected by a critical section still needs interior mutability, such as `Cell`, `RefCell`, or a target mutex type. The critical section controls when access is allowed; the cell type controls how mutation is expressed.

```text
thread panicked at 'already borrowed: BorrowMutError'
```
This is a runtime `RefCell` failure, not a compiler error. It usually means code tried to take overlapping mutable borrows inside the same critical section. Keep borrows scoped tightly and avoid calling back into code that may borrow the same resource.

## Best practice
- ✅ Keep critical sections as short as possible; copy data out, then process it after interrupts are restored.
- ✅ Encode the requirement with a `CriticalSection` token or an established interrupt-aware mutex type.
- ✅ Use one critical section to access several related resources instead of nesting repeated sections.
- ✅ Prefer atomics for simple counters and flags when the target supports the operation you need.
- ✅ Copy snapshots out under the token, then parse, format, transmit, or compute after interrupts are restored.
- ✅ Initialize `Option<T>`-wrapped peripherals before enabling the corresponding interrupt source.
- ✅ Check whether the target or framework supports nested priorities; a critical section may mask only some interrupt levels.

## Pitfalls
- ⚠️ Doing slow work in a critical section, such as formatting logs, polling hardware, or waiting for a peripheral.
- ⚠️ Assuming the pattern is automatically valid on multi-core hardware; disabling local interrupts is not a global lock.
- ⚠️ Entering an interrupt before the shared `Option<T>` has been filled; enable the interrupt only after initialization.
- ⚠️ Using critical sections to hide broad global mutability instead of designing smaller ownership boundaries.
- ⚠️ Holding a `RefMut` across calls into driver code that may re-enter the same shared resource.
- ⚠️ Implementing your own interrupt masking without saving and restoring the prior mask state.

## See also
[[Interrupts and Concurrency (Embedded)]] · [[Unsynchronized static mut in Interrupts]] · [[Memory-Mapped I/O]] · [[Peripheral Access Crates]] · [[Interior Mutability]] · [[The Drop Trait]] · [[Atomics]] · [[Borrowing]] · [[Unsafe Rust]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "Concurrency: Critical Sections, Mutexes, Sharing Peripherals" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/concurrency/index.html
- `core::cell::Cell`,
  https://doc.rust-lang.org/core/cell/struct.Cell.html
- `core::cell::RefCell`,
  https://doc.rust-lang.org/core/cell/struct.RefCell.html
