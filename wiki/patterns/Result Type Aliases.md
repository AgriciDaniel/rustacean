---
type: pattern
title: "Result Type Aliases"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, pattern, result, aliases, errors]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[Type Aliases]]", "[[Result]]", "[[The Question Mark Operator]]", "[[Custom Error Types]]", "[[Propagating Errors]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-03-advanced-types.html#type-synonyms-and-type-aliases", "https://doc.rust-lang.org/std/io/type.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Result Type Aliases

A `Result` type alias fixes the error type once so functions can return `Result<T>` without repeating `Result<T, E>` everywhere.

## What it is
The standard library uses this pattern in `std::io::Result<T>`, which aliases `std::result::Result<T, std::io::Error>`.
Crates often use the same idea:
`pub type Result<T> = std::result::Result<T, Error>;`.

This is a readability pattern, not a new error type.
The alias stays compatible with [[The Question Mark Operator]], `map_err`, `?`, and every method on `Result<T, E>` because it is still the same underlying type.

Use this pattern when a module, crate, or subsystem has a dominant error type.
Avoid it when a function intentionally returns different error families and the explicit error type is useful documentation.

## How it works
Define the alias near the error type it fixes.
Use `std::result::Result` inside the alias to avoid recursively referring to the alias itself.
Then write function signatures as `Result<T>`.

For public APIs, decide whether the alias helps users.
It often does when the crate exposes a single `Error` enum.
It can hurt when readers must jump to the alias to discover the error type.

The alias does not change how [[The Question Mark Operator]] works.
`?` still requires the incoming error to be the same error type or convertible into it through `From`.
That means a crate-level alias pairs naturally with a crate-level error enum that implements `From<io::Error>`, `From<ParseIntError>`, and similar conversions.

Aliases can have more than one type parameter, but the common `Result<T>` pattern intentionally fixes `E`.
If every function needs to customize `E`, the alias is probably not buying much.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
enum ConfigError {
    Empty,
}

type Result<T> = std::result::Result<T, ConfigError>;

fn parse_name(input: &str) -> Result<String> {
    let trimmed = input.trim();
    if trimmed.is_empty() {
        Err(ConfigError::Empty)
    } else {
        Ok(trimmed.to_owned())
    }
}

fn main() {
    assert_eq!(parse_name(" ferris "), Ok(String::from("ferris")));
    assert_eq!(parse_name("   "), Err(ConfigError::Empty));
}
```

## More realistic example
```rust
use std::fs;
use std::num::ParseIntError;
use std::{fmt, io};

#[derive(Debug)]
enum AppError {
    Io(io::Error),
    Parse(ParseIntError),
}

impl From<io::Error> for AppError {
    fn from(error: io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<ParseIntError> for AppError {
    fn from(error: ParseIntError) -> Self {
        Self::Parse(error)
    }
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(error) => write!(f, "I/O error: {error}"),
            Self::Parse(error) => write!(f, "parse error: {error}"),
        }
    }
}

type Result<T> = std::result::Result<T, AppError>;

fn read_port(path: &str) -> Result<u16> {
    let text = fs::read_to_string(path)?;
    let port = text.trim().parse::<u16>()?;
    Ok(port)
}

fn main() {
    let _ = read_port("config/port.txt");
}
```

The short return type works because both fallible operations can convert their errors into `AppError`.

## Common errors
```rust
#[derive(Debug)]
struct Error;

// type Result<T> = Result<T, Error>;
// error[E0107] or a cycle diagnostic from recursively referring to the alias

type Result<T> = std::result::Result<T, Error>;
```

Always qualify the standard `Result` inside the alias definition when the alias itself is named `Result`.

```rust
#[derive(Debug)]
struct AppError;

type Result<T> = std::result::Result<T, AppError>;

fn parse_number(input: &str) -> Result<u32> {
    // let number = input.parse::<u32>()?;
    // error[E0277]: `?` couldn't convert the error to `AppError`
    let number = input.parse::<u32>().map_err(|_| AppError)?;
    Ok(number)
}
```

The alias fixes the error type; it does not create conversions.
Implement `From<ParseIntError> for AppError` or map the error explicitly.

## Best practice
- ✅ Use `type Result<T> = std::result::Result<T, Error>;` when a scope has one primary error type.
- ✅ Keep aliases close to the `Error` type and document the alias in public APIs.
- ✅ Prefer explicit `std::result::Result<T, OtherError>` when a function intentionally leaves the local error family.
- ✅ Pair this pattern with [[Custom Error Types]] and [[Propagating Errors]].
- ✅ Implement `From` conversions on the fixed error type when you expect `?` to propagate lower-level errors.
- ✅ Use module-qualified names such as `crate::error::Result<T>` in public examples when several `Result` aliases are in scope.

## Pitfalls
- ⚠️ Do not hide unrelated error types behind one vague alias; it makes API behavior harder to audit.
- ⚠️ Avoid defining many different `Result` aliases in one module; the short name becomes ambiguous to readers.
- ⚠️ Remember this is still only a [[Type Aliases]] pattern; it does not wrap or convert errors by itself.
- ⚠️ Do not export a `Result<T>` alias if your crate has no coherent public error type; explicit signatures may be clearer.
- ⚠️ Avoid using the alias in examples where teaching the concrete error type is the point.

## See also
[[Type Aliases]] · [[Result]] · [[The Question Mark Operator]] · [[Custom Error Types]] · [[Propagating Errors]] · [[Error Sources and Chains]] · [[Recoverable vs Unrecoverable Errors]] · [[Using Type Aliases as Newtypes]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.3 "Type Synonyms and Type Aliases" — [[the-book]], https://doc.rust-lang.org/book/ch20-03-advanced-types.html#type-synonyms-and-type-aliases
- Standard library `std::io::Result` — https://doc.rust-lang.org/std/io/type.Result.html
