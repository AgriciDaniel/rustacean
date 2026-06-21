---
type: pattern
title: "Adding Error Context"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, context, diagnostics]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Error Sources and Chains]]", "[[Application Errors with anyhow]]", "[[Error Handling with thiserror]]", "[[Propagating Errors]]", "[[Stringly-Typed Errors]]", "[[Error Handling]]"]
sources: ["[[anyhow]]", "[[thiserror]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/io/struct.Error.html", "https://doc.rust-lang.org/std/fmt/trait.Display.html"]
rust_version: "edition 2024 / 1.85+"
---

# Adding Error Context

Adding error context records what your code was trying to do so a low-level failure becomes actionable.

## What it is
Many source errors are technically accurate but incomplete.
`io::ErrorKind::NotFound` says a file was missing, but not which operation needed it or why it mattered.

Context belongs at abstraction boundaries.
Each layer should add the information only that layer knows, while preserving [[Error Sources and Chains]].

## How it works
In application code, `anyhow::Context` provides `.context(...)` and `.with_context(...)`.
In typed library code, add fields to [[Custom Error Types]] and expose the lower-level cause via `source`.

Context should be specific: include paths, IDs, user names, operation names, or external service names when they matter.
Do not replace the source error with a string.
Good context answers "what was this code trying to do?" while the source answers "what mechanism failed?"
Context belongs near the operation because that is where path, key, request ID, or operation name are still available.
The final reporter can then print a useful chain without every intermediate layer logging.

## Example
```rust
use std::error::Error;
use std::fmt;
use std::fs;
use std::io;

#[derive(Debug)]
struct ReadConfigError {
    path: String,
    source: io::Error,
}

impl fmt::Display for ReadConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "failed to read config {}", self.path)
    }
}

impl Error for ReadConfigError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        Some(&self.source)
    }
}

fn read_config(path: &str) -> Result<String, ReadConfigError> {
    fs::read_to_string(path).map_err(|source| ReadConfigError {
        path: path.to_string(),
        source,
    })
}

fn main() {
    let _ = read_config("app.toml");
}
```

## Second example
In application code, use lazy context for values that only matter on the error path.

```rust
// Cargo.toml: anyhow = "1"
use anyhow::{Context, Result};
use std::fs;
use std::path::Path;

fn read_profile(path: &Path) -> Result<String> {
    fs::read_to_string(path)
        .with_context(|| format!("failed to read profile {}", path.display()))
}

fn main() -> Result<()> {
    let _ = read_profile(Path::new("profile.toml"))?;
    Ok(())
}
```

## Common errors
Replacing an error with formatted prose destroys the chain:

```text
fs::read_to_string(path).map_err(|error| format!("failed: {error}"))?
```

The next `?` often fails because `String` does not implement `Error` in the way the surrounding type expects, and even when it compiles the source is gone.
Fix it with a typed wrapper that stores `source`, or with `anyhow::Context` in application code.

## Best practice
- ✅ Add context where information would otherwise be lost, especially around IO and external systems.
- ✅ Preserve the original source error so root-cause details remain available.
- ✅ Make messages useful to the operator or caller, not just to the function author.
- ✅ Prefer lazy context construction when formatting strings only matters on the error path.
- ✅ Include stable identifiers such as paths, IDs, and operation names; avoid dumping secrets.
- ✅ Add context once per abstraction boundary, not once per line of code.

## Pitfalls
- ⚠️ Replacing an error with `format!("{error}")` destroys its type and source chain.
- ⚠️ Adding vague context like "operation failed" gives no extra signal.
- ⚠️ Duplicating the source message in every layer creates noisy reports.
- ⚠️ Logging context at every propagation point can be as bad as [[Swallowing Errors]] in production diagnostics.
- ⚠️ Context that includes raw user input may leak sensitive data into logs or crash reports.

## See also
[[Error Sources and Chains]] · [[Application Errors with anyhow]] · [[Error Handling with thiserror]] · [[Propagating Errors]] · [[Custom Error Types]] · [[The Error Trait]] · [[Stringly-Typed Errors]] · [[Error Handling]]

## Sources
- `anyhow::Context` documentation — [[anyhow]], https://docs.rs/anyhow/latest/anyhow/trait.Context.html
- Rust standard library, `Error` and `io::Error` — https://doc.rust-lang.org/std/error/trait.Error.html and https://doc.rust-lang.org/std/io/struct.Error.html
