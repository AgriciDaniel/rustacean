---
type: pattern
title: "Result Returning Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, result]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Test Functions]]", "[[Assertion Macros in Tests]]", "[[Result]]", "[[The Question Mark Operator]]", "[[Broad should_panic Tests]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-01-writing-tests.html#using-resultt-e-in-tests", "https://doc.rust-lang.org/reference/attributes/testing.html#the-test-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Result Returning Tests

Return `Result<(), E>` from a test when fallible setup or actions should use `?`; assert expected `Err` values explicitly instead of using `?` on the result being tested.

## What it is
A `#[test]` function may return a type that implements `Termination`, including `Result<(), E>` where the error is printable for diagnostics.

This pattern keeps tests readable when setup opens files, parses values, builds temporary state, or calls APIs that return `Result`. If any setup step returns `Err`, `?` exits the test and the harness marks it failed.

It is not a replacement for assertions. Use `?` for "this operation must succeed for the test to proceed"; use `assert!`, `assert_eq!`, or pattern matching for "this is the behavior being tested."

## How it works
The test harness calls the returned value's termination reporting logic. `Ok(())` passes; `Err(e)` fails and prints the error through the test framework.

`#[should_panic]` cannot be used on `Result`-returning tests. If the API under test should return an error, do not apply `?` to that result, because `?` would make the test fail before you can inspect it.

For richer checks, match the error variant or compare an error kind rather than only checking `is_err()`.

The important distinction is setup failure versus expected behavior. `?` is excellent for setup
failure because it preserves the first error and stops the test. It is wrong for an operation whose
error is the point of the test, because the harness will see a failed test before your assertion runs.

## Example
```rust
fn parse_port(input: &str) -> Result<u16, std::num::ParseIntError> {
    input.parse()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_valid_port() -> Result<(), std::num::ParseIntError> {
        let port = parse_port("8080")?;
        assert_eq!(port, 8080);
        Ok(())
    }

    #[test]
    fn rejects_invalid_port() {
        let result = parse_port("not-a-port");
        assert!(result.is_err());
    }
}
```

## More realistic example
```rust
use std::fs;
use std::io;
use std::path::Path;

fn read_trimmed(path: &Path) -> io::Result<String> {
    Ok(fs::read_to_string(path)?.trim().to_owned())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reads_trimmed_file_contents() -> io::Result<()> {
        let path = std::env::temp_dir().join(format!("read-trimmed-{}.txt", std::process::id()));
        fs::write(&path, "  rust\n")?;

        assert_eq!(read_trimmed(&path)?, "rust");

        let _ = fs::remove_file(path);
        Ok(())
    }
}
```

## Common errors
Combining `#[should_panic]` and `Result` returns is rejected by the test model:

```text
error: functions using `#[should_panic]` must return `()`
```

Fix by choosing one contract. Use `#[should_panic(expected = "...")]` for a panic contract, or return
`Result` and assert `Err` for recoverable failure.

## Best practice
- ✅ Use `Result` returns to remove noisy setup `match` blocks when every setup error should fail the test.
- ✅ Keep the behavior assertion explicit after setup succeeds.
- ✅ Inspect expected errors directly instead of letting `?` consume them.
- ✅ Prefer domain-specific error assertions when the error type supports them.
- ✅ Return concrete error types such as `io::Result<()>` in simple tests; use boxed errors only when setup spans unrelated error types.
- ✅ Clean up fallible fixtures even in passing tests; when cleanup itself is not the behavior under test, log or ignore its failure deliberately.

## Pitfalls
- ⚠️ Combining `#[should_panic]` with a `Result`-returning test is invalid; see [[Broad should_panic Tests]] for panic-specific checks.
- ⚠️ Applying `?` to the operation expected to fail makes the test fail for the wrong reason.
- ⚠️ Returning `Result` from every trivial test can obscure simple boolean or equality expectations.
- ⚠️ Using `unwrap()` throughout fallible setup loses context that a returned error would have reported cleanly.

## See also
[[Test Functions]] · [[Assertion Macros in Tests]] · [[Result]] · [[The Question Mark Operator]] · [[Recoverable vs Unrecoverable Errors]] · [[Broad should_panic Tests]] · [[Shared State Between Parallel Tests]] · [[Test Harness and cargo test]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.1 "Using Result<T, E> in Tests" — [[the-book]], https://doc.rust-lang.org/book/ch11-01-writing-tests.html#using-resultt-e-in-tests
- The Rust Reference, "The test attribute" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/testing.html#the-test-attribute
