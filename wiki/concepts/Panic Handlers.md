---
type: concept
title: "Panic Handlers"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, panic, no-std, embedded, wasm]
domain: "WebAssembly, no_std & Targets"
difficulty: advanced
related: ["[[Panic Strategy Selection]]", "[[Panic Unwinding and Abort]]", "[[panic!]]", "[[no_std Crate Design]]", "[[Global Allocators]]", "[[Panicking in Libraries]]"]
sources: ["[[the-reference]]", "[[embedded-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/reference/panic.html#the-panic_handler-attribute", "https://doc.rust-lang.org/stable/embedded-book/start/panicking.html", "https://doc.rust-lang.org/std/panic/fn.set_hook.html", "https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/template-deep-dive/src-utils-rs.html", "https://docs.rs/console_error_panic_hook/latest/console_error_panic_hook/"]
rust_version: "edition 2024 / 1.85+"
---

# Panic Handlers

A panic handler is the one function in a `no_std` final artifact that defines what happens after `panic!`; it has signature `fn(&PanicInfo) -> !` and must be chosen by the final program, not by ordinary libraries.

## What it is
Panicking is Rust's built-in path for unrecoverable errors such as violated invariants, failed assertions, and some bounds checks.
On normal `std` targets, the standard library supplies panic behavior.
Depending on the [[Panic Strategy Selection]], that behavior unwinds or aborts.

In `no_std` final artifacts, `std` is not present to provide that runtime behavior.
The Rust Reference says `#[panic_handler]` defines panic behavior and may only be applied to a function with signature `fn(&PanicInfo) -> !`.
It also says there must be a single panic handler function in the dependency graph.
The Embedded Rust Book states the same operational rule for programs without the standard library.

`PanicInfo` carries information such as the panic message and location.
The handler returns `!` because panicking does not resume normal control flow from that point.
A handler might halt, reset, trap, blink an LED, log over a debug channel, abort, or enter a target-specific safe state.

This is different from a `std` panic hook.
`std::panic::set_hook` runs before the standard panic runtime continues.
It is useful for diagnostics on hosted or wasm-with-std targets, but it is not a `#[panic_handler]` replacement for all-`no_std` binaries.

## How it works
The final linked artifact owns panic policy.
A bare-metal firmware binary may link a panic handler crate or define a local handler.
A reusable driver, parser, or protocol library should not provide one, because that would force every downstream final binary into the same panic behavior.

The handler should do very little.
It runs after an unrecoverable path has already started.
Many targets cannot safely allocate, take locks, access complex peripherals, or rely on interrupts during panic.
If the handler logs, the logging path should be bounded and target-specific.
If it cannot log safely, a tight halt loop is often clearer than a clever but fragile path.

Allocation failure can also reach panic policy.
The standard allocation error path diverges.
On all-`no_std` binaries, `handle_alloc_error` calls `panic!`, so the configured panic handler applies to OOM behavior too.
That makes [[Global Allocators]] and panic policy part of the same final-artifact design.

For wasm, many Rust projects use a hosted panic hook for better browser or Node diagnostics.
The RustWasm wasm-pack template page is from a legacy docs domain, but it shows the common pattern of calling `console_error_panic_hook::set_once()` behind a Cargo feature so panics are reported through `console.error`.
As verified on 2026-06-21, docs.rs reports `console_error_panic_hook` latest as `0.1.7`; verify the latest version and maintenance status before pinning it.

## Example
```rust
#![no_std]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {
        core::hint::spin_loop();
    }
}
```

This is the minimal shape of a `no_std` panic handler.
Real firmware might replace the loop body with a target halt instruction, watchdog reset, debug breakpoint, or carefully reviewed logging path.

## Hosted wasm diagnostic hook
```rust
pub fn checked_index(values: &[u8], index: usize) -> Option<u8> {
    values.get(index).copied()
}

fn main() {
    assert_eq!(checked_index(&[10, 20, 30], 1), Some(20));
    assert_eq!(checked_index(&[10, 20, 30], 5), None);
}
```

The portable API avoids panic for expected out-of-range input.
In a wasm-bindgen package, a separate initialization function may install `console_error_panic_hook` for debugging unexpected panics.
That hook is a `std` panic hook, not the same mechanism as `#[panic_handler]`.

## Best practice
- ✅ Put exactly one `#[panic_handler]` in a `no_std` final artifact or link exactly one panic-handler crate.
- ✅ Keep reusable libraries free of panic handlers; return [[Result]] or [[Option]] for expected failures.
- ✅ Make the handler divergent and simple: halt, abort, reset, trap, or use a proven target logging path.
- ✅ Decide debug versus release behavior intentionally, such as logging in debug and halting or resetting in release.
- ✅ Treat allocation failure policy, panic strategy, and panic handler behavior as one design surface.
- ✅ Use `std::panic::set_hook` or `console_error_panic_hook` only when `std` panic hooks are available for that target setup.
- ✅ Verify docs.rs latest versions for panic-handler and wasm diagnostic crates before adopting them.
- ✅ Document what operators or developers can observe after panic: debugger halt, LED code, console message, trap, or reset.

## Pitfalls
- ⚠️ Defining a panic handler in a library creates duplicate-handler conflicts or forces downstream policy.
- ⚠️ Confusing `std::panic::set_hook` with `#[panic_handler]`; hooks decorate `std` panic behavior, handlers define missing `no_std` behavior.
- ⚠️ Allocating or formatting heavily inside a panic handler can recurse into [[Global Allocators]] and fail again.
- ⚠️ Assuming destructors run on every panic; aborting handlers and some targets do not unwind.
- ⚠️ Expecting wasm panics to become typed JavaScript exceptions without designing that boundary explicitly.
- ⚠️ Using panic for routine input validation in libraries; see [[Panicking in Libraries]].
- ⚠️ Linking two panic-handler crates at once causes duplicate `panic_impl` style errors.
- ⚠️ Leaving panic behavior implicit in firmware makes field failures much harder to diagnose.

## See also
[[Panic Strategy Selection]]
[[Panic Unwinding and Abort]]
[[panic!]]
[[Panicking in Libraries]]
[[Recoverable vs Unrecoverable Errors]]
[[no_std Crate Design]]
[[Global Allocators]]
[[Using alloc without std]]
[[Rust WebAssembly Targets]]
[[wasm-bindgen Basics]]
[[Bare-Metal Programming]]
[[WebAssembly, no_std & Targets]]

## Sources
- The Rust Reference, "`panic_handler` attribute" - [[the-reference]],
  https://doc.rust-lang.org/reference/panic.html#the-panic_handler-attribute
- The Embedded Rust Book, "Panicking" - [[embedded-book]],
  https://doc.rust-lang.org/stable/embedded-book/start/panicking.html
- Rust standard library, `std::panic::set_hook` - [[std]],
  https://doc.rust-lang.org/std/panic/fn.set_hook.html
- RustWasm wasm-pack docs, `src/utils.rs` panic hook setup - verify current template guidance before copying,
  https://rustwasm.github.io/docs/wasm-pack/tutorials/npm-browser-packages/template-deep-dive/src-utils-rs.html
- `console_error_panic_hook` crate documentation, verify latest version before pinning,
  https://docs.rs/console_error_panic_hook/latest/console_error_panic_hook/
