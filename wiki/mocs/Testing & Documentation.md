---
type: moc
title: "Testing & Documentation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, documentation, moc]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Test Functions]]", "[[Documentation Tests]]", "[[rustdoc]]", "[[Documentation Comments]]", "[[Test Organization]]", "[[Assertion Macros in Tests]]"]
sources: ["[[the-book]]", "[[rustdoc-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch11-00-testing.html", "https://doc.rust-lang.org/rustdoc/", "https://doc.rust-lang.org/reference/attributes/testing.html"]
rust_version: "edition 2024 / 1.85+"
---

# Testing & Documentation

Testing and documentation in Rust form an executable feedback loop: tests protect behavior, rustdoc explains public APIs, and doctests keep examples honest.

## Concepts
- [[Test Functions]]
- [[Assertion Macros in Tests]]
- [[Unit Tests]]
- [[Integration Tests]]
- [[Test Harness and cargo test]]
- [[Ignored Tests]]
- [[Documentation Comments]]
- [[Documentation Tests]]
- [[Doctest Attributes]]
- [[Intra-doc Links]]
- [[rustdoc]]

## Patterns
- [[Test Organization]]
- [[Result Returning Tests]]
- [[Testable Documentation Examples]]
- [[Test-Driven Development in Rust]]
- [[Snapshot Testing]]

## Antipatterns
- [[Broad should_panic Tests]]
- [[Shared State Between Parallel Tests]]
- [[Untested Documentation Examples]]

## See also
[[Testing & Documentation]] · [[Cargo & Dependencies]] · [[Modules & Project Structure]] · [[Error Handling]] · [[Publishing to crates.io]] · [[Documentation Comments]] · [[Test Functions]]

## Sources
- The Rust Programming Language, ch. 11 "Writing Automated Tests" — [[the-book]], https://doc.rust-lang.org/book/ch11-00-testing.html
- The Rust Programming Language, ch. 14.2 "Publishing a Crate to Crates.io" — [[the-book]], https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html
- The rustdoc book — [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/
- The Rust Reference, "Testing attributes" — [[the-reference]], https://doc.rust-lang.org/reference/attributes/testing.html
