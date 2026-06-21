---
type: antipattern
title: "Shared State Between Parallel Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, parallelism]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Test Harness and cargo test]]", "[[Unit Tests]]", "[[Integration Tests]]", "[[Ignored Tests]]", "[[Shared State with Mutex]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-02-running-tests.html#running-tests-in-parallel-or-consecutively"]
rust_version: "edition 2024 / 1.85+"
---

# Shared State Between Parallel Tests

Tests that mutate the same file, environment variable, current directory, port, or global value are flaky under Rust's default parallel test execution.

## The mistake
By default, the test harness runs multiple tests in parallel. If tests depend on the same external state, they can interfere with each other even when the production code is correct.

The common version is a fixed filename such as `test-output.txt`: one test writes it while another reads or overwrites it. Similar failures happen with process-wide environment variables, global loggers, current working directory, local ports, and shared databases.

These failures are hard to diagnose because `cargo test -- --test-threads=1` may make them disappear.

## Why it happens
Parallel execution improves feedback time, so Rust uses it by default. The harness makes no promise that tests run in source order.

Rust's ownership model prevents data races inside safe Rust values, but it cannot automatically isolate operating-system resources or process-wide state.

The better fix is usually isolation: unique temporary directories, unique filenames, independent fixtures, local state passed as parameters, or explicit synchronization around unavoidable globals.

Serialization can be necessary for truly process-global state, but it should be explicit and narrow.
Safe Rust prevents unsynchronized memory data races; it does not make `std::env::set_var`, the
current directory, a shared database row, or a fixed TCP port independent per test.

## Example
```rust
use std::fs;
use std::path::PathBuf;

fn write_report(path: PathBuf, body: &str) -> std::io::Result<String> {
    fs::write(&path, body)?;
    fs::read_to_string(path)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn writes_report_to_unique_path() -> std::io::Result<()> {
        let path = std::env::temp_dir().join(format!(
            "report-{}-{}.txt",
            std::process::id(),
            "writes_report_to_unique_path"
        ));
        assert_eq!(write_report(path.clone(), "ok")?, "ok");
        let _ = fs::remove_file(path);
        Ok(())
    }
}
```

## More realistic example
```rust
use std::fs;
use std::io;
use std::path::PathBuf;

fn unique_test_file(test_name: &str) -> PathBuf {
    std::env::temp_dir().join(format!(
        "{}-{}-{test_name}.txt",
        env!("CARGO_PKG_NAME"),
        std::process::id()
    ))
}

fn round_trip_report(test_name: &str, body: &str) -> io::Result<String> {
    let path = unique_test_file(test_name);
    fs::write(&path, body)?;
    let output = fs::read_to_string(&path)?;
    let _ = fs::remove_file(path);
    Ok(output)
}

#[test]
fn report_round_trip_isolated_by_name() -> io::Result<()> {
    assert_eq!(round_trip_report("report_round_trip_isolated_by_name", "ok")?, "ok");
    Ok(())
}
```

## Common errors
Order-dependent tests usually fail intermittently, not with a stable compiler error. The symptom is
a test that passes alone but fails in the full suite:

```text
test reads_cached_config ... FAILED
test writes_cached_config ... ok
```

Fix by removing the dependency between tests, giving each test isolated state, or placing the truly
global mutation behind one serialized helper and documenting why parallelism cannot be preserved.

## Best practice
- ✅ Prefer per-test temporary paths, unique ports, and local fixture objects.
- ✅ Pass state into functions instead of reading process globals inside the code under test.
- ✅ Use `cargo test -- --test-threads=1` as a diagnostic or last resort, not as the primary design.
- ✅ Put truly expensive serialized checks behind [[Ignored Tests]] or a dedicated CI job.
- ✅ Include the process id and test name in ad hoc temporary resources when a fixture crate is not available.
- ✅ Restore environment variables and current directories in a guard type if a test must mutate them.

## Pitfalls
- ⚠️ Fixed filenames in `/tmp` or the project root become race points.
- ⚠️ Environment-variable tests can affect unrelated tests in the same process.
- ⚠️ Assuming test source order is execution order leads to order-dependent suites.
- ⚠️ A `Mutex` around test code serializes only cooperating tests; it does not protect against other processes, doctests, or external tools.

## See also
[[Test Harness and cargo test]] · [[Unit Tests]] · [[Integration Tests]] · [[Ignored Tests]] · [[Shared State with Mutex]] · [[Test Organization]] · [[Result Returning Tests]] · [[RAII and Drop Guards]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 11.2 "Running Tests in Parallel or Consecutively" — [[the-book]], https://doc.rust-lang.org/book/ch11-02-running-tests.html#running-tests-in-parallel-or-consecutively
