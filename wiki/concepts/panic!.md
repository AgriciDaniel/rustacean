---
type: concept
title: "panic!"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, panic, errors, invariants]
domain: "Error Handling"
difficulty: basic
related: ["[[Recoverable vs Unrecoverable Errors]]", "[[Panic Unwinding and Abort]]", "[[Unwrap and Expect Overuse]]", "[[Panicking in Libraries]]", "[[Result]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-01-unrecoverable-errors-with-panic.html", "https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html", "https://doc.rust-lang.org/std/macro.panic.html"]
rust_version: "edition 2024 / 1.85+"
---

# panic!

`panic!` signals an unrecoverable bug or violated contract and stops normal execution instead of returning a recoverable error.

## What it is
`panic!` is a macro for entering Rust's panic path.
It is appropriate when the program is in a state where continuing would be incorrect, unsafe, or misleading.

Common panics include explicit `panic!`, failed `assert!`, indexing out of bounds, and `unwrap` or `expect` on an `Err` or `None`.

## How it works
By default, a panic prints a message and location, unwinds the stack, runs destructors for frames it exits, and terminates the thread or process if uncaught.
With `panic = "abort"`, the process exits immediately without stack unwinding.
Use `RUST_BACKTRACE=1` to request a backtrace when diagnosing a panic.

`panic!` is not Rust's general error mechanism.
For normal failure, return [[Result]] and let the caller decide.
`assert!`, `assert_eq!`, `todo!`, `unimplemented!`, indexing out of bounds, and `unwrap`/`expect` all use the same panic mechanism.
Only unwinding panics can be caught with `std::panic::catch_unwind`, and even then catching is intended for isolation boundaries, not ordinary control flow.
Code must not rely on destructors after panic when the binary may be built with aborting panics.

## Example
```rust
pub struct Percent(u8);

impl Percent {
    pub fn new(value: u8) -> Self {
        assert!(value <= 100, "percentage must be <= 100, got {value}");
        Self(value)
    }

    pub fn get(self) -> u8 {
        self.0
    }
}

fn main() {
    let loaded = Percent::new(42);
    assert_eq!(loaded.get(), 42);
}
```

## Second example
Prefer a fallible constructor when invalid data is expected from outside the program.

```rust
#[derive(Debug, PartialEq, Eq)]
pub struct Percent(u8);

#[derive(Debug, PartialEq, Eq)]
pub struct PercentError {
    value: u8,
}

impl Percent {
    pub fn try_new(value: u8) -> Result<Self, PercentError> {
        if value <= 100 {
            Ok(Self(value))
        } else {
            Err(PercentError { value })
        }
    }
}

fn main() {
    assert!(Percent::try_new(101).is_err());
}
```

## Common errors
The usual failure is a runtime panic, not a compiler error:

```text
thread 'main' panicked at 'percentage must be <= 100, got 150', src/main.rs:5:9
```

Fix the API if the input is external: return `Result` or `Option`.
Keep the panic only when a correct caller should have upheld the documented precondition.

## Best practice
- ✅ Panic for contract violations that represent caller bugs, especially when continuing would be harmful.
- ✅ Prefer `assert!` or `debug_assert!` when checking invariants; they communicate intent better than a bare `panic!`.
- ✅ Explain public panics in documentation and make valid states easy to construct correctly.
- ✅ Use `expect("reason")` only when you have more information than the compiler and the reason is stable.
- ✅ Use `RUST_BACKTRACE=1` or `RUST_BACKTRACE=full` while diagnosing unexpected panics.
- ✅ Treat `catch_unwind` as a containment tool for plugin/test/FFI-like boundaries, not as normal error handling.

## Pitfalls
- ⚠️ Panicking for missing files, bad input, or network failures removes caller choice; see [[Panicking in Libraries]].
- ⚠️ `.unwrap()` hides the invariant being relied on; see [[Unwrap and Expect Overuse]].
- ⚠️ Assuming all destructors run during panic is wrong under aborting strategies; see [[Panic Unwinding and Abort]].
- ⚠️ Catching panics as routine control flow fights the language design.
- ⚠️ Panic messages that include secrets, tokens, or credentials can leak into logs and crash reports.

## See also
[[Recoverable vs Unrecoverable Errors]] · [[Panic Unwinding and Abort]] · [[Result]] · [[Unwrap and Expect Overuse]] · [[Panicking in Libraries]] · [[Returning Result from main]] · [[Propagating Errors]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.1 "Unrecoverable Errors with `panic!`" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-01-unrecoverable-errors-with-panic.html
- The Rust Programming Language, ch. 9.3 "To `panic!` or Not to `panic!`" — https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html
- Rust standard library, `panic!` macro — https://doc.rust-lang.org/std/macro.panic.html
