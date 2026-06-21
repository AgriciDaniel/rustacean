---
type: concept
title: "Aliasing and Provenance"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, aliasing, provenance]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Raw Pointers]]", "[[Dereferencing Raw Pointers]]", "[[Undefined Behavior]]", "[[Miri]]", "[[Unsafe Rust]]", "[[Soundness vs Safety]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/behavior-considered-undefined.html#undefinedalias", "https://doc.rust-lang.org/nomicon/aliasing.html", "https://doc.rust-lang.org/std/ptr/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Aliasing and Provenance

Aliasing is about which pointers may access overlapping memory, while provenance is the allocation history that makes a pointer meaningful beyond its numeric address.

## What it is
Two pointers alias when they can access overlapping bytes. Rust gives references
strong aliasing meaning: `&T` promises shared read-only access except through
`UnsafeCell`, and `&mut T` promises exclusive access while live.

Provenance is the abstract origin of a pointer. A pointer is not only an integer
address; it is tied to the allocation and derivation path that make dereferencing
it meaningful. This is why an integer with the right address is not automatically
a valid pointer to dereference.

The exact aliasing model is still not fully formalized, so this note is marked
`mature` for practical Rust work but still notes that the formal model is evolving.
The practical obligations in the Reference are binding today.

## How it works
Optimizations depend on aliasing. If a function takes `input: &u32` and
`output: &mut u32`, the compiler may assume writing `output` cannot mutate
`input`. Unsafe code that creates overlapping live references can make such
optimizations miscompile the program.

Raw pointers have fewer immediate aliasing guarantees than references, but using
them to create references, read, or write can still violate the reference model.
Pointer arithmetic also has to stay within the relevant allocation, and integer
casts can lose the information needed to justify later dereference.

Use the strict provenance APIs in `std::ptr` when preserving pointer provenance
while manipulating address bits.

Strict-provenance APIs are useful because they separate "change the address bits"
from "invent a pointer." `addr()` exposes the address, and `with_addr`/`map_addr`
produce a pointer with the original provenance and a different address. That is
not permission to leave the allocation; it is a way to preserve the allocation
history while doing operations such as pointer tagging within a valid design.

## Example
```rust
fn add_one(value: &mut u32) {
    let ptr = value as *mut u32;

    // SAFETY: ptr was derived from the unique &mut value, and no other access
    // to value occurs during this raw write.
    unsafe {
        *ptr += 1;
    }
}

fn main() {
    let mut n = 41;
    add_one(&mut n);
    assert_eq!(n, 42);
}
```

## Worked example
```rust
fn tag_low_bit<T>(ptr: *mut T) -> *mut T {
    assert_eq!(ptr.addr() & 1, 0, "pointer must have a free low bit");
    ptr.map_addr(|addr| addr | 1)
}

fn clear_low_bit<T>(ptr: *mut T) -> *mut T {
    ptr.map_addr(|addr| addr & !1)
}

fn main() {
    let mut value = 10_u32;
    let ptr = &raw mut value;
    let tagged = tag_low_bit(ptr);
    let clean = clear_low_bit(tagged);

    // SAFETY: clean has the original pointer provenance and address, value is
    // still alive, and no conflicting access occurs during the write.
    unsafe { *clean = 11 };
    assert_eq!(value, 11);
}
```

This example manipulates address bits without round-tripping through `usize` as
the source of a new pointer. The pointer still may only be dereferenced after the
tag is cleared and the usual validity, alignment, lifetime, and aliasing facts
are true.

## Common errors
The compiler often cannot diagnose provenance bugs directly. [[Miri]] may report
them dynamically with messages about pointer provenance, dangling pointers, or a
borrow being invalidated. A typical unsafe-code symptom is not a stable compiler
error but a Miri failure at the later dereference.

The fix is to keep raw pointers derived from real allocations, avoid integer
round-trips for pointer manipulation, and delay reference creation until you can
prove the reference's aliasing contract for its whole lifetime.

## Best practice
- ✅ Derive raw pointers from real allocations and keep their lifetime/provenance obvious.
- ✅ Create references from raw pointers only when you can satisfy reference aliasing rules for the full reference lifetime.
- ✅ Use `addr`, `with_addr`, or `map_addr` rather than lossy integer round trips when doing pointer tagging.
- ✅ Run pointer-heavy tests under [[Miri]], including strict provenance flags when relevant.
- ✅ Use `UnsafeCell` as the explicit escape hatch for mutation through shared references.
- ✅ Keep pointer-tagging schemes internal to one abstraction so callers never handle tagged pointers as ordinary `*mut T`.

## Pitfalls
- ⚠️ Creating two live `&mut T` references to the same memory through raw pointers.
- ⚠️ Mutating behind an `&T` outside `UnsafeCell`; shared references imply immutability of reachable bytes.
- ⚠️ Casting pointer to `usize`, modifying it, and casting back as if provenance were preserved.
- ⚠️ Assuming raw pointers make aliasing irrelevant; the UB often occurs at the later read, write, or reference creation.
- ⚠️ Comparing pointer addresses and then using equality as proof that two pointers have the same provenance or access rights.

## See also
[[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[Undefined Behavior]] · [[Miri]] · [[Unsafe Rust]] · [[Soundness vs Safety]] · [[UnsafeCell]] · [[Transmute as a Shortcut]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Reference, "Breaking the pointer aliasing rules" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html#undefinedalias
- The Rustonomicon, "Aliasing" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/aliasing.html
- The standard library, `std::ptr` strict provenance APIs — https://doc.rust-lang.org/std/ptr/index.html
