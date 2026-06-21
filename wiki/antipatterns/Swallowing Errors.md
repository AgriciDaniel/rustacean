---
type: antipattern
title: "Swallowing Errors"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, diagnostics, logging]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Result]]", "[[Option vs Result]]", "[[Adding Error Context]]", "[[Error Sources and Chains]]", "[[Propagating Errors]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html", "https://doc.rust-lang.org/std/result/enum.Result.html", "https://doc.rust-lang.org/std/option/enum.Option.html"]
rust_version: "edition 2024 / 1.85+"
---

# Swallowing Errors

Swallowing errors means discarding a failure without handling, propagating, logging at the right boundary, or documenting why it is safe to ignore.

## The mistake
Common forms include `let _ = fallible_call();`, converting `Result` to `Option` with `.ok()` too early, returning defaults for every error, and logging an error but continuing as if the operation succeeded.

Sometimes ignoring an error is correct.
The antipattern is ignoring it silently or before you know whether the caller needed it.

## Why it happens
Rust makes failures explicit, but it still lets you discard values.
A developer may silence a warning, avoid changing a return type, or treat an error as unlikely.

The result is usually worse diagnostics.
The visible symptom appears later, far away from the real cause, with the original [[Error Sources and Chains]] gone.
`Result` is marked `#[must_use]`, so the compiler helps catch accidental discards.
But explicit discards, broad defaults, and early `.ok()` conversions can still erase the failure deliberately.
Good code makes the discard policy obvious and narrow.

## Example
```rust
use std::fs;
use std::io;

fn read_optional_config(path: &str) -> Result<Option<String>, io::Error> {
    match fs::read_to_string(path) {
        Ok(text) => Ok(Some(text)),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(None),
        Err(error) => Err(error),
    }
}

fn main() {
    let config = read_optional_config("missing.toml");
    assert!(matches!(config, Ok(None) | Err(_)));
}
```

## Second example
If cleanup failure is ignorable, say so in code and keep it narrow.

```rust
use std::fs;
use std::io;

fn remove_cache_file(path: &str) -> Result<(), io::Error> {
    match fs::remove_file(path) {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error),
    }
}

fn main() {
    let _ = remove_cache_file("target/nonexistent-cache-file");
}
```

## Common errors
Accidentally ignoring a fallible call produces:

```text
warning: unused `Result` that must be used
```

Fix it by propagating with `?`, handling specific expected errors, or assigning to a named `_ignored` variable with a comment when the discard is intentional.
Avoid `.ok()` unless losing the reason is exactly what the caller needs.

## Best practice
- ✅ Ignore only specific, understood errors, and encode that decision in code.
- ✅ Convert to `Option` only when the error reason truly no longer matters; see [[Option vs Result]].
- ✅ Propagate unexpected errors with `?`.
- ✅ Add context before handing errors to application-level reporting.
- ✅ Let the compiler warning push you toward a real decision instead of silencing it mechanically.
- ✅ Prefer `match` with guards for expected ignorable cases such as `NotFound`.

## Pitfalls
- ⚠️ `let _ = result;` silences `#[must_use]` without making a decision visible.
- ⚠️ `.unwrap_or_default()` can hide parse or IO failures behind plausible empty values.
- ⚠️ Logging and continuing may still be wrong if the caller needed to know the operation failed.
- ⚠️ Converting every error to `None` erases the difference between absence and failure.
- ⚠️ Retrying after swallowing the original error can make logs point at the retry symptom rather than the root cause.

## See also
[[Result]] · [[Option vs Result]] · [[Propagating Errors]] · [[Adding Error Context]] · [[Error Sources and Chains]] · [[Application Errors with anyhow]] · [[Unwrap and Expect Overuse]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "Recoverable Errors with `Result`" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html
- Rust standard library, `Result` and `Option` — https://doc.rust-lang.org/std/result/enum.Result.html and https://doc.rust-lang.org/std/option/enum.Option.html
