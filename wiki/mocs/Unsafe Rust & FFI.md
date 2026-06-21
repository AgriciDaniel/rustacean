---
type: moc
title: "Unsafe Rust & FFI"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, ffi, moc]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[FFI with C]]", "[[Undefined Behavior]]", "[[Raw Pointers]]", "[[MaybeUninit]]", "[[Miri]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html", "https://doc.rust-lang.org/reference/unsafety.html", "https://doc.rust-lang.org/nomicon/"]
rust_version: "edition 2024 / 1.85+"
---

# Unsafe Rust & FFI

Unsafe Rust and FFI are the parts of Rust where correctness depends on explicit human-maintained invariants around memory, aliasing, layout, ABI, initialization, and foreign code.

## Concepts
[[Unsafe Rust]]

[[Raw Pointers]]

[[Dereferencing Raw Pointers]]

[[Extern statics]]

[[unsafe fn]]

[[Undefined Behavior]]

[[FFI with C]]

[[unsafe extern Blocks]]

[[Unions]]

[[MaybeUninit]]

[[Aliasing and Provenance]]

[[Miri]]

[[Soundness vs Safety]]

## Patterns
[[Safe Abstractions over Unsafe Code]]

[[SAFETY Comments]]

[[FFI Wrapper Types]]

[[Pin projection]]

## Antipatterns
[[The static mut Footgun and &raw]]

[[Transmute as a Shortcut]]

## Sources
- The Rust Programming Language, ch. 20.1 "Unsafe Rust" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
- The Rust Reference, "Unsafety" — [[the-reference]], https://doc.rust-lang.org/reference/unsafety.html
- The Rust Reference, "External blocks" — [[the-reference]], https://doc.rust-lang.org/reference/items/external-blocks.html
- The Rust Reference, "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html
- The Rustonomicon — [[rustonomicon]], https://doc.rust-lang.org/nomicon/
