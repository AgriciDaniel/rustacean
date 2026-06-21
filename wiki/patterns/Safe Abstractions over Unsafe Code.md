---
type: pattern
title: "Safe Abstractions over Unsafe Code"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, api, pattern]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Soundness vs Safety]]", "[[Raw Pointers]]", "[[Dereferencing Raw Pointers]]", "[[SAFETY Comments]]", "[[Miri]]"]
sources: ["[[the-book]]", "[[rustonomicon]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#creating-a-safe-abstraction-over-unsafe-code", "https://doc.rust-lang.org/nomicon/working-with-unsafe.html", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html"]
rust_version: "edition 2024 / 1.85+"
---

# Safe Abstractions over Unsafe Code

A safe abstraction over unsafe code performs all required validation internally so callers can use an ordinary safe API without being able to cause undefined behavior.

## What it is
This pattern is the core productive use of [[Unsafe Rust]]. Unsafe implementation
details are isolated inside a module, and the public surface uses safe Rust types,
checked constructors, lifetimes, ownership, and error returns to enforce invariants.

The standard `split_at_mut` idea is the classic example: unsafe pointer arithmetic
can create two mutable slices, but the public function is safe because it first
checks that the ranges do not overlap and remain within one slice.

## How it works
Design the safe API first. Identify the invariant the compiler cannot express, then
prove it before the unsafe operation. Place the unsafe operation in the smallest
block possible, with a [[SAFETY Comments|SAFETY comment]] that refers to the exact
prior checks.

The abstraction is sound only if every safe caller is covered. Do not rely on caller
discipline unless the API is intentionally `unsafe fn` and documents the obligation.

The public API should make invalid states hard or impossible to express. Use private
fields, checked constructors, lifetimes tied to real borrows, and ownership transfer
instead of comments that ask safe callers to behave. Comments explain the proof;
types should carry as much of the proof as practical.

## Example
```rust
use std::slice;

fn split_one(values: &mut [i32]) -> Option<(&mut [i32], &mut [i32])> {
    if values.is_empty() {
        return None;
    }
    let ptr = values.as_mut_ptr();
    let len = values.len();

    // SAFETY: ptr comes from one live mutable slice; lengths partition the slice
    // into non-overlapping in-bounds ranges.
    let parts = unsafe {
        (
            slice::from_raw_parts_mut(ptr, 1),
            slice::from_raw_parts_mut(ptr.add(1), len - 1),
        )
    };
    Some(parts)
}

fn main() {
    let mut data = [1, 2, 3];
    let (head, tail) = split_one(&mut data).unwrap();
    head[0] = 9;
    tail[0] = 8;
    assert_eq!(data, [9, 8, 3]);
}
```

## Worked example
```rust
pub struct InitBuf {
    bytes: Vec<u8>,
}

impl InitBuf {
    pub fn new(len: usize) -> Self {
        Self { bytes: vec![0; len] }
    }

    pub fn as_mut_ptr_and_len(&mut self) -> (*mut u8, usize) {
        (self.bytes.as_mut_ptr(), self.bytes.len())
    }

    pub fn byte(&self, index: usize) -> Option<u8> {
        if index < self.bytes.len() {
            // SAFETY: index is checked and Vec elements are initialized.
            Some(unsafe { *self.bytes.as_ptr().add(index) })
        } else {
            None
        }
    }
}

fn main() {
    let mut buf = InitBuf::new(2);
    let (ptr, len) = buf.as_mut_ptr_and_len();
    assert_eq!(len, 2);
    // SAFETY: ptr came from buf, len is 2, and buf is not reallocated here.
    unsafe { ptr.write(7) };
    assert_eq!(buf.byte(0), Some(7));
}
```

This example deliberately keeps ownership in `InitBuf`; callers can get a raw
pointer for FFI-style filling, but safe reads still go through checked methods.
If the pointer were stored and used after resizing the vector, the abstraction
would need a stricter borrowing API.

## Common errors
A common compiler error while building this pattern is E0499, caused by trying to
return two mutable references that the borrow checker cannot prove are disjoint:

```text
error[E0499]: cannot borrow `*values` as mutable more than once at a time
```

The fix is either to use the standard safe API such as `split_at_mut`, or to write
a small unsafe block that constructs non-overlapping slices after checking the
partition proof yourself.

## Best practice
- ✅ Keep unsafe code private unless callers truly need to uphold part of the contract.
- ✅ Encode invariants in types, lengths, lifetimes, ownership, and constructors.
- ✅ Validate before entering the unsafe block, then make the unsafe block mechanically small.
- ✅ Exercise boundary cases under [[Miri]].
- ✅ Re-audit every unsafe block when adding new constructors, setters, trait impls, or `pub` fields.
- ✅ Prefer borrowing APIs that prevent reallocation while raw pointers are in use.

## Pitfalls
- ⚠️ Providing a safe constructor that accepts unchecked raw pointers and lengths.
- ⚠️ Letting safe users observe partially initialized or internally aliased states.
- ⚠️ Mixing unrelated unsafe operations in one block, making the proof impossible to review.
- ⚠️ Exposing C resources without `Drop`, leading to leaks or use-after-free when callers guess the protocol.
- ⚠️ Writing a safe wrapper that validates only today's call path but leaves future methods able to break the invariant.

## See also
[[Unsafe Rust]] · [[Soundness vs Safety]] · [[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[SAFETY Comments]] · [[Miri]] · [[FFI Wrapper Types]] · [[MaybeUninit]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Creating a Safe Abstraction over Unsafe Code" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#creating-a-safe-abstraction-over-unsafe-code
- The Rustonomicon, "Working with Unsafe" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/working-with-unsafe.html
- The Rust Reference, "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html
