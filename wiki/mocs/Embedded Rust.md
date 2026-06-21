---
type: moc
title: "Embedded Rust"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, embedded, moc]
domain: "Embedded Rust"
difficulty: basic
related: ["[[no_std]]", "[[Embedded Rust Basics]]", "[[Bare-Metal Programming]]", "[[Memory-Mapped I/O]]", "[[Peripheral Access Crates]]", "[[Interrupts and Concurrency (Embedded)]]", "[[Critical Sections in Embedded Rust]]", "[[Heapless Collections in Embedded Rust]]", "[[Unsynchronized static mut in Interrupts]]"]
sources: ["[[embedded-book]]"]
source_urls: ["https://doc.rust-lang.org/stable/embedded-book/"]
rust_version: "edition 2024 / 1.85+"
---

# Embedded Rust

Embedded Rust is the domain of writing Rust for firmware and hardware-facing systems, especially `no_std` and bare-metal targets where ownership, volatile access, and interrupt-safe sharing must model the machine directly.

## Concepts
- [[Embedded Rust Basics]]
- [[no_std]]
- [[Bare-Metal Programming]]
- [[Memory-Mapped I/O]]
- [[Peripheral Access Crates]]
- [[Interrupts and Concurrency (Embedded)]]

## Patterns
- [[Critical Sections in Embedded Rust]]
- [[Heapless Collections in Embedded Rust]]

## Antipatterns
- [[Unsynchronized static mut in Interrupts]]

## Source Trail
Start with [[embedded-book]], then read the notes in this order: [[Embedded Rust Basics]], [[no_std]], [[Bare-Metal Programming]], [[Memory-Mapped I/O]], [[Peripheral Access Crates]], and [[Interrupts and Concurrency (Embedded)]]. The patterns and antipattern explain the main design pressure: hardware is mutable global state, but Rust code should expose it through narrow, synchronized ownership.

## See also
[[Ownership]] · [[Borrowing]] · [[Unsafe Rust]] · [[Panic Unwinding and Abort]] · [[Result]] · [[The Never Type]] · [[Atomics]] · [[Interior Mutability]]

## Sources
- The Embedded Rust Book — [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/
