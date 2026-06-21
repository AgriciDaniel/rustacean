---
type: concept
title: "Conversion Traits"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, conversions, traits, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[From and Into]]", "[[TryFrom and TryInto]]", "[[AsRef for Flexible Arguments]]", "[[Borrow for Equivalent Keys]]", "[[Conversion Method Prefixes]]"]
sources: ["[[rust-by-example]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/index.html", "https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/convert/trait.TryFrom.html", "https://doc.rust-lang.org/std/convert/trait.AsRef.html"]
rust_version: "edition 2024 / 1.85+"
---

# Conversion Traits

Conversion traits are the standard-library vocabulary for changing how a value is viewed, owned, or validated; choosing the right one tells callers whether conversion is cheap, consuming, or fallible.

## What it is
Rust does not rely on implicit user-defined conversions.
Instead, APIs expose explicit conversion traits such as `From`, `Into`, `TryFrom`, `TryInto`, `AsRef`, and `Borrow`.
That makes ownership, cost, and failure visible at the call site and composable in generic bounds.

The high-level split is:

1. `From` / `Into` for infallible value-to-value conversions.
2. `TryFrom` / `TryInto` for fallible value-to-value conversions.
3. `AsRef` for cheap borrowed views.
4. `Borrow` for borrowed views whose `Eq`, `Ord`, and `Hash` behavior matches the owned value.

## How it works
`From<T> for U` automatically gives `Into<U> for T` through a blanket implementation, so library authors normally implement `From` and accept `Into` in caller-facing generic APIs.
`TryFrom<T> for U` similarly gives `TryInto<U> for T`.

`AsRef<T>` and `Borrow<T>` both start from `&self`, but they do not mean the same thing.
`AsRef` is an ergonomic view conversion.
`Borrow` is a stronger contract used by collections such as `HashMap` so an owned key can be queried by an equivalent borrowed key.

The compiler does not perform arbitrary implicit conversions at function-call boundaries.
Method lookup may auto-borrow or auto-deref, and numeric literals may be inferred, but a `String` does not silently become a `PathBuf` or an `Email`.
That explicitness is why conversion traits carry API-design meaning: the trait bound becomes part of the documented cost and failure model.

Blanket implementations matter for coherence.
If a crate owns `Port`, it can implement `From<u16> for Port`; downstream crates then receive `u16: Into<Port>` without writing another impl.
Because of the orphan rules, you cannot freely add conversion impls between two foreign types; wrap one side in a [[Newtype Pattern]] when you need a local conversion relationship.

## Example
```rust
use std::convert::TryFrom;

#[derive(Debug, PartialEq, Eq)]
struct Port(u16);

impl From<u16> for Port {
    fn from(value: u16) -> Self {
        Self(value)
    }
}

impl TryFrom<i32> for Port {
    type Error = &'static str;

    fn try_from(value: i32) -> Result<Self, Self::Error> {
        let value = u16::try_from(value).map_err(|_| "port out of range")?;
        Ok(Self(value))
    }
}

fn connect(port: impl Into<Port>) -> Port {
    port.into()
}

fn main() {
    assert_eq!(connect(443_u16), Port(443));
    assert_eq!(Port::try_from(8080), Ok(Port(8080)));
    assert!(Port::try_from(-1).is_err());
}
```

## Edge cases
Error conversions are a legitimate `From` use because they are infallible wrappers, not validation.
The `?` operator calls `From::from` to convert the source error into the function's error type.

```rust
use std::{io, num::ParseIntError};

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

fn parse_port(input: &str) -> Result<u16, ConfigError> {
    let port = input.trim().parse::<u16>()?;
    Ok(port)
}

fn main() {
    assert_eq!(parse_port("443").unwrap(), 443);
    assert!(parse_port("not-a-port").is_err());
}
```

## Common errors
Trying to use a conversion trait that has not been implemented usually produces a trait-bound error:

```text
error[E0277]: the trait bound `Port: From<i32>` is not satisfied
```

Fix the call-site type (`443_u16` instead of `443`), implement the appropriate local `From` or `TryFrom`, or use an explicit checked conversion such as `u16::try_from(value)`.
Do not paper over the error by adding a lossy or panicking `From` implementation.

## Best practice
- ✅ Implement `From` rather than `Into`; the reciprocal `Into` implementation is provided automatically.
- ✅ Implement `TryFrom` rather than panicking when conversion can reject input.
- ✅ Use `AsRef` for flexible borrowed parameters such as paths, strings, and byte slices.
- ✅ Reserve `Borrow` for lookup-equivalent borrowed forms, especially collection keys.
- ✅ Use conversion traits at API boundaries, then switch to concrete domain types inside the function body.
- ✅ Prefer named inherent methods when there are multiple plausible conversions, such as endian-specific byte decoding.

## Pitfalls
- ⚠️ Do not put validation failure inside `From`; use [[TryFrom and TryInto]] or a named constructor.
- ⚠️ Do not implement `Borrow` for "just one field" unless equality, ordering, and hashing match; see [[Implementing Borrow for Partial Views]].
- ⚠️ Avoid inventing parallel conversion names when [[Conversion Method Prefixes]] or standard traits already express the operation.
- ⚠️ Avoid accepting `impl Into<T>` and then calling `.into()` repeatedly; conversion should happen once.
- ⚠️ Do not use trait conversions to hide expensive work that would surprise callers; document allocation or prefer a named method.

## See also
[[From and Into]] · [[TryFrom and TryInto]] · [[AsRef for Flexible Arguments]] · [[Borrow for Equivalent Keys]] · [[Conversion Method Prefixes]] · [[Constructor Naming]] · [[Newtype Pattern]] · [[The Question Mark Operator]] · [[Option vs Result]] · [[Idioms & API Design]]

## Sources
- Rust By Example, "From and Into" and "TryFrom and TryInto" - [[rust-by-example]], https://doc.rust-lang.org/rust-by-example/conversion/from_into.html and https://doc.rust-lang.org/rust-by-example/conversion/try_from_try_into.html
- Standard library conversion traits - https://doc.rust-lang.org/std/convert/index.html
- `From` - https://doc.rust-lang.org/std/convert/trait.From.html
- `TryFrom` - https://doc.rust-lang.org/std/convert/trait.TryFrom.html
- `AsRef` - https://doc.rust-lang.org/std/convert/trait.AsRef.html
