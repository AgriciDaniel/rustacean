---
type: concept
title: "Infallible Conversion Traits (std)"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, conversions, from, into]
domain: "std: Core Trait Catalog"
difficulty: basic
related: ["[[From and Into]]", "[[TryFrom and TryInto]]", "[[Conversion Traits]]", "[[The Question Mark Operator]]"]
sources: ["[[std]]", "[[the-book]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/convert/trait.Into.html", "https://doc.rust-lang.org/book/ch09-00-error-handling.html"]
rust_version: "edition 2024 / 1.85+"
---

# Infallible Conversion Traits (std)

`From<T>` and `Into<U>` are the standard-library traits for consuming a value and converting it into another value without failure, loss of meaning, or surprising behavior.

## What it is
`From<T> for U` says that a `U` can always be built from a `T`.
It consumes the input value.
It returns `Self`, not `Result`.
That return type is the contract: failure does not belong here.

`Into<U> for T` is the caller-facing mirror of the same relationship.
The standard library provides a blanket implementation.
If `U: From<T>`, then `T: Into<U>` automatically.
That is why library authors normally implement `From`, not `Into`.

The existing pattern note [[From and Into]] covers the common API design rule.
This note focuses on the std trait contract.

`From` is reflexive.
Every type can be converted from itself.
That matters in generic APIs where `impl Into<T>` can accept a `T` directly.

## How it works
The required method is `fn from(value: T) -> Self`.
It is an associated function on the destination type.
`String::from("text")` is the classic example.

The standard library documentation describes `From` conversions as infallible, lossless, value-preserving, and obvious.
These are semantic expectations, not just type-checking facts.
For example, `i32: From<u16>` is valid because every `u16` fits in `i32`.
But `u16: From<u32>` is not valid because many `u32` values do not fit.

`From` also participates in error conversion.
The `?` operator can convert an error with `From::from` when the function returns a different error type.
That is why custom error enums often implement `From<io::Error>` and `From<num::ParseIntError>`.

Use [[Fallible Conversion Traits (std)]] when validation, parsing, or bounds checking can fail.
Use named constructors when multiple conversions are reasonable.
Use formatting traits like [[Display and Debug Formatting Traits]] when the goal is text representation.

## Example
```rust
use std::io;
use std::num::ParseIntError;

#[derive(Debug)]
enum ConfigError {
    Io(io::Error),
    Port(ParseIntError),
}

impl From<io::Error> for ConfigError {
    fn from(error: io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<ParseIntError> for ConfigError {
    fn from(error: ParseIntError) -> Self {
        Self::Port(error)
    }
}

fn parse_port(text: &str) -> Result<u16, ConfigError> {
    let port: u16 = text.trim().parse()?;
    Ok(port)
}

fn label(id: impl Into<String>) -> String {
    let id = id.into();
    format!("service-{id}")
}

fn main() {
    assert_eq!(label("api"), "service-api");
    assert_eq!(parse_port("8080").unwrap(), 8080);
}
```

## Best practice
- ✅ Implement `From<T> for U` when conversion is infallible, lossless, value-preserving, and obvious.
- ✅ Accept `impl Into<U>` at public API boundaries when caller flexibility is useful.
- ✅ Convert once at the boundary, then keep internals concrete.
- ✅ Use `From` for source error types that your error enum wraps without losing information.
- ✅ Prefer named constructors for conversions with policy choices, units, encodings, or multiple plausible meanings.

## Pitfalls
- ⚠️ Do not panic from `From`; use [[Fallible Conversion Traits (std)]] for checked conversion and link the mistake to [[Panicking From Implementations]].
- ⚠️ Do not use `From` for lossy narrowing such as `u32` to `u16`.
- ⚠️ Do not confuse text formatting with conversion; use [[Display and Debug Formatting Traits]] for user-facing text.
- ⚠️ Avoid `impl Into<String>` on every function when a borrowed `&str` would avoid allocation pressure.

## See also
[[std: Core Trait Catalog]] · [[From and Into]] · [[TryFrom and TryInto]] · [[Conversion Traits]] · [[Fallible Conversion Traits (std)]] · [[The Question Mark Operator]] · [[Custom Error Types]] · [[The Error Trait]] · [[Newtype Pattern]] · [[Panicking From Implementations]]

## Sources
- Rust standard library, `std::convert::From` - [[std]], https://doc.rust-lang.org/std/convert/trait.From.html
- Rust standard library, `std::convert::Into` - [[std]], https://doc.rust-lang.org/std/convert/trait.Into.html
- The Rust Programming Language, error handling - [[the-book]], https://doc.rust-lang.org/book/ch09-00-error-handling.html
