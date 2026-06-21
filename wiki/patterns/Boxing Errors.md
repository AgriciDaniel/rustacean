---
type: pattern
title: "Boxing Errors"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, boxed-error, trait-objects]
domain: "Error Handling"
difficulty: intermediate
related: ["[[The Error Trait]]", "[[Returning Result from main]]", "[[Application Errors with anyhow]]", "[[Custom Error Types]]", "[[Stringly-Typed Errors]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[rust-by-example]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#where-to-use-the--operator", "https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/boxing_errors.html", "https://doc.rust-lang.org/std/error/trait.Error.html"]
rust_version: "edition 2024 / 1.85+"
---

# Boxing Errors

`Box<dyn Error>` is the standard-library way to return heterogeneous error types when callers only need to report them.

## What it is
A boxed error stores any concrete type implementing [[The Error Trait]] behind a trait object.
The common signature is `Result<T, Box<dyn std::error::Error>>`.

This is a dependency-free middle ground between precise [[Custom Error Types]] and [[Application Errors with anyhow]].

## How it works
The standard library provides conversions that let many concrete errors flow into a boxed error with `?`.
A type alias can keep signatures readable.

Use `Box<dyn Error + Send + Sync + 'static>` when the error may cross thread boundaries or be stored in broadly reusable infrastructure.
For public libraries where callers need to match variants, prefer a typed error enum.
The box performs type erasure: the caller can print the error and walk `source()`, but the concrete type is hidden behind dynamic dispatch.
Downcasting is possible only when the concrete type is `'static`, and relying on it as an API contract is brittle.
Boxing does not add context; it only gives different error types one return type.

## Example
```rust
use std::error::Error;
use std::fs;
use std::num::ParseIntError;

type BoxError = Box<dyn Error + Send + Sync + 'static>;

fn read_number(path: &str) -> Result<u32, BoxError> {
    let text = fs::read_to_string(path)?;
    let number: u32 = parse_number(text.trim())?;
    Ok(number)
}

fn parse_number(input: &str) -> Result<u32, ParseIntError> {
    input.parse()
}

fn main() -> Result<(), BoxError> {
    let _ = read_number("number.txt");
    Ok(())
}
```

## Second example
A boxed error works well at a `run` boundary that glues several small helpers together.

```rust
use std::error::Error;
use std::fs;
use std::num::ParseIntError;

type BoxError = Box<dyn Error + Send + Sync + 'static>;

fn parse_limit(text: &str) -> Result<u32, ParseIntError> {
    text.trim().parse()
}

fn run(path: &str) -> Result<u32, BoxError> {
    let text = fs::read_to_string(path)?;
    let limit = parse_limit(&text)?;
    Ok(limit)
}

fn main() {
    let _ = run("limit.txt");
}
```

## Common errors
Threaded or async code may reject a plain boxed error:

```text
error[E0277]: `dyn std::error::Error` cannot be sent between threads safely
```

Fix the alias to `Box<dyn Error + Send + Sync + 'static>` when the error crosses thread or task boundaries.
If the error is part of a public library contract, consider a typed enum instead.

## Best practice
- ✅ Use boxed errors for examples, small binaries, build scripts, prototypes, and glue code.
- ✅ Add `Send + Sync + 'static` when using boxed errors in async or threaded infrastructure.
- ✅ Move to [[Application Errors with anyhow]] when you want ergonomic context and reporting.
- ✅ Move to [[Custom Error Types]] when callers need stable, branchable failure modes.
- ✅ Use a local type alias so signatures reveal intent without repeating trait-object bounds.
- ✅ Add context before boxing if the concrete source message is too low-level.

## Pitfalls
- ⚠️ Public library APIs using boxed errors can force callers into brittle downcasting.
- ⚠️ `Box<dyn Error>` does not automatically add operation context; see [[Adding Error Context]].
- ⚠️ Omitting `Send + Sync` can later block moving errors across threads.
- ⚠️ Boxing a [[Stringly-Typed Errors]] value still leaves it unstructured.
- ⚠️ Treating downcast success as guaranteed can break when an implementation changes its concrete source error.

## See also
[[The Error Trait]] · [[Returning Result from main]] · [[Application Errors with anyhow]] · [[Custom Error Types]] · [[Adding Error Context]] · [[Stringly-Typed Errors]] · [[Propagating Errors]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 `main` returning `Result<(), Box<dyn Error>>` — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#where-to-use-the--operator
- Rust By Example, "Boxing errors" — https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/boxing_errors.html
- Rust standard library, `Error` — https://doc.rust-lang.org/std/error/trait.Error.html
