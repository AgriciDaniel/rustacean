---
type: concept
title: "Panic Strategy Selection"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, panic, no-std, wasm, abort, unwind]
domain: "WebAssembly, no_std & Targets"
difficulty: advanced
related: ["[[Panic Unwinding and Abort]]", "[[panic!]]", "[[no_std Crate Design]]", "[[Rust WebAssembly Targets]]", "[[Panicking in Libraries]]"]
sources: ["[[embedded-book]]", "[[rustc-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/panic.html", "https://doc.rust-lang.org/rustc/codegen-options/index.html#panic", "https://doc.rust-lang.org/stable/embedded-book/start/panicking.html", "https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html#unwinding"]
rust_version: "edition 2024 / 1.85+"
---

# Panic Strategy Selection

Panic strategy selection is the build and runtime policy for what a panic does: unwind and run destructors where supported, abort immediately, or use a `no_std` panic handler chosen by the final artifact.

## What it is
The broader [[Panic Unwinding and Abort]] note explains ordinary panic semantics.
This note focuses on targets where the default is not enough.
Embedded firmware, kernels, `no_std` binaries, wasm modules, and FFI artifacts often need an explicit panic policy.

The Rust Reference says the panic strategy defines the kind of panic behavior a crate is built to support.
The rustc `-C panic` option supports `abort`, `immediate-abort`, and `unwind`.
The default depends on the target.
When linking with `std`, the flag also influences which panic handler is used.
For `no_std` final artifacts, a panic handler is required.

## How it works
In a `std` desktop binary, unwinding is common.
With unwinding, destructors run while stack frames are left.
With aborting, the process terminates and Rust destructors on the panic path do not run.
With `panic = "abort"` in Cargo profiles, binaries often become smaller and panic paths simpler.

In `no_std`, panicking behavior is not supplied by `std`.
The Embedded Rust Book says a `#[panic_handler]` function must appear exactly once in the dependency graph of a final program and has signature `fn(&PanicInfo) -> !`.
Many embedded projects link a panic handler crate such as `panic-halt`, `panic-abort`, `panic-itm`, or `panic-semihosting`.
Check crates.io and docs.rs for current crate versions before adopting one.

For wasm, `wasm32-unknown-unknown` is compiled with `-Cpanic=abort` by default.
The rustc book documents experimental paths for unwinding with rebuilt standard libraries and WebAssembly exception handling, but that is not the default stable deployment path.

## Example
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MathError {
    DivisionByZero,
}

pub fn checked_ratio(numerator: u32, denominator: u32) -> Result<u32, MathError> {
    if denominator == 0 {
        return Err(MathError::DivisionByZero);
    }
    Ok(numerator / denominator)
}

fn main() {
    assert_eq!(checked_ratio(8, 2), Ok(4));
    assert_eq!(checked_ratio(8, 0), Err(MathError::DivisionByZero));
}
```

The most portable panic strategy is often to avoid panicking for expected failures.
Return [[Result]] for inputs the caller can handle.

## Edge case
```rust
#[cfg(any(target_os = "none", target_family = "wasm"))]
pub fn panic_policy_hint() -> &'static str {
    "choose abort, halt, trap, or target-specific reporting deliberately"
}

#[cfg(not(any(target_os = "none", target_family = "wasm")))]
pub fn panic_policy_hint() -> &'static str {
    "std target: profile panic setting and FFI boundaries still matter"
}

fn main() {
    println!("{}", panic_policy_hint());
}
```

This compiles everywhere and keeps panic policy visible near target policy.

## Best practice
- ✅ Use [[Result]] for recoverable errors and reserve panic for bugs or violated invariants.
- ✅ Set `panic = "abort"` in profiles only when binary size, target support, or policy calls for it.
- ✅ Put exactly one `#[panic_handler]` in a `no_std` final program, never in a general library.
- ✅ Document wasm panic behavior for JS callers because abort/trap is not a typed Rust error.
- ✅ Use different panic handler crates by profile only when that is intentional and documented.
- ✅ Verify current panic handler crate versions on docs.rs or crates.io before pinning them.

## Pitfalls
- ⚠️ Assuming destructors run during panic on an aborting target.
- ⚠️ Letting a library impose a panic handler on downstream binaries.
- ⚠️ Expecting `catch_unwind` to work when the binary is built with aborting panics.
- ⚠️ Treating wasm unwinding as a default stable assumption.
- ⚠️ Panicking for expected API errors; see [[Panicking in Libraries]].

## See also
[[Panic Unwinding and Abort]]
[[panic!]]
[[Panicking in Libraries]]
[[Recoverable vs Unrecoverable Errors]]
[[Returning Result from main]]
[[no_std Crate Design]]
[[Rust WebAssembly Targets]]
[[Cargo Cross-Compilation Setup]]
[[Target-Specific cfg Boundaries]]
[[WebAssembly, no_std & Targets]]

## Sources
- The Rust Reference, "Panic" - [[the-reference]],
  https://doc.rust-lang.org/reference/panic.html
- The rustc book, `-C panic` - [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html#panic
- The Embedded Rust Book, "Panicking" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/panicking.html
- The rustc book, wasm unwinding - [[rustc-book]],
  https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html#unwinding
