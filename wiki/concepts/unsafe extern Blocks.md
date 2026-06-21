---
type: concept
title: "unsafe extern Blocks"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ffi, extern, unsafe]
domain: "Unsafe Rust & FFI"
difficulty: intermediate
related: ["[[FFI with C]]", "[[Unsafe Rust]]", "[[unsafe fn]]", "[[Undefined Behavior]]", "[[FFI Wrapper Types]]", "[[SAFETY Comments]]"]
sources: ["[[the-reference]]", "[[the-book]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/external-blocks.html", "https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-extern-functions-to-call-external-code", "https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html"]
rust_version: "edition 2024 / 1.85+"
---

# unsafe extern Blocks

An `unsafe extern` block declares foreign functions or statics and records the author's promise that the ABI, names, types, and safety qualifiers match the external reality.

## What it is
External blocks are declarations for items not defined in the current crate. In
edition 2024, the `unsafe` keyword is semantically required before `extern`
blocks. Earlier editions allowed omitting it, but 2024 makes the obligation
visible at the declaration site.

External blocks may declare functions and statics. The ABI string, such as `"C"`
or `"system"`, describes the low-level calling convention. If no ABI is written,
the block defaults to `"C"`.

## How it works
Items in an `unsafe extern` block are implicitly unsafe unless marked `safe`.
Use `safe fn` only when every possible Rust call satisfying the Rust type signature
is memory-safe. Most pointer-taking C functions remain unsafe because Rust cannot
prove the pointer, length, ownership, and lifetime requirements.

Extern statics are also unsafe to access unless marked `safe`, even if immutable,
because foreign code is responsible for initializing the bytes. Mutating an immutable
extern static after Rust code starts is UB unless mutation is inside `UnsafeCell`.

The block's unsafety is about declaring the signatures correctly. Calling an unsafe
extern item is a separate unsafe operation.

`safe fn` in an extern block is a strong statement: every Rust call that type-checks
must be memory-safe. Pure functions such as `abs(i32) -> i32` can qualify; functions
taking raw pointers, variadic functions, functions depending on global initialization,
or functions that may use thread-local foreign state usually should stay unsafe.

Extern statics deserve the same skepticism. Even an immutable declaration may be
invalid if the foreign side fails to initialize it according to the Rust type, and
mutable extern statics need synchronization just like Rust `static mut`.

## Example
```rust
unsafe extern "C" {
    safe fn abs(input: i32) -> i32;
    unsafe fn strlen(s: *const std::os::raw::c_char) -> usize;
}

fn main() {
    assert_eq!(abs(-4), 4);

    let text = c"rust";
    // SAFETY: text.as_ptr() is a valid NUL-terminated C string.
    let len = unsafe { strlen(text.as_ptr()) };
    assert_eq!(len, 4);
}
```

## Worked example
```rust
use std::os::raw::{c_char, c_int};

unsafe extern "C" {
    safe fn abs(input: c_int) -> c_int;
    unsafe fn puts(s: *const c_char) -> c_int;
}

fn print_line() -> bool {
    let msg = c"hello from C";
    // SAFETY: msg is a live NUL-terminated string for the duration of the call.
    unsafe { puts(msg.as_ptr()) >= 0 }
}

fn main() {
    assert_eq!(abs(-11), 11);
    assert!(print_line());
}
```

The block-level `unsafe` says the declarations were audited against the C headers
and platform ABI. The call to `puts` remains unsafe because Rust cannot prove the
pointer is a valid C string from the function type alone.

## Common errors
In edition 2024, an extern block missing `unsafe` is rejected:

```text
error: extern blocks must be unsafe
```

Fix the declaration to `unsafe extern "C" { ... }`, then classify individual
items with `safe` only after proving that all well-typed Rust calls are sound.
Do not silence this by moving declarations to an older-edition module.

## Best practice
- ✅ Write `unsafe extern "C"` in edition 2024 code and classify each item as `safe` only after audit.
- ✅ Keep declarations close to the module that wraps them, not spread through application code.
- ✅ Prefer generated bindings for large C APIs, then manually review and wrap them.
- ✅ Include ABI, layout, ownership, and thread-safety assumptions in [[SAFETY Comments]] or module docs.
- ✅ Declare variadic C functions as unsafe unless the function cannot inspect the variadic arguments.
- ✅ Use `"system"` for platform APIs whose calling convention differs across targets.

## Pitfalls
- ⚠️ Using `safe fn` because a C function "usually works"; safe means all safe Rust calls are sound.
- ⚠️ Forgetting that extern statics may be invalid or concurrently mutated by foreign code.
- ⚠️ Declaring `extern "C"` when the actual function uses another ABI; wrong ABI is [[Undefined Behavior]].
- ⚠️ Assuming Rust validates declarations against headers or link-time type information.
- ⚠️ Marking a pointer-taking function safe because the pointer is checked for null inside C; Rust may also need lifetime, alignment, aliasing, and initialization guarantees.

## See also
[[FFI with C]] · [[Unsafe Rust]] · [[unsafe fn]] · [[Undefined Behavior]] · [[FFI Wrapper Types]] · [[SAFETY Comments]] · [[Raw Pointers]] · [[The static mut Footgun and &raw]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Reference, "External blocks" — [[the-reference]], https://doc.rust-lang.org/reference/items/external-blocks.html
- The Rust Programming Language, ch. 20.1 "Using extern Functions to Call External Code" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-extern-functions-to-call-external-code
- The Edition Guide, "Unsafe extern blocks" — https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
