---
type: concept
title: "The Error Trait"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, error-trait, std, interoperability]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Custom Error Types]]", "[[Error Sources and Chains]]", "[[Error Handling with thiserror]]", "[[Boxing Errors]]", "[[Stringly-Typed Errors]]", "[[Error Handling]]"]
sources: ["[[std]]", "[[rust-api-guidelines]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/fmt/trait.Display.html", "https://doc.rust-lang.org/std/fmt/trait.Debug.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Error Trait

`std::error::Error` is Rust's interoperability trait for error values: an error must be printable with `Display`, printable diagnostically with `Debug`, and able to expose an optional source.

## What it is
`Error` is the trait ecosystem code expects for fallible APIs, trait objects, and error chaining.
It has supertraits `Debug` and `Display`, and its key stable method is `source()`.

The trait does not decide whether an error is recoverable.
That decision belongs to the API returning [[Result]].

## How it works
`Display` should be the concise human-facing message for this error level.
`Debug` is for programmer diagnostics.
`source()` returns the lower-level cause, enabling [[Error Sources and Chains]].

For broadly reusable error trait objects, prefer bounds like `dyn Error + Send + Sync + 'static`.
Those bounds make errors easier to move across threads and inspect by type when necessary.
`Error::description()` and `Error::cause()` are deprecated; current code uses `Display` and `source()`.
The experimental `provide()` API remains nightly-only, so stable public APIs should not depend on it for core diagnostics.
An error type does not need to be an enum, but it should carry enough fields for `Display`, `source`, and caller decisions.

## Example
```rust
use std::error::Error;
use std::fmt;

#[derive(Debug)]
struct ParseWidgetError {
    input: String,
}

impl fmt::Display for ParseWidgetError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "invalid widget id: {}", self.input)
    }
}

impl Error for ParseWidgetError {}

fn parse_widget(input: &str) -> Result<u32, ParseWidgetError> {
    input.parse().map_err(|_| ParseWidgetError {
        input: input.to_string(),
    })
}

fn main() {
    let error = parse_widget("x").unwrap_err();
    assert_eq!(error.to_string(), "invalid widget id: x");
}
```

## Second example
Expose a source when the current error wraps a lower-level failure.

```rust
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
struct WidgetIdError {
    source: ParseIntError,
}

impl fmt::Display for WidgetIdError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "widget id must be a positive integer")
    }
}

impl Error for WidgetIdError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        Some(&self.source)
    }
}

fn parse_widget_id(input: &str) -> Result<u32, WidgetIdError> {
    input.parse::<u32>().map_err(|source| WidgetIdError { source })
}

fn main() {
    let error = parse_widget_id("abc").unwrap_err();
    assert!(error.source().is_some());
}
```

## Common errors
Forgetting either `Debug` or `Display` prevents implementing `Error`:

```text
error[E0277]: `MyError` doesn't implement `std::fmt::Display`
```

Fix it by deriving or implementing `Debug`, implementing `Display`, and then implementing `Error`.
Avoid reviving deprecated `description()` or `cause()` methods; they are not the modern reporting path.

## Best practice
- ✅ Implement `Error` for custom error types that leave a module boundary.
- ✅ Keep `Display` lowercase and concise, usually without trailing punctuation.
- ✅ Use `source()` or [[Error Handling with thiserror]] fields to preserve underlying causes.
- ✅ Add `Send + Sync + 'static` to boxed error aliases that may cross threads.
- ✅ Keep each `Display` message at one abstraction level; let reporters walk `source()` for lower levels.
- ✅ Derive `Debug` unless a manual implementation is needed to avoid sensitive data.

## Pitfalls
- ⚠️ Using `()` or `String` as a public error type prevents useful error-chain behavior; see [[Stringly-Typed Errors]].
- ⚠️ Including the source's message in both `Display` and `source()` causes duplicated reports.
- ⚠️ Implementing deprecated `description()` or `cause()` is obsolete.
- ⚠️ Treating `Debug` as the user-facing error message usually produces noisy output.
- ⚠️ Depending on nightly-only `provide()` behavior in stable library docs sets callers up for portability problems.

## See also
[[Custom Error Types]] · [[Error Sources and Chains]] · [[Error Handling with thiserror]] · [[Boxing Errors]] · [[Stringly-Typed Errors]] · [[Adding Error Context]] · [[Application Errors with anyhow]] · [[Error Handling]]

## Sources
- Rust standard library, `std::error::Error` — [[std]],
  https://doc.rust-lang.org/std/error/trait.Error.html
- Rust standard library, formatting traits — https://doc.rust-lang.org/std/fmt/trait.Display.html and https://doc.rust-lang.org/std/fmt/trait.Debug.html
