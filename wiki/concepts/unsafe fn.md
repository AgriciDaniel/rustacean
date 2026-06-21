---
type: concept
title: "unsafe fn"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, api, contracts]
domain: "Unsafe Rust & FFI"
difficulty: intermediate
related: ["[[Unsafe Rust]]", "[[SAFETY Comments]]", "[[Soundness vs Safety]]", "[[Safe Abstractions over Unsafe Code]]", "[[FFI with C]]", "[[unsafe extern Blocks]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#calling-an-unsafe-function-or-method", "https://doc.rust-lang.org/reference/unsafe-keyword.html", "https://doc.rust-lang.org/reference/unsafety.html"]
rust_version: "edition 2024 / 1.85+"
---

# unsafe fn

An `unsafe fn` is a function whose caller must uphold extra safety conditions that Rust cannot check before the function may be called soundly.

## What it is
`unsafe fn` changes the caller contract, not the implementation's correctness
requirements. Calling it requires an unsafe context because the caller is claiming
that the documented preconditions hold.

This is different from a safe function that contains unsafe blocks. A safe function
must be sound for every safe caller. An `unsafe fn` may require the caller to prove
facts such as pointer validity, exclusive access, initialized memory, ABI correctness,
or thread-safety conditions.

## How it works
Declare an unsafe function with `unsafe fn name(...)`. Call it only inside an
`unsafe { ... }` block after checking its contract.

Current idiom is to keep unsafe operations inside the body in explicit unsafe
blocks as well. The Reference describes unsafe blocks as the dual of unsafe
functions: functions declare proof obligations, blocks discharge proof obligations.

Public unsafe functions should have a documentation section named `# Safety` that
states what callers must guarantee. Internal unsafe functions should still carry a
nearby [[SAFETY Comments|SAFETY comment]] or private docs explaining the invariant.

An `unsafe fn` is not an escape hatch for implementation mistakes. The function
body must still be written so that, if the caller satisfies the documented contract,
no UB occurs. Edition-2024 style makes this visible by requiring local unsafe
blocks for unsafe operations inside the body, so caller obligations and callee
operations remain separate.

## Example
```rust
/// Returns the first byte at `ptr`.
///
/// # Safety
///
/// `ptr` must be non-null, aligned for `u8`, and valid to read one byte.
unsafe fn read_one(ptr: *const u8) -> u8 {
    // SAFETY: guaranteed by this function's caller.
    unsafe { *ptr }
}

fn main() {
    let byte = 9_u8;
    // SAFETY: &byte is live and valid for one byte.
    let got = unsafe { read_one(&byte) };
    assert_eq!(got, 9);
}
```

## Worked example
```rust
/// Interprets a non-null pointer and length as a byte slice.
///
/// # Safety
///
/// `ptr` must be valid for reads of `len` bytes, aligned for `u8`, and all bytes
/// must be in a single allocation that lives at least as long as `'a`.
unsafe fn bytes_from_raw<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    // SAFETY: guaranteed by this function's caller.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}

fn bytes_from_slice(data: &[u8]) -> &[u8] {
    // SAFETY: the pointer and length come from a live slice, including the
    // non-null dangling pointer used by empty slices.
    unsafe { bytes_from_raw(data.as_ptr(), data.len()) }
}

fn main() {
    let data = [1, 2, 3];
    let view = bytes_from_slice(&data);
    assert_eq!(view, &[1, 2, 3]);
}
```

The safe wrapper is sound because it derives the pointer and length from a real
slice borrow. A public wrapper accepting arbitrary raw pointers could not safely
invent `'a`; it should be `unsafe fn` or return an owned copy after validating
through an external contract.

## Common errors
With `unsafe_op_in_unsafe_fn`, unsafe operations inside an unsafe function still
need a local unsafe block:

```text
warning[E0133]: call to unsafe function is unsafe and requires unsafe block
```

In edition-2024 code, treat this as a design error to fix immediately. Put a
`// SAFETY:` comment on the local operation and make sure it refers either to the
function's `# Safety` contract or to checks performed in the body.

## Best practice
- ✅ Make a function `unsafe` only when safe callers cannot be prevented from violating required invariants.
- ✅ Put caller obligations in a `# Safety` docs section for public APIs.
- ✅ Use safe wrapper functions when you can validate the preconditions internally.
- ✅ Keep unsafe operations inside the body in explicit, commented blocks.
- ✅ Name parameters and lifetimes so the contract can state exactly what must outlive what.
- ✅ Prefer returning `Result` from a safe function when invalid input can be detected instead of pushing that obligation to callers.

## Pitfalls
- ⚠️ Marking a whole API `unsafe` because implementation was hard; callers should inherit only real obligations.
- ⚠️ Hiding safety requirements in prose elsewhere; unsafe callers need the exact contract at the call site.
- ⚠️ Assuming an `unsafe fn` body may freely perform unsafe operations without local proof.
- ⚠️ Returning references from raw pointers without tying the lifetime to a real borrow.
- ⚠️ Writing `unsafe fn new_unchecked` constructors whose unchecked invariant is later relied on by safe methods but never documented.

## See also
[[Unsafe Rust]] · [[SAFETY Comments]] · [[Soundness vs Safety]] · [[Safe Abstractions over Unsafe Code]] · [[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[unsafe extern Blocks]] · [[Undefined Behavior]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Calling an Unsafe Function or Method" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#calling-an-unsafe-function-or-method
- The Rust Reference, "The unsafe keyword" — [[the-reference]], https://doc.rust-lang.org/reference/unsafe-keyword.html
- The Rust Reference, "Unsafety" — [[the-reference]], https://doc.rust-lang.org/reference/unsafety.html
