---
type: concept
title: "The Question Mark Operator"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, result, option, question-mark]
domain: "Error Handling"
difficulty: intermediate
related: ["[[Result]]", "[[Option vs Result]]", "[[Propagating Errors]]", "[[Custom Error Types]]", "[[Returning Result from main]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#the--operator-shortcut", "https://doc.rust-lang.org/std/result/", "https://doc.rust-lang.org/std/convert/trait.From.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Question Mark Operator

The `?` operator unwraps success and returns early on failure, converting the error with `From::from` when needed.

## What it is
`?` is postfix syntax for common propagation code.
On `Result<T, E>`, it yields `T` for `Ok(T)` and returns `Err(...)` from the current function for `Err(E)`.
On `Option<T>`, it yields `T` for `Some(T)` and returns `None` for `None`.

It is the core ergonomic tool behind [[Propagating Errors]].

## How it works
For `Result`, `?` does not merely return the original error.
It converts the error into the current function's error type through the `From` trait.
That is why `impl From<io::Error> for MyError` or `#[from]` in [[Error Handling with thiserror]] makes `?` work across several error sources.

The current function must return a compatible type: usually `Result<_, E>` for `Result` propagation or `Option<_>` for `Option` propagation.
Use `ok_or`, `ok_or_else`, or `Result::ok` when converting explicitly between [[Option vs Result]].
Conceptually, `expr?` is a match: success unwraps the inner value, failure returns from the surrounding function.
The real implementation is based on the language's `Try` machinery, but on stable Rust you should design around the visible contracts: `Result`, `Option`, and `From` conversions.
The operator never logs, never adds context by itself, and never retries.

## Example
```rust
use std::fs;
use std::io;

fn first_line(path: &str) -> Result<String, io::Error> {
    let text = fs::read_to_string(path)?;
    Ok(text.lines().next().unwrap_or("").to_string())
}

fn last_char_of_first_line(text: &str) -> Option<char> {
    text.lines().next()?.chars().last()
}

fn main() {
    assert_eq!(last_char_of_first_line("abc\ndef"), Some('c'));
    assert_eq!(last_char_of_first_line(""), None);
    let _ = first_line("Cargo.toml");
}
```

## Second example
When moving from lookup-style code to error-reporting code, convert `Option` into `Result` at the boundary where the missing value becomes a failure.

```rust
fn env_value<'a>(pairs: &'a [(&str, &str)], key: &str) -> Result<&'a str, String> {
    pairs
        .iter()
        .find(|(name, _)| *name == key)
        .map(|(_, value)| *value)
        .ok_or_else(|| format!("missing required setting {key}"))
}

fn first_char(pairs: &[(&str, &str)], key: &str) -> Result<char, String> {
    let value = env_value(pairs, key)?;
    value.chars().next().ok_or_else(|| format!("{key} is empty"))
}

fn main() {
    let pairs = [("HOST", "localhost")];
    assert_eq!(first_char(&pairs, "HOST"), Ok('l'));
    assert!(first_char(&pairs, "PORT").is_err());
}
```

## Common errors
Using `?` in a function that returns `()` commonly produces:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`
```

Using `?` on an `Option` inside a `Result` function produces the same family of error because Rust will not invent an error value for `None`.
Fix it with `ok_or_else`, or change the function to return `Option` if absence is the whole contract.

## Best practice
- ✅ Use `?` when the current function cannot add meaningful recovery logic at that level.
- ✅ Define `From` conversions intentionally, usually with [[Custom Error Types]] or [[Error Handling with thiserror]].
- ✅ Add context before `?` at abstraction boundaries; see [[Adding Error Context]].
- ✅ Keep the surrounding function signature honest: `Result` means failure is part of the contract.
- ✅ Convert `Option` to `Result` with a specific error at the point where missing data becomes a reportable failure.
- ✅ Prefer `with_context` or typed wrapper variants before `?` when a low-level error lacks the operation name.

## Pitfalls
- ⚠️ `?` cannot be used in a function returning `()` unless you change the return type or handle the error locally.
- ⚠️ `?` does not automatically convert `Option` to `Result`; use `ok_or_else` and choose an error.
- ⚠️ Blind propagation can produce context-poor errors; see [[Adding Error Context]].
- ⚠️ Too many automatic conversions can hide which failures callers can actually handle.
- ⚠️ A broad `From` impl can make unrelated errors collapse into a variant that callers cannot interpret.

## See also
[[Result]] · [[Option vs Result]] · [[Propagating Errors]] · [[Returning Result from main]] · [[Custom Error Types]] · [[Error Handling with thiserror]] · [[Adding Error Context]] · [[Application Errors with anyhow]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "The `?` Operator Shortcut" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#the--operator-shortcut
- Rust standard library, `std::result` module — https://doc.rust-lang.org/std/result/
