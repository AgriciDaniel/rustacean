---
type: antipattern
title: "Unsynchronized static mut in Interrupts"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, interrupts, unsafe]
domain: "Embedded Rust"
difficulty: intermediate
related: ["[[Interrupts and Concurrency (Embedded)]]", "[[Critical Sections in Embedded Rust]]", "[[Memory-Mapped I/O]]", "[[no_std]]", "[[Unsafe Rust]]", "[[Atomics]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/concurrency/index.html", "https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#accessing-or-modifying-a-mutable-static-variable", "https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html", "https://doc.rust-lang.org/core/sync/atomic/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Unsynchronized static mut in Interrupts

Unsynchronized `static mut` shared between foreground code and interrupt handlers is a footgun because `unsafe` access does not make read-modify-write operations atomic or protect them from preemption.

## The mistake
Embedded code often needs state that both `main` and an interrupt handler can reach. The tempting low-level answer is a global `static mut` counter, flag, buffer, or peripheral slot.

The problem is that `static mut` access is unsafe precisely because the compiler cannot enforce aliasing or concurrency rules for it. Wrapping the access in `unsafe` only says "I checked this"; it does not disable interrupts, acquire a lock, or turn an increment into an atomic instruction.

The classic bug is a counter increment in foreground code while a timer interrupt resets the same counter. The increment may compile into load, add, store. If the interrupt fires between load and store, the reset can be lost.

## Why it happens
Hardware interrupts introduce preemption without any visible thread spawn in the source code. The foreground code and handler are effectively separate execution contexts.

Rust's safety model still applies, but `static mut` opts out of the compiler's usual checks. The compiler cannot know whether an interrupt may run halfway through a sequence. It also cannot know whether another priority level or core accesses the same location.

Volatile access is not the fix. Volatile can force an individual load or store to occur, but it does not make a compound operation indivisible. Correct alternatives are atomics, critical sections, interrupt-aware mutexes, RTIC-style resource management, or a design that avoids sharing.

Edition 2024 makes this sharper by denying references to `static mut` by default. Creating `&T` or `&mut T` to a mutable static has always required a global aliasing argument that local Rust code cannot check. If code truly must operate at that level, it should use raw pointers via `&raw const` or `&raw mut`, then confine dereferencing to a reviewed unsafe abstraction.

The race can be purely logical even when the hardware is single-core. A read-modify-write increment is several machine-level actions: load the old value, compute the new value, then store it. An interrupt between those actions can observe stale data or overwrite a foreground update.

## Example
```rust
#![no_std]

use core::sync::atomic::{AtomicU32, Ordering};

static EDGE_COUNT: AtomicU32 = AtomicU32::new(0);

pub fn foreground_edge_detected() {
    EDGE_COUNT.fetch_add(1, Ordering::Relaxed);
}

pub fn timer_interrupt_take_count() -> u32 {
    EDGE_COUNT.swap(0, Ordering::Relaxed)
}
```

This correct alternative uses a safe `static` atomic. For a simple single-core counter that does not publish other memory, relaxed ordering is enough for the counter operation itself. For compound data, use [[Critical Sections in Embedded Rust]] or a stronger synchronization design.

## Counterexample
```rust
#![no_std]

static mut BUFFER_READY: bool = false;

pub fn foreground_poll() -> bool {
    unsafe {
        if BUFFER_READY {
            BUFFER_READY = false;
            true
        } else {
            false
        }
    }
}

pub fn dma_interrupt() {
    unsafe {
        BUFFER_READY = true;
    }
}
```

This looks harmless because `bool` fits in one byte, but the poll-and-clear sequence is compound. If the interrupt runs after the read and before the clear, the foreground can erase a newly published event. Use an `AtomicBool::swap`, a critical section, or a queue that records every event.

## Common errors
```text
error: creating a shared reference to mutable static
```
In Rust edition 2024 this is denied by default. Fix it by replacing `static mut` with an atomic or an interrupt-aware mutex. If raw access is unavoidable, use `&raw const` or `&raw mut` and keep the pointer dereference inside a small unsafe API.

```text
error[E0133]: use of mutable static is unsafe and requires unsafe block
```
An unsafe block only acknowledges the risk; it is not synchronization. The real fix is to choose the correct primitive for the sharing pattern.

## Best practice
- ✅ Use `Atomic*` types for simple interrupt-shared counters and flags when the target supports the needed atomic operation.
- ✅ Use a critical section or interrupt-aware mutex for compound state and non-`Copy` peripherals.
- ✅ Keep unavoidable `unsafe` inside a tiny abstraction whose API enforces the synchronization rule.
- ✅ Enable interrupt sources only after the shared state they touch is initialized.
- ✅ Use `AtomicBool::swap` or `AtomicU*::fetch_*` for single-word handoff where the target supports the operation.
- ✅ Use `Mutex<RefCell<Option<T>>>`-style ownership for peripherals initialized in `main` but used by an interrupt.
- ✅ Treat interrupt priority and nesting as part of the safety proof; document why no higher-priority context can access the same state unsafely.

## Pitfalls
- ⚠️ Assuming "works in testing" means race-free. Interrupt timing bugs often require unlucky timing or different optimization to appear.
- ⚠️ Replacing `static mut` with volatile reads and writes for synchronization. Volatile is for externally observable memory access, not mutual exclusion.
- ⚠️ Using a critical section too broadly and causing unacceptable interrupt latency.
- ⚠️ Applying single-core critical-section reasoning to multi-core devices.
- ⚠️ Creating `&mut` references to a mutable static and then passing them through safe-looking helper functions. The helper's signature can hide a global aliasing violation.
- ⚠️ Clearing flags with load-then-store when an atomic `swap(false, ...)` or critical section is required to avoid lost events.

## See also
[[Interrupts and Concurrency (Embedded)]] · [[Critical Sections in Embedded Rust]] · [[Memory-Mapped I/O]] · [[Peripheral Access Crates]] · [[no_std]] · [[Unsafe Rust]] · [[Atomics]] · [[Interior Mutability]] · [[Borrowing]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "Concurrency: Global Mutable Data, Critical Sections, Atomic Access" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/concurrency/index.html
- The Rust Programming Language, "Accessing or Modifying a Mutable Static Variable",
  https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#accessing-or-modifying-a-mutable-static-variable
- The Rust Edition Guide, "Disallow references to static mut",
  https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html
- `core::sync::atomic`,
  https://doc.rust-lang.org/core/sync/atomic/index.html
