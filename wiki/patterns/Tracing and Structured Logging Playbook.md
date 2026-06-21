---
type: pattern
title: "Tracing and Structured Logging Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, tracing, logging, observability, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Tokio Runtime Playbook]]", "[[Error Handling]]", "[[Debugging]]", "[[Async Rust]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[tokio]]", "[[tooling-project-hygiene]]", "docs.rs/tracing", "docs.rs/tracing-subscriber"]
source_urls: ["https://docs.rs/tracing/latest/tracing/", "https://docs.rs/tracing-subscriber/latest/tracing_subscriber/", "https://docs.rs/tracing/latest/tracing/attr.instrument.html", "https://docs.rs/tracing/latest/tracing/struct.Span.html"]
rust_version: "edition 2024 / 1.85+"
---

# Tracing and Structured Logging Playbook

Use `tracing` for structured events and spans so logs preserve request context, async task context, and machine-readable fields.

## What it is
`tracing` is the Rust ecosystem's structured diagnostics framework.
It records events, spans, levels, targets, and fields.
An event is a point-in-time fact.
A span is a period of work with context attached.
Subscribers decide how records are filtered, formatted, exported, or ignored.
This model fits async applications better than plain line logging because work hops between tasks and threads.
It is especially useful with [[Tokio Runtime Playbook]], [[Reqwest HTTP Client Playbook]], and [[Axum Web Service Playbook]].

## How it works
Use macros such as `info!`, `warn!`, `error!`, and `debug!` for events.
Attach fields as key-value pairs instead of formatting everything into one string.
Use `#[instrument]` to create spans around functions, skipping large or sensitive arguments.
Initialize a subscriber once in `main`.
Libraries should emit tracing events but should not install a global subscriber.
Applications own formatting, filtering, and export policy.
`tracing-subscriber` provides common subscriber setup.
Verify the latest `tracing` and `tracing-subscriber` versions on docs.rs before editing dependencies.

## Example
```rust
use tracing::{info, instrument};

#[instrument(skip(password), fields(user_id = user_id))]
fn authenticate(user_id: u64, password: &str) -> bool {
    let accepted = password == "correct horse battery staple";
    info!(accepted, "authentication checked");
    accepted
}

fn main() {
    tracing_subscriber::fmt().with_target(false).init();
    assert!(authenticate(7, "correct horse battery staple"));
}
```

Cargo dependencies for this example:
```toml
[dependencies]
tracing = { version = "0.1", features = ["attributes"] }
tracing-subscriber = "0.3"
```

## Best practice
- ✅ Put subscriber initialization in the binary entry point.
- ✅ Use fields like `request_id`, `user_id`, `status`, and `elapsed_ms` instead of string-only logs.
- ✅ Use spans around requests, jobs, and important units of work.
- ✅ Skip secrets and large payloads in `#[instrument]`.
- ✅ Prefer errors with context and record them with fields.
- ✅ Make log filtering configurable with environment or config.
- ✅ Keep libraries subscriber-agnostic.
- ✅ Verify the latest `tracing` crate versions on docs.rs before dependency updates.

## Pitfalls
- ⚠️ Logging secrets, tokens, passwords, cookies, or full authorization headers.
- ⚠️ Formatting structured data into one message string and losing queryable fields.
- ⚠️ Initializing the global subscriber in a library.
- ⚠️ Instrumenting noisy hot functions and creating high-cardinality field explosions.
- ⚠️ Assuming `Debug` output is safe for public logs.
- ⚠️ Treating logs as error handling; errors still need typed propagation.
- ⚠️ Forgetting async context and relying only on thread IDs.

## See also
[[Ecosystem & Crate Playbooks]] · [[Tokio Runtime Playbook]] · [[Reqwest HTTP Client Playbook]] · [[Axum Web Service Playbook]] · [[Error Handling]] · [[Application Errors with anyhow]] · [[The Debug Trait]] · [[Async Rust]] · [[Tasks and spawn]] · [[Choosing the Right Rust Crate]]

## Sources
- tracing crate docs — https://docs.rs/tracing/latest/tracing/; verify the latest version before editing `Cargo.toml`.
- tracing `instrument` docs — https://docs.rs/tracing/latest/tracing/attr.instrument.html
- tracing-subscriber crate docs — https://docs.rs/tracing-subscriber/latest/tracing_subscriber/; verify the latest version.
- Existing source notes — [[tokio]], [[tooling-project-hygiene]].
