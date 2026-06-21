---
type: concept
title: "Type Layout and repr"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, repr, layout, ffi, unsafe]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Type layout]]", "[[FFI with C]]", "[[Newtype Pattern]]", "[[Raw Pointers]]", "[[Zero-Sized Types]]", "[[Enums]]", "[[Unsafe Rust]]", "[[Transmute as a Shortcut]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/type-layout.html#representations", "https://doc.rust-lang.org/reference/type-layout.html#the-c-representation", "https://doc.rust-lang.org/reference/type-layout.html#the-transparent-representation", "https://doc.rust-lang.org/nomicon/other-reprs.html"]
rust_version: "edition 2024 / 1.85+"
---

# Type Layout and repr

`#[repr(...)]` is Rust's way to request specific layout guarantees for user-defined composite types.
Use it only when layout is part of the contract, such as FFI, transparent newtypes, primitive enum tags, or carefully audited unsafe code.

## What it is
All structs, enums, and unions have a representation.
The default is `repr(Rust)`, which gives the compiler freedom to choose efficient layout while preserving Rust's soundness guarantees.
The `repr` attribute changes that representation.
The stable representation families are `Rust`, `C`, primitive integer representations for enums, and `transparent`.
The `align(N)` and `packed(N)` modifiers raise or lower alignment for structs and unions, and can modify either Rust or C representation.

Representation is attached to the item, not to a specific monomorphization.
For a generic type `Wrapper<T>`, `Wrapper<u8>` and `Wrapper<u64>` have the same representation rules even though the field type layouts differ.
`repr` can change padding around fields and the representation of the outer type, but it does not rewrite the representation of an inner field's own type.

## How it works
`#[repr(C)]` gives C-like layout for structs, unions, and enums under Rust's documented rules.
For structs, fields are laid out in declaration order with padding inserted to satisfy alignment, and the final size is rounded up to the struct alignment.
For unions, every field starts at offset 0 and the size and alignment come from the maximum required by the fields.
For enums with fields, `repr(C)` is described as a tagged union: a tag plus a union of variant payload structs.

`#[repr(transparent)]` applies to a struct or single-variant enum with any number of fields whose size is 0 and alignment is 1, plus at most one other field.
It promises the same layout and ABI as that one field.
This is the right representation for a newtype that must be ABI-compatible with its inner value while preserving a distinct Rust type.
It cannot be combined with other representations.

Primitive representations such as `#[repr(u8)]` apply only to enums.
For fieldless enums, they set the enum's size and alignment to the primitive type and constrain discriminants to the representable range.
For enums with fields, they define a tagged-union style layout with the primitive tag.
Combining `repr(C, u8)` on an enum with fields uses the C enum-with-fields shape but replaces the tag representation with `u8`.

`#[repr(packed)]` lowers field alignment and can remove inter-field padding.
It can make fields unaligned, so taking references to those fields is not allowed.
Use raw borrow operators and `read_unaligned` or `write_unaligned` when access is truly needed.
`#[repr(align(N))]` raises type alignment, often for cache-line or ABI requirements.
`align` and `packed` cannot be applied to the same type.

## Example
```rust
use std::mem::{align_of, offset_of, size_of};

#[repr(transparent)]
#[derive(Copy, Clone, Debug, Eq, PartialEq)]
struct UserId(u64);

#[repr(C)]
struct Record {
    tag: u8,
    id: UserId,
}

fn main() {
    assert_eq!(size_of::<UserId>(), size_of::<u64>());
    assert_eq!(align_of::<UserId>(), align_of::<u64>());

    assert_eq!(offset_of!(Record, tag), 0);
    assert!(offset_of!(Record, id) >= 1);

    let id = UserId(42);
    assert_eq!(id.0, 42);
}
```

This example uses `repr(transparent)` for the newtype and `repr(C)` where declaration-order field layout is part of the demonstration.
It does not transmute values; it lets the type system keep `UserId` distinct while documenting the layout contract.

## Choosing a representation
Use the default representation for normal Rust-only types.
It gives the compiler maximum freedom and avoids accidentally promising an ABI you did not mean to support.
Use `repr(C)` for C FFI structs and unions that are passed by value or inspected by C code.
Use `repr(transparent)` for newtypes that wrap one ABI-relevant field.
Use primitive enum representations when the tag size is part of a wire, FFI, or unsafe contract.
Use `repr(align(N))` when over-alignment is the contract.
Use `repr(packed)` rarely, and prefer explicit parsing for external packed byte formats.

Representation does not make invalid values valid.
A `repr(u8)` fieldless enum with variants `A = 0` and `B = 1` still cannot legally hold the byte value `2`.
A `repr(C)` Rust fieldless enum is not the same semantic type as a C enum that can contain arbitrary integer values.
For C bitflags, use an integer or a bitflags wrapper rather than a Rust enum with invalid states.

## Best practice
- ✅ Keep `repr(Rust)` for ordinary internal data structures.
- ✅ Use `#[repr(C)]` on FFI structs and unions whose layout crosses a C boundary.
- ✅ Use `#[repr(transparent)]` for ABI-compatible newtypes with one real field.
- ✅ Document any public layout guarantee in prose, especially for transparent wrappers with private fields.
- ✅ Use primitive enum reprs only when the tag representation is truly part of the contract.
- ✅ Access packed fields by copying, or by raw pointers plus unaligned reads and writes.
- ✅ Pair `repr` use with tests or bindgen/cbindgen checks when matching external ABIs.

## Pitfalls
- ⚠️ Adding `repr(C)` to every type; it can freeze layout and suppress useful enum layout optimizations.
- ⚠️ Assuming `repr(C)` makes every Rust type FFI-safe; DST pointers, Rust tuples, and many enums still need care.
- ⚠️ Treating a Rust fieldless enum as a C enum that can hold arbitrary integer values.
- ⚠️ Combining layout assumptions with `transmute` instead of using typed APIs; see [[Transmute as a Shortcut]].
- ⚠️ Taking references to fields of packed structs; use `&raw const`/`&raw mut` and unaligned pointer methods.
- ⚠️ Using `repr(packed)` for file or network formats when explicit byte parsing would be safer and clearer.
- ⚠️ Forgetting that `repr(transparent)` cannot be combined with another representation.

## See also
[[Advanced Type System]]
[[Type layout]]
[[FFI with C]]
[[Newtype Pattern]]
[[Tuple Structs]]
[[Enums]]
[[Raw Pointers]]
[[The static mut Footgun and &raw]]
[[Zero-Sized Types]]
[[Unsafe Rust]]
[[Transmute as a Shortcut]]
[[Aliasing and Provenance]]

## Sources
- The Rust Reference, "Representations" — [[the-reference]],
  https://doc.rust-lang.org/reference/type-layout.html#representations
- The Rust Reference, "`repr(C)`" — [[the-reference]],
  https://doc.rust-lang.org/reference/type-layout.html#the-c-representation
- The Rust Reference, "`repr(transparent)`" — [[the-reference]],
  https://doc.rust-lang.org/reference/type-layout.html#the-transparent-representation
- The Rustonomicon, "Alternative representations" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/other-reprs.html
