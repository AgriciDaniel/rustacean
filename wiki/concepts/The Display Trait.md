---
type: concept
title: "The Display Trait"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, display, formatting, traits]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[The Debug Trait]]", "[[Readable Generic APIs]]", "[[Functions]]", "[[Documentation Comments]]", "[[Result]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-02-traits.html", "https://doc.rust-lang.org/std/fmt/trait.Display.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Display Trait

`std::fmt::Display` defines a user-facing representation via `{}`; implement it by hand (not derivable).

## What it is
`Display` is the standard formatting trait for user-facing text. It powers `{}` in formatting macros,
`format!`, `println!`, and the blanket `ToString` implementation.

Use `Display` when a type has one obvious textual representation for humans. If there are many valid
representations, prefer explicit methods or wrapper types instead of making `Display` guess.

`Display` cannot be derived because Rust cannot know which user-facing representation is correct for
your domain.

## How it works
Formatting macros select `Display` when the placeholder is `{}`. The trait method receives a
`fmt::Formatter` and writes into it with `write!`, returning `fmt::Result`.

Any type that implements `Display` automatically gets `ToString` through a blanket implementation.
The reverse is not true: you normally implement `Display`, not `ToString`, for your own type.

`Display` implementations should be cheap enough for formatting and should not perform surprising
I/O. The formatter is already the output sink.

## Example
```rust
use std::fmt;

struct Celsius(f64);

impl fmt::Display for Celsius {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:.1} C", self.0)
    }
}

fn main() {
    let temp = Celsius(21.25);
    assert_eq!(temp.to_string(), "21.2 C");
}
```

## Edge cases
Use small wrapper types when the same data needs multiple legitimate display formats:

```rust
use std::fmt;

struct Bytes(u64);
struct HexBytes(u64);

impl fmt::Display for Bytes {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} bytes", self.0)
    }
}

impl fmt::Display for HexBytes {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "0x{:x}", self.0)
    }
}

fn main() {
    assert_eq!(Bytes(255).to_string(), "255 bytes");
    assert_eq!(HexBytes(255).to_string(), "0xff");
}
```

## Common errors
Printing a custom type with `{}` before implementing `Display` produces E0277:

```rust
struct UserId(u64);

fn main() {
    // println!("{}", UserId(7));
}
```

Typical diagnostic:

```text
error[E0277]: `UserId` doesn't implement `std::fmt::Display`
```

Fix it by implementing `Display`, or use `{:?}` after deriving [[The Debug Trait]] for diagnostic
output.

## Best practice
- ✅ Implement `Display` for domain values that have one canonical human-readable form.
- ✅ Implement `Display` on error types so messages compose with [[Result]] and `?`-based callers.
- ✅ Put alternate views in wrapper types or named methods.
- ✅ Keep `fmt` side-effect free except for writing to the formatter.
- ✅ Prefer implementing `Display` over implementing `ToString` directly.

## Pitfalls
- ⚠️ Do not use `Display` when callers need a stable parseable wire format unless you explicitly document and test that contract.
- ⚠️ Do not derive expectations from `Debug`; `Display` is a separate trait with a different audience.
- ⚠️ Avoid allocation-heavy formatting when a sequence of `write!` calls would stream directly.
- ⚠️ Remember the orphan rule: you cannot implement `Display` for a standard-library type in your crate.
- ⚠️ Do not hide lossy conversion behind `Display` for values users may need to round-trip.

## See also
[[The Debug Trait]] · [[PartialEq]] · [[Readable Generic APIs]] · [[Functions]] · [[Result]] · [[Documentation Comments]] · [[Type Inference]] · [[Scalar Types]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 10.2 "Traits: Defining Shared Behavior" — [[the-book]], https://doc.rust-lang.org/book/ch10-02-traits.html
- Standard library, `std::fmt::Display` — https://doc.rust-lang.org/std/fmt/trait.Display.html
