---
type: concept
title: "Unsafe Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, memory, ffi]
domain: "Unsafe Rust & FFI"
difficulty: intermediate
related: ["[[Raw Pointers]]", "[[Dereferencing Raw Pointers]]", "[[unsafe fn]]", "[[Undefined Behavior]]", "[[Soundness vs Safety]]", "[[Safe Abstractions over Unsafe Code]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html", "https://doc.rust-lang.org/reference/unsafety.html", "https://doc.rust-lang.org/nomicon/what-unsafe-does.html"]
rust_version: "edition 2024 / 1.85+"
---

# Unsafe Rust

Unsafe Rust is ordinary Rust plus a small set of operations whose memory-safety obligations the compiler cannot prove; `unsafe` marks where a human proof is required.

## What it is
`unsafe` is not a mode that disables Rust. Type checking, move checking, visibility,
and the borrow checker still apply. The keyword only opens access to operations that
can cause [[Undefined Behavior]] if their contracts are violated.

The Book groups these operations as five unsafe capabilities:

1. Dereference a [[Raw Pointers|raw pointer]].
2. Call an [[unsafe fn]] or unsafe method, including many FFI functions.
3. Access or modify a mutable static variable.
4. Implement an unsafe trait.
5. Access a `union` field.

The Rustonomicon frames the safe/unsafe split around one promise: safe Rust must not
be able to cause UB. Unsafe code exists so Rust can still express low-level systems
work, data structures, hardware access, and [[FFI with C]].

## How it works
There are two different uses of `unsafe`.

An `unsafe fn` or unsafe trait declares a contract the caller or implementor must
uphold. An `unsafe { ... }` block says the author has checked the obligations of
the unsafe operations inside that block.

This distinction matters. A safe function may contain an unsafe block if it can
prove that all callers, using only safe Rust, receive a sound abstraction. A public
`unsafe fn`, by contrast, exposes part of the proof obligation to the caller and
must document that obligation.

In edition 2024, unsafe operations inside an `unsafe fn` still need explicit
`unsafe` blocks under the current idiom and lint expectations. This keeps the actual
operations small and auditable instead of treating the whole function body as trusted.

At compile time, `unsafe` is a marker in the type system and lint system; it is not
a runtime guard. The generated machine code does not remember that a block was
unsafe. The benefit is reviewability: the block tells humans and tooling where
proof obligations such as alignment, initialization, ABI correctness, and aliasing
must be checked.

The important design question is where the proof lives. If the function can check
all preconditions itself, keep the function safe and confine the unsafe operation
inside it. If a required fact is known only to the caller, make the function an
[[unsafe fn]] and document that fact in a `# Safety` section.

## Example
```rust
fn get_or_zero(values: &[u8], index: usize) -> u8 {
    if index < values.len() {
        let ptr = values.as_ptr();
        // SAFETY: index was checked to be in bounds for values.
        unsafe { *ptr.add(index) }
    } else {
        0
    }
}

fn main() {
    let bytes = [10, 20, 30];
    assert_eq!(get_or_zero(&bytes, 1), 20);
    assert_eq!(get_or_zero(&bytes, 99), 0);
}
```

## Worked example
```rust
fn copy_prefix(src: &[u8], dst: &mut [u8], count: usize) -> bool {
    if count > src.len() || count > dst.len() {
        return false;
    }

    // SAFETY: both pointers come from live slices, count was checked against
    // both lengths, and copy_nonoverlapping is valid because &mut dst cannot
    // alias src for mutation through safe Rust at this call site.
    unsafe {
        std::ptr::copy_nonoverlapping(src.as_ptr(), dst.as_mut_ptr(), count);
    }
    true
}

fn main() {
    let src = [1, 2, 3, 4];
    let mut dst = [0; 4];
    assert!(copy_prefix(&src, &mut dst, 3));
    assert_eq!(dst, [1, 2, 3, 0]);
    assert!(!copy_prefix(&src, &mut dst, 9));
}
```

This is a safe abstraction only because the function checks both lengths before
the unsafe copy. If overlap were possible, the operation would need `ptr::copy`
instead of `copy_nonoverlapping`, and the comment would need to name that different
contract.

## Common errors
Trying to perform an unsafe operation outside an unsafe context produces E0133:

```text
error[E0133]: dereference of raw pointer is unsafe and requires unsafe block
```

The fix is not to wrap a large region in `unsafe`. First write the precondition
checks in safe code, then put only the raw dereference, unsafe call, mutable static
access, union field access, or unsafe trait implementation in the unsafe boundary.

## Best practice
- ✅ Treat every `unsafe` as a proof boundary, not as an optimization hint.
- ✅ Keep unsafe blocks as small as the unsafe operation requires; place safe checks outside.
- ✅ Prefer [[Safe Abstractions over Unsafe Code]] so most callers never need `unsafe`.
- ✅ Document each exposed unsafe contract with [[SAFETY Comments]] and a `# Safety` docs section.
- ✅ Turn on `#![deny(unsafe_op_in_unsafe_fn)]` or at least respect the lint in unsafe-heavy crates.
- ✅ Review unsafe code against the exact operation used: dereference, pointer arithmetic, FFI call, static access, or trait implementation each has different obligations.

## Pitfalls
- ⚠️ Assuming `unsafe` disables borrow checking; references inside unsafe code still carry Rust aliasing rules.
- ⚠️ Making a safe function that can be driven to UB by safe inputs; that is an unsound API, not merely an internal bug.
- ⚠️ Using unsafe to bypass an ownership design problem; first consider [[Borrowing]], [[Interior Mutability]], or a different API shape.
- ⚠️ Letting one large unsafe block cover validation, pointer math, and normal logic; it obscures the actual proof.
- ⚠️ Treating a green test run as proof that unsafe code is sound; add adversarial tests and run [[Miri]] where possible.

## See also
[[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[unsafe fn]] · [[Undefined Behavior]] · [[Soundness vs Safety]] · [[Safe Abstractions over Unsafe Code]] · [[SAFETY Comments]] · [[Miri]] · [[FFI with C]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Unsafe Rust" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
- The Rust Reference, "Unsafety" — [[the-reference]], https://doc.rust-lang.org/reference/unsafety.html
- The Rustonomicon, "What Unsafe Rust Can Do" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/what-unsafe-does.html
