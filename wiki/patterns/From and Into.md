---
type: pattern
title: "From and Into"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, from, into, conversions, api-design]
domain: "Idioms & API Design"
difficulty: basic
related: ["[[Conversion Traits]]", "[[TryFrom and TryInto]]", "[[Conversion Method Prefixes]]", "[[Panicking From Implementations]]", "[[Newtype Pattern]]"]
sources: ["[[rust-by-example]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rust-by-example/conversion/from_into.html", "https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/convert/trait.Into.html"]
rust_version: "edition 2024 / 1.85+"
---

# From and Into

`From` and `Into` model infallible value conversions; implement `From<T> for U`, then accept `impl Into<U>` when callers should choose the input type.

## What it is
`From` answers "how do I build this type from that value without failure?"
`Into` answers the same relationship from the caller's side: "convert this value into the target type."

The standard library links them with a blanket implementation.
If `U: From<T>`, then `T: Into<U>` automatically.
That is why public APIs usually implement `From` and rarely implement `Into` directly.

## How it works
An infallible conversion must not reject input, silently lose meaning, or panic.
Good examples include wrapping a primitive in a [[Newtype Pattern]], converting `&str` to `String`, or converting a smaller integer into a wider integer.

Function arguments can use `impl Into<T>` to let the caller pass either `T` or something convertible to `T`.
Inside the function, convert once at the boundary and use the concrete type after that.

`From` is also reflexive: every `T` can be converted from itself.
That keeps `impl Into<T>` ergonomic for callers that already have `T`.
Because `From<T> for U` implies `Into<U> for T`, implement the destination-side `From` whenever the orphan rules allow it.

The standard-library documentation describes good `From` conversions as infallible, lossless, value-preserving, and obvious.
If any of those words feels strained, a named method or [[TryFrom and TryInto]] is usually clearer.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct UserId(u64);

impl From<u64> for UserId {
    fn from(value: u64) -> Self {
        Self(value)
    }
}

fn load_user(id: impl Into<UserId>) -> String {
    let id = id.into();
    format!("user-{}", id.0)
}

fn main() {
    let direct = UserId::from(42);
    let inferred: UserId = 7_u64.into();

    assert_eq!(load_user(direct), "user-42");
    assert_eq!(load_user(inferred), "user-7");
    assert_eq!(load_user(9_u64), "user-9");
}
```

## Error conversion example
`From` is idiomatic for wrapping lower-level errors into one public error enum.
This is still infallible: the error value is preserved inside a larger error type.

```rust
use std::{fs, io, num::ParseIntError};

#[derive(Debug)]
enum LoadError {
    Io(io::Error),
    Parse(ParseIntError),
}

impl From<io::Error> for LoadError {
    fn from(error: io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<ParseIntError> for LoadError {
    fn from(error: ParseIntError) -> Self {
        Self::Parse(error)
    }
}

fn parse_contents(contents: &str) -> Result<u32, LoadError> {
    Ok(contents.trim().parse()?)
}

fn load_number(path: &str) -> Result<u32, LoadError> {
    let contents = fs::read_to_string(path)?;
    parse_contents(&contents)
}

fn main() {
    assert_eq!(parse_contents("42").unwrap(), 42);
    assert!(parse_contents("NaN").is_err());
}
```

## Common errors
When inference cannot find the target type for `.into()`, the compiler asks for a type annotation:

```text
error[E0283]: type annotations needed
```

Prefer `UserId::from(value)` when the destination type should be obvious to the reader, or add a binding type such as `let id: UserId = value.into();`.
Avoid long chains of `.into()` calls where the target type is only known several expressions later.

## Best practice
- ✅ Implement `From<T> for U` when conversion is obvious, infallible, and meaning-preserving.
- ✅ Accept `impl Into<U>` at API boundaries when several input types are genuinely useful.
- ✅ Convert to the concrete type once, then keep internal code simple.
- ✅ Prefer [[TryFrom and TryInto]] when validation, bounds checking, parsing, or allocation failure can matter.
- ✅ Use `From` for error wrapping that preserves the original error and enables `?`.
- ✅ Choose named constructors when there are multiple equally reasonable conversions.

## Pitfalls
- ⚠️ Do not implement `Into` directly when `From` is possible; you lose the conventional direction and blanket behavior.
- ⚠️ Never panic in `From`; see [[Panicking From Implementations]].
- ⚠️ Avoid `impl Into<String>` everywhere if callers always have `&str`; generic flexibility is not free.
- ⚠️ Do not use `From` for lossy numeric narrowing, parsing text, or validation-heavy construction.
- ⚠️ Do not make public APIs depend on ambiguous `.into()` inference when an explicit constructor would read better.

## See also
[[Conversion Traits]] · [[TryFrom and TryInto]] · [[Conversion Method Prefixes]] · [[Panicking From Implementations]] · [[Newtype Pattern]] · [[Constructor Naming]] · [[The Question Mark Operator]] · [[Custom Error Types]] · [[Idioms & API Design]]

## Sources
- Rust By Example, "From and Into" - [[rust-by-example]], https://doc.rust-lang.org/rust-by-example/conversion/from_into.html
- `From` - https://doc.rust-lang.org/std/convert/trait.From.html
- `Into` - https://doc.rust-lang.org/std/convert/trait.Into.html
