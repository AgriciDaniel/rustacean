---
type: moc
title: "Anti-patterns & Footguns"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, antipatterns, footguns]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Ownership]]", "[[Result]]", "[[Option vs Result]]", "[[Concurrency]]", "[[Borrowing]]", "[[Unwrap and Expect Overuse]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html", "https://doc.rust-lang.org/book/ch16-00-concurrency.html", "https://doc.rust-lang.org/book/ch17-00-async-await.html"]
rust_version: "edition 2024 / 1.85+"
---

# Anti-patterns & Footguns

Anti-patterns and footguns are Rust habits that compile but undermine Rust's guarantees, clarity, performance, or error behavior; the cure is usually to move intent into ownership, types, pattern matching, and explicit failure paths.

## Concepts
- [[Ownership]]
- [[Borrowing]]
- [[Option vs Result]]
- [[Result]]
- [[Panic Unwinding and Abort]]
- [[Concurrency]]
- [[Async and Await]]
- [[Interior Mutability]]
- [[Integer Types]]

## Patterns
- [[Newtype Pattern]]
- [[Message Passing]]
- [[Propagating Errors]]
- [[Custom Error Types]]
- [[Error Handling with thiserror]]
- [[Adding Error Context]]

## Antipatterns
- [[Needless Clone]]
- [[Rc RefCell Overuse]]
- [[Premature Arc Mutex]]
- [[Deref Polymorphism Antipattern]]
- [[Stringly-Typed Code]]
- [[Integer Overflow Assumptions]]
- [[Blocking in Async]]
- [[Index Panics vs get]]
- [[Unnecessary Collect]]
- [[Is Some Then Unwrap]]
- [[Sentinel Values]]
- [[Unwrap and Expect Overuse]]
- [[Panicking in Libraries]]
- [[Stringly-Typed Errors]]

## Reading Path
Start with [[Needless Clone]], [[Index Panics vs get]], and [[Is Some Then Unwrap]] for local code smells. Then read [[Stringly-Typed Code]], [[Sentinel Values]], and [[Integer Overflow Assumptions]] for type-system design habits. Finish with [[Rc RefCell Overuse]], [[Premature Arc Mutex]], [[Blocking in Async]], and [[Deref Polymorphism Antipattern]] for architecture-level footguns.

## Sources
- The Rust Programming Language, ch. 4 "Understanding Ownership" — [[the-book]], https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
- The Rust Programming Language, ch. 16 "Fearless Concurrency" — [[the-book]], https://doc.rust-lang.org/book/ch16-00-concurrency.html
- The Rust Programming Language, ch. 17 "Fundamentals of Asynchronous Programming" — [[the-book]], https://doc.rust-lang.org/book/ch17-00-async-await.html
