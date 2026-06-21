---
type: pattern
title: "Constructor Naming"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, constructors, naming, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[Builder Pattern]]", "[[Naming Conventions (Rust API Guidelines)]]", "[[From and Into]]", "[[TryFrom and TryInto]]", "[[Conversion Method Prefixes]]"]
sources: ["[[the-book]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-03-method-syntax.html", "https://doc.rust-lang.org/std/default/trait.Default.html", "https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/convert/trait.TryFrom.html"]
rust_version: "edition 2024 / 1.85+"
---

# Constructor Naming

Constructor names should tell callers whether they are getting the obvious default shape, a capacity/configuration variant, a domain action, or a conversion.

## What it is
Rust constructors are ordinary associated functions.
The conventional primary constructor is `new`.
Alternative constructors should be named for the distinction they introduce.

Common names include `with_capacity`, `from_bytes`, `open`, `connect`, and `default`.
Use [[From and Into]] or [[TryFrom and TryInto]] instead of ad hoc constructor names when the relationship is a standard conversion.

## How it works
`new` should be the obvious, unsurprising way to create a value.
`with_*` names usually add configuration while preserving the same conceptual constructor.
Domain verbs such as `File::open` or `TcpStream::connect` are better when construction performs a domain action.

If a type has many optional settings, switch to [[Builder Pattern]] rather than growing a family of confusing positional constructors.

Constructors are part of semver.
For public structs, exposing fields lets downstream code construct values directly; adding a new field can then become a breaking change.
Private fields plus constructors or builders preserve room to evolve the representation.

`Default` is not a synonym for `new`.
Implement `Default` only when there is a useful, unsurprising default value.
When construction can fail, the return type should say so with `Result`, or the constructor should be named as a fallible domain action such as `parse`, `open`, or `connect`.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct Buffer {
    bytes: Vec<u8>,
}

impl Buffer {
    fn new() -> Self {
        Self { bytes: Vec::new() }
    }

    fn with_capacity(capacity: usize) -> Self {
        Self { bytes: Vec::with_capacity(capacity) }
    }

    fn from_bytes(bytes: Vec<u8>) -> Self {
        Self { bytes }
    }

    fn len(&self) -> usize {
        self.bytes.len()
    }
}

fn main() {
    assert_eq!(Buffer::new().len(), 0);
    assert_eq!(Buffer::with_capacity(16).len(), 0);
    assert_eq!(Buffer::from_bytes(vec![1, 2, 3]).len(), 3);
}
```

## Fallible constructor example
A fallible constructor should expose failure directly and preserve a precise type after success.

```rust
#[derive(Debug, PartialEq, Eq)]
struct NonEmptyName(String);

impl NonEmptyName {
    fn new(value: impl Into<String>) -> Result<Self, &'static str> {
        let value = value.into();
        if value.trim().is_empty() {
            Err("name must not be empty")
        } else {
            Ok(Self(value))
        }
    }

    fn as_str(&self) -> &str {
        &self.0
    }
}

fn main() {
    assert_eq!(NonEmptyName::new("Ferris").unwrap().as_str(), "Ferris");
    assert_eq!(NonEmptyName::new("   "), Err("name must not be empty"));
}
```

## Common errors
Calling a private-field constructor directly from another module produces:

```text
error[E0451]: field `bytes` of struct `Buffer` is private
```

That is usually a healthy API boundary.
Use the public constructor, add a new constructor with a clear name, or expose a builder if callers need more configuration.

## Best practice
- ✅ Use `new` for the primary constructor when there is one obvious construction path.
- ✅ Use `with_*` for constructors that add configuration such as capacity.
- ✅ Use domain verbs when construction does IO, connection, parsing, or another named action.
- ✅ Prefer conversion traits when construction is just conversion.
- ✅ Keep fields private when constructors enforce invariants or preserve semver flexibility.
- ✅ Use `Default` only for a real default, and consider implementing it by delegating to `new` when they mean the same thing.

## Pitfalls
- ⚠️ Avoid multiple positional constructors whose differences are not obvious from the name.
- ⚠️ Do not use `new` for a fallible operation unless the failure is explicit in the return type.
- ⚠️ Do not keep adding constructor overloads by name when [[Builder Pattern]] would make call sites clearer.
- ⚠️ Avoid `from_*` names for ambiguous conversions without naming the representation, such as byte order or encoding.
- ⚠️ Do not expose public fields just to avoid writing constructors; that gives up invariant and compatibility control.

## See also
[[Builder Pattern]] · [[Naming Conventions (Rust API Guidelines)]] · [[From and Into]] · [[TryFrom and TryInto]] · [[Conversion Method Prefixes]] · [[Making Invalid States Unrepresentable]] · [[The Default Trait]] · [[Newtype Pattern]] · [[Idioms & API Design]]

## Sources
- The Rust Programming Language, "Method Syntax" - [[the-book]], https://doc.rust-lang.org/book/ch05-03-method-syntax.html
- `Default` - https://doc.rust-lang.org/std/default/trait.Default.html
- `From` - https://doc.rust-lang.org/std/convert/trait.From.html
- `TryFrom` - https://doc.rust-lang.org/std/convert/trait.TryFrom.html
