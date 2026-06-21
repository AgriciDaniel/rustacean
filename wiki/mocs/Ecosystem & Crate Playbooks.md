---
type: moc
title: "Ecosystem & Crate Playbooks"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ecosystem, crates, moc]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Choosing the Right Rust Crate]]", "[[Minimizing Dependencies]]", "[[Cargo & Dependencies]]", "[[Tooling & Getting Started]]"]
sources: ["[[tooling-project-hygiene]]", "[[dependency-supply-chain-security]]", "docs.rs"]
source_urls: ["https://docs.rs/", "https://doc.rust-lang.org/cargo/reference/features.html", "https://rustsec.org/", "https://mozilla.github.io/cargo-vet/"]
rust_version: "edition 2024 / 1.85+"
---

# Ecosystem & Crate Playbooks

This MOC links practical Rust crate playbooks for choosing, configuring, and using major ecosystem crates without losing sight of dependency hygiene.

## What it is
This domain is about crate-level judgment.
Rust's standard library is intentionally focused.
Real applications commonly add crates for async runtimes, serialization, HTTP, CLIs, logging, regexes, iterator helpers, web services, and parallelism.
Those crates are productivity multipliers, but they also create dependency, feature, security, MSRV, and public-API commitments.
Use this MOC as the front door when deciding whether to add a crate and how to use it idiomatically.

## How it works
Read the decision note first when adding a new dependency.
Then read the crate-specific playbook for usage patterns, feature flags, examples, and pitfalls.
For crates used together, follow the stack links: Tokio under async work, Serde at data boundaries, tracing across observability, and dependency hygiene across every `Cargo.toml` edit.
The crate docs linked here use docs.rs `latest` URLs, so verify the current version before copying a dependency line.
When an upstream API changes, update the playbook and keep the example minimal enough to compile.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct CrateChoice {
    name: &'static str,
    reason: &'static str,
}

fn choose_playbook(need: &str) -> Option<CrateChoice> {
    match need {
        "async runtime" => Some(CrateChoice {
            name: "tokio",
            reason: "runs async tasks, timers, and I/O",
        }),
        "json dto" => Some(CrateChoice {
            name: "serde",
            reason: "derives typed serialization boundaries",
        }),
        "cpu parallelism" => Some(CrateChoice {
            name: "rayon",
            reason: "splits CPU-bound iterator work across threads",
        }),
        _ => None,
    }
}

fn main() {
    let choice = choose_playbook("async runtime").expect("known need");
    assert_eq!(choice.name, "tokio");
}
```

## Core Decision Note
Start here before adding a dependency:
[[Choosing the Right Rust Crate]]

This note connects API fit to maintenance, feature flags, supply-chain trust, and dependency surface.
It should be read with [[Minimizing Dependencies]], [[Dependencies and Version Requirements]], [[Feature Flags]], and [[cargo-audit and cargo-deny]].

## Async and Web Stack
These notes cover the common async service stack:
[[Tokio Runtime Playbook]]
[[Reqwest HTTP Client Playbook]]
[[Axum Web Service Playbook]]
[[Tracing and Structured Logging Playbook]]

Tokio is the runtime boundary.
Reqwest is outbound HTTP.
Axum is inbound HTTP.
Tracing is observability across async tasks, handlers, and clients.
Read [[Blocking in Async]], [[Blocking the Async Executor]], and [[Holding Locks Across Await]] before mixing synchronous work into this stack.

## Data and Interfaces
These notes cover data formats and user interfaces:
[[Serde Data Format Playbook]]
[[clap Command Line Playbook]]
[[Command-Line Parsing]]
[[Configuration Loading]]

Serde defines wire and storage formats through Rust types.
clap defines command-line contracts through Rust types.
Configuration loading turns defaults, files, environment variables, and sometimes CLI values into typed settings.
These patterns often use derive macros, so they also connect to [[Derive Macros]], [[Build-Time Code Execution]], and [[Feature Flags]].

## Text, Iterators, and CPU Work
These notes cover focused utility crates:
[[Regex Text Matching Playbook]]
[[Itertools Iterator Helpers Playbook]]
[[Rayon Data Parallelism Playbook]]

Use regex for regular text matching, not full parsers.
Use itertools when standard iterators are almost enough.
Use Rayon for CPU-bound data parallelism, not async I/O.
Read [[Iterator Performance]], [[String and str]], [[Bytes Chars and Unicode]], [[Concurrency]], and [[Threads]] alongside these notes.

## Operational Playbooks
These notes cover diagnostics and runtime operation:
[[Debugging]]
[[Tracing and Structured Logging Playbook]]
[[Configuration Loading]]

Debugging starts with reproducible failures and typed diagnostics.
Tracing provides structured events and spans once the program is running.
Configuration loading makes operational settings explicit and testable.

## Dependency Hygiene Links
Dependency choice is inseparable from project hygiene.
Keep these existing notes close:
[[Cargo Workspaces]]
[[Cargo.toml Manifest]]
[[Cargo.lock]]
[[Feature Flags]]
[[MSRV Policy]]
[[Semantic Versioning]]
[[Minimizing Dependencies]]
[[Build-Time Code Execution]]
[[cargo-audit and cargo-deny]]

## Playbook Index
- [[Choosing the Right Rust Crate]]
- [[Tokio Runtime Playbook]]
- [[Serde Data Format Playbook]]
- [[clap Command Line Playbook]]
- [[Command-Line Parsing]]
- [[Configuration Loading]]
- [[Reqwest HTTP Client Playbook]]
- [[Rayon Data Parallelism Playbook]]
- [[Tracing and Structured Logging Playbook]]
- [[Debugging]]
- [[Regex Text Matching Playbook]]
- [[Itertools Iterator Helpers Playbook]]
- [[Axum Web Service Playbook]]

## Best practice
- ✅ Treat crate selection as design, not just installation.
- ✅ Verify the latest crate version on docs.rs before changing `Cargo.toml`.
- ✅ Keep dependencies centralized in workspaces where possible.
- ✅ Prefer narrow feature sets and test important feature combinations.
- ✅ Audit dependencies continuously with RustSec-backed tooling.
- ✅ Vet new dependencies that add proc macros, `build.rs`, network code, crypto, or parsing.
- ✅ Keep crate-specific types out of public APIs unless the dependency is part of your contract.
- ✅ Link new crate notes back to this MOC and to relevant concept, pattern, and antipattern notes.

## Pitfalls
- ⚠️ Adding crates before checking whether `std` already solves the problem.
- ⚠️ Copying examples without their required feature flags.
- ⚠️ Using download counts as a security signal.
- ⚠️ Treating async crates as a general-purpose performance solution.
- ⚠️ Letting one crate's public types leak through every layer.
- ⚠️ Forgetting to update examples when upstream APIs change.
- ⚠️ Ignoring supply-chain checks because the code is memory-safe Rust.

## See also
[[Cargo & Dependencies]] · [[Tooling & Getting Started]] · [[Async Rust]] · [[Error Handling]] · [[Performance & Optimization]] · [[Concurrency]] · [[Testing & Documentation]] · [[Idioms & API Design]] · [[Anti-patterns & Footguns]] · [[Ownership]]

## Sources
- Tooling and project hygiene — [[tooling-project-hygiene]].
- Dependency and supply-chain security — [[dependency-supply-chain-security]].
- docs.rs crate documentation index — https://docs.rs/; verify the latest version of each crate before dependency updates.
- Cargo feature reference — https://doc.rust-lang.org/cargo/reference/features.html
