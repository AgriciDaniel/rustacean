---
type: concept
title: "Raw Pointers"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, pointers, memory]
domain: "Unsafe Rust & FFI"
difficulty: intermediate
related: ["[[Unsafe Rust]]", "[[Dereferencing Raw Pointers]]", "[[Aliasing and Provenance]]", "[[MaybeUninit]]", "[[The static mut Footgun and &raw]]", "[[FFI with C]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#dereferencing-a-raw-pointer", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#raw-borrow-operators", "https://doc.rust-lang.org/reference/types/pointer.html"]
rust_version: "edition 2024 / 1.85+"
---

# Raw Pointers

Raw pointers are `*const T` and `*mut T`: pointer values that may be created in safe code but require unsafe proof before dereference or many pointer operations.

## What it is
Raw pointers are Rust's low-level pointer types. They are common at FFI boundaries,
inside data structures, and when working with memory whose validity cannot yet be
represented as a reference, such as [[MaybeUninit]].

Unlike `&T` and `&mut T`, raw pointers:

- may be null;
- may dangle;
- may be unaligned;
- do not automatically enforce exclusive access;
- do not participate in automatic cleanup;
- can point to memory whose value is not currently valid for `T`.

Creating a raw pointer is usually safe. Using one as if it were a valid `T` is where
the [[Undefined Behavior]] risk appears.

## How it works
Use the raw borrow operators when deriving a raw pointer from an existing place:
`&raw const place` produces `*const T`, and `&raw mut place` produces `*mut T`.

These operators are especially important when a normal borrow would itself be UB:
for example, a field in a `repr(packed)` struct may be unaligned, and a field inside
uninitialized memory may not yet contain a valid value. A raw pointer can be formed
without claiming the validity and alignment guarantees that a reference would claim.

The `as` cast can also create raw pointers, including from integers, but such
pointers usually lack meaningful provenance. Prefer raw borrows and pointer APIs
derived from real allocations; see [[Aliasing and Provenance]].

Raw pointers are `Copy` values. Copying the pointer does not copy or keep alive
the pointed-to allocation, and dropping the pointer does nothing. Ownership still
lives somewhere else: a stack variable, a `Box`, a `Vec`, a C allocation, or an
opaque handle managed by [[FFI Wrapper Types]].

The mutability in `*mut T` describes what operations the pointer type permits; it
does not prove exclusive access. You still need a separate argument that no live
reference or raw access conflicts with the write you are about to perform.

## Example
```rust
fn main() {
    let mut value = 42;

    let read_ptr: *const i32 = &raw const value;
    let write_ptr: *mut i32 = &raw mut value;

    // SAFETY: both pointers came from value, value is alive, and these accesses
    // are sequenced so no reference aliasing rule is violated.
    unsafe {
        assert_eq!(*read_ptr, 42);
        *write_ptr = 7;
        assert_eq!(value, 7);
    }
}
```

## Worked example
```rust
#[repr(packed)]
struct Header {
    tag: u8,
    len: u32,
}

fn read_len(header: &Header) -> u32 {
    let ptr = &raw const header.len;

    // SAFETY: repr(packed) may make len unaligned, so use read_unaligned.
    // The field is initialized because header is a valid Header.
    unsafe { ptr.read_unaligned() }
}

fn main() {
    let h = Header { tag: 1, len: 0x0102_0304 };
    assert_eq!(h.tag, 1);
    assert_eq!(read_len(&h), 0x0102_0304);
}
```

This is exactly the kind of place where `&header.len as *const u32` is wrong: the
intermediate reference would claim alignment that a packed field may not have.
`&raw const` creates the pointer without first creating an invalid reference.

## Common errors
Dereferencing a raw pointer without an unsafe block is E0133:

```text
error[E0133]: dereference of raw pointer is unsafe and requires unsafe block
```

Creating a reference to an unaligned packed field is commonly rejected with E0793:

```text
error[E0793]: reference to packed field is unaligned
```

Use a raw borrow plus `read_unaligned` or copy the field through an API that does
not create an unaligned reference.

## Best practice
- ✅ Use `&raw const` and `&raw mut` to create raw pointers to places, especially for packed fields, `static mut`, and partially initialized data.
- ✅ Convert raw pointers to references only for the smallest scope where you can prove validity, alignment, aliasing, and initialization.
- ✅ Prefer `NonNull<T>` in APIs when null is not a valid state but ownership is still not represented by a reference.
- ✅ Keep pointer arithmetic inside wrappers that check bounds before calling unsafe operations.
- ✅ Preserve the original owner in the same abstraction so the raw pointer cannot outlive the allocation it points into.
- ✅ Use `ptr::addr`, `with_addr`, or `map_addr` for address manipulation that must retain provenance.

## Pitfalls
- ⚠️ Treating `*mut T` as "like `&mut T` but easier"; raw pointers do not grant exclusive access by themselves.
- ⚠️ Casting arbitrary integers to pointers and dereferencing them; address bits are not enough to prove provenance or allocation validity.
- ⚠️ Creating `&T` or `&mut T` just to get a pointer when the place is unaligned or uninitialized; use `&raw` instead.
- ⚠️ Returning raw pointers to stack locals; the pointer will dangle after the function returns.
- ⚠️ Letting a raw pointer escape from a `Vec` or `String` and then reallocating the collection before using the pointer.

## See also
[[Unsafe Rust]] · [[Dereferencing Raw Pointers]] · [[Aliasing and Provenance]] · [[MaybeUninit]] · [[The static mut Footgun and &raw]] · [[FFI with C]] · [[FFI Wrapper Types]] · [[Miri]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Dereferencing a Raw Pointer" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#dereferencing-a-raw-pointer
- The Rust Reference, "Raw borrow operators" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#raw-borrow-operators
- The Rust Reference, "Pointer types" — [[the-reference]], https://doc.rust-lang.org/reference/types/pointer.html
