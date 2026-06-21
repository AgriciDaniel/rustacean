---
type: moc
title: "Collections & Strings"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, strings, moc]
domain: "Collections & Strings"
difficulty: basic
related: ["[[Vec]]", "[[String and str]]", "[[HashMap]]", "[[The Entry API]]", "[[Iterating Collections]]", "[[Choosing Collection Types]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-00-common-collections.html", "https://doc.rust-lang.org/std/collections/index.html", "https://doc.rust-lang.org/std/string/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Collections & Strings

Collections and strings are Rust's owned, borrowed, growable, and iterable building blocks for runtime-sized data.

## Concepts
- [[Vec]]
- [[String and str]]
- [[HashMap]]
- [[BTreeMap and BTreeSet]]
- [[VecDeque]]
- [[Capacity and Reallocation]]
- [[Set Collections with HashSet and BTreeSet]]
- [[BinaryHeap Priority Queues]]
- [[The Slice Type]]

## Patterns
- [[Borrowing Strings and Slices]]
- [[The Entry API]]
- [[Iterating Collections]]
- [[Choosing Collection Types]]
- [[Sorting and Binary Search on Slices]]

## Antipatterns
- [[String Byte Indexing]]
- [[Holding Collection Element References Across Mutation]]
- [[Stale Slice Indices]]

## Adjacent Notes
[[Ownership]] · [[Borrowing]] · [[Dynamically Sized Types]] · [[Index Panics vs get]] · [[Needless Clone]] · [[Unnecessary Collect]] · [[Copy and Clone]]

## Sources
- The Rust Programming Language, ch. 8 "Common Collections" — [[the-book]], https://doc.rust-lang.org/book/ch08-00-common-collections.html
- Standard library collections overview — [[std]], https://doc.rust-lang.org/std/collections/index.html
- Standard library string module overview — [[std]], https://doc.rust-lang.org/std/string/index.html
