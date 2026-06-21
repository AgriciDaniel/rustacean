---
type: moc
title: "Error Handling"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, moc]
domain: "Error Handling"
difficulty: basic
related: ["[[Result]]", "[[panic!]]", "[[The Question Mark Operator]]", "[[The Error Trait]]", "[[Propagating Errors]]", "[[Panicking in Libraries]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-00-error-handling.html", "https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html", "https://doc.rust-lang.org/std/error/trait.Error.html"]
rust_version: "edition 2024 / 1.85+"
---

# Error Handling

Rust error handling is built around `Result` for recoverable failures, `panic!` for broken invariants, and error types that preserve enough information for callers and operators.

## What it is
This MOC links the atomic notes for the Error Handling domain.
Start with [[Recoverable vs Unrecoverable Errors]], then read [[Result]], [[The Question Mark Operator]], and [[panic!]].

The practical center is simple: model expected failure in types, propagate with `?`, add context where it matters, and reserve panics for bugs.

## Concepts
- [[Recoverable vs Unrecoverable Errors]] — the top-level decision between `Result` and panic.
- [[Result]] — the standard recoverable-error enum.
- [[The Question Mark Operator]] — early-return propagation for `Result` and `Option`.
- [[panic!]] — unrecoverable failure and contract violations.
- [[Option vs Result]] — absence versus failure with a reason.
- [[The Error Trait]] — std interoperability for error values.
- [[Custom Error Types]] — typed domain errors for branchable failure.
- [[Error Sources and Chains]] — preserving root causes through `source()`.
- [[Panic Unwinding and Abort]] — what happens after a panic begins.

## Patterns
- [[Propagating Errors]] — return failures upward when the current layer cannot recover.
- [[Returning Result from main]] — use `?` in binaries and exit cleanly.
- [[Error Handling with thiserror]] — derive typed library errors.
- [[Application Errors with anyhow]] — use opaque context-rich errors in applications.
- [[Adding Error Context]] — make failures actionable without losing their sources.
- [[Boxing Errors]] — std-only heterogeneous error return.

## Antipatterns
- [[Unwrap and Expect Overuse]] — accidental panics in recoverable paths.
- [[Stringly-Typed Errors]] — prose instead of structured failure.
- [[Swallowing Errors]] — discarding failure before handling it.
- [[Panicking in Libraries]] — forcing crash policy on callers.

## How it works
The notes are intentionally layered.
The concept notes define the language and standard-library contracts.
The pattern notes show idiomatic ways to structure real code.
The antipattern notes mark the places where Rust code often compiles but loses reliability or caller agency.

## Example
```rust
use std::fs;
use std::io;

fn load_name(path: &str) -> Result<String, io::Error> {
    let name = fs::read_to_string(path)?;
    Ok(name.trim().to_string())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let name = load_name("name.txt")?;
    println!("hello, {name}");
    Ok(())
}
```

## Best practice
- ✅ Use [[Result]] for expected failure and [[panic!]] for violated invariants.
- ✅ Prefer [[The Question Mark Operator]] and [[Propagating Errors]] over nested boilerplate.
- ✅ Use [[Error Handling with thiserror]] when callers need typed variants.
- ✅ Use [[Application Errors with anyhow]] when a binary mostly reports failures.
- ✅ Add [[Adding Error Context]] while preserving [[Error Sources and Chains]].

## Pitfalls
- ⚠️ [[Unwrap and Expect Overuse]] makes recoverable failures crash.
- ⚠️ [[Stringly-Typed Errors]] weakens public APIs.
- ⚠️ [[Swallowing Errors]] destroys diagnostics.
- ⚠️ [[Panicking in Libraries]] takes control away from downstream code.

## See also
[[Recoverable vs Unrecoverable Errors]] · [[Result]] · [[The Question Mark Operator]] · [[panic!]] · [[The Error Trait]] · [[Custom Error Types]] · [[Error Handling with thiserror]] · [[Application Errors with anyhow]]

## Sources
- The Rust Programming Language, ch. 9 "Error Handling" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-00-error-handling.html
- Rust standard library, `std::error::Error` and `std::result` — https://doc.rust-lang.org/std/error/trait.Error.html and https://doc.rust-lang.org/std/result/
