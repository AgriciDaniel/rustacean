---
type: concept
title: "Error Sources and Chains"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, source, diagnostics]
domain: "Error Handling"
difficulty: intermediate
related: ["[[The Error Trait]]", "[[Adding Error Context]]", "[[Custom Error Types]]", "[[Application Errors with anyhow]]", "[[Error Handling with thiserror]]", "[[Error Handling]]"]
sources: ["[[std]]", "[[anyhow]]", "[[thiserror]]"]
source_urls: ["https://doc.rust-lang.org/std/error/trait.Error.html", "https://doc.rust-lang.org/std/result/enum.Result.html", "https://doc.rust-lang.org/std/fmt/trait.Display.html"]
rust_version: "edition 2024 / 1.85+"
---

# Error Sources and Chains

An error chain is a sequence of causes exposed through `Error::source()`, letting reports show both high-level context and the root failure.

## What it is
Many useful errors wrap lower-level errors.
For example, "failed to load config" may wrap "no such file or directory".
The outer error explains the operation; the inner source explains the mechanism.

[[The Error Trait]] standardizes this relationship with `source() -> Option<&(dyn Error + 'static)>`.

## How it works
Each layer's `Display` should describe that layer.
The source should be returned from `source()`, not copied into every `Display` message.
Generic reporters can then walk the chain and decide how much detail to print.

[[Error Handling with thiserror]] can mark sources with `#[source]` or infer them from a field named `source`.
[[Application Errors with anyhow]] keeps chains and prints them with alternate formatting such as `{:#}`.
On stable Rust, the chain is a linked list: each error returns at most one immediate source.
If an operation has several peer failures, model them in your custom type instead of trying to force several sources into `source()`.
Reporters should treat the exact chain shape as diagnostic information unless the API documents it as stable behavior.

## Example
```rust
use std::error::Error;
use std::fmt;
use std::io;

#[derive(Debug)]
struct LoadError {
    path: String,
    source: io::Error,
}

impl fmt::Display for LoadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "failed to load {}", self.path)
    }
}

impl Error for LoadError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        Some(&self.source)
    }
}

fn main() {
    let error = LoadError {
        path: "config.toml".to_string(),
        source: io::Error::new(io::ErrorKind::NotFound, "missing"),
    };
    assert_eq!(error.to_string(), "failed to load config.toml");
    assert!(error.source().is_some());
}
```

## Second example
Walking a chain is straightforward because each `source()` returns the next lower-level error.

```rust
use std::error::Error;
use std::io;

fn chain_messages(mut error: &(dyn Error + 'static)) -> Vec<String> {
    let mut messages = vec![error.to_string()];
    while let Some(source) = error.source() {
        messages.push(source.to_string());
        error = source;
    }
    messages
}

fn main() {
    let source = io::Error::new(io::ErrorKind::PermissionDenied, "denied");
    let error: Box<dyn Error> = Box::new(source);
    assert_eq!(chain_messages(error.as_ref()), vec!["denied".to_string()]);
}
```

## Common errors
The most common diagnostic failure is duplicated output:

```text
failed to load config.toml: No such file or directory
caused by: No such file or directory
```

Fix it by keeping the outer `Display` focused on the high-level operation and returning the lower error from `source()`.
Do not paste `source` into `Display` and also expose it through the chain.

## Best practice
- ✅ Store the original error when wrapping so the root cause remains available.
- ✅ Put operation-specific detail in the outer error and mechanism-specific detail in the source.
- ✅ Let the final reporting boundary decide how to print the chain.
- ✅ Use [[Adding Error Context]] at abstraction boundaries where information would otherwise be lost.
- ✅ Keep source relationships acyclic and simple; one wrapper should point to the immediate cause.
- ✅ Test `source()` on custom error types when chain preservation is part of the design.

## Pitfalls
- ⚠️ Duplicating source text inside `Display` causes repeated messages when a reporter walks the chain.
- ⚠️ Discarding the source while adding context makes diagnosis much harder.
- ⚠️ Logging every layer of the chain creates duplicate noise; see [[Swallowing Errors]] for the opposite failure mode.
- ⚠️ Treating chains as stable public structure can be brittle unless your API documents that contract.
- ⚠️ Returning a source that borrows non-`'static` data will not satisfy `Error::source()`; store an owned source error instead.

## See also
[[The Error Trait]] · [[Adding Error Context]] · [[Custom Error Types]] · [[Error Handling with thiserror]] · [[Application Errors with anyhow]] · [[Boxing Errors]] · [[Stringly-Typed Errors]] · [[Error Handling]]

## Sources
- Rust standard library, `std::error::Error` and `source()` — [[std]],
  https://doc.rust-lang.org/std/error/trait.Error.html
- Rust standard library, `Display` — https://doc.rust-lang.org/std/fmt/trait.Display.html
