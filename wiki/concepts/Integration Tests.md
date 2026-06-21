---
type: concept
title: "Integration Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, integration-tests]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Unit Tests]]", "[[Test Organization]]", "[[Test Functions]]", "[[Packages and Crates]]", "[[Visibility and Privacy]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-03-test-organization.html#integration-tests"]
rust_version: "edition 2024 / 1.85+"
---

# Integration Tests

Integration tests live in the top-level `tests/` directory and exercise a library crate through its public API, the way downstream users do.

## What it is
An integration test is external to the library being tested. Each Rust file directly under `tests/` is compiled as a separate crate, so it must import the library by crate name.

Integration tests validate that multiple modules and public API pieces work together. They cannot call private functions, which is the point: they verify the public contract.

Cargo treats `tests/` specially. Files there are compiled only during `cargo test`, so they do not need `#[cfg(test)]`.

## How it works
For a library crate named `adder`, a file such as `tests/integration_test.rs` can write `use adder::add_two;` and then normal `#[test]` functions.

Cargo prints a separate test section for each integration test crate. You can run a single integration test crate with `cargo test --test integration_test`, using the filename without `.rs`.

Shared helpers should go in a submodule such as `tests/common/mod.rs`, then be imported with `mod common;`. A direct `tests/common.rs` file is treated as its own integration test crate and appears as a separate section with zero tests.

Because each integration test file is its own crate, it has its own crate root, imports, feature
visibility boundary, and test binary. That separation is deliberate: integration tests should feel
like examples a downstream crate could compile, not like privileged access to internals.

## Example
```rust
// In a real package, this module would be the external library crate
// imported with `use adder::add_two;` from tests/addition.rs.
mod adder {
    pub fn add_two(value: u64) -> u64 {
        value + 2
    }
}

use adder::add_two;

#[test]
fn adds_two_through_public_api() {
    let result = add_two(2);
    assert_eq!(result, 4);
}
```

## More realistic layout
```text
my_crate/
├── Cargo.toml
├── src/
│   ├── lib.rs
│   └── main.rs
└── tests/
    ├── common/
    │   └── mod.rs
    └── public_api.rs
```

```rust
// tests/public_api.rs
use my_crate::parse_nonzero_port;

mod common;

#[test]
fn parses_cli_port_argument() {
    common::install_test_logger();
    assert_eq!(parse_nonzero_port("8080"), Ok(8080));
}
```

Keep `src/main.rs` as a thin command-line wrapper and put reusable behavior in `src/lib.rs`; otherwise
the integration test crate has nothing importable to exercise.

## Common errors
Trying to import private items from an integration test fails because the test is outside the crate:

```text
error[E0603]: function `parse_impl` is private
```

Fix by testing through the public API, making the item intentionally public, or moving the check to a
unit test if it is truly an implementation-detail invariant.

## Best practice
- ✅ Put user-visible workflows in integration tests, especially behavior that crosses module boundaries.
- ✅ Keep important binary logic in `src/lib.rs` and call it from `src/main.rs` so integration tests can exercise it.
- ✅ Use `tests/common/mod.rs` for shared integration-test helpers.
- ✅ Run focused integration suites with `cargo test --test name` when debugging.
- ✅ Treat integration tests as public API clients: import by crate name and avoid reaching through module layout that callers cannot use.
- ✅ Group larger workflows by file, such as `tests/parsing.rs` or `tests/cli_contract.rs`, so Cargo's `--test` filter stays useful.

## Pitfalls
- ⚠️ Trying to import functions from `src/main.rs` will not work; binary crates are run as programs, not imported as libraries.
- ⚠️ Putting helpers in `tests/common.rs` creates an extra integration test crate; use `tests/common/mod.rs` instead.
- ⚠️ Duplicating only unit-test coverage through the public API can be slow without adding confidence; target cross-module behavior.
- ⚠️ Depending on private modules through accidental `pub` visibility turns integration tests into implementation tests; narrow the public surface.

## See also
[[Unit Tests]] · [[Test Organization]] · [[Test Functions]] · [[Test Harness and cargo test]] · [[Packages and Crates]] · [[Visibility and Privacy]] · [[Shared State Between Parallel Tests]] · [[Test-Driven Development in Rust]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.3 "Integration Tests" — [[the-book]], https://doc.rust-lang.org/book/ch11-03-test-organization.html#integration-tests
