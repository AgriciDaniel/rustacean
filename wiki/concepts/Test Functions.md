---
type: concept
title: "Test Functions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, test-attribute]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Assertion Macros in Tests]]", "[[Unit Tests]]", "[[Integration Tests]]", "[[Test Harness and cargo test]]", "[[Result Returning Tests]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-01-writing-tests.html", "https://doc.rust-lang.org/reference/attributes/testing.html#the-test-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Test Functions

Test functions are ordinary Rust functions marked with `#[test]`; when compiled in test mode, the harness discovers them, runs them, and classifies each as passed or failed.

## What it is
The `#[test]` attribute marks a free function as a test. Running `cargo test` compiles the crate in test mode, builds a test harness, and executes those functions.

A test usually does three things: set up data, run code under test, and assert the observed behavior. A test passes when it returns successful termination and does not panic; it fails when it panics or returns a failing termination value.

The Reference gives the precise shape: a `#[test]` function must be a monomorphic free function, take no arguments, and return a type that implements `std::process::Termination`.

## How it works
`cargo test` passes test-mode options through to `rustc`, which enables the `test` configuration option. Functions annotated with `#[test]` are compiled only in this mode, so they are available to the generated harness but are not part of a normal `cargo build`.

Most tests return `()`. Tests may also return `Result<(), E>` where `E: Debug`, which is useful when setup can fail and the `?` operator makes the test clearer.

Test names are paths. For a unit test inside `mod tests`, the harness reports a name such as `tests::parses_port`, and that path can be used as a filter with `cargo test parses_port`.

Under the hood, a test build is not the same artifact as a normal library build. The compiler sees
the `test` cfg, includes test-only modules, and emits a binary whose generated `main` function calls
the harness. The harness runs each registered test, catches panic-based failure, interprets the
`Termination` result, captures output, and then prints the summary.

## Example
```rust
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_two_numbers() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

## More realistic example
```rust
pub fn parse_nonzero_port(text: &str) -> Result<u16, &'static str> {
    let port = text.parse::<u16>().map_err(|_| "not a number")?;
    if port == 0 {
        return Err("port 0 is reserved for automatic assignment");
    }
    Ok(port)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_valid_nonzero_port() {
        assert_eq!(parse_nonzero_port("443"), Ok(443));
    }

    #[test]
    fn rejects_zero_port() {
        assert_eq!(
            parse_nonzero_port("0"),
            Err("port 0 is reserved for automatic assignment")
        );
    }
}
```

## Common errors
Putting `#[test]` on a method or generic function is rejected because the harness needs a concrete
zero-argument free function to call.

```text
error: the `#[test]` attribute may only be used on a non-associated function
```

Fix by moving the test into a `#[cfg(test)] mod tests` free function. If the code under test is a
method, construct the receiver inside the test and call the method there.

## Best practice
- ✅ Give tests behavior names such as `rejects_empty_input` rather than generic names such as `test_1`.
- ✅ Keep each test focused on one observable behavior so a failure points at a small cause.
- ✅ Put shared setup in helper functions, but keep the assertion in the test body where the expected behavior is visible.
- ✅ Use `Result`-returning tests when setup uses fallible APIs; use assertion macros for the actual condition.
- ✅ Name edge-case tests after the boundary they protect, such as `rejects_zero_port` or `accepts_max_u16_port`.
- ✅ Keep test data local unless sharing it materially reduces noise; hidden coupling between tests is harder to see than duplicated literals.

## Pitfalls
- ⚠️ Putting `#[test]` on methods, generic functions, or functions with parameters is outside the allowed shape for test functions.
- ⚠️ Testing only the happy path gives false confidence; add edge cases and error-path tests with [[Assertion Macros in Tests]] or [[Result Returning Tests]].
- ⚠️ Using one broad test for many unrelated behaviors makes failures noisy; split it unless the behaviors are intentionally coupled.
- ⚠️ Expecting tests to run in source order is incorrect; design each test to pass independently under the parallel harness.

## See also
[[Assertion Macros in Tests]] · [[Unit Tests]] · [[Integration Tests]] · [[Test Harness and cargo test]] · [[Result Returning Tests]] · [[Test-Driven Development in Rust]] · [[Ignored Tests]] · [[Shared State Between Parallel Tests]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.1 "How to Write Tests" — [[the-book]], https://doc.rust-lang.org/book/ch11-01-writing-tests.html
- The Rust Reference, "The test attribute" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/testing.html#the-test-attribute
