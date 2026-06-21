---
type: concept
title: "Bare-Metal Programming"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, bare-metal, startup]
domain: "Embedded Rust"
difficulty: intermediate
related: ["[[no_std]]", "[[Embedded Rust Basics]]", "[[Memory-Mapped I/O]]", "[[Peripheral Access Crates]]", "[[Panic Unwinding and Abort]]", "[[The Never Type]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html", "https://doc.rust-lang.org/stable/embedded-book/start/index.html", "https://doc.rust-lang.org/stable/embedded-book/start/panicking.html"]
rust_version: "edition 2024 / 1.85+"
---

# Bare-Metal Programming

Bare-metal Rust is firmware Rust for systems where no operating system prepares the process; the program supplies startup, memory layout, panic behavior, and direct hardware control.

## What it is
In a hosted environment, the OS loader and `std` runtime prepare a process before `main` runs. In a bare-metal environment, the CPU begins at a reset vector or boot entry point, and the firmware image is responsible for reaching Rust code correctly.

That difference explains the familiar embedded attributes: `#![no_std]` because there is no standard OS interface, `#![no_main]` because the normal Rust `main` interface is not the target entry path, and a divergent entry function because firmware should not fall off the end of the only program on the device.

Bare-metal work also includes linker scripts, memory sections, vector tables, cross-compilation targets, flashing, semihosting or target logging, and debugging over a hardware probe or emulator.

## How it works
Startup code initializes memory that Rust relies on: `.data` is copied from flash to RAM, `.bss` is zeroed, the stack pointer is set, and the interrupt vector table is made available according to the target architecture. Frameworks such as `cortex-m-rt` provide this glue for Cortex-M targets.

After startup, the entry function configures clocks and peripherals, enables interrupts when the shared state is ready, and enters a loop. That loop may poll hardware, sleep until interrupt, run a scheduler, or delegate to an RTOS or framework.

Panics need an explicit behavior in `no_std` binaries. The firmware may halt for debugging, abort, log over semihosting, write to ITM, reset the board, or enter a safe state. The right choice depends on product requirements; the important rule is that exactly one panic handler must be linked.

The linker script is part of the program contract, not just build scaffolding. It decides where flash, RAM, stack, initialized statics, zeroed statics, vector tables, and sometimes special DMA or retention sections live. If that description is wrong, Rust's type system can still be perfectly satisfied while the CPU fetches the wrong vector or the stack grows into a buffer.

Bare-metal entry points usually return `!` because there is no caller prepared to resume control. A runtime macro such as `#[entry]` often checks that shape for the target. If the firmware should sleep, it normally loops around a wait-for-interrupt instruction or scheduler call rather than returning.

## Example
```rust
#![no_std]

pub enum Event {
    ButtonPressed,
    Tick,
}

pub struct Firmware {
    ticks: u32,
    led_on: bool,
}

impl Firmware {
    pub const fn new() -> Self {
        Self { ticks: 0, led_on: false }
    }

    pub fn handle(&mut self, event: Event) {
        match event {
            Event::ButtonPressed => self.led_on = !self.led_on,
            Event::Tick => self.ticks = self.ticks.wrapping_add(1),
        }
    }

    pub fn led_on(&self) -> bool {
        self.led_on
    }
}
```

This is not a complete firmware binary, but it is the kind of `no_std` state machine that a bare-metal entry function can drive after startup and peripheral initialization.

## More realistic example
```rust
#![no_std]

pub enum InitError {
    ClockFailed,
    UartUnavailable,
}

pub struct Board {
    heartbeat_enabled: bool,
}

impl Board {
    pub fn init(clock_ready: bool, uart_present: bool) -> Result<Self, InitError> {
        if !clock_ready {
            return Err(InitError::ClockFailed);
        }
        if !uart_present {
            return Err(InitError::UartUnavailable);
        }

        Ok(Self { heartbeat_enabled: true })
    }

    pub fn idle_once(&mut self) {
        self.heartbeat_enabled = !self.heartbeat_enabled;
    }
}

pub fn run_forever(mut board: Board) -> ! {
    loop {
        board.idle_once();
        core::hint::spin_loop();
    }
}
```

Real startup code would get `clock_ready` and `uart_present` from PAC or HAL operations. The important firmware shape is explicit initialization failure followed by a divergent run path.

## Common errors
```text
error: `#[panic_handler]` function required, but not found
```
Fix it by linking one panic handler crate or defining one local handler in the final binary. Do not put a panic handler in a reusable driver library.

```text
error[E0152]: found duplicate lang item `panic_impl`
```
This usually means two panic handler crates, or a crate and a local handler, are linked at once. Fix it by selecting exactly one behavior for the final firmware image.

## Best practice
- ✅ Use a proven runtime crate for your architecture unless you are deliberately writing startup code.
- ✅ Make the entry function small: acquire peripherals, configure clocks and pins, initialize shared state, then enter the main control path.
- ✅ Enable interrupts only after the data and peripherals they use have been initialized.
- ✅ Pick a panic behavior intentionally and make debug versus release differences explicit.
- ✅ Keep memory layout files reviewed with the same care as Rust code; they define where safe Rust objects physically reside.
- ✅ Use `#[cfg(debug_assertions)]` or build-profile features when debug firmware should log or halt differently from release firmware.
- ✅ Make fallible hardware initialization return `Result`; reserve panic for invariant violations or unrecoverable bring-up failures.

## Pitfalls
- ⚠️ Returning from the firmware entry path. A bare-metal application normally has nowhere meaningful to return to; use a divergent loop or low-power wait.
- ⚠️ Treating linker scripts and memory maps as boilerplate. Incorrect RAM or flash layout can corrupt stacks, statics, DMA buffers, or vector tables.
- ⚠️ Calling host-only APIs through accidental `std` dependencies; see [[no_std]].
- ⚠️ Using panics for routine embedded errors, especially in interrupt handlers; prefer explicit [[Result]] or bounded fallback paths.
- ⚠️ Enabling clocks, DMA, or interrupts in a different order from the reference manual. Type-safe APIs help, but they cannot infer every board-level timing rule.
- ⚠️ Assuming debugger or semihosting behavior exists in production. A semihosting panic path can hang if no debugger is attached.

## See also
[[no_std]] · [[Embedded Rust Basics]] · [[Memory-Mapped I/O]] · [[Peripheral Access Crates]] · [[Interrupts and Concurrency (Embedded)]] · [[Critical Sections in Embedded Rust]] · [[Panic Unwinding and Abort]] · [[The Never Type]] · [[Result]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "A no_std Rust Environment" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html
- The Embedded Rust Book, "Getting started" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/index.html
- The Embedded Rust Book, "Panicking" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/panicking.html
