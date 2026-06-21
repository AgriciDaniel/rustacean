---
type: antipattern
title: "Panicking From Implementations"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, conversions, panic, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[From and Into]]", "[[TryFrom and TryInto]]", "[[Conversion Traits]]", "[[panic!]]", "[[Unwrap and Expect Overuse]]"]
sources: ["[[rust-by-example]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/convert/trait.TryFrom.html", "https://doc.rust-lang.org/rust-by-example/conversion/try_from_try_into.html", "https://doc.rust-lang.org/std/panic/macro.panic.html"]
rust_version: "edition 2024 / 1.85+"
---

# Panicking From Implementations

A `From` implementation that can panic is a broken conversion contract; fallible validation belongs in `TryFrom` or a named constructor.

## The mistake
`From` communicates infallible conversion.
When an implementation panics on invalid input, generic code that reasonably trusts `T: Into<U>` becomes unexpectedly crash-prone.

The mistake often appears when wrapping a validated value:
`impl From<String> for Email` checks the string and panics if it is not an email.
That makes the type look easier to construct, but it lies about failure.

## Why it happens
`From` has an ergonomic call site and automatically enables `Into`, so it is tempting to use it everywhere.
But the trait has no place to return an error.
If a conversion can fail, `TryFrom` is the standard shape.

This antipattern also hides invalid states instead of applying [[Making Invalid States Unrepresentable]] honestly at the boundary.

The standard-library contract for `From` is stronger than "can be implemented."
It should be infallible, lossless, value-preserving, and obvious.
Panicking violates the infallible part, and generic code that accepts `impl Into<T>` cannot reasonably defend itself against a hidden panic.

This is especially damaging in libraries.
A downstream caller may pass your type into unrelated generic code, see only an `Into` bound, and still get a domain-specific panic from your implementation.

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
            Err("missing @")
        }
    }
}

fn main() {
    assert!(Email::try_from(String::from("ferris@example.com")).is_ok());
    assert_eq!(Email::try_from(String::from("not-email")), Err("missing @"));
}
```

## Bad example
This compiles, but it lies to callers:

```rust
#[derive(Debug, PartialEq, Eq)]
struct NonZeroPort(u16);

impl From<u16> for NonZeroPort {
    fn from(value: u16) -> Self {
        assert!(value != 0, "port must be nonzero");
        Self(value)
    }
}

fn main() {
    let port = NonZeroPort::from(443);
    assert_eq!(port, NonZeroPort(443));
}
```

The fix is `TryFrom<u16>` returning `Result<NonZeroPort, PortError>`, or a named constructor such as `NonZeroPort::new(value) -> Option<Self>` when there is only one possible failure.

## Common errors
After removing a bad `From` impl, call sites that relied on implicit `Into` conversion may fail with:

```text
error[E0277]: the trait bound `NonZeroPort: From<u16>` is not satisfied
```

That is the correct pressure.
Update the caller to handle `NonZeroPort::try_from(value)?`, or validate earlier and pass an already precise type.

## Best practice
- ✅ Use [[From and Into]] only for infallible, meaning-preserving conversions.
- ✅ Use [[TryFrom and TryInto]] for validation, parsing, numeric narrowing, and checked construction.
- ✅ Give library errors names that help callers recover or report the problem.
- ✅ Convert at API boundaries so the rest of the program receives precise types.
- ✅ Use `From` for error wrapping only when the original error is preserved without failure.
- ✅ Audit `impl Into<T>` parameters if any accepted conversion can panic; the panic belongs at an explicit boundary or should become a `Result`.

## Pitfalls
- ⚠️ Do not call `unwrap`, `expect`, or `panic!` inside `From` to enforce a domain invariant.
- ⚠️ Do not silently substitute a default value on invalid input; that is often worse than panicking.
- ⚠️ Do not accept `impl Into<T>` if some accepted path can panic during conversion.
- ⚠️ Do not claim a conversion is "obvious" when callers could reasonably expect parsing, validation, or normalization.
- ⚠️ Avoid using panicking `From` impls in tests as a shortcut; tests teach future production API shape.

## See also
[[From and Into]] · [[TryFrom and TryInto]] · [[Conversion Traits]] · [[panic!]] · [[Unwrap and Expect Overuse]] · [[Making Invalid States Unrepresentable]] · [[Constructor Naming]] · [[Option vs Result]] · [[Idioms & API Design]]

## Sources
- `From` - https://doc.rust-lang.org/std/convert/trait.From.html
- `TryFrom` - https://doc.rust-lang.org/std/convert/trait.TryFrom.html
- Rust By Example, "TryFrom and TryInto" - [[rust-by-example]], https://doc.rust-lang.org/rust-by-example/conversion/try_from_try_into.html
- `panic!` - https://doc.rust-lang.org/std/panic/macro.panic.html
