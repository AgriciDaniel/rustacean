---
type: concept
title: "Display and Debug Formatting Traits"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, formatting, display, debug]
domain: "std: Core Trait Catalog"
difficulty: basic
related: ["[[The Display Trait]]", "[[The Debug Trait]]", "[[The Error Trait]]", "[[Custom Error Types]]"]
sources: ["[[std]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/fmt/trait.Display.html", "https://doc.rust-lang.org/std/fmt/trait.Debug.html", "https://doc.rust-lang.org/std/fmt/"]
rust_version: "edition 2024 / 1.85+"
---

# Display and Debug Formatting Traits

`Display` is the single user-facing `{}` representation of a value, while `Debug` is the programmer-facing `{:?}` representation that can usually be derived.

## What it is
Rust formatting is trait-driven.
`Display` powers `{}`.
`Debug` powers `{:?}` and `{:#?}`.
Both live in `std::fmt`.

`Display` cannot be derived because Rust cannot infer the one canonical human-readable representation for a custom type.
Implementors choose the text.
The standard docs warn that `Display` may be incomplete or lossy unless documented otherwise.

`Debug` can be derived.
It is intended for diagnostics and developer inspection.
Its output is not a stable serialization format.

`std::error::Error` requires both `Debug` and `Display`.
That makes these traits central to [[Custom Error Types]] and [[The Error Trait]].

## How it works
Both traits implement `fmt`.
The method receives a formatter and returns `fmt::Result`.
Formatting should return `Err` only when the formatter reports an error.
String formatting itself is treated as infallible.

Implementing `Display` automatically enables `ToString` through a blanket implementation.
Prefer implementing `Display` instead of implementing `ToString` manually.

Because a type can have only one `Display` implementation, alternative views should use adapter wrappers.
Examples in std include `Path::display()` and string escaping adapters.
Use a wrapper when a value has multiple reasonable textual forms.

## Example
```rust
use std::fmt;

#[derive(Debug, PartialEq, Eq)]
struct UserId(u64);

impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "user-{}", self.0)
    }
}

fn main() {
    let id = UserId(42);

    assert_eq!(format!("{id}"), "user-42");
    assert_eq!(format!("{id:?}"), "UserId(42)");
    assert_eq!(id.to_string(), "user-42");
}
```

## Best practice
- ✅ Derive `Debug` on most public data types unless there is a privacy or stability reason not to.
- ✅ Implement `Display` only when there is a clear canonical human-facing representation.
- ✅ Document whether `Display` output is parseable if users may rely on round-tripping.
- ✅ Use display adapters for alternate formats rather than trying to overload `Display`.
- ✅ Keep error `Display` messages concise, lowercase, and without trailing punctuation unless grammar demands it.

## Pitfalls
- ⚠️ Do not treat `Debug` output as a stable format for tests, logs, or wire protocols.
- ⚠️ Do not implement `ToString` directly when `Display` is the intended source.
- ⚠️ Do not leak secrets through derived `Debug` for credential-bearing types.
- ⚠️ Do not make `Display` panic on ordinary values.

## See also
[[std: Core Trait Catalog]] · [[The Display Trait]] · [[The Debug Trait]] · [[The Error Trait]] · [[Custom Error Types]] · [[String and str]] · [[panic!]] · [[Documentation Tests]] · [[Infallible Conversion Traits (std)]] · [[Fallible Conversion Traits (std)]]

## Sources
- Rust standard library, `std::fmt::Display` - [[std]], https://doc.rust-lang.org/std/fmt/trait.Display.html
- Rust standard library, `std::fmt::Debug` - [[std]], https://doc.rust-lang.org/std/fmt/trait.Debug.html
- Rust standard library, formatting module - [[std]], https://doc.rust-lang.org/std/fmt/
