---
type: concept
title: "Custom Error Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, enums, api-design]
domain: "Error Handling"
difficulty: intermediate
related: ["[[The Error Trait]]", "[[Result]]", "[[Error Handling with thiserror]]", "[[Stringly-Typed Errors]]", "[[Error Sources and Chains]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]", "[[thiserror]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html", "https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/convert/trait.From.html"]
rust_version: "edition 2024 / 1.85+"
---

# Custom Error Types

A custom error type names the ways an operation can fail and preserves the information callers need to handle or report those failures.

## What it is
Custom errors are usually enums for multiple failure modes or structs for one failure mode with fields.
They are the typed alternative to [[Stringly-Typed Errors]].

For public APIs, a custom type says: these are the failures this abstraction exposes.
For internal code, it gives [[The Question Mark Operator]] a target type for conversion.

## How it works
A complete custom error generally implements `Debug`, `Display`, and [[The Error Trait]].
It may also implement `From<SourceError>` so `?` can convert lower-level errors into the custom type.
The [[Error Handling with thiserror]] pattern derives most of that boilerplate.

Design variants around caller action, not every private helper that happened to fail.
If callers cannot do anything different, prefer [[Adding Error Context]] and an opaque application error.
The shape of the error type is part of the public contract.
Enum variants are easy for callers to match, but adding or removing public variants can affect downstream code.
Use `#[non_exhaustive]` for public enums when you expect to add variants without forcing a major redesign of caller matches.

## Example
```rust
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
enum PortError {
    Parse(ParseIntError),
    Zero,
}

impl fmt::Display for PortError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Parse(_) => write!(f, "port is not a number"),
            Self::Zero => write!(f, "port must be nonzero"),
        }
    }
}

impl Error for PortError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Parse(error) => Some(error),
            Self::Zero => None,
        }
    }
}

impl From<ParseIntError> for PortError {
    fn from(error: ParseIntError) -> Self {
        Self::Parse(error)
    }
}

fn parse_port(input: &str) -> Result<u16, PortError> {
    let port = input.parse::<u16>()?;
    if port == 0 { Err(PortError::Zero) } else { Ok(port) }
}

fn main() {
    assert!(matches!(parse_port("0"), Err(PortError::Zero)));
}
```

## Second example
A struct error is often clearer when there is one failure mode with useful fields.

```rust
use std::error::Error;
use std::fmt;

#[derive(Debug)]
struct RangeError {
    field: &'static str,
    min: u32,
    max: u32,
    actual: u32,
}

impl fmt::Display for RangeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} must be between {} and {}", self.field, self.min, self.max)
    }
}

impl Error for RangeError {}

fn validate_retries(actual: u32) -> Result<u32, RangeError> {
    if (1..=10).contains(&actual) {
        Ok(actual)
    } else {
        Err(RangeError { field: "retries", min: 1, max: 10, actual })
    }
}

fn main() {
    let error = validate_retries(99).unwrap_err();
    assert_eq!(error.actual, 99);
}
```

## Common errors
Using `?` without a conversion into your custom error produces:

```text
error[E0277]: `?` couldn't convert the error to `PortError`
```

Fix it by implementing `From<SourceError> for PortError`, using `map_err`, or changing the function's error type.
Do not add a broad conversion unless the resulting variant accurately represents the source failure.

## Best practice
- ✅ Expose variants that callers can meaningfully match on.
- ✅ Preserve lower-level causes through `source()` or `#[source]`.
- ✅ Implement `From` only for conversions that are semantically lossless enough for `?`.
- ✅ Use [[Error Handling with thiserror]] for production code unless handwritten impls are clearer.
- ✅ Use fields for actionable data such as path, key, status code, or offending value.
- ✅ Consider `#[non_exhaustive]` for public error enums whose variant set may grow.

## Pitfalls
- ⚠️ One variant per internal call site creates a brittle "ball of mud" API.
- ⚠️ Returning `String` loses type information and chains; see [[Stringly-Typed Errors]].
- ⚠️ Hiding all detail behind `Box<dyn Error>` can make library errors hard to handle; see [[Boxing Errors]].
- ⚠️ Forgetting context fields leaves users with technically correct but useless messages.
- ⚠️ Making fields public too early can freeze representation details; prefer accessors if the type may evolve.

## See also
[[The Error Trait]] · [[Result]] · [[The Question Mark Operator]] · [[Error Sources and Chains]] · [[Error Handling with thiserror]] · [[Adding Error Context]] · [[Stringly-Typed Errors]] · [[Boxing Errors]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "`?` and `From`" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#the--operator-shortcut
- Rust standard library, `Error` and `From` — https://doc.rust-lang.org/std/error/trait.Error.html and https://doc.rust-lang.org/std/convert/trait.From.html
