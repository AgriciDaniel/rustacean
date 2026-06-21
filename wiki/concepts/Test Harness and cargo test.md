---
type: concept
title: "Test Harness and cargo test"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, cargo]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Test Functions]]", "[[Unit Tests]]", "[[Integration Tests]]", "[[Ignored Tests]]", "[[Shared State Between Parallel Tests]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-02-running-tests.html", "https://doc.rust-lang.org/reference/attributes/testing.html", "https://doc.rust-lang.org/rustc/tests/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Test Harness and cargo test

`cargo test` builds test binaries and runs the Rust test harness; Cargo arguments come before `--`, while harness arguments such as filters, thread count, and output flags come after it.

## What it is
The test harness is the runner generated for crates compiled in test mode. It discovers `#[test]` functions, runs them, captures their output, and reports passed, failed, ignored, measured, and filtered tests.

`cargo test` is the usual entry point. It compiles unit tests, integration tests, and documentation tests, then runs the resulting binaries.

The command has two argument layers: options before `--` are for Cargo, and options after `--` are for the test binary.

## How it works
By default, tests run in parallel and stdout from passing tests is captured. Failed tests show captured stdout in the failure report.

Use `cargo test name_fragment` to run tests whose path contains a fragment. Use `cargo test -- --show-output` to show stdout for successful tests too. Use `cargo test -- --test-threads=1` when shared process state cannot be isolated.

Ignored tests are compiled but skipped by default. `cargo test -- --ignored` runs only ignored tests, and `cargo test -- --include-ignored` runs both normal and ignored tests.

Cargo may build several test executables for one package: a unit-test binary for the library, one
for each binary target with tests, one per integration test file, and rustdoc-managed doctest
executables. The familiar output sections correspond to those separate artifacts, which is why a
failed unit-test section can prevent later integration or doc-test sections from running.

## Example
```rust
fn double(value: i32) -> i32 {
    println!("doubling {value}");
    value * 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn doubles_small_number() {
        assert_eq!(double(4), 8);
    }

    #[test]
    #[ignore = "slow external fixture"]
    fn doubles_large_fixture() {
        assert_eq!(double(1024), 2048);
    }
}
```

## Command examples
```text
cargo test parse_port
cargo test --lib
cargo test --test public_api
cargo test --doc
cargo test -- --show-output
cargo test -- --test-threads=1
cargo test -- --ignored
cargo test -- --include-ignored
```

Use the first non-option argument as a name filter. The filter matches the full test path, including
module names, so `cargo test parser` can run every test whose path contains `parser`.

## Common errors
Harness flags placed before the separator are parsed by Cargo instead of the test binary:

```text
error: unexpected argument '--show-output' found
```

Fix by placing harness options after `--`: `cargo test -- --show-output`. Conversely, Cargo target
selection such as `--lib`, `--bin name`, and `--test name` belongs before the separator.

## Best practice
- ✅ Learn the separator: `cargo test -- --help` documents harness flags, while `cargo test --help` documents Cargo flags.
- ✅ Prefer unique test names so filtering is predictable.
- ✅ Leave tests parallel by default; isolate files, directories, environment variables, and ports instead.
- ✅ Use `#[ignore = "reason"]` for expensive or environment-dependent tests, then run them intentionally in CI jobs that provide the dependency.
- ✅ Use `--lib`, `--test name`, or `--doc` to shorten a debugging loop without teaching the suite to depend on test order.
- ✅ Keep diagnostic `println!` output temporary or pair it with `--show-output`; assertions should carry the durable explanation.

## Pitfalls
- ⚠️ Passing harness flags before `--` sends them to Cargo, where they may be rejected or mean something else.
- ⚠️ Relying on printed output from passing tests hides diagnostics unless `--show-output` is used.
- ⚠️ Tests that share mutable process state can fail only under parallel runs; see [[Shared State Between Parallel Tests]].
- ⚠️ Assuming `cargo test name_a name_b` runs two filters is wrong; the first filter value is the one used by the harness.

## See also
[[Test Functions]] · [[Unit Tests]] · [[Integration Tests]] · [[Ignored Tests]] · [[Shared State Between Parallel Tests]] · [[Documentation Tests]] · [[Test Organization]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.2 "Controlling How Tests Are Run" — [[the-book]], https://doc.rust-lang.org/book/ch11-02-running-tests.html
- The Rust Reference, "Testing attributes" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/testing.html
- The rustc book, "Tests" — [[rustc-book]], https://doc.rust-lang.org/rustc/tests/index.html
