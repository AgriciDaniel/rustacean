---
type: concept
title: "Fallible Conversion Traits (std)"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, conversions, tryfrom, tryinto]
domain: "std: Core Trait Catalog"
difficulty: basic
related: ["[[TryFrom and TryInto]]", "[[From and Into]]", "[[Option vs Result]]", "[[Making Invalid States Unrepresentable]]"]
sources: ["[[std]]", "[[rust-by-example]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/trait.TryFrom.html", "https://doc.rust-lang.org/std/convert/trait.TryInto.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Fallible Conversion Traits (std)

`TryFrom<T>` and `TryInto<U>` are the standard-library traits for conversions that can reject input and therefore return `Result` instead of pretending every value is valid.

## What it is
`TryFrom<T> for U` says that a `U` may be built from a `T`.
It consumes the input value.
It returns `Result<U, Error>`.
The associated `Error` type explains why conversion failed.

`TryInto<U> for T` is the caller-facing mirror.
As with `From` and `Into`, implement the destination-side trait when possible.
The blanket implementation gives callers `try_into()`.

This is the trait pair for numeric narrowing, validated newtypes, parser-like conversions, and invariant checks.
The existing pattern note [[TryFrom and TryInto]] covers API idiom.
This note focuses on the std contract and its edge cases.

## How it works
The required method is `fn try_from(value: T) -> Result<Self, Self::Error>`.
The implementation decides the validation rule.
Once `Ok(Self)` is returned, the new type should actually satisfy the invariant its name promises.

The traits compose with [[The Question Mark Operator]].
Inside a function returning `Result`, `?` can propagate the conversion error.
If the function's error type is different, `?` can additionally use [[Infallible Conversion Traits (std)]] to convert that error.

There is a reflexive implementation too.
Trying to convert `T` into `T` cannot fail.
Its error type is `Infallible`.

Do not use `TryFrom` to hide arbitrary business workflows.
It should still be a conversion from one representation to another.
If the operation contacts a database, reads files, or needs runtime context, a named method usually communicates better.

## Example
```rust
use std::convert::TryFrom;

#[derive(Debug, PartialEq, Eq)]
struct Percentage(u8);

#[derive(Debug, PartialEq, Eq)]
struct PercentageError(u8);

impl TryFrom<u8> for Percentage {
    type Error = PercentageError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        if value <= 100 {
            Ok(Self(value))
        } else {
            Err(PercentageError(value))
        }
    }
}

fn discount(input: u8) -> Result<Percentage, PercentageError> {
    input.try_into()
}

fn main() {
    assert_eq!(Percentage::try_from(80), Ok(Percentage(80)));
    assert_eq!(discount(120), Err(PercentageError(120)));
}
```

## Best practice
- ✅ Use `TryFrom` when a conversion can fail because of range, syntax, encoding, or domain invariants.
- ✅ Make the error type useful enough for callers to distinguish expected failure cases.
- ✅ Convert loose input into invariant-carrying types at boundaries.
- ✅ Prefer `TryFrom` over panicking constructors for library APIs.
- ✅ Use `Infallible` only when the generic shape requires a fallible trait but this specific conversion cannot fail.

## Pitfalls
- ⚠️ Do not return `Option` when the failure mode matters; use `Result` and keep diagnostics.
- ⚠️ Do not use [[Infallible Conversion Traits (std)]] when invalid input exists.
- ⚠️ Avoid validating into a type whose fields remain public and can immediately violate the invariant.
- ⚠️ Do not use `unwrap()` after `try_into()` at API boundaries; propagate or handle the error.

## See also
[[std: Core Trait Catalog]] · [[TryFrom and TryInto]] · [[From and Into]] · [[Infallible Conversion Traits (std)]] · [[Option vs Result]] · [[Result]] · [[The Question Mark Operator]] · [[Making Invalid States Unrepresentable]] · [[Newtype Pattern]] · [[Panicking From Implementations]]

## Sources
- Rust standard library, `std::convert::TryFrom` - [[std]], https://doc.rust-lang.org/std/convert/trait.TryFrom.html
- Rust standard library, `std::convert::TryInto` - [[std]], https://doc.rust-lang.org/std/convert/trait.TryInto.html
- Rust standard library, `Result` - [[std]], https://doc.rust-lang.org/std/result/enum.Result.html
