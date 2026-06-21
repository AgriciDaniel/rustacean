---
type: antipattern
title: "Stringly-Typed Errors"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, strings, api-design]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Custom Error Types]]", "[[The Error Trait]]", "[[Result]]", "[[Adding Error Context]]", "[[Boxing Errors]]", "[[Error Handling]]"]
sources: ["[[std]]", "[[rust-api-guidelines]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/string/struct.String.html", "https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Stringly-Typed Errors

Stringly-typed errors use `String` or `&str` as the error contract, which makes failures easy to print but hard to inspect, chain, or evolve.

## The mistake
`Result<T, String>` can be acceptable inside a tiny local function, but it is a weak public API.
The caller receives prose instead of structure.
They cannot match variants, inspect fields, or traverse sources through [[The Error Trait]].

This often starts as convenience and becomes technical debt when callers need real behavior.

## Why it happens
Strings are easy to construct with `format!`, and they satisfy the immediate desire to show a message.
But error messages are for humans; error types are for programs.

Use [[Custom Error Types]] when callers need to branch.
Use [[Application Errors with anyhow]] or [[Boxing Errors]] when callers only need to report.
The deeper issue is that prose has no stable schema.
Changing capitalization, wording, localization, or punctuation can break callers that parse strings.
Strings also cannot implement `source()` for the lower-level cause they replaced.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
enum LoginError {
    EmptyName,
    BadPasswordLength { min: usize },
}

fn validate_login(name: &str, password: &str) -> Result<(), LoginError> {
    if name.trim().is_empty() {
        return Err(LoginError::EmptyName);
    }
    if password.len() < 12 {
        return Err(LoginError::BadPasswordLength { min: 12 });
    }
    Ok(())
}

fn main() {
    let error = validate_login("", "short").unwrap_err();
    assert_eq!(error, LoginError::EmptyName);
}
```

## Second example
Keep the human message in `Display`, while preserving data for callers.

```rust
use std::fmt;

#[derive(Debug, PartialEq, Eq)]
enum UploadError {
    TooLarge { limit: u64, actual: u64 },
    UnsupportedType { extension: String },
}

impl fmt::Display for UploadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::TooLarge { limit, .. } => write!(f, "upload exceeds {limit} bytes"),
            Self::UnsupportedType { extension } => write!(f, "unsupported file type {extension}"),
        }
    }
}

fn validate_upload(extension: &str, size: u64) -> Result<(), UploadError> {
    if size > 10_000 {
        return Err(UploadError::TooLarge { limit: 10_000, actual: size });
    }
    if extension != "txt" {
        return Err(UploadError::UnsupportedType { extension: extension.to_string() });
    }
    Ok(())
}

fn main() {
    assert!(matches!(validate_upload("png", 1), Err(UploadError::UnsupportedType { .. })));
}
```

## Common errors
Stringly APIs often lead to brittle tests and caller code:

```text
if error.to_string().contains("not found") { ... }
```

Fix it by matching an enum variant or inspecting a field such as `io::ErrorKind`.
If only final reporting is needed, convert to [[Application Errors with anyhow]] at the application boundary instead of making a public `String` contract.

## Best practice
- ✅ Use enums or structs for public, branchable errors.
- ✅ Implement [[The Error Trait]] when errors cross module or crate boundaries.
- ✅ Keep human messages in `Display`, not as the whole data model.
- ✅ Use context-carrying opaque errors only when matching is not required.
- ✅ Preserve machine-readable fields for values callers may need, such as `limit`, `path`, or `status`.
- ✅ Keep `Result<T, String>` local and temporary if used during sketching.

## Pitfalls
- ⚠️ Matching on error strings is brittle and localization-hostile.
- ⚠️ A `String` cannot expose a source chain by itself.
- ⚠️ Retrofitting structured variants later can become a breaking API change.
- ⚠️ Boxing a string does not recover the lost domain information.
- ⚠️ Formatting an error source into a string discards downcasting and chain traversal.

## See also
[[Custom Error Types]] · [[The Error Trait]] · [[Result]] · [[Error Handling with thiserror]] · [[Application Errors with anyhow]] · [[Boxing Errors]] · [[Adding Error Context]] · [[Error Handling]]

## Sources
- Rust standard library, `std::error::Error` — [[std]],
  https://doc.rust-lang.org/std/error/trait.Error.html
- The Rust Programming Language, ch. 9.2 "Recoverable Errors with `Result`" — https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html
