---
type: pattern
title: "Debugging"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, debugging, diagnostics, backtrace, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[The Debug Trait]]", "[[Tracing and Structured Logging Playbook]]", "[[Application Errors with anyhow]]", "[[panic!]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[std]]", "[[the-book]]", "[[tooling-project-hygiene]]", "docs.rs/tracing"]
source_urls: ["https://doc.rust-lang.org/std/macro.dbg.html", "https://doc.rust-lang.org/std/backtrace/index.html", "https://doc.rust-lang.org/cargo/reference/profiles.html", "https://docs.rs/tracing/latest/tracing/"]
rust_version: "edition 2024 / 1.85+"
---

# Debugging

Debugging Rust is fastest when you combine typed errors, `Debug` output, backtraces, tests, and structured instrumentation instead of relying on scattered `println!` calls.

## What it is
Debugging is the process of making a program's state and control flow inspectable enough to explain a failure.
In Rust, the first debugger is often the compiler.
Ownership, borrowing, exhaustiveness, and trait bounds remove whole classes of runtime faults before execution.

Runtime debugging still matters.
Logic bugs, bad input, race conditions, configuration mistakes, performance cliffs, and integration failures all survive compilation.
Rust gives several layers for those cases:
`dbg!` for quick local inspection, `Debug` implementations for developer-facing values, `Result` and error context for expected failures, `panic!` and backtraces for violated invariants, and crates such as `tracing` for structured diagnostics.

Use the lightest tool that preserves signal.
A failing unit test with a clear assertion is better than a manual debugger session.
An error chain with context is better than a panic for user-caused failures.
Structured spans are better than free-form log lines for async services.

## How it works
The `dbg!` macro prints the source location, expression text, and `Debug` value to stderr, then returns the value unchanged.
It moves non-`Copy` expressions unless you pass a reference such as `dbg!(&value)`.
It also works in release builds, so do not leave it in production paths by accident.

`#[derive(Debug)]` makes most domain values printable with `{:?}` and usable in assertion failures.
Write a manual `Debug` implementation for types that contain secrets.
Do not treat `Debug` output as stable serialization or user-facing output.

Backtraces help when a panic or error needs call-site context.
Set `RUST_BACKTRACE=1` when running a program or tests to get panic backtraces.
Use `std::backtrace::Backtrace` when an error type or diagnostic path needs a captured trace.
Backtraces are most useful when binaries contain debug information.
Cargo's `dev` profile is the default for `cargo build` and includes full debug info by default; `release` defaults to no debug info.

For services and async programs, prefer [[Tracing and Structured Logging Playbook]].
Events and spans preserve context across task switches better than thread-local assumptions.
Libraries may emit tracing events, but applications should install the subscriber.
Verify the latest `tracing` and `tracing-subscriber` versions on docs.rs before editing dependencies.

## Example
```rust
use std::backtrace::Backtrace;

#[derive(Debug, PartialEq, Eq)]
struct Job {
    name: String,
    retries: u8,
}

fn parse_job(line: &str) -> Result<Job, String> {
    let (name, retries) = line
        .split_once(':')
        .ok_or_else(|| format!("expected NAME:RETRIES, got {line:?}"))?;

    let retries = retries
        .parse::<u8>()
        .map_err(|err| format!("invalid retry count {retries:?}: {err}"))?;

    let job = Job {
        name: name.trim().to_owned(),
        retries,
    };

    Ok(dbg!(job))
}

fn main() {
    let job = parse_job("backup:3").expect("valid demo job");
    assert_eq!(
        job,
        Job {
            name: "backup".to_owned(),
            retries: 3,
        }
    );

    if std::env::var_os("RUST_BACKTRACE").is_some() {
        eprintln!("{:?}", Backtrace::capture());
    }
}
```

## Debugging workflow
Start by reproducing the failure with a command, test, fixture, or minimized input.
Then tighten the observation point.
Use assertions for invariants that should always hold.
Use `Result` and context for failures callers can handle.
Use `dbg!(&value)` or temporary tracing events to inspect intermediate state.
When the problem depends on optimization, run the same test under the relevant profile.

For command-line programs, print user-facing failures through [[Application Errors with anyhow]] or typed application errors.
For libraries, return errors and let callers decide how to display them.
For async services, attach request IDs, peer addresses, operation names, and elapsed time as structured fields.
For data races and shared state bugs, inspect ownership boundaries and synchronization before adding more logs.

## Best practice
- ✅ Derive or implement [[The Debug Trait]] on types used in tests and diagnostics.
- ✅ Prefer failing tests and assertions over one-off manual inspection.
- ✅ Add error context at each boundary where local information would be lost.
- ✅ Use `dbg!(&value)` when you want inspection without moving ownership.
- ✅ Enable `RUST_BACKTRACE=1` when investigating panics or unexpected error paths.
- ✅ Use Cargo's dev or test profile for normal source-level debugging.
- ✅ Use `tracing` spans and fields for async, service, and multi-step workflows.
- ✅ Redact secrets in `Debug`, logs, traces, and panic messages.

## Pitfalls
- ⚠️ Leaving `dbg!` calls in production code; it writes to stderr and runs in release builds.
- ⚠️ Debugging user-caused errors with `panic!` instead of returning `Result`.
- ⚠️ Logging passwords, tokens, cookies, private keys, or full authorization headers.
- ⚠️ Trusting `Debug` output as a stable format for tests, files, or protocols.
- ⚠️ Installing a global tracing subscriber from a library.
- ⚠️ Debugging optimized release binaries without considering missing variables, inlining, and stripped debug info.
- ⚠️ Swallowing errors and then trying to recover the missing context from logs later.

## See also
[[Ecosystem & Crate Playbooks]] · [[The Debug Trait]] · [[Display and Debug Formatting Traits]] · [[Tracing and Structured Logging Playbook]] · [[Application Errors with anyhow]] · [[Adding Error Context]] · [[panic!]] · [[Panic Unwinding and Abort]] · [[Result Returning Tests]] · [[Test Harness and cargo test]] · [[Concurrency]] · [[Ownership]]

## Sources
- Standard library `dbg!` macro — https://doc.rust-lang.org/std/macro.dbg.html
- Standard library backtrace module — https://doc.rust-lang.org/std/backtrace/index.html
- Cargo profiles and debug info — https://doc.rust-lang.org/cargo/reference/profiles.html
- tracing crate docs — https://docs.rs/tracing/latest/tracing/; verify the latest version before editing `Cargo.toml`.
- Tooling and project hygiene — [[tooling-project-hygiene]].
