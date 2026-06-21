---
type: concept
title: "Interrupts and Concurrency (Embedded)"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, interrupts, concurrency]
domain: "Embedded Rust"
difficulty: intermediate
related: ["[[Critical Sections in Embedded Rust]]", "[[Unsynchronized static mut in Interrupts]]", "[[Memory-Mapped I/O]]", "[[Peripheral Access Crates]]", "[[Shared State in Async]]", "[[Atomics]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/start/interrupts.html", "https://doc.rust-lang.org/stable/embedded-book/concurrency/index.html", "https://doc.rust-lang.org/core/sync/atomic/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Interrupts and Concurrency (Embedded)

Embedded concurrency includes interrupt handlers, schedulers, and sometimes multiple cores; Rust makes it tractable by forcing shared state through atomics, critical sections, or carefully designed synchronization types.

## What it is
An interrupt is hardware-driven control flow. The main loop may be executing one instruction, then a timer, GPIO, UART, DMA controller, or other peripheral requests service, and the CPU runs an interrupt handler before returning.

That means embedded programs can be concurrent even without threads or async tasks. If `main` and an interrupt handler both access the same memory or peripheral, they are separate execution contexts for safety reasoning.

Interrupt handlers are target-specific. On Cortex-M, the architecture defines exceptions such as SysTick, while vendor devices define interrupt names and vector positions. Device crates commonly re-export an `#[interrupt]` attribute so the compiler can check that the handler name belongs to the target.

## How it works
The simple case is no concurrency: a main loop owns all peripherals, polls inputs, computes outputs, and writes hardware. Once interrupts enter the design, data shared between an interrupt and foreground code must be synchronized.

Good options depend on the data and target. A single integer flag or counter can often be an atomic. A non-atomic compound state may need a critical section, where interrupts are temporarily disabled. A peripheral shared between foreground and an interrupt may be stored behind an interrupt-aware mutex plus interior mutability.

Ordering matters. Initialize shared state first, then enable the interrupt source in the peripheral, then enable the interrupt in the controller. Interrupt handlers should do bounded work, clear the hardware reason for the interrupt when required, and avoid blocking on locks that foreground code might hold.

The compiler does not treat an interrupt handler like a spawned Rust thread, but the memory model problem is similar: if two contexts can access the same location and at least one writes, the access must be synchronized. `unsafe` can suppress local checks, but it cannot make a load-add-store increment indivisible.

Atomic ordering deserves local reasoning. `Relaxed` is often right for an isolated event counter where no other data is published through the counter. If a flag announces that a buffer is ready, the producer usually needs a release operation and the consumer an acquire operation, or the design should use a critical section that protects both the flag and the buffer.

## Example
```rust
#![no_std]

use core::sync::atomic::{AtomicU32, Ordering};

static EDGES: AtomicU32 = AtomicU32::new(0);

pub fn foreground_saw_rising_edge() {
    EDGES.fetch_add(1, Ordering::Relaxed);
}

pub fn timer_interrupt_snapshot_and_reset() -> u32 {
    EDGES.swap(0, Ordering::Relaxed)
}

pub fn last_period_was_active(edges: u32) -> bool {
    edges != 0
}
```

This models a common interrupt-safe counter shape. On a single-core target where no other memory is synchronized through the counter, `Relaxed` is enough for the counter itself; more complex communication may require stronger ordering or a different primitive.

## More realistic example
```rust
#![no_std]

use core::sync::atomic::{AtomicBool, AtomicU16, Ordering};

static SAMPLE_READY: AtomicBool = AtomicBool::new(false);
static SAMPLE_MV: AtomicU16 = AtomicU16::new(0);

pub fn adc_interrupt_publish(sample_mv: u16) {
    SAMPLE_MV.store(sample_mv, Ordering::Relaxed);
    SAMPLE_READY.store(true, Ordering::Release);
}

pub fn foreground_take_sample() -> Option<u16> {
    if SAMPLE_READY.swap(false, Ordering::Acquire) {
        Some(SAMPLE_MV.load(Ordering::Relaxed))
    } else {
        None
    }
}
```

Here the release/acquire pair makes the sample store visible before the foreground observes the ready flag. If the data were a multi-field struct instead of one atomic integer, a short critical section or lock-free buffer would be a better fit.

## Common errors
```text
error[E0594]: cannot assign to immutable static item
```
A plain `static` cannot be mutated directly. Use an atomic, a critical-section mutex with interior mutability, or a target framework that owns the resource.

```text
error: creating a shared reference to mutable static
```
In edition 2024, references to `static mut` are denied by default. Prefer `static` atomics or mutex-protected state. If raw pointers are unavoidable, use `&raw const` or `&raw mut` and keep the unsafe abstraction tiny.

## Best practice
- ✅ Prefer atomics for simple counters and flags when the target supports the needed atomic operations.
- ✅ Use critical sections for short, bounded access to shared non-atomic state on single-core interrupt-driven systems.
- ✅ Enable interrupts only after their shared state and peripherals are fully initialized.
- ✅ Keep interrupt handlers short: acknowledge hardware, capture data, update bounded state, and defer heavier work.
- ✅ Use release/acquire ordering when an interrupt publishes data through a flag; use relaxed only when the atomic value is the whole communication.
- ✅ Document interrupt priority assumptions when two handlers can touch the same resource.
- ✅ Prefer queues, ring buffers, or wake flags for handoff; avoid doing protocol parsing or formatting inside the handler.

## Pitfalls
- ⚠️ Treating `unsafe { static mut ... }` as synchronization. It is only a promise to the compiler, not protection from preemption.
- ⚠️ Blocking inside an interrupt handler on a mutex that foreground code may hold; that can deadlock.
- ⚠️ Forgetting nested interrupt priorities. A low-priority handler may be preempted by a higher-priority handler that touches the same state.
- ⚠️ Assuming critical sections protect multi-core systems. Disabling interrupts on one core does not stop another core.
- ⚠️ Clearing an interrupt flag too late or in the wrong order, causing immediate retriggering or lost events.
- ⚠️ Using atomics unsupported by the target. Some small MCUs support only atomic loads and stores for certain widths, not all read-modify-write operations.

## See also
[[Critical Sections in Embedded Rust]] · [[Unsynchronized static mut in Interrupts]] · [[Memory-Mapped I/O]] · [[Peripheral Access Crates]] · [[Atomics]] · [[Shared State in Async]] · [[Heapless Collections in Embedded Rust]] · [[Bare-Metal Programming]] · [[Unsafe Rust]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "Interrupts" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/interrupts.html
- The Embedded Rust Book, "Concurrency" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/concurrency/index.html
- `core::sync::atomic`,
  https://doc.rust-lang.org/core/sync/atomic/index.html
