---
type: pattern
title: "Test-Driven Development in Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, tdd]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Test Functions]]", "[[Assertion Macros in Tests]]", "[[Unit Tests]]", "[[Integration Tests]]", "[[Result Returning Tests]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-00-testing.html", "https://doc.rust-lang.org/book/ch12-04-testing-the-librarys-functionality.html"]
rust_version: "edition 2024 / 1.85+"
---

# Test-Driven Development in Rust

Test-driven development in Rust means writing a failing executable specification first, making it pass with the smallest useful implementation, and then refactoring while the compiler and tests guard behavior.

## What it is
TDD is a workflow rather than a Rust language feature. The Book demonstrates the testing mechanics in chapter 11 and applies tests to library behavior in the command-line project in chapter 12.

In Rust, TDD benefits from the type system: many invalid designs fail before tests run, while tests focus on behavior the compiler cannot infer, such as parsing rules, boundary conditions, and output content.

The usual loop is red, green, refactor: write a failing test, implement enough code to pass, then improve the design without changing behavior.

## How it works
Start with the smallest public or private contract that matters. Use a unit test when you are shaping a small function or parser. Use an integration test when you are defining user-visible library behavior.

Let compile errors participate in the loop. A new test might fail to compile because the API does not exist yet; creating the API is part of making the test reach a meaningful failing assertion.

After a test passes, refactor toward idiomatic Rust: clearer ownership, narrower borrowing, better error types, or simpler module boundaries. The test should still describe behavior rather than implementation.

Rust's compiler changes the red phase slightly. Sometimes the first red signal is a compile error:
the function, type, lifetime, or visibility boundary does not exist yet. That is still useful
feedback. Once the code compiles, the next red signal should be a failing assertion that names the
behavior being implemented.

## Example
```rust
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents
        .lines()
        .filter(|line| line.contains(query))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_lines_containing_query() {
        let contents = "Rust:\nsafe, fast, productive.\nPick three.";
        assert_eq!(search("duct", contents), vec!["safe, fast, productive."]);
    }
}
```

## More realistic example
```rust
pub fn search_case_insensitive<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    let query = query.to_lowercase();
    contents
        .lines()
        .filter(|line| line.to_lowercase().contains(&query))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_lines_ignoring_ascii_case() {
        let contents = "Rust:\nsafe, fast, productive.\nTrust me.";
        assert_eq!(
            search_case_insensitive("rust", contents),
            vec!["Rust:", "Trust me."]
        );
    }

    #[test]
    fn returns_empty_vector_when_query_is_absent() {
        assert!(search_case_insensitive("borrow", "ownership\nlifetimes").is_empty());
    }
}
```

## Common errors
Early TDD tests often fail to compile because the desired API does not exist yet:

```text
error[E0425]: cannot find function `search_case_insensitive` in this scope
```

Fix by adding the smallest public or private function signature that expresses the contract, then
continue until the failure is a meaningful assertion rather than a missing item.

## Best practice
- ✅ Write tests around behavior names before implementation names.
- ✅ Use unit tests for the design loop and integration tests for public API commitments.
- ✅ Add regression tests before fixing a bug so the bug cannot silently return.
- ✅ Keep examples small enough that a failing assertion reveals the next change.
- ✅ Let type signatures carry invariants when they can; write tests for behavior the type system cannot prove.
- ✅ Refactor after green by simplifying ownership and error flow, then rerun focused tests and the broader suite.

## Pitfalls
- ⚠️ Writing tests after implementation often mirrors the current code instead of challenging the requirement.
- ⚠️ Testing private steps too aggressively can freeze an immature design; use [[Integration Tests]] for stable public behavior.
- ⚠️ Letting broad assertions pass for incidental reasons weakens the TDD loop; use [[Assertion Macros in Tests]] precisely.
- ⚠️ Treating compile errors as noise misses part of Rust's feedback loop; many design mistakes should be fixed before runtime tests exist.

## See also
[[Test Functions]] · [[Assertion Macros in Tests]] · [[Unit Tests]] · [[Integration Tests]] · [[Result Returning Tests]] · [[Test Organization]] · [[Test Harness and cargo test]] · [[Shared State Between Parallel Tests]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11 "Writing Automated Tests" — [[the-book]], https://doc.rust-lang.org/book/ch11-00-testing.html
- The Rust Programming Language, ch. 12.4 "Developing the Library's Functionality with Test-Driven Development" — [[the-book]], https://doc.rust-lang.org/book/ch12-04-testing-the-librarys-functionality.html
