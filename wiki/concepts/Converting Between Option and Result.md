---
type: concept
title: "Converting Between Option and Result"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, conversion, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option vs Result]]", "[[Option Combinators]]", "[[Result Combinators]]", "[[Converting Option to Result with ok_or]]", "[[Question Mark with Option]]", "[[Swallowing Errors]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or_else", "https://doc.rust-lang.org/std/result/enum.Result.html#method.ok", "https://doc.rust-lang.org/std/result/enum.Result.html#method.err"]
rust_version: "edition 2024 / 1.85+"
---

# Converting Between Option and Result

Convert `Option` to `Result` when absence needs a reason, and convert `Result` to `Option` only when the error is intentionally irrelevant.

## What it is
`Option` represents presence or absence.
`Result` represents success or failure with an error value.
Conversions between them change how much failure information exists.
`Option::ok_or` and `Option::ok_or_else` add an error to the missing case.
`Result::ok` discards an error and keeps only the success value.
`Result::err` discards a success value and keeps only the error.
`transpose` changes nesting between `Option<Result<T, E>>` and `Result<Option<T>, E>`.
These methods are small, but they mark an important semantic boundary.
The boundary should match the API promise you want to make.
Absence is not automatically an error, and an error is not automatically ignorable.

## How it works
`Some(t).ok_or_else(f)` becomes `Ok(t)`.
`None.ok_or_else(f)` becomes `Err(f())`.
`Ok(t).ok()` becomes `Some(t)`.
`Err(e).ok()` becomes `None`, dropping `e`.
`Ok(t).err()` becomes `None`, dropping `t`.
`Err(e).err()` becomes `Some(e)`.
Use `ok()` for cases like parsing optional user input where all parse failures mean "not usable here."
Use `ok_or_else()` when a lookup failed and the caller needs a diagnostic.
Use `err()` mostly for tests, metrics, or branch-specific extraction.
Use `transpose()` when optional work can fail and you need to keep parse or I/O errors.
The direction of conversion should be visible in code review because it changes observability.

## Example
```rust
fn required_id(raw: Option<&str>) -> Result<u64, String> {
    let text = raw.ok_or_else(|| "missing id".to_string())?;
    text.parse::<u64>()
        .map_err(|err| format!("invalid id: {err}"))
}

fn optional_number(raw: &str) -> Option<u64> {
    raw.parse::<u64>().ok()
}

fn main() {
    assert_eq!(required_id(Some("42")), Ok(42));
    assert_eq!(required_id(None), Err("missing id".to_string()));
    assert!(required_id(Some("abc")).unwrap_err().starts_with("invalid id"));

    assert_eq!(optional_number("42"), Some(42));
    assert_eq!(optional_number("abc"), None);
}
```

## Best practice
- ✅ Use `Option` when absence is normal and needs no explanation.
- ✅ Use `Result` when callers need to react to or report failure.
- ✅ Use `ok_or_else` to add context at the point where absence becomes an error.
- ✅ Use `Result::ok` only when discarding the error is part of the API contract.
- ✅ Use `transpose` instead of hand-matching optional fallible values.
- ✅ Keep conversion close to the reason for conversion.
- ✅ Prefer custom error variants over generic strings in reusable libraries.
- ✅ Add tests for both conversion directions when error loss is intentional.

## Pitfalls
- ⚠️ `result.ok()` can silently swallow parse, I/O, or validation errors; see [[Swallowing Errors]].
- ⚠️ `ok_or` eagerly builds its error value; see [[Eager Work in Option and Result Defaults]].
- ⚠️ Turning every `None` into `Err("missing")` can overstate normal absence.
- ⚠️ Turning every `Err` into `None` can make production failures look like empty data.
- ⚠️ `Option` cannot carry an error source chain; use `Result` for diagnostics.
- ⚠️ Mixed `Option<Result<...>>` and `Result<Option<...>>` often needs [[Transpose and Flatten]].

## See also
[[std: Option & Result Combinators]] ·
[[Option]] ·
[[Result]] ·
[[Option vs Result]] ·
[[Converting Option to Result with ok_or]] ·
[[Question Mark with Option]] ·
[[Transpose and Flatten]] ·
[[Propagating Errors]] ·
[[Recoverable vs Unrecoverable Errors]] ·
[[Swallowing Errors]] ·
[[Custom Error Types]]

## Sources
- Rust standard library, `Option::ok_or` and `Option::ok_or_else` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or_else
- Rust standard library, `Result::ok` and `Result::err` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html#method.ok
