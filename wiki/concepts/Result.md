---
type: concept
title: "Result"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, result, errors, enum]
domain: "Error Handling"
difficulty: basic
related: ["[[Recoverable vs Unrecoverable Errors]]", "[[The Question Mark Operator]]", "[[Propagating Errors]]", "[[Custom Error Types]]", "[[Option vs Result]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html", "https://doc.rust-lang.org/std/result/enum.Result.html", "https://doc.rust-lang.org/std/result/"]
rust_version: "edition 2024 / 1.85+"
---

# Result

`Result<T, E>` is Rust's standard enum for fallible operations: `Ok(T)` carries success, and `Err(E)` carries a recoverable failure.

## What it is
`Result` is defined conceptually as:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

The success type `T` and error type `E` are both explicit, so a function signature says both what it returns and how it can fail.
This makes error handling visible at compile time instead of implicit in exceptions.

## How it works
Callers usually handle a `Result` by matching, transforming it with combinators, or propagating it with [[The Question Mark Operator]].
The compiler warns when a `Result` is ignored because `Result` is marked `#[must_use]`.

The error type should be chosen for the caller.
Use a precise enum from [[Custom Error Types]] when callers need to branch, or an opaque application error from [[Application Errors with anyhow]] when the program only needs to report and exit.
`Result` is an ordinary enum, so matching consumes it by default.
Use `.as_ref()` or `.as_mut()` when you want to inspect or transform borrowed contents without moving owned success or error values.
Combinators such as `map`, `map_err`, `and_then`, and `or_else` are just structured ways to match one side while leaving the other side untouched.

## Example
```rust
fn reciprocal(n: i32) -> Result<f64, &'static str> {
    if n == 0 {
        Err("cannot divide by zero")
    } else {
        Ok(1.0 / f64::from(n))
    }
}

fn main() {
    match reciprocal(4) {
        Ok(value) => println!("{value}"),
        Err(error) => eprintln!("error: {error}"),
    }

    assert_eq!(reciprocal(0), Err("cannot divide by zero"));
}
```

## Second example
Use `map_err` when the current layer can add a better error type without losing the underlying cause.

```rust
use std::num::ParseIntError;

#[derive(Debug)]
enum CountError {
    Parse(ParseIntError),
    TooLarge(u32),
}

fn parse_count(input: &str) -> Result<u32, CountError> {
    let count = input.parse::<u32>().map_err(CountError::Parse)?;
    if count > 100 {
        return Err(CountError::TooLarge(count));
    }
    Ok(count)
}

fn main() {
    assert!(matches!(parse_count("101"), Err(CountError::TooLarge(101))));
}
```

## Common errors
Ignoring a `Result` triggers the `unused_must_use` lint:

```text
warning: unused `Result` that must be used
```

Fix it by handling the value, propagating it with `?`, or explicitly documenting a safe discard with a targeted pattern.
`let _ = fallible();` should be rare because it hides the decision from reviewers and future maintainers.

## Best practice
- ✅ Use `Result<T, E>` for expected failure, especially in public APIs and IO-heavy code.
- ✅ Pick an error type that preserves useful information; see [[The Error Trait]] and [[Custom Error Types]].
- ✅ Prefer `?` over repetitive `match` when the current function should propagate the error.
- ✅ Match explicitly when the current function can recover differently from different failures.
- ✅ Use `as_ref()` before inspecting a `Result<String, E>` if you still need the owned value afterward.
- ✅ Use `map_err` for local conversion and `From` for conversion that should be reusable by `?`.

## Pitfalls
- ⚠️ Calling `.unwrap()` everywhere converts recoverable errors into panics; see [[Unwrap and Expect Overuse]].
- ⚠️ Using `Result<T, String>` in public APIs discards structured information; see [[Stringly-Typed Errors]].
- ⚠️ Ignoring `Result` with `let _ = ...` can lose important failures; see [[Swallowing Errors]].
- ⚠️ Returning one giant enum with irrelevant variants can expose implementation detail instead of caller intent.
- ⚠️ Calling `.ok()` too early converts every failure into `None`; make sure [[Option vs Result]] says that is the right abstraction.

## See also
[[Recoverable vs Unrecoverable Errors]] · [[The Question Mark Operator]] · [[Propagating Errors]] · [[Returning Result from main]] · [[Option vs Result]] · [[Custom Error Types]] · [[The Error Trait]] · [[Swallowing Errors]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "Recoverable Errors with `Result`" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html
- Rust standard library, `Result` — https://doc.rust-lang.org/std/result/enum.Result.html
