---
type: concept
title: "Panic Unwinding and Abort"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, panic, unwind, abort]
domain: "Error Handling"
difficulty: advanced
related: ["[[panic!]]", "[[Recoverable vs Unrecoverable Errors]]", "[[Panicking in Libraries]]", "[[Unwrap and Expect Overuse]]", "[[Returning Result from main]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-01-unrecoverable-errors-with-panic.html#unwinding-the-stack-or-aborting-in-response-to-a-panic", "https://doc.rust-lang.org/reference/items/functions.html#unwinding", "https://doc.rust-lang.org/reference/destructors.html#process-termination-without-unwinding"]
rust_version: "edition 2024 / 1.85+"
---

# Panic Unwinding and Abort

Rust panics either unwind the stack and run destructors or abort the process immediately, depending on the panic strategy and ABI boundary.

## What it is
Unwinding means Rust walks back through stack frames after a [[panic!]], dropping values as it leaves each frame.
Aborting means the process terminates without unwinding, leaving cleanup to the operating system.

Cargo profiles can opt into aborting panics with `panic = "abort"`.
Some ABI boundaries also constrain whether unwinding is allowed.

## How it works
The default standard Rust panic strategy is usually unwind, but code should not rely on panic as a normal cleanup path.
The Rust Reference notes that process termination without unwinding does not run destructors.
It also specifies that unwinding across non-unwinding ABI boundaries can abort.
With `panic=unwind`, Rust panics normally run `Drop` as stack frames are exited.
With `panic=abort`, the panic handler terminates the process immediately, so operating-system cleanup happens but Rust destructors do not run.
Across FFI, `"C-unwind"` and other unwind-capable ABI strings are the current way to declare that unwinding may cross the boundary; ordinary `"C"` is non-unwinding.

For ordinary application failures, [[Result]] and [[Returning Result from main]] are clearer and more predictable.

## Example
```rust
struct Guard(&'static str);

impl Drop for Guard {
    fn drop(&mut self) {
        println!("dropping {}", self.0);
    }
}

fn may_panic(should_panic: bool) {
    let _guard = Guard("resource");
    if should_panic {
        panic!("simulated invariant failure");
    }
}

fn main() {
    may_panic(false);
}
```

## Second example
Use `catch_unwind` only when isolating a panic boundary, and require unwind safety.

```rust
use std::panic;

fn run_plugin(callback: impl FnOnce() + panic::UnwindSafe) -> Result<(), &'static str> {
    panic::catch_unwind(callback).map_err(|_| "plugin panicked")
}

fn main() {
    assert_eq!(run_plugin(|| {}).is_ok(), true);
    assert_eq!(run_plugin(|| panic!("boom")), Err("plugin panicked"));
}
```

This does not catch aborting panics, process aborts, or all foreign unwinding cases.
It also does not turn panic into a good library error model; prefer [[Result]] for expected plugin failures.

## Common errors
Relying on unwind cleanup under an aborting profile causes surprises rather than compiler errors:

```text
[profile.release]
panic = "abort"
```

In that profile, `Drop` cleanup after panic is not run.
If cleanup is part of correctness, return `Result` and perform cleanup on ordinary control-flow paths.

## Best practice
- ✅ Treat unwinding as panic behavior, not as a substitute for structured error returns.
- ✅ Use [[Result]] for failures that need cleanup decisions, retries, or user-facing messages.
- ✅ Choose `panic = "abort"` deliberately for binary size, embedded targets, or policy reasons.
- ✅ Be especially careful around FFI boundaries; use unwind-capable ABI strings only when you intend to support unwinding.
- ✅ Put critical cleanup behind explicit success/error paths, not only `Drop` during panic.
- ✅ Document panic strategy assumptions for embedded, plugin, or FFI-heavy binaries.

## Pitfalls
- ⚠️ Assuming destructors always run after panic is wrong with aborting strategies.
- ⚠️ Letting library code panic for expected errors forces downstream users into your panic policy; see [[Panicking in Libraries]].
- ⚠️ Catching panics as business logic obscures the difference between bugs and recoverable failure.
- ⚠️ Crossing FFI boundaries with unwinds you did not design for can abort or be undefined for foreign unwinds.
- ⚠️ `catch_unwind` requires unwind safety and is not a general substitute for validation or typed errors.

## See also
[[panic!]] · [[Recoverable vs Unrecoverable Errors]] · [[Panicking in Libraries]] · [[Returning Result from main]] · [[Result]] · [[The Error Trait]] · [[Unwrap and Expect Overuse]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.1 "Unwinding the Stack or Aborting in Response to a Panic" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-01-unrecoverable-errors-with-panic.html#unwinding-the-stack-or-aborting-in-response-to-a-panic
- The Rust Reference, "Unwinding" and "Process termination without unwinding" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/functions.html#unwinding and https://doc.rust-lang.org/reference/destructors.html#process-termination-without-unwinding
