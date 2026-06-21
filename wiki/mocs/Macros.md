---
type: moc
title: "Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, moc]
domain: "Macros"
---

# Macros

Macros are Rust's compile-time code generation tools: use declarative macros for token-pattern transcription and procedural macros when compile-time Rust code must transform token streams.

## Concepts
- [[Declarative Macros]] — pattern-based macros by example.
- [[macro_rules!]] — the construct for writing declarative macros.
- [[Macro Fragment Specifiers]] — syntax categories captured by macro metavariables.
- [[Macro Repetitions]] — variable-length matching and transcription.
- [[Macro Hygiene]] — name resolution in macro expansions.
- [[Procedural Macros]] — token-stream macros implemented as compile-time Rust functions.
- [[Derive Macros]] — `#[derive(...)]`-driven item generation.
- [[Attribute Macros]] — custom outer attributes that transform items.
- [[Function-like Macros]] — `name!(...)` invocation syntax for declarative, built-in, and procedural macros.
- [[syn and quote]] — the common parse-and-generate toolkit for procedural macro crates.
- [[Macro Diagnostics]] — compile-time errors, spans, and messages emitted by macros.

## Patterns
- [[Exporting macro_rules Macros]] — publish declarative macros with stable paths and `$crate` helper references.
- [[Procedural Macro Crate Structure]] — split proc-macro entry points from runtime APIs and downstream tests.
- [[Testing Macros with trybuild]] — compile fixture files to test macro success and failure diagnostics.

## Antipatterns
- [[Ambiguous macro_rules Matchers]] — macro grammars that the parser cannot disambiguate.
- [[Unhygienic Procedural Macro Output]] — unqualified generated names captured by caller scope.

## See also
[[Ownership]] · [[Functions]] · [[Traits]] · [[Generics]] · [[Modules]] · [[Cargo.toml Manifest]] · [[Build Scripts (build.rs)]] · [[Documentation Comments]]

## Sources
- The Rust Programming Language, ch. 20.5 "Macros" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Macros by example" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html
- The Rust Reference, "Procedural macros" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html
