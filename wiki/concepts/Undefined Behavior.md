---
type: concept
title: "Undefined Behavior"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, ub, memory]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Soundness vs Safety]]", "[[Raw Pointers]]", "[[Aliasing and Provenance]]", "[[MaybeUninit]]", "[[Miri]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/behavior-considered-undefined.html", "https://doc.rust-lang.org/nomicon/what-unsafe-does.html", "https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html"]
rust_version: "edition 2024 / 1.85+"
---

# Undefined Behavior

Undefined behavior is a violation of Rust's semantic rules that makes the entire program invalid and gives the compiler permission to assume the violation never happens.

## What it is
UB is not a recoverable error, panic, or platform-specific oddity. Rust programs
must never exhibit UB, including inside unsafe blocks and unsafe functions. The
Reference says `unsafe` merely shifts the obligation to the programmer.

The Reference's list includes data races, invalid pointer accesses, broken aliasing,
invalid values, wrong ABIs, unsupported target features, incorrect inline assembly,
and runtime assumption violations such as deallocating a Rust stack frame without
running destructors.

## How it works
The optimizer relies on Rust's rules to transform programs. If unsafe code creates
an invalid `bool`, reads uninitialized memory, aliases an `&mut T`, or calls a
function with the wrong ABI, later optimized code may behave in ways unrelated to
the line where the bug began.

Important categories:

- data races;
- loading from or storing to dangling or misaligned places;
- out-of-bounds place projection;
- breaking aliasing rules for references and boxes;
- mutating immutable bytes outside `UnsafeCell`;
- producing invalid values such as bad `bool`, `char`, `enum`, reference, or `NonNull`;
- wrong call ABI or unwinding across a frame that does not permit it;
- invalid inline assembly or runtime assumption violations.

UB is contagious at the program level. If Rust calls C and the C function performs
C undefined behavior, the mixed program has gone outside the assumptions Rust code
may rely on too. The reverse is also true: Rust UB before or after an FFI call can
invalidate the behavior of surrounding foreign code.

A key review habit is distinguishing UB from other serious bugs. A memory leak,
panic, deadlock, wrong answer, or `Result::Err` is not automatically UB. Unsafe-code
review should name the exact Reference category being avoided; that keeps the proof
from becoming a vague "this seems dangerous" argument.

## Example
```rust
fn checked_first(values: &[u8]) -> Option<u8> {
    if values.is_empty() {
        None
    } else {
        let ptr = values.as_ptr();
        // SAFETY: non-empty slice means ptr is valid to read one initialized u8.
        Some(unsafe { *ptr })
    }
}

fn main() {
    assert_eq!(checked_first(&[1, 2, 3]), Some(1));
    assert_eq!(checked_first(&[]), None);
}
```

## Worked example
```rust
use std::num::NonZeroU8;

fn parse_nonzero(byte: u8) -> Option<NonZeroU8> {
    NonZeroU8::new(byte)
}

fn main() {
    assert_eq!(parse_nonzero(7).map(NonZeroU8::get), Some(7));
    assert!(parse_nonzero(0).is_none());
}
```

This safe version validates a value-level invariant instead of manufacturing a
`NonZeroU8` from raw bits. The same principle applies to `bool`, `char`, Rust enums,
references, `NonNull<T>`, and `str`: creating an invalid value is already UB, even
if later code never appears to use it.

## Common errors
The compiler catches some invalid-value attempts when they are expressed in safe
code, such as out-of-range character literals:

```text
error: invalid unicode character escape
```

Unsafe code can bypass those front doors, so the fix is to validate before calling
`assume_init`, `from_utf8_unchecked`, `new_unchecked`, `transmute`, or FFI wrappers
that claim a Rust type has been produced.

## Best practice
- ✅ Audit unsafe code against the Reference UB categories, not against whether it "works locally."
- ✅ Prefer APIs that make invalid states unrepresentable before any unsafe operation runs.
- ✅ Use [[Miri]] to execute tests under Rust's dynamic UB checks.
- ✅ Treat C UB crossing [[FFI with C|FFI]] as UB for the whole mixed-language program.
- ✅ Separate "could panic" from "could be UB" in reviews; the mitigation and documentation are different.
- ✅ Validate foreign data as bytes or integers before converting it into Rust references, enums, `char`, `bool`, or `str`.

## Pitfalls
- ⚠️ Producing an invalid value and assuming UB occurs only when the value is later inspected.
- ⚠️ Reading uninitialized integers, floats, or raw pointers; these must still be initialized values.
- ⚠️ Calling an FFI function with a signature that is "close enough"; ABI and type mismatches can be UB.
- ⚠️ Assuming deadlocks, leaks, and integer overflow are UB; they may be bugs, but Rust classifies them separately.
- ⚠️ Relying on debug-mode behavior to justify unsafe code; optimizations may exploit UB assumptions in release builds.

## See also
[[Unsafe Rust]] · [[Soundness vs Safety]] · [[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[Aliasing and Provenance]] · [[MaybeUninit]] · [[Transmute as a Shortcut]] · [[Miri]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Reference, "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html
- The Rustonomicon, "What Unsafe Rust Can Do" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/what-unsafe-does.html
- The Rust Programming Language, ch. 20.1 "Unsafe Rust" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
