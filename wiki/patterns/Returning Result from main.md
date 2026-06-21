---
type: pattern
title: "Returning Result from main"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, main, result, cli]
domain: "Error Handling"
difficulty: basic
related: ["[[Result]]", "[[The Question Mark Operator]]", "[[Propagating Errors]]", "[[Boxing Errors]]", "[[Application Errors with anyhow]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#where-to-use-the--operator", "https://doc.rust-lang.org/std/process/trait.Termination.html", "https://doc.rust-lang.org/std/error/trait.Error.html"]
rust_version: "edition 2024 / 1.85+"
---

# Returning Result from main

`main` can return `Result<(), E>`, which lets command-line programs use `?` at the top level and exit nonzero on error.

## What it is
Rust's `main` is allowed to return types that implement `std::process::Termination`.
`Result<(), E>` is the common choice for fallible binaries.

This pattern avoids a top-level nest of `match` statements and keeps [[The Question Mark Operator]] available.

## How it works
When `main` returns `Ok(())`, the program exits successfully.
When `main` returns `Err(error)`, Rust reports the error and exits with failure.

For std-only code, `Box<dyn std::error::Error>` is a convenient error type.
For applications with richer context, prefer [[Application Errors with anyhow]].
The standard library routes the returned value through `std::process::Termination`.
`Result<(), E>` works when `E: Debug`, which is why top-level errors may be printed with debug-style formatting.
If you need polished CLI output, custom exit codes, or logging setup, put the fallible work in `run()` and keep `main` responsible for presentation.

## Example
```rust
use std::error::Error;
use std::fs;

fn main() -> Result<(), Box<dyn Error>> {
    let manifest = fs::read_to_string("Cargo.toml")?;
    println!("manifest has {} bytes", manifest.len());
    Ok(())
}
```

## Second example
Separate `run` from `main` when the binary needs a custom message or exit code.

```rust
use std::error::Error;
use std::fs;
use std::process::ExitCode;

fn run() -> Result<(), Box<dyn Error>> {
    let manifest = fs::read_to_string("Cargo.toml")?;
    println!("manifest has {} bytes", manifest.len());
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("error: {error}");
            ExitCode::FAILURE
        }
    }
}
```

## Common errors
Using `?` directly in plain `main` produces:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`
```

Fix it with `fn main() -> Result<(), E>` for simple programs, or move the work into `run() -> Result<(), E>` and handle the error in `main`.

## Best practice
- ✅ Return `Result<(), E>` from small binaries and examples that perform fallible setup.
- ✅ Use [[Boxing Errors]] for dependency-free prototypes or [[Application Errors with anyhow]] for real application context.
- ✅ Keep core logic in a separate `run() -> Result<(), E>` when `main` must do reporting or exit-code mapping.
- ✅ Prefer `?` over top-level `unwrap` so failures become normal process errors, not panics.
- ✅ Add context before errors reach `main`, because `main` usually knows too little about the failed operation.
- ✅ Use `ExitCode` when different classes of failure need different process statuses.

## Pitfalls
- ⚠️ `fn main() { fallible()? }` does not compile because `main` returns `()`.
- ⚠️ `unwrap` in `main` prints panic diagnostics instead of clean application errors; see [[Unwrap and Expect Overuse]].
- ⚠️ `Box<dyn Error>` is convenient but can be too opaque for library APIs; see [[Boxing Errors]].
- ⚠️ Returning `Result` from `main` is not a substitute for adding context to low-level errors.
- ⚠️ Assuming the default `Result` termination output is your final UX can leave users with `Os { code: ... }` diagnostics.

## See also
[[Result]] · [[The Question Mark Operator]] · [[Propagating Errors]] · [[Boxing Errors]] · [[Application Errors with anyhow]] · [[Adding Error Context]] · [[Unwrap and Expect Overuse]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "Where to Use the `?` Operator" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#where-to-use-the--operator
- Rust standard library, `Termination` — https://doc.rust-lang.org/std/process/trait.Termination.html
