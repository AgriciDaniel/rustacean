---
type: pattern
title: "TryFrom and TryInto"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, tryfrom, tryinto, conversions, api-design]
domain: "Idioms & API Design"
difficulty: basic
related: ["[[Conversion Traits]]", "[[From and Into]]", "[[Making Invalid States Unrepresentable]]", "[[The Question Mark Operator]]", "[[Panicking From Implementations]]"]
sources: ["[[rust-by-example]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rust-by-example/conversion/try_from_try_into.html", "https://doc.rust-lang.org/std/convert/trait.TryFrom.html", "https://doc.rust-lang.org/std/convert/trait.TryInto.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# TryFrom and TryInto

`TryFrom` and `TryInto` model fallible value conversions, returning `Result` instead of smuggling validation failure into panics or sentinel values.

## What it is
Use `TryFrom` when converting from one type to another can fail for domain reasons.
Common cases include numeric narrowing, checked parsing, validated strings, bounded IDs, and converting raw input into an invariant-carrying type.

Like `From` and `Into`, these traits are paired.
Implement `TryFrom<T> for U`, and the standard library provides `TryInto<U> for T`.

## How it works
The implementation names an associated `Error` type and returns `Result<Self, Self::Error>`.
That makes the failure explicit and integrates with [[The Question Mark Operator]].
Once conversion succeeds, downstream code can rely on the new type's invariant without rechecking it.

This is one of the most direct ways to practice [[Making Invalid States Unrepresentable]] at IO and parsing boundaries.

`TryFrom` has a blanket relationship with `TryInto`, so callers can write whichever direction reads best.
It also participates in numeric conversion APIs such as `u16::try_from(i32_value)`, where narrowing might reject out-of-range values.
The successful conversion consumes the input value, which is useful for validated wrappers because no extra allocation is needed when the input is already owned.

For public libraries, prefer an error enum or small error struct over `&'static str`.
That lets callers match specific failure cases and keeps room for richer diagnostics without parsing strings.

## Example
```rust
use std::convert::TryFrom;

#[derive(Debug, PartialEq, Eq)]
struct Email(String);

impl TryFrom<String> for Email {
    type Error = &'static str;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        if value.contains('@') {
            Ok(Self(value))
        } else {
            Err("email must contain @")
        }
    }
}

fn main() {
    let ok = Email::try_from(String::from("ferris@example.com"));
    let bad: Result<Email, _> = String::from("not-an-email").try_into();

    assert!(ok.is_ok());
    assert_eq!(bad, Err("email must contain @"));
}
```

## Numeric narrowing example
Use `TryFrom` instead of `as` when an out-of-range value should be rejected rather than wrapped or truncated.

```rust
use std::convert::TryFrom;

#[derive(Debug, PartialEq, Eq)]
struct Percentage(u8);

impl TryFrom<u16> for Percentage {
    type Error = &'static str;

    fn try_from(value: u16) -> Result<Self, Self::Error> {
        if value <= 100 {
            Ok(Self(u8::try_from(value).expect("0..=100 always fits in u8")))
        } else {
            Err("percentage must be <= 100")
        }
    }
}

fn main() {
    assert_eq!(Percentage::try_from(80), Ok(Percentage(80)));
    assert_eq!(Percentage::try_from(101), Err("percentage must be <= 100"));
}
```

## Common errors
Forgetting to bring `TryInto` into scope used to be a common edition issue; in edition 2024 it is in the prelude, so modern code can call `.try_into()` directly.
More often, the target type is ambiguous:

```text
error[E0283]: type annotations needed
```

Fix it with `let value: Target = input.try_into()?;`, `Target::try_from(input)?`, or a turbofish on a helper method.
Do not replace the checked conversion with `as` unless truncation or wrapping is explicitly intended.

## Best practice
- ✅ Use `TryFrom` for validation and checked narrowing.
- ✅ Return an error type that callers can inspect or display; upgrade from `&'static str` to a real enum in library code.
- ✅ Convert unchecked input at the boundary, then pass the validated type inward.
- ✅ Pair this with [[Newtype Pattern]] for validated scalar values.
- ✅ Keep error messages stable only if they are part of your API; otherwise expose structured variants.
- ✅ Use `TryFrom` for owned validation and `FromStr` when the source is specifically textual parsing.

## Pitfalls
- ⚠️ Do not use [[From and Into]] when conversion can reject input.
- ⚠️ Do not turn conversion failure into `None` unless absence is truly the whole error; use `Result` for diagnostics.
- ⚠️ Avoid validating the same loose `String` repeatedly instead of creating a precise type once.
- ⚠️ Avoid `as` casts for fallible domain conversions; they do not report failure.
- ⚠️ Do not make `TryFrom` perform surprising side effects such as network IO; use a named async or IO method.

## See also
[[Conversion Traits]] · [[From and Into]] · [[Making Invalid States Unrepresentable]] · [[The Question Mark Operator]] · [[Option vs Result]] · [[Newtype Pattern]] · [[Panicking From Implementations]] · [[Constructor Naming]] · [[Idioms & API Design]]

## Sources
- Rust By Example, "TryFrom and TryInto" - [[rust-by-example]], https://doc.rust-lang.org/rust-by-example/conversion/try_from_try_into.html
- `TryFrom` - https://doc.rust-lang.org/std/convert/trait.TryFrom.html
- `TryInto` - https://doc.rust-lang.org/std/convert/trait.TryInto.html
- `Result` - https://doc.rust-lang.org/std/result/enum.Result.html
