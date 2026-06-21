---
type: pattern
title: "FFI Wrapper Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ffi, unsafe, pattern]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[FFI with C]]", "[[unsafe extern Blocks]]", "[[Safe Abstractions over Unsafe Code]]", "[[Raw Pointers]]", "[[SAFETY Comments]]", "[[Undefined Behavior]]"]
sources: ["[[rustonomicon]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/nomicon/ffi.html#creating-a-safe-interface", "https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-extern-functions-to-call-external-code", "https://doc.rust-lang.org/reference/items/external-blocks.html"]
rust_version: "edition 2024 / 1.85+"
---

# FFI Wrapper Types

FFI wrapper types hide raw C handles behind Rust ownership, validation, and `Drop` so safe callers cannot misuse the foreign API.

## What it is
Many C APIs expose resources as pointers plus manual create/destroy functions. A Rust
wrapper type turns that protocol into ownership: construction validates the pointer,
methods enforce argument rules, and `Drop` releases the resource exactly once.

This is a specialized form of [[Safe Abstractions over Unsafe Code]]. It narrows the
unsafe surface to the boundary module while giving the rest of the crate a Rust API.

## How it works
Represent the raw handle as a private field, often `NonNull<T>` for non-null opaque
pointers. Make constructors return `Result` or `Option` when C can fail. Implement
`Drop` for cleanup. Add or withhold `Send` and `Sync` based on the C library's actual
thread-safety contract.

Use `PhantomData` or lifetime parameters when the C handle borrows Rust data. Avoid
pretending a borrowed pointer is owned, or that an owned pointer cannot outlive the
C library state it depends on.

A wrapper should also encode thread-safety. Rust will not know whether a C handle
may be sent to another thread or used concurrently. If the raw field prevents auto
traits, add `unsafe impl Send` or `unsafe impl Sync` only when the C documentation
guarantees it; if the handle is thread-affine, keep the type non-`Send` by storing
a marker such as `PhantomData<std::rc::Rc<()>>`.

## Example
```rust
use std::ptr::NonNull;

struct CHandle {
    raw: NonNull<u8>,
}

impl CHandle {
    /// Adopts an owned raw handle.
    ///
    /// # Safety
    ///
    /// `raw` must be either null or an owned handle from the matching C create
    /// function, and this wrapper must become responsible for destroying it.
    unsafe fn from_raw(raw: *mut u8) -> Option<Self> {
        NonNull::new(raw).map(|raw| Self { raw })
    }

    fn as_ptr(&self) -> *mut u8 {
        self.raw.as_ptr()
    }
}

impl Drop for CHandle {
    fn drop(&mut self) {
        // In real FFI, call the matching C destroy function here.
    }
}

fn main() {
    let mut byte = 1_u8;
    // SAFETY: this example's Drop is a no-op; real wrappers should pass only
    // handles returned by the matching C create function.
    let handle = unsafe { CHandle::from_raw(&mut byte) }.unwrap();
    assert_eq!(handle.as_ptr(), &raw mut byte);
}
```

## Worked example
```rust
use std::marker::PhantomData;
use std::ptr::NonNull;
use std::rc::Rc;

struct UiHandle {
    raw: NonNull<u8>,
    _not_send_or_sync: PhantomData<Rc<()>>,
}

impl UiHandle {
    /// Adopts an owned raw UI handle.
    ///
    /// # Safety
    ///
    /// `raw` must be either null or a live handle owned by the current thread.
    unsafe fn from_raw(raw: *mut u8) -> Option<Self> {
        NonNull::new(raw).map(|raw| Self {
            raw,
            _not_send_or_sync: PhantomData,
        })
    }

    fn as_ptr(&self) -> *mut u8 {
        self.raw.as_ptr()
    }
}

fn main() {
    let mut token = 0_u8;
    // SAFETY: token stands in for a live thread-affine handle in this example.
    let handle = unsafe { UiHandle::from_raw(&mut token) }.unwrap();
    assert_eq!(handle.as_ptr(), &raw mut token);
}
```

This models a common GUI or event-loop C handle that must stay on its owning thread.
The marker prevents accidental `Send`/`Sync` auto-trait derivation while the wrapper
still validates nullness and keeps the raw field private.

## Common errors
A frequent design error is exposing `fn destroy(raw: *mut T)` as a safe function.
The compiler cannot prevent double-destroy, destroying a borrowed handle, or using
the handle after destruction.

The fix is an owning wrapper with a private handle and a single `Drop` implementation.
If C can transfer ownership back and forth, model that transfer with consuming
methods such as `into_raw(self)` and unsafe constructors such as `from_owned_raw`.

## Best practice
- ✅ Keep raw extern functions and raw handles private to the FFI module.
- ✅ Use `Drop` for required cleanup and prevent double-free through ownership.
- ✅ Validate null, length, encoding, return-code, and initialization contracts before exposing safe results.
- ✅ Be conservative with `unsafe impl Send` and `unsafe impl Sync`; document the C thread-safety guarantee.
- ✅ Use `NonNull<T>` for non-null handles and `Option<NonNull<T>>` when null is a meaningful state.
- ✅ Provide explicit ownership-transfer methods (`into_raw`, `from_owned_raw`) instead of leaking raw fields.

## Pitfalls
- ⚠️ Exposing a raw destroy function to safe callers and expecting them to call it exactly once.
- ⚠️ Storing Rust references in C without a lifetime or unregister protocol.
- ⚠️ Treating all C pointers as non-null; many APIs use null as an error or optional value.
- ⚠️ Letting a panic unwind through a C callback registered from the wrapper.
- ⚠️ Deriving or manually implementing thread-safety traits based on the Rust wrapper's fields rather than the C library's documented guarantee.

## See also
[[FFI with C]] · [[unsafe extern Blocks]] · [[Safe Abstractions over Unsafe Code]] · [[Raw Pointers]] · [[SAFETY Comments]] · [[Undefined Behavior]] · [[The Drop Trait]] · [[Soundness vs Safety]] · [[Unsafe Rust & FFI]]

## Sources
- The Rustonomicon, "Creating a safe interface" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/ffi.html#creating-a-safe-interface
- The Rust Programming Language, ch. 20.1 "Using extern Functions to Call External Code" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-extern-functions-to-call-external-code
- The Rust Reference, "External blocks" — [[the-reference]], https://doc.rust-lang.org/reference/items/external-blocks.html
