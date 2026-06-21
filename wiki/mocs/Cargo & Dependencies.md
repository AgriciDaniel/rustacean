---
type: moc
title: "Cargo & Dependencies"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, dependencies, moc]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Dependencies and Version Requirements]]", "[[Feature Flags]]", "[[Cargo.lock]]"]
sources: ["[[cargo-book]]", "[[tooling-project-hygiene]]", "[[dependency-supply-chain-security]]"]
source_urls: ["https://doc.rust-lang.org/cargo/", "https://doc.rust-lang.org/cargo/reference/manifest.html", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo & Dependencies

Cargo is Rust's package manager, build orchestrator, dependency resolver, and publishing client; this map groups the atomic notes for manifests, dependency resolution, features, workspaces, release hygiene, and supply-chain practice.

## Concepts
- [[Cargo.toml Manifest]]
- [[Dependencies and Version Requirements]]
- [[Semantic Versioning]]
- [[Feature Flags]]
- [[Feature Resolver]]
- [[Cargo Workspaces]]
- [[Build Scripts (build.rs)]]
- [[Publishing to crates.io]]
- [[Cargo.lock]]
- [[Cargo Configuration Hierarchy]]
- [[Cargo Source Overrides]]
- [[Profiles and Optimization Settings]]
- [[MSRV Policy]]

## Patterns
- [[cargo-audit and cargo-deny]]
- [[Minimizing Dependencies]]
- [[Workspace Dependency Inheritance]]
- [[cargo publish, yank and owners]]

## Antipatterns
- [[Overbroad Version Requirements]]
- [[Non-Additive Feature Flags]]

## See also
[[Ownership]] · [[Error Handling]] · [[The Error Trait]] · [[Concurrency]] · [[Unsafe Rust]] · [[Testing]] · [[Documentation Tests]]

## Sources
- The Cargo Book — [[cargo-book]], https://doc.rust-lang.org/cargo/
- The Cargo Book, "The Manifest Format" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/manifest.html
- The Cargo Book, "Specifying Dependencies" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
