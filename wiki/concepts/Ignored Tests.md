---
type: concept
title: "Ignored Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, ignore]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Test Harness and cargo test]]", "[[Test Functions]]", "[[Integration Tests]]", "[[Shared State Between Parallel Tests]]", "[[Documentation Tests]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-02-running-tests.html#ignoring-tests-unless-specifically-requested", "https://doc.rust-lang.org/reference/attributes/testing.html#the-ignore-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Ignored Tests

Ignored tests are compiled but skipped by default, letting slow or environment-dependent checks stay in the suite without running on every `cargo test`.

## What it is
`#[ignore]` is a testing attribute used together with `#[test]`. The harness lists the test as ignored and does not execute it during a normal run.

The attribute can be written as `#[ignore]` or with a reason string, such as `#[ignore = "requires a local database"]`. The reason form is more useful in long-lived test suites.

Ignored tests are not dead tests. They should still be intentionally run with `cargo test -- --ignored` or included in a broader run with `cargo test -- --include-ignored`.

## How it works
The Reference says ignored tests are still compiled in test mode. This means syntax, type checking, imports, and most compile-time drift are still caught, even when the body is not run.

`cargo test -- --ignored` runs only ignored tests. `cargo test -- --include-ignored` runs ignored and non-ignored tests in the same command.

Use ignored tests for cost or environment reasons, not because a behavior is broken. A test for not-yet-implemented behavior should normally be deleted, fixed, or tracked as a failing task rather than quietly ignored forever.

Ignored tests still participate in name filtering. For example, `cargo test slow_case -- --ignored`
runs ignored tests whose full path contains `slow_case`, while `cargo test slow_case` will report the
matching test as ignored but will not execute it.

## Example
```rust
fn normalize(input: &str) -> String {
    input.trim().to_lowercase()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_small_input() {
        assert_eq!(normalize("  Rust "), "rust");
    }

    #[test]
    #[ignore = "large corpus test runs in nightly CI"]
    fn normalizes_large_corpus() {
        assert_eq!(normalize("  RUST "), "rust");
    }
}
```

## More realistic example
```rust
fn import_large_fixture(bytes: &[u8]) -> usize {
    bytes.iter().filter(|byte| **byte != b'\n').count()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn imports_small_fixture() {
        assert_eq!(import_large_fixture(b"a\nb\n"), 2);
    }

    #[test]
    #[ignore = "loads the full production fixture; run in scheduled CI"]
    fn imports_full_fixture() {
        let fixture = include_bytes!("../../fixtures/full-import.bin");
        assert!(import_large_fixture(fixture) > 1_000_000);
    }
}
```

## Common errors
Putting `#[ignore]` on a helper function does not make it a skipped test; the harness only runs or
skips functions also marked `#[test]`.

```text
warning: unused attribute `ignore`
```

Fix by applying it to a real test function, or by moving slow setup behind a helper that is called by
an ignored test.

## Best practice
- ✅ Include a reason string so future maintainers know why the test is skipped.
- ✅ Run ignored tests in a scheduled or specialized CI job if they protect real behavior.
- ✅ Prefer a feature flag, environment check, or test fixture design when the test can be made cheap and deterministic.
- ✅ Keep ignored tests compiling by leaving them in the normal test target.
- ✅ Add an owner or CI job name in the reason when the ignored test depends on external infrastructure.
- ✅ Revisit ignored tests during release work; a permanently ignored regression test is usually an issue tracker item, not a test.

## Pitfalls
- ⚠️ Using `#[ignore]` to hide a failing regression turns the test suite into misleading documentation.
- ⚠️ Forgetting to run ignored tests lets expensive workflows rot even though they still compile.
- ⚠️ Applying `ignore` without `test` is not meaningful; the attribute is for test functions.
- ⚠️ Marking doctests `ignore` is usually weaker than `no_run`, because `ignore` gives up compile checking too.

## See also
[[Test Harness and cargo test]] · [[Test Functions]] · [[Integration Tests]] · [[Shared State Between Parallel Tests]] · [[Documentation Tests]] · [[Test Organization]] · [[Untested Documentation Examples]] · [[Testable Documentation Examples]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.2 "Ignoring Tests Unless Specifically Requested" — [[the-book]], https://doc.rust-lang.org/book/ch11-02-running-tests.html#ignoring-tests-unless-specifically-requested
- The Rust Reference, "The ignore attribute" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/testing.html#the-ignore-attribute
