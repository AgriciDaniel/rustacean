---
type: concept
title: "Unions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, union, ffi, layout]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Undefined Behavior]]", "[[MaybeUninit]]", "[[Type Layout and repr]]", "[[FFI with C]]", "[[Transmute as a Shortcut]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]", "[[06-unsafe-and-ffi]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/unions.html", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html", "https://doc.rust-lang.org/nomicon/"]
rust_version: "edition 2024 / 1.85+"
---

# Unions

Unions are Rust's untagged overlapping-storage type: every field shares the same memory, and reading a field is unsafe because the programmer must prove the stored bits are valid for that field's type.

## What it is
The `union` item is a language feature for representing one storage location as one of several field types.
It looks syntactically close to a `struct`, but its fields do not occupy independent storage.
Writing one field overwrites the bytes that another field would read.

Unions are mainly useful at unsafe boundaries:

- matching a C `union` in an [[FFI with C]] type;
- implementing low-level bit reinterpretation with explicit validity checks;
- building primitives such as [[MaybeUninit]], which is itself a standard-library union;
- encoding layout-sensitive data where a safe Rust enum would not match an external ABI.

Unlike an enum, a union does not store a discriminant.
Rust does not remember an "active field" for you.
If a program writes `u.bits` and later reads `u.float`, that read is just a reinterpretation of the overlapping bytes.
For `#[repr(C)]` unions, the Reference compares this shape to a `transmute` from the written field type to the read field type, with the same obligation to avoid invalid values.

## How it works
All union fields share common storage, and the union's size is determined by the largest field, subject to layout rules.
Without `#[repr(C)]`, Rust does not promise C-compatible field layout.
Use `#[repr(C)]` when a union mirrors a C definition or participates in an ABI contract.

Union fields are restricted so field writes do not implicitly drop an overwritten value.
A field must be one of:

- a `Copy` type;
- a reference type;
- `ManuallyDrop<T>`;
- a tuple or array whose elements are allowed union-field types.

Creating a union value initializes exactly one field.
Writing to a union field is safe because the write only replaces bytes and cannot run drop glue.
Reading a union field is unsafe because Rust cannot check that the current bytes are a valid value of the field's type.

The validity rule is the core hazard.
Every type has validity requirements.
A `u32` can hold any 32-bit pattern, but a `bool` can only be `0` or `1`, a reference must be non-null, aligned, and point to a valid referent for its lifetime, and many enums have invalid discriminants.
Reading a union field whose bits violate the field type is [[Undefined Behavior]], even inside an `unsafe` block.

Unions can have methods, trait implementations, privacy, generics, and even a manual `Drop` implementation.
Those features do not make field reads safe.
A safe abstraction must put the tag, validity proof, and access policy somewhere outside the raw union read.

## Example
```rust
#[repr(C)]
union WordBytes {
    word: u32,
    bytes: [u8; 4],
}

impl WordBytes {
    fn from_word(word: u32) -> Self {
        Self { word }
    }

    fn bytes(self) -> [u8; 4] {
        // SAFETY: every byte array is valid for `[u8; 4]`; reading the byte view
        // of initialized `u32` storage does not create an invalid value.
        unsafe { self.bytes }
    }
}

fn main() {
    let value = WordBytes::from_word(0x1234_5678);
    let bytes = value.bytes();

    assert_eq!(bytes.len(), 4);
}
```

This example is intentionally narrow.
It reads a field type where every possible byte pattern is valid.
It does not use a union to read a `bool`, reference, enum, or other type with stricter validity invariants.
If you only need integer-to-byte conversion in normal code, prefer safe APIs such as `u32::to_ne_bytes`.

## Best practice
- ✅ Prefer safe Rust enums for Rust-only sum types; use unions when layout or FFI requires untagged overlapping storage.
- ✅ Put `#[repr(C)]` on unions that model C `union`s or are shared across an ABI boundary.
- ✅ Keep raw union field reads inside small, audited methods that document the active variant or validity invariant.
- ✅ Pair a union with an explicit tag when modeling a C tagged union; check the tag before reading the matching field.
- ✅ Use `ManuallyDrop<T>` only when you have a complete plan for initialization, access, and destruction.
- ✅ Prefer dedicated safe conversion APIs (`to_ne_bytes`, `from_bits`, pointer casts with documented provenance) when a union is not necessary.
- ✅ Run unsafe wrappers through [[Miri]] where possible, especially when a union interacts with references, aliasing, or partially initialized data.

## Pitfalls
- ⚠️ Reading the "wrong" field is not merely a logic bug; it is UB if the bytes are invalid for that field's type.
- ⚠️ A union has no active-field tracking. If you need a tag, store one explicitly or use an enum.
- ⚠️ `#[repr(C)]` controls C-compatible union layout, but it does not validate bytes, lifetimes, aliasing, or provenance.
- ⚠️ References stored in unions are still real Rust references with normal validity and aliasing requirements.
- ⚠️ Wrapping a non-`Copy` field in `ManuallyDrop<T>` moves drop responsibility to your code.
- ⚠️ Using a union as a casual replacement for `transmute` recreates [[Transmute as a Shortcut]] with a different spelling.
- ⚠️ Borrowing one union field borrows the whole union storage for that lifetime, because every field overlaps.

## See also
[[Unsafe Rust]] · [[Undefined Behavior]] · [[MaybeUninit]] · [[Type Layout and repr]] ·
[[FFI with C]] · [[Raw Pointers]] · [[Aliasing and Provenance]] · [[Miri]] ·
[[Transmute as a Shortcut]] · [[Safe Abstractions over Unsafe Code]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Reference, "Unions" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/unions.html
- The Rust Reference, "Behavior considered undefined" — [[the-reference]],
  https://doc.rust-lang.org/reference/behavior-considered-undefined.html
- The Rustonomicon, unsafe code and FFI background — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/
- Research report, "Unsafe Rust and FFI" — [[06-unsafe-and-ffi]]
