---
type: pattern
title: "Reqwest HTTP Client Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, reqwest, http, async, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Tokio Runtime Playbook]]", "[[Serde Data Format Playbook]]", "[[Error Handling]]", "[[Async Rust]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[tokio]]", "[[serde]]", "[[tooling-project-hygiene]]", "docs.rs/reqwest"]
source_urls: ["https://docs.rs/reqwest/latest/reqwest/", "https://docs.rs/reqwest/latest/reqwest/struct.Client.html", "https://docs.rs/reqwest/latest/reqwest/struct.Response.html", "https://docs.rs/reqwest/latest/reqwest/blocking/"]
rust_version: "edition 2024 / 1.85+"
---

# Reqwest HTTP Client Playbook

Use one reused `reqwest::Client` for outbound HTTP, set timeouts, deserialize at the edge, and choose TLS/features deliberately.

## What it is
`reqwest` is the ergonomic HTTP client most Rust applications reach for.
It supports async clients, an optional blocking API, JSON integration through Serde, TLS backends, redirects, headers, request builders, and response handling.
It is commonly used with [[Tokio Runtime Playbook]] because the async client runs on an async runtime.
For libraries, consider whether accepting a client or trait boundary is better than constructing a global policy internally.
For binaries, centralize client construction so timeouts, headers, and TLS policy are consistent.

## How it works
Create a `Client` once and reuse it.
The client owns connection pooling and configuration.
Building a new client for every request discards pooling and spreads policy across the codebase.
Requests are builders.
`send().await?` performs the request.
`error_for_status()?` converts non-success HTTP statuses into errors when that is what your application wants.
`json::<T>().await?` deserializes through Serde when the `json` feature is enabled.
Use explicit request timeouts so bad networks do not become hung tasks.
Choose TLS features intentionally, often `rustls-tls` for a pure-Rust TLS stack.
Verify the latest reqwest version and feature list on docs.rs before editing `Cargo.toml`.

## Example
```rust
use std::time::Duration;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct ApiStatus {
    ok: bool,
}

async fn fetch_status(client: &reqwest::Client, url: &str) -> Result<ApiStatus, reqwest::Error> {
    client
        .get(url)
        .timeout(Duration::from_secs(5))
        .send()
        .await?
        .error_for_status()?
        .json::<ApiStatus>()
        .await
}

#[tokio::main]
async fn main() {
    let client = reqwest::Client::new();
    let _future = fetch_status(&client, "https://example.com/status");
}
```

Cargo dependencies for this example:
```toml
[dependencies]
reqwest = { version = "0.12", default-features = false, features = ["rustls-tls", "json"] }
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

## Best practice
- ✅ Reuse one `Client` per policy boundary.
- ✅ Set request or client timeouts.
- ✅ Call `error_for_status` when HTTP 4xx/5xx should be treated as failures.
- ✅ Deserialize into typed DTOs from [[Serde Data Format Playbook]].
- ✅ Keep retry policy explicit and idempotency-aware.
- ✅ Use `default-features = false` when you need a specific TLS backend or smaller surface.
- ✅ Log URLs and status classes carefully without leaking secrets.
- ✅ Verify the latest reqwest version and enabled features on docs.rs before updates.

## Pitfalls
- ⚠️ Creating a client for each request and losing connection reuse.
- ⚠️ Forgetting timeouts and letting a slow remote service pin tasks indefinitely.
- ⚠️ Treating every non-transport response as success because `send` returned `Ok`.
- ⚠️ Retrying non-idempotent requests without a clear application contract.
- ⚠️ Logging authorization headers, cookies, tokens, or full query strings.
- ⚠️ Using the blocking client inside async code; see [[Blocking the Async Executor]].
- ⚠️ Exposing `reqwest::Error` from a library API if you may swap clients later.

## See also
[[Ecosystem & Crate Playbooks]] · [[Tokio Runtime Playbook]] · [[Serde Data Format Playbook]] · [[Async Rust]] · [[Error Handling]] · [[Application Errors with anyhow]] · [[Blocking in Async]] · [[Blocking the Async Executor]] · [[Feature Flags]] · [[Choosing the Right Rust Crate]] · [[Tracing and Structured Logging Playbook]]

## Sources
- reqwest crate docs — https://docs.rs/reqwest/latest/reqwest/; verify the latest version before editing `Cargo.toml`.
- reqwest `Client` docs — https://docs.rs/reqwest/latest/reqwest/struct.Client.html
- reqwest `Response` docs — https://docs.rs/reqwest/latest/reqwest/struct.Response.html
- Existing source notes — [[tokio]], [[serde]], [[tooling-project-hygiene]].
