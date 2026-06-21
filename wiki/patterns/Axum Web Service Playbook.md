---
type: pattern
title: "Axum Web Service Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, axum, web, http, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Tokio Runtime Playbook]]", "[[Serde Data Format Playbook]]", "[[Tracing and Structured Logging Playbook]]", "[[Error Handling]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[tokio]]", "[[serde]]", "[[tooling-project-hygiene]]", "docs.rs/axum"]
source_urls: ["https://docs.rs/axum/latest/axum/", "https://docs.rs/axum/latest/axum/routing/", "https://docs.rs/axum/latest/axum/extract/", "https://docs.rs/axum/latest/axum/response/"]
rust_version: "edition 2024 / 1.85+"
---

# Axum Web Service Playbook

Use axum to build Tokio-based HTTP services from typed extractors, handlers, routers, shared state, and explicit response/error types.

## What it is
`axum` is a web framework built on Tokio, Hyper, Tower, and Serde-friendly patterns.
Routes map HTTP methods and paths to async handler functions.
Extractors pull typed data from the request: path parameters, query strings, JSON bodies, headers, state, and more.
Responses are values implementing `IntoResponse`.
Middleware and services come through Tower layers.
Axum works best when handlers stay thin and application logic lives in testable functions or services.

## How it works
Build a `Router`.
Attach routes with `get`, `post`, and other routing helpers.
Handlers are async functions whose parameters are extractors.
Return plain strings, JSON values, status tuples, or custom response types.
Use `State<T>` for shared application state, typically an `Arc`-backed cloneable handle to pools or services.
Keep database clients, HTTP clients, and config in state rather than globals.
Use Serde DTOs for request and response bodies.
Use `tracing` middleware and spans for observability.
Verify the latest axum version and serving API on docs.rs before editing dependencies because web stack versions evolve.

## Example
```rust
use axum::{extract::Path, routing::get, Json, Router};
use serde::Serialize;

#[derive(Serialize)]
struct UserDto {
    id: u64,
    name: String,
}

async fn get_user(Path(id): Path<u64>) -> Json<UserDto> {
    Json(UserDto {
        id,
        name: "Ada".to_owned(),
    })
}

#[tokio::main]
async fn main() {
    let app: Router = Router::new().route("/users/{id}", get(get_user));
    let _ = app;
}
```

Cargo dependencies for this example:
```toml
[dependencies]
axum = "0.8"
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

## Best practice
- ✅ Keep handlers small: extract, authorize, call domain logic, map response.
- ✅ Use typed DTOs from [[Serde Data Format Playbook]] for request and response bodies.
- ✅ Put shared clients and pools in `State`, not in lazy globals.
- ✅ Use typed application errors that implement or convert into `IntoResponse`.
- ✅ Add `tracing` spans and request IDs early.
- ✅ Test handlers and routers with Tower service utilities where practical.
- ✅ Keep route paths and API compatibility intentional.
- ✅ Verify the latest axum version on docs.rs before copying serving or routing examples.

## Pitfalls
- ⚠️ Putting business logic directly into large handlers.
- ⚠️ Returning inconsistent ad hoc error JSON from every endpoint.
- ⚠️ Holding locks across `.await` inside stateful handlers; see [[Holding Locks Across Await]].
- ⚠️ Treating extractors as validation for all business rules.
- ⚠️ Cloning heavy state values instead of cloneable handles such as pools or `Arc`.
- ⚠️ Forgetting body size, timeout, and authentication layers for public services.
- ⚠️ Logging request bodies or authorization headers through instrumentation.

## See also
[[Ecosystem & Crate Playbooks]] · [[Tokio Runtime Playbook]] · [[Serde Data Format Playbook]] · [[Tracing and Structured Logging Playbook]] · [[Reqwest HTTP Client Playbook]] · [[Error Handling]] · [[Application Errors with anyhow]] · [[Async Rust]] · [[Shared State in Async]] · [[Choosing the Right Rust Crate]]

## Sources
- axum crate docs — https://docs.rs/axum/latest/axum/; verify the latest version before editing `Cargo.toml`.
- axum routing docs — https://docs.rs/axum/latest/axum/routing/
- axum extractor docs — https://docs.rs/axum/latest/axum/extract/
- Existing source notes — [[tokio]], [[serde]], [[tooling-project-hygiene]].
