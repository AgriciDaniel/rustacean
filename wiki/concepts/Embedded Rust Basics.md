---
type: concept
title: "Embedded Rust Basics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, firmware, basics]
domain: "Embedded Rust"
difficulty: basic
related: ["[[no_std]]", "[[Bare-Metal Programming]]", "[[Memory-Mapped I/O]]", "[[Peripheral Access Crates]]", "[[Interrupts and Concurrency (Embedded)]]", "[[Ownership]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/", "https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html"]
rust_version: "edition 2024 / 1.85+"
---

# Embedded Rust Basics

Embedded Rust is Rust used where software directly controls hardware resources, usually with `no_std`, cross-compilation, explicit startup code, and APIs that model peripherals as owned values.

## What it is
Embedded programming covers a wide range: small microcontrollers with only a few KiB of memory, application processors running a hosted operating system, and boards somewhere between those extremes. Rust can be used across that range, but the most distinctive embedded Rust style appears on bare-metal targets.

The basic mental model is that the firmware is often the only program running. It owns the machine after reset, configures clocks and memory, initializes peripherals, reacts to interrupts, and normally never returns from its main control loop.

Rust's contribution is to express hardware access through ordinary language tools: ownership for exclusive peripherals, borrowing for read-only or read-write access, traits for portable drivers, typestates for pin and peripheral modes, and small `unsafe` boundaries around the places where the compiler cannot see the hardware contract.

## How it works
A typical embedded Rust stack has layers. At the bottom, startup code and linker scripts describe how the binary is laid out and how reset reaches Rust. A micro-architecture crate provides CPU-wide functionality such as interrupt control. A Peripheral Access Crate exposes chip-specific register blocks. A HAL crate wraps PAC types into more ergonomic and state-aware APIs. A board crate may preconfigure a particular development board.

The firmware target is selected with a target triple such as a `thumb*` ARM target. The generated artifact is usually inspected with binary tools, flashed through a probe, and debugged with probe-rs, OpenOCD, GDB, or a vendor tool.

The core design habit is to keep hardware facts in types. If a UART needs clocks configured first, the HAL constructor can require a clock token. If a pin must be in alternate-function mode before it can drive SPI, the type can change when the pin is configured. This shifts many hardware sequencing mistakes from runtime into compile-time errors.

The compiler only sees normal Rust values; the hardware meaning comes from the APIs around those values. A PAC register method may compile to a volatile load or store. A HAL pin type may be zero-sized apart from ownership of the corresponding PAC register block. A driver generic over traits can be portable while still monomorphizing to direct calls for the concrete bus type.

The result is a useful split: target support crates own the low-level contracts, while application code should mostly move, borrow, and configure typed capabilities. When a design keeps peripherals as values rather than ambient globals, ordinary borrow errors become useful signals that two parts of the firmware are trying to own the same hardware.

## Example
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Level {
    Low,
    High,
}

#[derive(Debug)]
pub struct Led {
    level: Level,
}

impl Led {
    pub fn new() -> Self {
        Self { level: Level::Low }
    }

    pub fn set(&mut self, level: Level) {
        self.level = level;
    }

    pub fn is_on(&self) -> bool {
        self.level == Level::High
    }
}

fn main() {
    let mut led = Led::new();
    led.set(Level::High);
    assert!(led.is_on());
}
```

This host-compilable example models the same ownership shape used in firmware: only the owner of `Led` can mutate it, while shared references can only observe it.

## More realistic example
```rust
pub trait OutputPin {
    type Error;

    fn set_high(&mut self) -> Result<(), Self::Error>;
    fn set_low(&mut self) -> Result<(), Self::Error>;
}

pub struct ActiveLowLed<P> {
    pin: P,
}

impl<P: OutputPin> ActiveLowLed<P> {
    pub fn new(pin: P) -> Self {
        Self { pin }
    }

    pub fn on(&mut self) -> Result<(), P::Error> {
        self.pin.set_low()
    }

    pub fn off(&mut self) -> Result<(), P::Error> {
        self.pin.set_high()
    }

    pub fn release(self) -> P {
        self.pin
    }
}
```

This is the shape used by many embedded drivers: the driver owns a pin or bus, exposes a domain-specific API, propagates hardware errors with `Result`, and can release the resource if another subsystem must reconfigure it.

## Common errors
```text
error[E0382]: use of moved value
```
This often appears after a peripheral, pin, or bus is moved into a driver constructor and then used again. Fix it by keeping all access behind the driver, splitting the peripheral into independent parts when the HAL supports it, or passing a borrow only when the driver does not need ownership.

```text
error[E0596]: cannot borrow `led` as mutable, as it is not declared as mutable
```
Firmware APIs frequently require `&mut self` because they change hardware state. Fix it by declaring the binding `mut`, or by changing the API to take `&self` only when mutation is genuinely internal and synchronized.

## Best practice
- ✅ Start from the target's established runtime, PAC, HAL, or board crate instead of inventing startup and register definitions by hand.
- ✅ Keep pure logic independent from the board so it can be unit-tested on the host.
- ✅ Represent hardware capabilities with owned values and narrow borrows, not global reachability.
- ✅ Treat every `unsafe` block as a hardware contract: document what register, address, interrupt rule, or aliasing guarantee makes it valid.
- ✅ Prefer driver APIs generic over small traits for buses and pins; this keeps application code portable across HALs.
- ✅ Model initialization order in constructors: clocks before UARTs, pin modes before buses, DMA buffers before DMA start.
- ✅ Keep interrupt enablement late in startup, after all shared state and peripheral configuration are complete.

## Pitfalls
- ⚠️ Copying desktop Rust assumptions into firmware: `std`, threads, files, environment variables, and unbounded allocation may not exist.
- ⚠️ Hiding all hardware behind global mutable variables; that throws away the help offered by [[Ownership]] and [[Borrowing]].
- ⚠️ Starting too low-level when a HAL or board crate already encodes the target's invariants.
- ⚠️ Ignoring interrupt concurrency until late; see [[Interrupts and Concurrency (Embedded)]] and [[Unsynchronized static mut in Interrupts]].
- ⚠️ Treating HAL examples as universal. Register names, clock trees, reset behavior, DMA rules, and interrupt priorities are chip-specific.
- ⚠️ Panicking on recoverable hardware errors. In firmware, a panic may halt the whole product; use explicit error paths where operation can continue.

## See also
[[no_std]] · [[Bare-Metal Programming]] · [[Memory-Mapped I/O]] · [[Peripheral Access Crates]] · [[Interrupts and Concurrency (Embedded)]] · [[Critical Sections in Embedded Rust]] · [[Heapless Collections in Embedded Rust]] · [[Unsynchronized static mut in Interrupts]] · [[Ownership]] · [[Embedded Rust]]

## Sources
- The Embedded Rust Book, "Introduction" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/
- The Embedded Rust Book, "A no_std Rust Environment" — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html
