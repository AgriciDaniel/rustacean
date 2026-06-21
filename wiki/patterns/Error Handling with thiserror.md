---
type: pattern
title: "Error Handling with thiserror"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, thiserror, errors, libraries]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Custom Error Types]]", "[[The Error Trait]]", "[[The Question Mark Operator]]", "[[Error Sources and Chains]]", "[[Panicking in Libraries]]", "[[Error Handling]]"]
sources: ["[[thiserror]]", "[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Error Handling with thiserror

`thiserror` derives idiomatic typed errors for libraries and reusable modules without exposing the macro crate in the public API.

## What it is
`thiserror` 2.x provides `#[derive(thiserror::Error)]` for structs and enums.
It generates `Display`, [[The Error Trait]], `source()`, and `From` implementations from attributes.

Use it when callers benefit from a concrete [[Custom Error Types]] enum they can match.

## How it works
`#[error("...")]` defines the `Display` message.
`#[from]` creates a `From` impl and marks the field as a source.
`#[source]` marks an underlying cause without creating `From`.
`#[error(transparent)]` delegates `Display` and `source` to an inner error.

The generated impl is equivalent to handwritten std traits, so using thiserror is not itself part of your public API.
The public API is your error type and its variants.
Callers do not need to depend on `thiserror` to match your enum, call `Display`, or walk `source()`.
Use `#[from]` only on variants where a source error alone is enough to construct the variant; variants with extra context usually need `map_err` or a struct-like variant.

## Example
```rust
// Cargo.toml: thiserror = "2"
use std::fs;
use std::num::ParseIntError;

#[derive(Debug, thiserror::Error)]
enum ConfigError {
    #[error("failed to read config")]
    Read(#[from] std::io::Error),
    #[error("invalid port")]
    Port(#[from] ParseIntError),
    #[error("port must be nonzero")]
    ZeroPort,
}

fn load_port(path: &str) -> Result<u16, ConfigError> {
    let text = fs::read_to_string(path)?;
    let port: u16 = text.trim().parse()?;
    if port == 0 { Err(ConfigError::ZeroPort) } else { Ok(port) }
}

fn main() {
    let _ = load_port("port.txt");
}
```

## Second example
Use a context-carrying variant when the source error needs a path or operation name.

```rust
// Cargo.toml: thiserror = "2"
use std::fs;
use std::path::PathBuf;

#[derive(Debug, thiserror::Error)]
enum ConfigError {
    #[error("failed to read config {path}")]
    Read {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },
}

fn load_config(path: impl Into<PathBuf>) -> Result<String, ConfigError> {
    let path = path.into();
    fs::read_to_string(&path).map_err(|source| ConfigError::Read { path, source })
}

fn main() {
    let _ = load_config("app.toml");
}
```

## Common errors
`#[from]` cannot construct a variant that needs unrelated extra fields:

```text
error: deriving From requires no fields other than source and backtrace
```

Fix it by removing `#[from]` and using `map_err` to fill the context fields.
If automatic conversion would hide important context, explicit conversion is the better design.

## Best practice
- ✅ Use `thiserror` for library-facing or module-facing error enums where variants matter.
- ✅ Keep variants aligned with caller decisions, not private implementation steps.
- ✅ Use `#[from]` only when automatic conversion is a good semantic fit.
- ✅ Preserve sources so [[Error Sources and Chains]] remain inspectable.
- ✅ Use struct-like variants when messages need named fields such as `path`, `key`, or `status`.
- ✅ Keep `#[error(...)]` messages concise and leave lower-level details to `source`.

## Pitfalls
- ⚠️ Exposing a huge enum full of private details makes your API hard to evolve.
- ⚠️ Using [[Application Errors with anyhow]] in a public API can erase branchable failure modes.
- ⚠️ Putting the same source text in `#[error(...)]` and `source()` duplicates reports.
- ⚠️ Panicking inside library error paths defeats the point; see [[Panicking in Libraries]].
- ⚠️ Treating `#[from]` as free boilerplate can make conversions available in places where they are semantically wrong.

## See also
[[Custom Error Types]] · [[The Error Trait]] · [[The Question Mark Operator]] · [[Error Sources and Chains]] · [[Adding Error Context]] · [[Application Errors with anyhow]] · [[Panicking in Libraries]] · [[Error Handling]]

## Sources
- `thiserror` crate documentation, derive macro details — [[thiserror]],
  https://docs.rs/thiserror/latest/thiserror/
- Rust standard library, `Error` and `From` — https://doc.rust-lang.org/std/error/trait.Error.html and https://doc.rust-lang.org/std/convert/trait.From.html
