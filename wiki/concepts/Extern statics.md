---
type: concept
title: "Extern statics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, ffi, extern, statics]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[unsafe extern Blocks]]", "[[FFI with C]]", "[[Static Items]]", "[[The static mut Footgun and &raw]]", "[[Undefined Behavior]]", "[[Raw Pointers]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]", "[[06-unsafe-and-ffi]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/external-blocks.html", "https://doc.rust-lang.org/reference/items/static-items.html", "https://doc.rust-lang.org/nomicon/ffi.html"]
rust_version: "edition 2024 / 1.85+"
---

# Extern statics

Extern statics declare global variables defined outside the current Rust crate; accessing them is unsafe by default because Rust cannot verify the foreign symbol's initialization, type validity, aliasing, or mutation discipline.

## What it is
An `extern` block declares items that Rust will link to but does not define in the current crate.
Inside an external block, Rust permits declarations of functions and statics.
An extern static is the static-variable half of [[FFI with C]].

In edition 2024, external blocks must be written as `unsafe extern`.
That `unsafe` belongs to the declaration block, not to every access.
It records that the author of the declaration has checked the foreign ABI, symbol name, type, mutability, and safety contract.

Extern statics can be immutable:

```rust
unsafe extern "C" {
    static VERSION: i32;
}
```

or mutable:

```rust
unsafe extern "C" {
    static mut GLOBAL_STATE: i32;
}
```

Unless an extern static is explicitly qualified as `safe`, accessing it is an unsafe operation.
This is true even for immutable extern statics.
The compiler cannot prove that arbitrary foreign code initialized the object before Rust ran, used a bit pattern valid for the declared Rust type, and will not mutate it after Rust begins.

## How it works
An extern static declaration creates a name in Rust's value namespace and tells the linker which external symbol should satisfy it.
The declaration has no initializer.
The storage belongs to some other object file, shared library, runtime, or exported symbol.

For immutable extern statics, the Reference requires the static to be initialized before any Rust code executes.
It is not enough for a foreign library to initialize it just before Rust reads it.
Once Rust code is running, mutating an immutable static from Rust or from foreign code is [[Undefined Behavior]], except for bytes inside an `UnsafeCell`.

For mutable extern statics, all reads and writes are unsafe.
A mutable foreign global has the same high-level hazards as Rust `static mut`, plus FFI-specific hazards:

- other languages may read or write it without Rust's aliasing rules;
- multiple threads may race on it unless the foreign API documents synchronization;
- a pointer stored in it may dangle after a Rust temporary is dropped;
- the declared Rust type may not match the actual C type or alignment.

Edition 2024 also makes accidental references to mutable statics more visible.
Prefer raw pointers with `&raw const` or `&raw mut` when the contract really needs an address, and prefer wrapper functions that copy scalar values in and out instead of exposing a global variable directly.
See [[The static mut Footgun and &raw]] for the Rust-side version of that rule.

External block items can be marked `safe` when the declaration itself is enough to make access safe for all callers.
Use that sparingly.
If a global can change behind Rust's back, has platform-specific initialization timing, or requires a lock, it should remain unsafe or be hidden behind a safe wrapper that enforces the contract.

## Example
```rust
#[unsafe(export_name = "RUST_FFI_ANSWER")]
pub static EXPORTED_ANSWER: i32 = 42;

unsafe extern "C" {
    #[link_name = "RUST_FFI_ANSWER"]
    safe static ANSWER_FROM_EXTERN: i32;
}

fn answer() -> i32 {
    ANSWER_FROM_EXTERN
}

fn main() {
    assert_eq!(answer(), 42);
}
```

The example is self-contained so it compiles without a C library.
Real FFI code usually gets the symbol from a native library through `#[link(name = "...")]`, a build script, or platform system libraries.
The important current-edition shape is the same: `unsafe extern "C"` declares the foreign item, and `safe static` is only used when ordinary Rust access is genuinely safe.

## Best practice
- ✅ Treat extern static declarations as unsafe API design, not as mechanical translations from headers.
- ✅ Verify the exact C type, alignment, mutability, symbol name, initialization order, and thread-safety contract.
- ✅ Use `unsafe extern "C"` in edition 2024 code and put item-level `safe` only on globals that are safe to read from any safe Rust caller.
- ✅ Prefer immutable extern statics or foreign accessor functions over mutable foreign globals.
- ✅ Wrap mutable extern globals in a small Rust API that documents synchronization and lifetime requirements.
- ✅ Copy scalar values out promptly; avoid handing out references to foreign global storage.
- ✅ Use `&raw const` or `&raw mut` for addresses of mutable statics instead of forming Rust references.
- ✅ Keep C strings, buffers, and callback pointers alive for as long as the foreign global can observe them.

## Pitfalls
- ⚠️ Declaring an unsafe global as `safe static` shifts a foreign invariant into safe Rust and can make the wrapper unsound.
- ⚠️ An immutable extern static is not safe merely because it lacks `mut`; foreign initialization and mutation still matter.
- ⚠️ A Rust type mismatch with the actual C object can cause invalid values, misalignment, or ABI breakage.
- ⚠️ Reading or writing a mutable extern static concurrently without synchronization can be a data race.
- ⚠️ Storing `CString::as_ptr()` or stack addresses in a foreign global after the owner drops creates dangling pointers.
- ⚠️ Creating `&T` or `&mut T` to mutable global storage can violate aliasing; use raw pointers and narrow unsafe blocks.
- ⚠️ Link attributes solve symbol lookup, not safety. The declared type and foreign contract still have to be correct.

## See also
[[unsafe extern Blocks]] · [[FFI with C]] · [[Static Items]] · [[The static mut Footgun and &raw]] ·
[[Undefined Behavior]] · [[Raw Pointers]] · [[Aliasing and Provenance]] · [[Safe Abstractions over Unsafe Code]] ·
[[SAFETY Comments]] · [[Unsafe Rust]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Reference, "External blocks / Statics" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/external-blocks.html
- The Rust Reference, "Static items" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/static-items.html
- The Rustonomicon, "FFI / Accessing foreign globals" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/ffi.html
- Research report, "Unsafe Rust and FFI" — [[06-unsafe-and-ffi]]
