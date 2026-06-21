---
type: concept
title: "Option vs Result"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, option, result, errors]
domain: "Error Handling"
difficulty: basic
related: ["[[Result]]", "[[The Question Mark Operator]]", "[[Recoverable vs Unrecoverable Errors]]", "[[Custom Error Types]]", "[[Stringly-Typed Errors]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#where-to-use-the--operator", "https://doc.rust-lang.org/std/option/enum.Option.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Option vs Result

Use `Option<T>` when absence is the whole story; use `Result<T, E>` when the caller needs to know why an operation failed.

## What it is
`Option<T>` represents either `Some(T)` or `None`.
It is right for lookups, optional fields, and APIs where absence is expected and no additional diagnostic is needed.

`Result<T, E>` represents either `Ok(T)` or `Err(E)`.
It is right when failure carries a reason, should be reported, or needs different handling by the caller.

## How it works
Both `Option` and `Result` work with [[The Question Mark Operator]], but they do not automatically convert into each other.
Use `.ok_or(error)` or `.ok_or_else(|| error)` to turn `Option<T>` into `Result<T, E>`.
Use `.ok()` to discard a `Result` error intentionally, but do so sparingly because it can become [[Swallowing Errors]].

Choosing between them is an information-design decision.
If the caller can act on the cause, keep the cause.
`Option` composes well with lookup APIs such as `get`, `first`, `find`, and `checked_*` arithmetic.
`Result` composes with error conversion, source chains, and reporting.
The conversion point should be visible in code because it is where "not present" becomes "this operation failed."

## Example
```rust
fn find_user(id: u64) -> Option<&'static str> {
    match id {
        1 => Some("Ada"),
        _ => None,
    }
}

fn require_user(id: u64) -> Result<&'static str, String> {
    find_user(id).ok_or_else(|| format!("user {id} does not exist"))
}

fn main() {
    assert_eq!(find_user(1), Some("Ada"));
    assert_eq!(find_user(2), None);
    assert_eq!(require_user(1), Ok("Ada"));
    assert!(require_user(2).is_err());
}
```

## Second example
When parsing optional input, keep missing fields distinct from malformed fields.

```rust
#[derive(Debug, PartialEq, Eq)]
enum PortError {
    Missing,
    Invalid,
}

fn parse_optional_port(input: Option<&str>) -> Result<Option<u16>, PortError> {
    let Some(text) = input else {
        return Ok(None);
    };
    let port = text.parse::<u16>().map_err(|_| PortError::Invalid)?;
    Ok(Some(port))
}

fn require_port(input: Option<&str>) -> Result<u16, PortError> {
    parse_optional_port(input)?.ok_or(PortError::Missing)
}

fn main() {
    assert_eq!(parse_optional_port(None), Ok(None));
    assert_eq!(require_port(Some("8080")), Ok(8080));
    assert_eq!(require_port(Some("abc")), Err(PortError::Invalid));
}
```

## Common errors
Using `?` on an `Option` inside a `Result` function usually fails with:

```text
error[E0277]: the `?` operator can only be used on `Result`s, not `Option`s, in a function that returns `Result`
```

Fix it by choosing the error explicitly: `maybe_value.ok_or_else(|| MyError::MissingField)?`.
That choice is part of the API, not boilerplate.

## Best practice
- ✅ Return `Option` for simple absence: cache miss, collection lookup, optional parsed field.
- ✅ Return [[Result]] when the caller or logs need a reason.
- ✅ Convert explicitly at the boundary where absence becomes an error.
- ✅ Use `ok_or_else` when constructing the error is nontrivial or allocates.
- ✅ Consider `Result<Option<T>, E>` when absence is valid but the lookup itself can fail.
- ✅ Use `Option::is_none_or` or `is_some_and` for simple predicates without destructuring.

## Pitfalls
- ⚠️ Returning `None` for multiple distinct failures forces callers to guess.
- ⚠️ Calling `.ok()` on a `Result` discards the error; see [[Swallowing Errors]].
- ⚠️ Encoding errors as `Option<String>` is usually a confused version of [[Result]].
- ⚠️ Using `unwrap` on `Option` for expected absence is [[Unwrap and Expect Overuse]].
- ⚠️ `Result<Option<T>, E>` can be clearer than nested ad hoc sentinels such as `Ok(0)` meaning "missing."

## See also
[[Result]] · [[The Question Mark Operator]] · [[Propagating Errors]] · [[Recoverable vs Unrecoverable Errors]] · [[Custom Error Types]] · [[Swallowing Errors]] · [[Stringly-Typed Errors]] · [[Unwrap and Expect Overuse]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "Where to Use the `?` Operator" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#where-to-use-the--operator
- Rust standard library, `Option` and `Result` — https://doc.rust-lang.org/std/option/enum.Option.html and https://doc.rust-lang.org/std/result/enum.Result.html
