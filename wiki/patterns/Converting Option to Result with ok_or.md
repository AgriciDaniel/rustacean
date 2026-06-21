---
type: pattern
title: "Converting Option to Result with ok_or"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, errors, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Converting Between Option and Result]]", "[[Question Mark with Option]]", "[[Lazy Evaluation]]", "[[Propagating Errors]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or", "https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or_else"]
rust_version: "edition 2024 / 1.85+"
---

# Converting Option to Result with ok_or

Use `ok_or` or `ok_or_else` when a missing `Option` value should become a `Result::Err` with an explicit reason.

## What it is
`Option<T>::ok_or` converts `Some(value)` into `Ok(value)` and `None` into `Err(err)`.
`Option<T>::ok_or_else` does the same conversion, but builds the error with a closure only when the option is `None`.
This is the standard bridge from optional lookup into recoverable error handling.
It is most useful at API boundaries where the caller needs to know why absence matters.
It pairs naturally with the `?` operator in functions returning `Result`.
It is also common after `HashMap::get`, slice `get`, iterator `find`, and configuration lookups.
Use it when `None` has become a domain error, not merely an allowed absence.
The conversion consumes the `Option`, so use `as_ref`, `as_deref`, or `copied` first when needed.
The error type can be a simple string, enum variant, custom error, or any type your function returns.
The important point is that the missing case becomes named and propagated.

## How it works
For `Some(t)`, both methods return `Ok(t)`.
For `None`, `ok_or(err)` returns `Err(err)` after evaluating `err`.
For `None`, `ok_or_else(|| err)` calls the closure and returns `Err(err)`.
For `Some(t)`, `ok_or_else` does not call the closure.
That lazy behavior matters when constructing the error allocates, formats, reads state, or clones data.
In a `Result`-returning function, `?` can immediately return the constructed error.
When borrowing from an `Option<String>`, `as_deref().ok_or_else(...)` yields `Result<&str, E>`.
When copying from an `Option<u32>`, `ok_or_else(...)` can move or copy the integer directly.
The method does not inspect why the option was missing; you choose the error message or variant.
That makes the call site responsible for good context.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct Config {
    token: Option<String>,
}

fn token(config: &Config) -> Result<&str, String> {
    config
        .token
        .as_deref()
        .ok_or_else(|| "missing auth token".to_string())
}

fn main() -> Result<(), String> {
    let config = Config {
        token: Some("abc123".to_string()),
    };

    assert_eq!(token(&config)?, "abc123");

    let missing = Config { token: None };
    assert_eq!(token(&missing), Err("missing auth token".to_string()));

    Ok(())
}
```

## Best practice
- ✅ Prefer `ok_or_else` when the error is allocated, formatted, cloned, or otherwise nontrivial.
- ✅ Use `ok_or` for cheap constants, enum variants, and copyable sentinel errors.
- ✅ Put enough context in the error for the caller to fix the missing value.
- ✅ Use `as_ref` or `as_deref` before conversion when you need to borrow rather than move.
- ✅ Use a real custom error type for library APIs instead of raw strings.
- ✅ Follow `ok_or_else(...)?` with straight-line code when absence should return early.
- ✅ Keep the conversion near the lookup so the error context stays local.
- ✅ Consider returning `Option` instead when absence is expected and needs no explanation.

## Pitfalls
- ⚠️ `ok_or(format!(...))` formats even when the option is `Some`; see [[Eager Work in Option and Result Defaults]].
- ⚠️ `ok_or("missing")` with a vague message can make debugging worse than a direct `match`.
- ⚠️ Calling `unwrap` after `is_some` is more fragile than converting once; see [[Is Some Then Unwrap]].
- ⚠️ Converting too early can force callers to handle errors for normal optional data.
- ⚠️ `ok_or_else` closures take no argument because `None` has no contained value to inspect.
- ⚠️ If you need to validate a present value too, use `and_then` or `Result` logic after the conversion.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Converting Between Option and Result]] ·
[[Question Mark with Option]] ·
[[Lazy Evaluation]] ·
[[Propagating Errors]] ·
[[Custom Error Types]] ·
[[The Question Mark Operator]] ·
[[Option vs Result]] ·
[[Eager Work in Option and Result Defaults]]

## Sources
- Rust standard library, `Option::ok_or` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or
- Rust standard library, `Option::ok_or_else` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or_else
