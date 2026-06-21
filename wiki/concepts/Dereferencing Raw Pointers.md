---
type: concept
title: "Dereferencing Raw Pointers"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, pointers, ub]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Raw Pointers]]", "[[Unsafe Rust]]", "[[Undefined Behavior]]", "[[Aliasing and Provenance]]", "[[Miri]]", "[[Safe Abstractions over Unsafe Code]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#dereferencing-a-raw-pointer", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html", "https://doc.rust-lang.org/std/ptr/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Dereferencing Raw Pointers

Dereferencing a raw pointer is unsafe because the compiler cannot verify that the pointer is non-null, aligned, live, initialized, in bounds, and compatible with Rust's aliasing rules.

## What it is
The expression `*ptr`, `ptr.read()`, `ptr.write(value)`, `ptr.add(n)`, and APIs
such as `slice::from_raw_parts` all rely on facts that are outside the type
system. They are the point where a raw address-like value becomes an actual
memory access or a reference-like view.

Raw pointer dereference is one of the core unsafe operations listed by the Book
and the Rustonomicon. The pointer may have been formed in safe code, but access
through it requires an `unsafe` context.

## How it works
Before dereferencing a raw pointer, prove at least these facts:

- the pointer is not null for non-zero-sized accesses;
- all pointed-to bytes are in one live allocation;
- the pointer has the alignment required by `T`, unless using explicit unaligned APIs;
- the memory contains a valid initialized `T` for reads;
- the access does not violate `&T`, `&mut T`, or `UnsafeCell` aliasing rules;
- any pointer arithmetic stayed in bounds of the same allocation.

The exact obligation depends on the operation. `ptr.write(value)` does not read or
drop the old value, which makes it useful for [[MaybeUninit]], but the destination
still must be valid for writes and properly aligned. `read_unaligned` handles
alignment differently, but it still requires the bytes to be valid to read as `T`.

Creating a reference from a raw pointer is often a bigger promise than copying a
value out. A temporary `&T` says the referent is valid, aligned, live, and obeys
shared-reference aliasing rules for the entire lifetime of that reference. If the
operation only needs one load, prefer `ptr.read()` or `read_unaligned()` when those
semantics match the proof.

## Example
```rust
fn first_or_none(values: &[u32]) -> Option<u32> {
    if values.is_empty() {
        None
    } else {
        let ptr = values.as_ptr();
        // SAFETY: values is non-empty, ptr came from values, and u32 is Copy.
        Some(unsafe { *ptr })
    }
}

fn main() {
    assert_eq!(first_or_none(&[5, 8]), Some(5));
    assert_eq!(first_or_none(&[]), None);
}
```

## Worked example
```rust
fn read_u32_le(bytes: &[u8]) -> Option<u32> {
    let chunk = bytes.get(..4)?;
    let ptr = chunk.as_ptr().cast::<[u8; 4]>();

    // SAFETY: chunk has exactly four initialized bytes and came from one slice
    // allocation. [u8; 4] has alignment 1, so this read is aligned.
    let array = unsafe { ptr.read() };
    Some(u32::from_le_bytes(array))
}

fn main() {
    assert_eq!(read_u32_le(&[1, 0, 0, 0, 9]), Some(1));
    assert_eq!(read_u32_le(&[1, 2, 3]), None);
}
```

The example avoids casting the bytes directly to `u32`. A `u32` load may require
stricter alignment and would also bake in native-endian interpretation. Copying a
four-byte array and then using `from_le_bytes` keeps the unsafe proof narrow.

## Common errors
The compiler rejects a raw dereference outside an unsafe context:

```text
error[E0133]: dereference of raw pointer is unsafe and requires unsafe block
```

The fix is to prove the pointer contract, not merely add syntax. For slice
construction, the usual checklist is: non-null for non-empty slices, one allocation,
`len * size_of::<T>() <= isize::MAX`, proper alignment, initialized elements, and
no conflicting mutable access for the returned lifetime.

## Best practice
- ✅ Perform safe bounds and lifetime checks before the unsafe dereference.
- ✅ Prefer safe slice/string APIs unless profiling proves the checked operation is the bottleneck.
- ✅ Use `ptr::read`, `ptr::write`, `read_unaligned`, or `write_unaligned` only when their exact semantics match the proof.
- ✅ Run tests under [[Miri]] for crates that dereference raw pointers.
- ✅ Keep the owner alive and immobile for the entire raw access; do not dereference pointers after collection reallocation or `Box` deallocation.
- ✅ Choose copying a value out over creating a reference when the reference lifetime would be hard to justify.

## Pitfalls
- ⚠️ Creating a slice from an arbitrary address and length; `from_raw_parts` requires one allocation, valid metadata, and initialized elements.
- ⚠️ Using `ptr.add(n)` without proving that `n` remains in bounds for the allocation.
- ⚠️ Reading uninitialized memory through a raw pointer; even integers and raw pointers must be initialized when read.
- ⚠️ Turning raw pointers into references too early; references assert stronger validity and aliasing guarantees.
- ⚠️ Using `copy_nonoverlapping` on overlapping ranges; use `ptr::copy` when overlap is possible and still valid.

## See also
[[Raw Pointers]] · [[Unsafe Rust]] · [[Undefined Behavior]] · [[Aliasing and Provenance]] · [[MaybeUninit]] · [[Miri]] · [[Safe Abstractions over Unsafe Code]] · [[SAFETY Comments]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Dereferencing a Raw Pointer" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#dereferencing-a-raw-pointer
- The Rust Reference, "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html
- The standard library, `std::ptr` — https://doc.rust-lang.org/std/ptr/index.html
