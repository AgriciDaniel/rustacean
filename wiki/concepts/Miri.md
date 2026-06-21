---
type: concept
title: "Miri"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, testing, miri]
domain: "Unsafe Rust & FFI"
difficulty: intermediate
related: ["[[Unsafe Rust]]", "[[Undefined Behavior]]", "[[Raw Pointers]]", "[[Aliasing and Provenance]]", "[[MaybeUninit]]", "[[Safe Abstractions over Unsafe Code]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-miri-to-check-unsafe-code", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html", "https://doc.rust-lang.org/nightly/reference/behavior-considered-undefined.html"]
rust_version: "edition 2024 / 1.85+"
---

# Miri

Miri is Rust's official MIR interpreter for dynamically detecting many forms of undefined behavior in the code paths your tests actually execute.

## What it is
Miri runs Rust programs and tests in an interpreter that checks rules the normal
compiler cannot prove at compile time. It is especially useful for unsafe code
because it can catch dangling pointers, invalid values, misaligned accesses,
some aliasing violations, data races in supported scenarios, and provenance issues.

Miri requires a nightly toolchain component, but using it does not change the Rust
version your crate targets. The Book recommends it as one of the best ways to gain
confidence in unsafe code.

## How it works
Install and run:

```sh
rustup +nightly component add miri
cargo +nightly miri test
```

Miri is dynamic analysis. It checks executed paths, not all possible paths. A green
Miri run is evidence, not a proof of soundness. A Miri failure is strong evidence
that the program performed UB or relied on behavior Miri intentionally rejects.

Miri is particularly valuable for [[Raw Pointers]], [[MaybeUninit]], and
[[Aliasing and Provenance]] because those are the areas where local testing often
appears to work while still violating Rust's memory model.

Because Miri interprets MIR, it is not a replacement for testing the exact native
binary under sanitizers or on target hardware. It intentionally models Rust rules,
not every quirk of an operating system, CPU, allocator, or external C library. For
FFI-heavy code, pair it with wrapper-level Rust tests and separate integration tests
for the foreign library.

## Example
```rust
fn first(values: &[u8]) -> Option<u8> {
    let ptr = values.as_ptr();
    if values.is_empty() {
        None
    } else {
        // SAFETY: non-empty slice makes ptr valid to read one u8.
        Some(unsafe { *ptr })
    }
}

fn main() {
    assert_eq!(first(&[3]), Some(3));
    assert_eq!(first(&[]), None);
}
```

## Worked example
```rust
fn checked_index(values: &[u16], index: usize) -> Option<u16> {
    let ptr = values.as_ptr();
    if index < values.len() {
        // SAFETY: index is within this slice, so add stays in-bounds and points
        // at an initialized u16.
        Some(unsafe { *ptr.add(index) })
    } else {
        None
    }
}

fn main() {
    assert_eq!(checked_index(&[10, 20], 1), Some(20));
    assert_eq!(checked_index(&[10, 20], 2), None);
}
```

This is the kind of tiny unsafe boundary Miri can exercise well. Add tests for
`index == len`, empty slices, and any panic/error cleanup path; Miri only checks
what the test suite executes.

## Common errors
Miri failures are runtime diagnostics rather than rustc error codes. Common messages
refer to undefined behavior caused by an out-of-bounds pointer, use-after-free,
unaligned access, invalid value, or borrow-stack violation.

The usual fix is to reduce the failing unsafe block until the violated precondition
is visible. If Miri warns about integer-to-pointer casts or exposed provenance,
prefer strict-provenance pointer APIs unless the exposed-provenance design is truly
part of the abstraction.

## Best practice
- ✅ Add `cargo +nightly miri test` for crates that contain unsafe code.
- ✅ Write tests that exercise boundary cases: empty slices, null pointers, error paths, panics, and aliasing-sensitive paths.
- ✅ Treat Miri diagnostics as design feedback; shrink unsafe blocks until the failing proof is visible.
- ✅ Pair Miri with sanitizer or platform testing for C FFI, because Miri does not execute arbitrary C libraries normally.
- ✅ Run the same safe wrapper tests under normal `cargo test` and Miri so UB checks cover real API behavior.
- ✅ Use targeted test fixtures for partially initialized values, destructor paths, and callback registration lifetimes.

## Pitfalls
- ⚠️ Assuming Miri proves soundness; it only checks paths that run.
- ⚠️ Skipping tests for panic/error cleanup in partially initialized code.
- ⚠️ Ignoring integer-to-pointer or provenance warnings because the program prints the expected value.
- ⚠️ Relying on Miri for APIs that are mostly exercised by foreign code without a Rust test harness.
- ⚠️ Disabling tests under Miri without recording which external dependency, OS call, or unsupported operation forced the exclusion.

## See also
[[Unsafe Rust]] · [[Undefined Behavior]] · [[Raw Pointers]] · [[Dereferencing Raw Pointers]] · [[Aliasing and Provenance]] · [[MaybeUninit]] · [[Safe Abstractions over Unsafe Code]] · [[SAFETY Comments]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Using Miri to Check Unsafe Code" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-miri-to-check-unsafe-code
- The Rust Reference, nightly "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/nightly/reference/behavior-considered-undefined.html
- The Rust Reference, "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html
