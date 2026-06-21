---
type: antipattern
title: "Broad should_panic Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, panic]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Test Functions]]", "[[Assertion Macros in Tests]]", "[[Result Returning Tests]]", "[[panic!]]", "[[Panicking in Libraries]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-01-writing-tests.html#checking-for-panics-with-should_panic", "https://doc.rust-lang.org/reference/attributes/testing.html#the-should_panic-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Broad should_panic Tests

A broad `#[should_panic]` test is a footgun because any panic passes; prefer an `expected` substring or, better, return `Result` and assert the specific error.

## The mistake
`#[should_panic]` makes a test pass if the test function panics at all. That is useful for APIs whose contract is explicitly panic-based, but it is easy to write a test that passes for the wrong panic.

For example, a bounds-check panic, an unwrap panic in setup, or a typo in test data can satisfy `#[should_panic]` even when the intended validation logic never ran.

The Book calls this imprecision out directly and shows using `expected = "..."` to verify the panic message contains identifying text.

## Why it happens
Panics are coarse control flow from the test harness's perspective. A plain `#[should_panic]` has only one bit of information: did the test unwind or abort as expected?

The Reference supports more precise forms. `#[should_panic(expected = "some message")]` and `#[should_panic = "some message"]` require the panic message to contain the given string.

Many library APIs should not panic for recoverable user errors at all. In those cases, the correct alternative is returning `Result` and asserting `Err`.

The expected string is a substring match against the panic message, not an exact structured error.
That makes it useful but still less precise than matching a typed error. Use panic tests for violated
preconditions and programmer errors, not for ordinary invalid input that callers can recover from.

## Example
```rust
pub fn percentage(value: u8) -> u8 {
    if value > 100 {
        panic!("percentage must be at most 100");
    }
    value
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "at most 100")]
    fn rejects_values_above_100() {
        percentage(101);
    }
}
```

## Better alternative for recoverable input
```rust
#[derive(Debug, PartialEq)]
pub enum PercentageError {
    TooLarge,
}

pub fn percentage(value: u8) -> Result<u8, PercentageError> {
    if value > 100 {
        return Err(PercentageError::TooLarge);
    }
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_values_above_100() {
        assert_eq!(percentage(101), Err(PercentageError::TooLarge));
    }
}
```

## Common errors
`#[should_panic]` does not combine with `Result`-returning tests:

```text
error: functions using `#[should_panic]` must return `()`
```

Fix by either testing a panic with a `()` test function, or testing a recoverable error with
`Result`/`Err` assertions and no `#[should_panic]`.

## Best practice
- ✅ Use `#[should_panic(expected = "...")]` with a stable, unique substring when panic is the documented contract.
- ✅ Prefer `Result`-returning APIs for recoverable errors, then assert `is_err()` or the exact error variant.
- ✅ Keep setup before the panic point minimal so setup panics cannot masquerade as success.
- ✅ Document panic conditions in [[Documentation Comments]] under a `# Panics` section for public APIs.
- ✅ Put the panicking call as the last meaningful line of the test so unrelated cleanup or follow-up code cannot affect the result.
- ✅ Prefer a small identifying substring over a full dynamic panic message when the message includes values.

## Pitfalls
- ⚠️ Plain `#[should_panic]` can pass because of an unrelated panic.
- ⚠️ `#[should_panic]` requires a `()` test return type; it does not combine with [[Result Returning Tests]].
- ⚠️ Testing panic messages too exactly can be brittle if the message includes dynamic data; use the smallest identifying substring.
- ⚠️ Converting every invalid input into a panic makes APIs harder to compose; reserve panics for contracts callers should not violate.

## See also
[[Test Functions]] · [[Assertion Macros in Tests]] · [[Result Returning Tests]] · [[panic!]] · [[Panicking in Libraries]] · [[Documentation Comments]] · [[Recoverable vs Unrecoverable Errors]] · [[Test Harness and cargo test]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.1 "Checking for Panics with should_panic" — [[the-book]], https://doc.rust-lang.org/book/ch11-01-writing-tests.html#checking-for-panics-with-should_panic
- The Rust Reference, "The should_panic attribute" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/testing.html#the-should_panic-attribute
