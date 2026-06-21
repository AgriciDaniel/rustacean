---
type: concept
title: "Practice: Tests"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, tests]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Test Harness and cargo test]]", "[[Test Functions]]", "[[Assertion Macros in Tests]]", "[[Unit Tests]]", "[[Result Returning Tests]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Tests

The tests group teaches using Rust's built-in test harness to specify behavior. The key idea is that tests are ordinary Rust functions marked with attributes and checked by `cargo test`.

## What it is
These exercises cover `#[test]`, assertion macros, panics in tests, `#[should_panic]`, and tests that return `Result`.

## How it works
The test harness discovers functions annotated with `#[test]`. A test passes if it returns normally or returns `Ok(())`; it fails if it panics or returns `Err`.

## Example
```rust
fn add(left: i32, right: i32) -> i32 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_two_numbers() {
        assert_eq!(add(2, 3), 5);
    }
}
```

## Best practice
- ✅ Name tests after the behavior they protect.
- ✅ Use `assert_eq!` and `assert_ne!` when comparing values so failures show both sides.
- ✅ Return `Result` from tests when `?` makes setup clearer.

## Pitfalls
- ⚠️ Do not write tests that only repeat the implementation.
- ⚠️ `#[should_panic]` should be narrow enough to catch the intended panic.
- ⚠️ Tests in a child module need `use super::*` or explicit paths to reach parent items.

## See also
[[Practice (Rustlings)]] · [[Test Harness and cargo test]] · [[Test Functions]] · [[Assertion Macros in Tests]] · [[Unit Tests]] · [[Result Returning Tests]] · [[Test Organization]]

## Sources
- Rustlings `17_tests` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

