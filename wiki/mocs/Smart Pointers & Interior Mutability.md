---
type: moc
title: "Smart Pointers & Interior Mutability"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, moc, smart-pointers, interior-mutability]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Ownership]]", "[[Borrowing]]", "[[The Drop Trait]]", "[[Arc]]", "[[Shared State with Mutex]]", "[[Deref Polymorphism Antipattern]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-00-smart-pointers.html", "https://doc.rust-lang.org/std/boxed/struct.Box.html", "https://doc.rust-lang.org/std/cell/index.html", "https://doc.rust-lang.org/std/rc/index.html", "https://doc.rust-lang.org/std/borrow/enum.Cow.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Smart Pointers"]
---

# Smart Pointers & Interior Mutability

Smart pointers combine ownership with pointer-like behavior, while interior mutability provides controlled mutation through shared references.

## Concepts
- [[Box]]
- [[Deref and DerefMut]]
- [[Rc]]
- [[RefCell]]
- [[Interior Mutability]]
- [[Cell]]
- [[Reference Cycles and Weak]]
- [[Cow]]

## Patterns
- [[Weak Back References]]

## Antipatterns
- [[Long-Lived RefCell Borrows]]

## Neighboring Notes
[[Ownership]] · [[Borrowing]] · [[The Drop Trait]] · [[Arc]] · [[Shared State with Mutex]] · [[Deref Polymorphism Antipattern]] · [[Rc RefCell Overuse]]

## Sources
- The Rust Programming Language, ch. 15 "Smart Pointers" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-00-smart-pointers.html
- Standard library, `std::boxed`, `std::cell`, `std::rc`, and `std::borrow::Cow` - [[std]],
  https://doc.rust-lang.org/std/boxed/struct.Box.html
  https://doc.rust-lang.org/std/cell/index.html
  https://doc.rust-lang.org/std/rc/index.html
  https://doc.rust-lang.org/std/borrow/enum.Cow.html
