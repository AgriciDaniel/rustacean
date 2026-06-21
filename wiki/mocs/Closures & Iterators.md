---
type: moc
title: "Closures & Iterators"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, iterators, moc]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Closures]]", "[[Iterators]]", "[[Fn, FnMut, FnOnce]]", "[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Zero-Cost Abstractions]]"]
sources: ["[[the-book]]", "[[std]]", "[[rust-performance-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-00-functional-features.html", "https://doc.rust-lang.org/book/ch13-01-closures.html", "https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/book/ch13-04-performance.html"]
rust_version: "edition 2024 / 1.85+"
---

# Closures & Iterators

Closures and iterators are Rust's core functional-style tools for local behavior customization and lazy sequence processing with low-level performance.

## Concepts
- [[Closures]]
- [[Closure Type Inference]]
- [[Capturing the Environment]]
- [[Fn, FnMut, FnOnce]]
- [[move Closures]]
- [[Iterators]]
- [[The Iterator Trait]]
- [[Iterator Adapters]]
- [[Consuming Adapters]]
- [[Lazy Evaluation]]
- [[Zero-Cost Abstractions]]

## Patterns
- [[Prefer Iterator Pipelines to Manual Indexing]]
- [[Return Iterators Instead of Collecting]]

## Antipatterns
- [[Unconsumed Iterator Adapters]]
- [[Moving Out of FnMut Closures]]
- [[Manual Index Loops for Speed]]

## Related Existing Notes
[[Function Pointers]] · [[Returning Closures]] · [[Boxed Closure Returns]] · [[Unnecessary Collect]] · [[While and For Loops]] · [[Needless Clone]] · [[Ownership]] · [[Borrowing]]

## Sources
- The Rust Programming Language, ch. 13 "Functional Language Features: Iterators and Closures" - [[the-book]], https://doc.rust-lang.org/book/ch13-00-functional-features.html
- The Rust Programming Language, ch. 13.1 "Closures" - [[the-book]], https://doc.rust-lang.org/book/ch13-01-closures.html
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-04-performance.html
