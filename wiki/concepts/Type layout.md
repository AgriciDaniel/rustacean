---
type: concept
title: "Type layout"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, layout, memory, repr, unsafe]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Type Layout and repr]]", "[[Zero-Sized Types]]", "[[Dynamically Sized Types]]", "[[Raw Pointers]]", "[[FFI with C]]", "[[Unsafe Rust]]", "[[Arrays]]", "[[Enums]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/type-layout.html", "https://doc.rust-lang.org/nomicon/other-reprs.html"]
rust_version: "edition 2024 / 1.85+"
---

# Type layout

Type layout is the compiler's placement contract for a value: its size, alignment, field offsets, and, for enums, discriminant representation.
Rust exposes some layout facts through stable APIs, but the default `repr(Rust)` layout intentionally leaves most composite-type details unspecified.

## What it is
Every Rust value has a size and an alignment.
For `Sized` types, `std::mem::size_of::<T>()` and `std::mem::align_of::<T>()` report those compile-time properties.
For dynamically sized values, `size_of_val` and `align_of_val` work from a reference to a concrete value.
The Reference defines layout as size, alignment, and relative field offsets; enum discriminant layout is also part of layout.

Layout is not the same as validity.
Two byte sequences may have the same size and alignment while only one is a valid value of its type.
For example, `bool` is one byte, but not every `u8` bit pattern is a valid `bool`.
Likewise, a reference-sized integer is not automatically a valid reference with provenance, alignment, and aliasing guarantees.
This distinction is central to [[Unsafe Rust]].

Layout is also not the same as call ABI.
The Reference notes that even types with the same layout can differ in how they are passed across function boundaries.
For FFI, use `extern "C"` APIs with explicitly documented ABI-safe types, not layout guesses.

## How it works
Primitive sizes such as `u8`, `u16`, `u32`, `u64`, `f32`, `f64`, and `char` have specified sizes.
Pointer and reference layout is pointer-like for sized pointees; pointers to unsized types are themselves sized but carry metadata.
Arrays `[T; N]` are contiguous and have size `size_of::<T>() * N`, with each element at `n * size_of::<T>()`.
Slices `[T]` have the same layout as the array section they represent.
`str` has the same layout as `[u8]`, with the additional UTF-8 validity invariant.

User-defined structs, enums, and unions have a representation.
Without a `repr` attribute, they use the default Rust representation.
For `repr(Rust)`, Rust guarantees only what is needed for soundness:
field offsets are aligned,
the type alignment is at least the maximum field alignment,
and struct fields do not overlap.
Field order, padding choices, and many enum optimizations are otherwise compiler decisions.
The compiler may change those decisions across compilation sessions, targets, or versions.

Zero-sized types are real types with size 0.
They can share addresses with other fields, and arrays of zero-sized elements require special care in raw pointer iteration.
Alignment is still at least 1 and always a power of two.
Size is always a multiple of alignment; zero is considered a multiple of any alignment.

## Example
```rust
use std::mem::{align_of, offset_of, size_of};

#[repr(C)]
struct Header {
    tag: u8,
    len: u32,
}

fn main() {
    assert_eq!(size_of::<u32>(), 4);
    assert_eq!(size_of::<[u16; 3]>(), 6);
    assert_eq!(align_of::<()>(), 1);
    assert_eq!(size_of::<()>(), 0);

    assert_eq!(offset_of!(Header, tag), 0);
    assert!(offset_of!(Header, len) >= 1);
    assert_eq!(size_of::<Header>() % align_of::<Header>(), 0);
}
```

The example uses `#[repr(C)]` for the field-offset assertion because declaration order is guaranteed for C-representation structs.
Do not write equivalent offset assertions for a default `repr(Rust)` struct unless all you rely on is a documented Rust-layout guarantee.

## Working with layout
Use `std::alloc::Layout` for allocation computations.
Manual `size * count` arithmetic can overflow or miss alignment rounding.
Use `offset_of!` when you need a stable field offset for a type whose representation provides one.
Use `&raw const` or `&raw mut` and unaligned pointer methods when working with potentially unaligned fields, especially in packed representations.
Use `MaybeUninit<T>` for uninitialized storage instead of pretending arbitrary bytes are a valid `T`.

Layout facts are target-dependent.
`usize`, pointer widths, primitive alignments, and C ABI details differ by target.
If a binary protocol needs exact bytes, encode and decode explicitly.
If FFI needs C compatibility, mirror the C declaration and validate the target ABI through bindings and tests.

## Best practice
- ✅ Treat default `repr(Rust)` field order and padding as private compiler choices.
- ✅ Use `size_of`, `align_of`, `size_of_val`, and `align_of_val` for introspection instead of hard-coded guesses.
- ✅ Use `std::alloc::Layout` for allocation size and alignment calculations.
- ✅ Add `#[repr(C)]` only when a type's layout is part of an unsafe or FFI contract.
- ✅ Keep public Rust APIs abstract over representation unless layout is deliberately promised.
- ✅ Use explicit serialization for file, network, and database formats instead of transmuting structs.
- ✅ Remember that equal layout does not imply equal validity, aliasing, provenance, or ABI.

## Pitfalls
- ⚠️ Assuming Rust declaration order is the memory order for default structs.
- ⚠️ Reading padding bytes; padding may be uninitialized and is not part of a field value.
- ⚠️ Treating a pointer-sized integer as a valid pointer without provenance.
- ⚠️ Building binary protocols from `size_of::<T>()` and raw struct bytes.
- ⚠️ Forgetting that zero-sized fields may have the same address as other fields.
- ⚠️ Assuming a wide pointer is exactly two machine words in portable unsafe code; current implementations often are, but the Reference does not promise that exact shape.
- ⚠️ Confusing layout compatibility with FFI call compatibility.

## See also
[[Advanced Type System]]
[[Type Layout and repr]]
[[Zero-Sized Types]]
[[Dynamically Sized Types]]
[[Raw Pointers]]
[[Aliasing and Provenance]]
[[MaybeUninit]]
[[FFI with C]]
[[Arrays]]
[[Enums]]
[[The Slice Type]]
[[Unsafe Rust]]

## Sources
- The Rust Reference, "Type layout" — [[the-reference]],
  https://doc.rust-lang.org/reference/type-layout.html
- The Rustonomicon, "Alternative representations" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/other-reprs.html
