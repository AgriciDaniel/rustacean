---
type: moc
title: "Performance & Optimization"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, optimization, moc]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Profiling Rust Programs]]", "[[Benchmarking with Criterion]]", "[[Reducing Heap Allocations]]", "[[Iterator Performance]]", "[[LTO and codegen-units]]", "[[Avoiding Premature Optimization]]", "[[Flamegraph and perf Workflow]]", "[[Allocator Choices]]", "[[SIMD and target_feature]]", "[[Cache-Friendly Data Layout]]"]
sources: ["[[the-book]]", "[[cargo-book]]", "[[the-reference]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/book/ch14-01-release-profiles.html", "https://doc.rust-lang.org/cargo/reference/profiles.html", "https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Performance & Optimization

Rust performance work starts with clear code, then uses profiling and benchmarking to justify targeted changes.

## Concepts
- [[Profiling Rust Programs]]
- [[Iterator Performance]]
- [[The inline Attribute]]
- [[SIMD and target_feature]]

## Patterns
- [[Benchmarking with Criterion]]
- [[Flamegraph and perf Workflow]]
- [[Reducing Heap Allocations]]
- [[Allocator Choices]]
- [[Bounds-Check Elimination]]
- [[Cache-Friendly Data Layout]]
- [[SmallVec for Inline Storage]]
- [[Arena Allocation]]
- [[LTO and codegen-units]]

## Antipatterns
- [[Avoiding Premature Optimization]]
- [[Speculative Micro-Optimization]]

## Neighboring Notes
- [[Profiles and Optimization Settings]]
- [[Codegen and Optimization Flags]]
- [[Zero-Cost Abstractions]]
- [[Capacity and Reallocation]]
- [[Manual Index Loops for Speed]]
- [[Needless Clone]]
- [[Unnecessary Collect]]
- [[Prefer Iterator Pipelines to Manual Indexing]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Programming Language, ch. 14.1 "Customizing Builds with Release Profiles" — [[the-book]],
  https://doc.rust-lang.org/book/ch14-01-release-profiles.html
- The Cargo Book, "Profiles" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html
- The Rust Reference, "Code generation attributes: inline" — [[the-reference]],
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute
