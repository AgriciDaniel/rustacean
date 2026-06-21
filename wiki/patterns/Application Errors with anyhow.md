---
type: pattern
title: "Application Errors with anyhow"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, anyhow, errors, applications]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Adding Error Context]]", "[[Propagating Errors]]", "[[Returning Result from main]]", "[[Error Sources and Chains]]", "[[Error Handling with thiserror]]", "[[Error Handling]]"]
sources: ["[[anyhow]]", "[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/result/enum.Result.html", "https://doc.rust-lang.org/std/process/trait.Termination.html"]
rust_version: "edition 2024 / 1.85+"
---

# Application Errors with anyhow

`anyhow` gives applications one ergonomic error type plus context, ideal when code mostly reports failures instead of matching on variants.

## What it is
`anyhow::Error` is an opaque, trait-object-based error type for application-level error handling.
`anyhow::Result<T>` is a convenient alias for `Result<T, anyhow::Error>`.

Use it when the caller does not need a typed contract for every failure mode.
That is common in binaries, tests, examples, migration scripts, and top-level orchestration.

## How it works
Most errors implementing [[The Error Trait]] can be converted into `anyhow::Error` with `?`.
The `Context` trait adds human-readable context while preserving downcasting behavior.

For reusable libraries, prefer [[Error Handling with thiserror]] when consumers need to match on failures.
The real question is caller intent, not merely whether the code lives in a binary or library crate.
`anyhow::Error` is intentionally opaque: it optimizes for propagation and reporting, not for a stable public error enum.
It requires errors to be safe to send and share across threads, which matches most application infrastructure.
Context layers become part of the displayed chain while the original source remains available for debugging and downcasting.

## Example
```rust
// Cargo.toml: anyhow = "1"
use anyhow::{Context, Result};
use std::fs;

fn load_config(path: &str) -> Result<String> {
    let text = fs::read_to_string(path)
        .with_context(|| format!("failed to read config from {path}"))?;
    Ok(text)
}

fn run() -> Result<()> {
    let config = load_config("app.toml")?;
    println!("loaded {} bytes", config.len());
    Ok(())
}

fn main() -> Result<()> {
    run()
}
```

## Second example
Keep typed errors below an application boundary, then add context at the top.

```rust
// Cargo.toml: anyhow = "1", thiserror = "2"
use anyhow::{Context, Result};

#[derive(Debug, thiserror::Error)]
enum ParsePortError {
    #[error("port must be nonzero")]
    Zero,
    #[error("port is not a number")]
    Parse(#[from] std::num::ParseIntError),
}

fn parse_port(text: &str) -> std::result::Result<u16, ParsePortError> {
    let port = text.parse::<u16>()?;
    if port == 0 { Err(ParsePortError::Zero) } else { Ok(port) }
}

fn run() -> Result<()> {
    let port = parse_port("8080").context("invalid server port")?;
    println!("listening on {port}");
    Ok(())
}

fn main() -> Result<()> {
    run()
}
```

## Common errors
Returning `anyhow::Result` from a public library API is not a compiler error, but it creates a design error: callers cannot reliably match your failure modes.
When callers need branches such as retry, ask credentials again, or report validation errors by field, expose a typed error instead.
Use `anyhow` at the binary, test, migration, or orchestration boundary where reporting is the main behavior.

## Best practice
- ✅ Use `anyhow::Result` in application code where errors are reported rather than matched.
- ✅ Add `.context(...)` or `.with_context(...)` close to the operation that has missing human detail.
- ✅ Keep typed errors underneath when a module has meaningful internal branches.
- ✅ Convert to user-facing messages at the boundary where the error is actually handled.
- ✅ Prefer `.with_context(|| format!(...))` when formatting context allocates or is expensive.
- ✅ Downcast only for exceptional integration boundaries; normal control flow should use typed errors before conversion.

## Pitfalls
- ⚠️ Public library APIs returning `anyhow::Error` deny callers stable variants to match.
- ⚠️ Adding no context leaves opaque low-level messages like "permission denied".
- ⚠️ Logging at every `?` hop creates repeated reports of the same chain.
- ⚠️ Treating `anyhow` as a replacement for domain modeling leads to weak control flow.
- ⚠️ Converting to `anyhow::Error` too early can make tests assert on prose instead of structured behavior.

## See also
[[Adding Error Context]] · [[Propagating Errors]] · [[Returning Result from main]] · [[Error Sources and Chains]] · [[Error Handling with thiserror]] · [[Boxing Errors]] · [[Custom Error Types]] · [[Error Handling]]

## Sources
- `anyhow` crate documentation — [[anyhow]], https://docs.rs/anyhow/latest/anyhow/
- `anyhow::Context` documentation — https://docs.rs/anyhow/latest/anyhow/trait.Context.html
- Rust standard library, `Error` — https://doc.rust-lang.org/std/error/trait.Error.html
