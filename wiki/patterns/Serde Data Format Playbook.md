---
type: pattern
title: "Serde Data Format Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, serde, serialization, json, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Derive Macros]]", "[[Structs]]", "[[Enums]]", "[[Error Handling]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[serde]]", "[[tooling-project-hygiene]]", "docs.rs/serde", "serde.rs"]
source_urls: ["https://docs.rs/serde/latest/serde/", "https://serde.rs/", "https://docs.rs/serde_json/latest/serde_json/", "https://serde.rs/attributes.html"]
rust_version: "edition 2024 / 1.85+"
---

# Serde Data Format Playbook

Use Serde to define Rust data models once and serialize or deserialize them across formats with explicit attributes at the compatibility boundary.

## What it is
Serde is Rust's standard ecosystem crate for serialization and deserialization.
The core crate defines `Serialize` and `Deserialize`.
Format crates such as `serde_json`, `toml`, `bincode`, `postcard`, and `serde_yaml` implement concrete encodings.
The usual path is deriving `Serialize` and `Deserialize` on strongly typed structs and enums.
Serde is most valuable at boundaries: config files, HTTP JSON, message queues, persistence snapshots, and test fixtures.

## How it works
The derive macros generate implementations for your data types.
Field attributes customize naming, defaults, skipped fields, optional fields, aliases, flattening, and custom conversion.
Container attributes customize enum tagging strategies and rename conventions.
Use these attributes deliberately because they become wire-format compatibility rules.
Adding an optional field with `#[serde(default)]` is usually backward-compatible.
Renaming a field without an alias is usually breaking for persisted data and external APIs.

Serde is format-agnostic, but formats differ.
JSON has strings, numbers, booleans, arrays, objects, and null.
Binary formats may preserve richer Rust shapes or require schema discipline.
For public APIs, prefer explicit DTO structs over serializing internal domain objects directly.
For libraries, avoid forcing `serde` as an always-on dependency unless serialization is core; consider a feature flag.
Verify the latest versions of `serde` and the format crate on docs.rs before updating `Cargo.toml`.

## Example
```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "snake_case")]
struct UserCreated {
    user_id: u64,
    email: String,
    #[serde(default)]
    marketing_opt_in: bool,
}

fn main() -> Result<(), serde_json::Error> {
    let json = r#"{"user_id":7,"email":"ada@example.com"}"#;
    let event: UserCreated = serde_json::from_str(json)?;
    assert_eq!(event.marketing_opt_in, false);

    let encoded = serde_json::to_string(&event)?;
    assert!(encoded.contains("user_id"));
    Ok(())
}
```

Cargo dependencies for this example:
```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

## Best practice
- ✅ Model external data with dedicated DTOs instead of exposing internal structs accidentally.
- ✅ Use `#[serde(default)]` for newly added fields that old data will not contain.
- ✅ Use `#[serde(rename_all = "...")]` to make naming conventions explicit.
- ✅ Use `Option<T>` only when absence is semantically meaningful.
- ✅ Keep format errors in your normal [[Error Handling]] path.
- ✅ Feature-gate Serde derives in libraries when serialization is optional.
- ✅ Add round-trip tests for formats you promise to support.
- ✅ Check docs.rs for the latest Serde and format-crate versions before dependency changes.

## Pitfalls
- ⚠️ Serializing domain types directly and freezing private implementation details into a public wire format.
- ⚠️ Using `#[serde(flatten)]` everywhere; it can obscure conflicts and versioning rules.
- ⚠️ Renaming fields or enum variants without migration or aliases.
- ⚠️ Treating `serde_json::Value` as the main domain model; see [[Stringly-Typed Code]].
- ⚠️ Enabling derive macros transitively in a no-proc-macro-sensitive crate without review.
- ⚠️ Forgetting that untagged enums can deserialize ambiguously when variants overlap.
- ⚠️ Assuming every format has JSON's semantics for numbers, maps, or null values.

## See also
[[Ecosystem & Crate Playbooks]] · [[Derive Macros]] · [[Structs]] · [[Enums]] · [[Making Invalid States Unrepresentable]] · [[Error Handling]] · [[Type-State Pattern]] · [[Stringly-Typed Code]] · [[Feature Flags]] · [[Reqwest HTTP Client Playbook]] · [[Axum Web Service Playbook]] · [[Choosing the Right Rust Crate]]

## Sources
- Serde crate docs — https://docs.rs/serde/latest/serde/; verify the latest version before editing `Cargo.toml`.
- Serde guide and attributes — https://serde.rs/, https://serde.rs/attributes.html
- serde_json crate docs — https://docs.rs/serde_json/latest/serde_json/; verify the latest version.
- Existing source notes — [[serde]], [[tooling-project-hygiene]].
