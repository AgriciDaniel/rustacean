---
type: concept
title: "MaybeUninit"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, memory, initialization]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Raw Pointers]]", "[[Dereferencing Raw Pointers]]", "[[Undefined Behavior]]", "[[The static mut Footgun and &raw]]", "[[Transmute as a Shortcut]]"]
sources: ["[[rustonomicon]]", "[[the-reference]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/mem/union.MaybeUninit.html", "https://doc.rust-lang.org/nomicon/uninitialized.html", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html#invalid-values"]
rust_version: "edition 2024 / 1.85+"
---

# MaybeUninit

`MaybeUninit<T>` is the standard wrapper for memory that may not yet contain a valid `T`, allowing initialization through raw pointers without creating invalid Rust values.

## What it is
Most Rust types have validity invariants. A `bool` must be `0` or `1`; a reference
must be non-null, aligned, live, and point to a valid value; an enum must have a
valid discriminant. Uninitialized bytes may violate those invariants.

`MaybeUninit<T>` has no requirement that its bytes currently form a valid `T`.
That makes it the correct tool for delayed initialization, partially initialized
arrays, FFI out-pointers, and low-level allocation code.

## How it works
Create uninitialized storage with `MaybeUninit::uninit()`. Write into it through
`write`, `as_mut_ptr`, or APIs that receive raw out-pointers. Convert to `T` only
with `assume_init` after proving every byte required by `T` is initialized and
valid on every control-flow path.

Do not create `&T` or `&mut T` to uninitialized memory. A reference itself asserts
validity for its referent. Use raw pointers and `&raw` field projection when working
inside a not-yet-initialized aggregate.

`MaybeUninit` does not drop its contents automatically. That avoids dropping garbage
but means partial initialization code must clean up already-initialized elements if
later initialization can fail or panic.

Initialization is a value-level property, not just a byte-count property. Filling
the bytes of a `bool` with `2`, a `char` with a surrogate, or a reference with a
non-null-looking address still does not create a valid `T`. `assume_init` asserts
both that the bytes are initialized and that they satisfy every invariant of `T`.

## Example
```rust
use std::mem::MaybeUninit;

fn make_pair(a: u32, b: u32) -> (u32, u32) {
    let mut slot = MaybeUninit::<(u32, u32)>::uninit();
    let ptr = slot.as_mut_ptr();

    // SAFETY: ptr points to storage for a tuple, and both fields are written
    // before assume_init is called.
    unsafe {
        (&raw mut (*ptr).0).write(a);
        (&raw mut (*ptr).1).write(b);
        slot.assume_init()
    }
}

fn main() {
    assert_eq!(make_pair(1, 2), (1, 2));
}
```

## Worked example
```rust
use std::mem::MaybeUninit;

/// Simulates a C out-parameter API.
///
/// # Safety
///
/// If `ok` is true, `out` must be valid writable storage for one `u32`.
unsafe fn c_fill(out: *mut u32, ok: bool) -> i32 {
    if ok {
        // SAFETY: caller provides valid writable storage for one u32.
        unsafe { out.write(99) };
        0
    } else {
        -1
    }
}

fn fill_from_c(ok: bool) -> Option<u32> {
    let mut slot = MaybeUninit::<u32>::uninit();
    // SAFETY: slot.as_mut_ptr() is writable storage for one u32.
    let code = unsafe { c_fill(slot.as_mut_ptr(), ok) };
    if code == 0 {
        // SAFETY: c_fill returned success only after writing one valid u32.
        Some(unsafe { slot.assume_init() })
    } else {
        None
    }
}

fn main() {
    assert_eq!(fill_from_c(true), Some(99));
    assert_eq!(fill_from_c(false), None);
}
```

This mirrors an FFI out-parameter pattern: allocate uninitialized Rust storage,
pass a raw pointer to the foreign function, and call `assume_init` only on the
documented success path.

## Common errors
Moving out of a `MaybeUninit<T>` through `assume_init` too early is often caught
only by tests or [[Miri]], not by rustc. A related safe-code diagnostic appears
when Rust can see a possibly-uninitialized local:

```text
error[E0381]: used binding is possibly-uninitialized
```

The unsafe-code fix is to track initialization explicitly. For arrays or loops,
store how many elements have been written and drop exactly that prefix if a later
step can fail or panic.

## Best practice
- ✅ Keep the initialization state simple and local; call `assume_init` at one obvious point.
- ✅ Use raw pointers or `&raw` for fields until the full value is valid.
- ✅ Prefer safe constructors and collection APIs unless partial initialization is necessary.
- ✅ For FFI out-parameters, check the C return code before assuming initialization happened.
- ✅ Use guard objects for panic-safe partial initialization when initializing multiple `Drop` values.
- ✅ Prefer `MaybeUninit::write` over assignment through `*ptr` when the old value is uninitialized.

## Pitfalls
- ⚠️ Replacing `MaybeUninit<T>` with `mem::zeroed::<T>()`; zero is invalid for many `T`.
- ⚠️ Calling `assume_init` after an error path that may skip writes.
- ⚠️ Assigning through a dereferenced `*mut T` in a way that drops an uninitialized old value; use `ptr::write`-style operations.
- ⚠️ Transmuting arbitrary `Container<MaybeUninit<T>>` to `Container<T>`; layout compatibility is container-specific.
- ⚠️ Forgetting that `MaybeUninit<T>` will not drop an initialized `T`; after successful initialization, convert or manually drop exactly once.

## See also
[[Unsafe Rust]] · [[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[Undefined Behavior]] · [[The static mut Footgun and &raw]] · [[Transmute as a Shortcut]] · [[FFI with C]] · [[Miri]] · [[Unsafe Rust & FFI]]

## Sources
- The standard library, `MaybeUninit` — https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- The Rustonomicon, "Working With Uninitialized Memory" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/uninitialized.html
- The Rust Reference, "Invalid values" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html#invalid-values
