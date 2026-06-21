---
type: concept
title: "FFI with C"
aliases: ["Foreign Function Interface (FFI)", "FFI"]
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ffi, c, unsafe]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[unsafe extern Blocks]]", "[[Raw Pointers]]", "[[FFI Wrapper Types]]", "[[Undefined Behavior]]", "[[SAFETY Comments]]", "[[The static mut Footgun and &raw]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-extern-functions-to-call-external-code", "https://doc.rust-lang.org/reference/items/external-blocks.html", "https://doc.rust-lang.org/nomicon/ffi.html"]
rust_version: "edition 2024 / 1.85+"
---

# FFI with C

FFI with C is Rust's way to declare, call, and export C-ABI functions and statics, but every boundary is a trust boundary for layout, lifetimes, initialization, aliasing, and unwinding.

## What it is
Foreign Function Interface work uses `extern` ABIs, raw pointers, C-compatible
layout, and often linker attributes to let Rust and C call each other. The common
ABI is `"C"`, and the platform-specific ABI is often `"system"`.

Rust can call C declarations inside [[unsafe extern Blocks]]. C can call Rust
functions declared as `extern "C"` and exported with attributes such as
`#[unsafe(no_mangle)]` when a stable symbol name is required.

## How it works
C does not enforce Rust's aliasing, initialization, lifetime, thread-safety, or
panic rules. Therefore a C declaration is a promise by the Rust author that the
signature, ABI, and safety classification are correct.

Use `#[repr(C)]` for structs that cross the boundary by value or are inspected by
C. Prefer opaque pointer handles for C-owned resources. Use `CString` and `CStr`
for NUL-terminated strings. Represent nullable function pointers with `Option`
over an extern function pointer where the nullable pointer optimization applies.

Unwinding needs explicit design. If Rust panics must not cross into C, catch them
and convert to error codes. If unwinding is intentionally allowed across a boundary,
use the appropriate `-unwind` ABI and understand the other runtime.

The boundary should translate C shapes into Rust shapes as early as possible:
nullable pointers become `Option`, status codes become `Result`, borrowed buffers
become slices tied to a real lifetime, and owned handles become [[FFI Wrapper Types]]
with `Drop`. Keep the raw `unsafe extern` declarations private unless the crate is
intentionally exposing a low-level binding layer.

## Example
```rust
use std::ffi::CStr;
use std::os::raw::c_char;

unsafe extern "C" {
    safe fn abs(input: i32) -> i32;
}

/// Returns the byte length of a C string.
///
/// # Safety
///
/// If `ptr` is non-null, it must point to a live NUL-terminated C string.
unsafe fn c_strlen(ptr: *const c_char) -> Option<usize> {
    if ptr.is_null() {
        return None;
    }
    // SAFETY: caller gave a non-null pointer; from_ptr still requires that it
    // points to a valid NUL-terminated C string.
    let s = unsafe { CStr::from_ptr(ptr) };
    Some(s.to_bytes().len())
}

fn main() {
    assert_eq!(abs(-3), 3);
    // SAFETY: c"hi" is a live NUL-terminated C string.
    assert_eq!(unsafe { c_strlen(c"hi".as_ptr()) }, Some(2));
}
```

## Worked example
```rust
use std::ffi::CStr;
use std::os::raw::c_char;

/// Reads a nullable C string and validates UTF-8.
///
/// # Safety
///
/// If `ptr` is non-null, it must point to a live NUL-terminated C string.
unsafe fn read_c_message(ptr: *const c_char) -> Result<String, &'static str> {
    if ptr.is_null() {
        return Err("missing message");
    }

    // SAFETY: caller must provide a live, NUL-terminated C string. This wrapper
    // validates UTF-8 before returning owned Rust text.
    let bytes = unsafe { CStr::from_ptr(ptr) }.to_bytes();
    std::str::from_utf8(bytes)
        .map(str::to_owned)
        .map_err(|_| "message is not UTF-8")
}

fn main() {
    // SAFETY: c"ok" is a live NUL-terminated C string.
    assert_eq!(unsafe { read_c_message(c"ok".as_ptr()) }, Ok(String::from("ok")));
    // SAFETY: null is explicitly allowed by read_c_message.
    assert_eq!(unsafe { read_c_message(std::ptr::null()) }, Err("missing message"));
}
```

This wrapper still depends on the C-string contract for non-null pointers. If the
pointer can come from untrusted foreign code, the function should be documented as
unsafe or the API should obtain the pointer from a narrower trusted source.

## Common errors
Calling an unsafe foreign item without an unsafe block is E0133:

```text
error[E0133]: call to unsafe function is unsafe and requires unsafe block
```

Edition 2024 also requires the declaration block itself to be written as
`unsafe extern "C" { ... }`. The block asserts that the Rust signature matches
the external symbol; the call-site unsafe block asserts that this particular call
satisfies the function's pointer, lifetime, and threading contract.

## Best practice
- ✅ Keep raw FFI declarations private and expose [[FFI Wrapper Types]] or safe Rust functions.
- ✅ Validate pointers, lengths, ownership, encodings, return codes, and thread-safety at the boundary.
- ✅ Use `repr(C)` only for types whose layout is part of the C contract.
- ✅ Prevent panics from crossing non-unwinding ABI boundaries with `catch_unwind` when exporting callbacks.
- ✅ Model C strings with `CStr`/`CString` and validate UTF-8 before producing `&str` or `String`.
- ✅ Treat C enums and bitflags as integer newtypes unless every possible C value is valid for a Rust enum.

## Pitfalls
- ⚠️ Modeling C enums as Rust field-less enums when C may pass unknown integer values.
- ⚠️ Passing Rust references to C that may store, mutate, or use them after return; prefer raw pointers plus explicit contracts.
- ⚠️ Assuming an extern declaration is checked by rustc against the C header; it is not.
- ⚠️ Exporting unmangled symbols without considering global symbol collisions; use `#[unsafe(no_mangle)]` deliberately.
- ⚠️ Returning borrowed Rust data to C without a clear lifetime, ownership, and unregister/free protocol.

## See also
[[unsafe extern Blocks]] · [[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[FFI Wrapper Types]] · [[Undefined Behavior]] · [[SAFETY Comments]] · [[Soundness vs Safety]] · [[Miri]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Using extern Functions to Call External Code" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-extern-functions-to-call-external-code
- The Rust Reference, "External blocks" — [[the-reference]], https://doc.rust-lang.org/reference/items/external-blocks.html
- The Rustonomicon, "Foreign Function Interface" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/ffi.html
