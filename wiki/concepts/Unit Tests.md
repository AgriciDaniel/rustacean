---
type: concept
title: "Unit Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, unit-tests]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Test Functions]]", "[[Integration Tests]]", "[[Test Organization]]", "[[Conditional Compilation (cfg)]]", "[[Visibility and Privacy]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-03-test-organization.html#unit-tests", "https://doc.rust-lang.org/reference/conditional-compilation.html#test"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Testing"]
---

# Unit Tests

Unit tests live next to the code they exercise, usually inside `#[cfg(test)] mod tests`, and can test both public behavior and private implementation details.

## What it is
A unit test checks a small piece of code in isolation. In Rust, unit tests are conventionally placed in the same source file as the code under test, inside a child module named `tests`.

The `#[cfg(test)]` attribute tells the compiler to include the module only when the crate is compiled in test mode. This keeps test-only helpers out of normal builds.

Because the test module is a normal child module, Rust privacy rules let it access items in ancestor modules. That means unit tests can call private functions when direct testing of internal behavior is useful.

## How it works
`cargo test` enables the `test` configuration option. Items behind `#[cfg(test)]` are compiled, the `#[test]` functions are registered with the harness, and each test is run.

Inside `mod tests`, `use super::*;` brings the parent module's items into scope. This is a common and accepted exception to avoiding glob imports because the module is local to tests and intentionally mirrors the file under test.

Unit tests are best for fast feedback: parsing helpers, small algorithms, invariant checks, and edge cases that would be hard to reach through the public API alone.

Because the test module is compiled only under `cfg(test)`, any helper functions, fixtures, or mock
types inside it are also absent from release artifacts and public rustdoc output. That boundary is
useful: put test-only scaffolding there, but keep production-only code outside it so integration tests
and downstream users can reach the public API.

## Example
```rust
pub fn add_two(value: u64) -> u64 {
    internal_add(value, 2)
}

fn internal_add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn internal_add_combines_operands() {
        assert_eq!(internal_add(2, 2), 4);
    }

    #[test]
    fn public_add_two_uses_internal_addition() {
        assert_eq!(add_two(10), 12);
    }
}
```

## More realistic example
```rust
pub fn first_nonempty_line(input: &str) -> Option<&str> {
    input.lines().map(str::trim).find(|line| !line.is_empty())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skips_blank_and_whitespace_only_lines() {
        let input = "\n   \n  cargo test  \nnext";
        assert_eq!(first_nonempty_line(input), Some("cargo test"));
    }

    #[test]
    fn returns_none_when_all_lines_are_blank() {
        assert_eq!(first_nonempty_line("\n \t\n"), None);
    }
}
```

## Common errors
Forgetting to import the parent module's items is a normal module-scope error, not a special test
failure:

```text
error[E0425]: cannot find function `internal_add` in this scope
```

Fix by using `use super::*;`, importing the specific item with `use super::internal_add;`, or calling
it through `super::internal_add(...)`. Prefer the specific import when a large file makes the tested
dependency unclear.

## Best practice
- ✅ Keep unit tests close to the code they protect so future edits see the contract immediately.
- ✅ Use `#[cfg(test)]` around test modules and test-only helpers in production source files.
- ✅ Prefer testing public behavior first; test private functions directly when they hold meaningful, complex logic.
- ✅ Make unit tests fast and deterministic so developers run them frequently.
- ✅ Cover boundary values in unit tests because they are usually cheapest to express close to the algorithm.
- ✅ Use small local fixtures instead of shared global fixtures unless setup cost is genuinely high.

## Pitfalls
- ⚠️ Forgetting `#[cfg(test)]` leaves test helpers in normal builds and public documentation if they are visible.
- ⚠️ Overfitting tests to private implementation details can make refactoring expensive without improving behavior confidence.
- ⚠️ Depending on global state can break under the parallel [[Test Harness and cargo test]] default; see [[Shared State Between Parallel Tests]].
- ⚠️ Hiding all testable behavior in private binary-only code prevents integration tests from checking it through the public crate.

## See also
[[Test Functions]] · [[Assertion Macros in Tests]] · [[Integration Tests]] · [[Test Organization]] · [[Conditional Compilation (cfg)]] · [[Visibility and Privacy]] · [[Shared State Between Parallel Tests]] · [[Test-Driven Development in Rust]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.3 "Unit Tests" — [[the-book]], https://doc.rust-lang.org/book/ch11-03-test-organization.html#unit-tests
- The Rust Reference, "test configuration option" — [[the-reference]], https://doc.rust-lang.org/reference/conditional-compilation.html#test
