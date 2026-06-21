---
type: pattern
title: "Test Organization"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, organization]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Unit Tests]]", "[[Integration Tests]]", "[[Test Functions]]", "[[Test Harness and cargo test]]", "[[Shared State Between Parallel Tests]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-03-test-organization.html"]
rust_version: "edition 2024 / 1.85+"
---

# Test Organization

Organize Rust tests by purpose: fast unit tests beside implementation code, public API integration tests under `tests/`, and doctests in documentation examples.

## What it is
Rust has three common test locations, each with a distinct role. Unit tests live beside implementation code and can inspect private details. Integration tests live in `tests/` and use only public APIs. Doctests live in documentation and protect examples.

Good organization keeps feedback fast and failures meaningful. The question is not "where can this test compile?" but "what contract does this test protect?"

Use the test layout to communicate intent to maintainers. A test in `src/foo.rs` says "this protects local behavior"; a test in `tests/cli.rs` says "this protects external use."

## How it works
Cargo treats each location differently. Unit tests are compiled into the crate's unit-test binary. Each file directly under `tests/` is compiled as a separate crate. Documentation examples are extracted and tested by rustdoc.

Integration test helpers should live in subdirectories such as `tests/common/mod.rs`. Direct files under `tests/` become integration test crates, even if they contain only helpers.

For binary projects, put reusable logic in `src/lib.rs` and keep `src/main.rs` thin. Integration tests can import the library crate, but they cannot import a binary's private `main.rs` internals.

Think of the locations as concentric contracts. Unit tests can protect local invariants before they
become public. Integration tests protect the crate boundary. Doctests protect the first examples a
reader is likely to copy. Moving a test outward should usually mean the behavior has become more
stable and more user-visible.

## Example
```rust
// src/lib.rs
pub fn add_two(value: u64) -> u64 {
    value + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unit_checks_local_arithmetic() {
        assert_eq!(add_two(1), 3);
    }
}

// A matching integration test would live in tests/add_two.rs:
// use my_crate::add_two;
// #[test]
// fn public_api_adds_two() { assert_eq!(add_two(1), 3); }
```

## More realistic layout
```text
src/
├── lib.rs          # public API, unit tests for local invariants
├── parser.rs       # parser unit tests near parsing edge cases
└── main.rs         # thin binary wrapper
tests/
├── common/
│   └── mod.rs      # shared integration helpers, not a test crate
├── cli_contract.rs # public workflow tests
└── parsing_api.rs  # public parser behavior
```

```rust
// tests/parsing_api.rs
use my_crate::parse_query;

#[test]
fn trims_and_rejects_empty_public_query() {
    assert!(parse_query("   ").is_err());
    assert_eq!(parse_query(" rust ").unwrap().as_str(), "rust");
}
```

## Common errors
Placing shared integration helpers directly at `tests/common.rs` creates an extra integration test
crate and a confusing `running 0 tests` section.

```text
Running tests/common.rs
running 0 tests
```

Fix by using `tests/common/mod.rs` and importing it from each integration test file with
`mod common;`.

## Best practice
- ✅ Use unit tests for dense edge cases and private helper behavior.
- ✅ Use integration tests for public workflows, compatibility expectations, and cross-module behavior.
- ✅ Use doctests for the examples users will copy first.
- ✅ Keep `src/main.rs` small so behavior can be tested through a library API.
- ✅ Put slow end-to-end tests in a clearly named integration file and mark them ignored only when their runtime or dependencies justify it.
- ✅ Let failure location guide placement: if a failed test should send maintainers to one module, prefer a unit test; if it should send them to an API contract, prefer integration or docs.

## Pitfalls
- ⚠️ Duplicating the same assertion in all three locations slows the suite without improving signal.
- ⚠️ Hiding all behavior behind private binary code makes integration testing awkward.
- ⚠️ Sharing mutable fixtures across tests can fail under parallel execution; see [[Shared State Between Parallel Tests]].
- ⚠️ Treating doctests as exhaustive tests makes docs noisy; keep deep matrices in unit or integration tests.

## See also
[[Unit Tests]] · [[Integration Tests]] · [[Documentation Tests]] · [[Test Functions]] · [[Test Harness and cargo test]] · [[Shared State Between Parallel Tests]] · [[Ignored Tests]] · [[Testable Documentation Examples]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.3 "Test Organization" — [[the-book]], https://doc.rust-lang.org/book/ch11-03-test-organization.html
