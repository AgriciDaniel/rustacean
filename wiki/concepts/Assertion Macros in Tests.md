---
type: concept
title: "Assertion Macros in Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, assertions]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Test Functions]]", "[[Result Returning Tests]]", "[[Broad should_panic Tests]]", "[[panic!]]", "[[Debug]]", "[[PartialEq]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-01-writing-tests.html#checking-results-with-assert", "https://doc.rust-lang.org/book/ch11-01-writing-tests.html#testing-equality-with-assert_eq-and-assert_ne"]
rust_version: "edition 2024 / 1.85+"
---

# Assertion Macros in Tests

Rust assertion macros turn expected behavior into executable checks: `assert!` checks a boolean condition, while `assert_eq!` and `assert_ne!` compare values and print useful diagnostics on failure.

## What it is
`assert!`, `assert_eq!`, and `assert_ne!` are standard macros used heavily in tests. If the assertion is false, the macro panics, and the test harness marks the test as failed.

Use `assert!` when the meaningful outcome is a predicate. Use `assert_eq!` when a value should equal a known result. Use `assert_ne!` when you only know a value must differ from another value.

All assertion macros accept optional custom failure-message arguments after their required arguments. Those arguments are formatted like `format!`, so they can include values that make the failure actionable.

## How it works
`assert_eq!` and `assert_ne!` use `==` and `!=` internally. When they fail, they print both compared values with debug formatting, so custom structs and enums need `PartialEq` and `Debug`.

Rust reports equality assertion sides as `left` and `right`, not as `expected` and `actual`. The order still matters for human readability, so use a consistent convention in a codebase.

`assert!` prints only the failed expression unless you provide a message. For predicates over strings, collections, or domain state, a custom message usually saves a debugging step.

The macros evaluate their inputs before panicking, then delegate failure to `panic!`. This means they
have the same control-flow behavior as any other panic in a test: destructors run during unwinding,
the harness records the panic, and later test sections may stop if an earlier test binary failed.

## Example
```rust
#[derive(Debug, PartialEq)]
struct Greeting(String);

fn greeting(name: &str) -> Greeting {
    Greeting(format!("Hello, {name}!"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn greeting_contains_name() {
        let result = greeting("Carol");
        assert!(
            result.0.contains("Carol"),
            "greeting should include the name; got {result:?}"
        );
        assert_eq!(result, Greeting(String::from("Hello, Carol!")));
    }
}
```

## More realistic example
```rust
#[derive(Debug, PartialEq)]
struct User {
    id: u64,
    email: String,
}

fn parse_user(row: &str) -> Option<User> {
    let (id, email) = row.split_once(',')?;
    Some(User {
        id: id.parse().ok()?,
        email: email.trim().to_lowercase(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_user_row_and_normalizes_email() {
        let user = parse_user("42, ROOT@EXAMPLE.COM").expect("row should parse");

        assert_eq!(user.id, 42);
        assert_eq!(user.email, "root@example.com");
        assert_ne!(user.email, "ROOT@EXAMPLE.COM", "email should be normalized");
    }
}
```

## Common errors
`assert_eq!` and `assert_ne!` need both equality and debug formatting. A custom type without those
traits produces compiler errors like:

```text
error[E0369]: binary operation `==` cannot be applied to type `User`
error[E0277]: `User` doesn't implement `Debug`
```

Fix by deriving or implementing the traits when equality is meaningful:

```rust
#[derive(Debug, PartialEq)]
struct User {
    id: u64,
}
```

## Best practice
- ✅ Prefer `assert_eq!` over `assert!(left == right)` so failures show both values.
- ✅ Derive `Debug` and `PartialEq` on small test-facing domain types to make assertions direct.
- ✅ Add custom messages when the assertion expression does not explain the domain expectation.
- ✅ Assert stable behavior, not incidental formatting or private implementation details.
- ✅ Use `matches!` inside `assert!` for enum-shape checks, then separately assert payload details when those matter.
- ✅ Put the value under test in a named local before asserting when the expression is complex; failure output and debugger use improve.

## Pitfalls
- ⚠️ Using `assert!` for equality hides the actual values that caused the failure.
- ⚠️ Writing assertions so broad that they pass for the wrong reason creates the same weakness as [[Broad should_panic Tests]].
- ⚠️ Overusing `assert_ne!` can leave the expected behavior underspecified; prefer exact expected values when the contract is exact.
- ⚠️ Comparing formatted strings when the real contract is structured data makes tests brittle; assert the structure before display text.

## See also
[[Test Functions]] · [[Result Returning Tests]] · [[Broad should_panic Tests]] · [[Unit Tests]] · [[Integration Tests]] · [[panic!]] · [[Debug]] · [[PartialEq]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.1 "Checking Results with assert!" — [[the-book]], https://doc.rust-lang.org/book/ch11-01-writing-tests.html#checking-results-with-assert
- The Rust Programming Language, ch. 11.1 "Testing Equality with assert_eq! and assert_ne!" — [[the-book]], https://doc.rust-lang.org/book/ch11-01-writing-tests.html#testing-equality-with-assert_eq-and-assert_ne
