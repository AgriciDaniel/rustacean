---
type: concept
title: "rustdoc"
aliases: ["Rustdoc"]
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, documentation, rustdoc]
domain: "Testing & Documentation"
difficulty: basic
related: ["[[Documentation Comments]]", "[[Documentation Tests]]", "[[Testable Documentation Examples]]", "[[Public API Documentation]]", "[[Cargo & Dependencies]]", "[[Testing & Documentation]]"]
sources: ["[[rustdoc-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rustdoc/what-is-rustdoc.html", "https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#making-useful-documentation-comments"]
rust_version: "edition 2024 / 1.85+"
---

# rustdoc

`rustdoc` is Rust's documentation generator: it reads crate roots or Markdown files and produces searchable HTML documentation, while also supporting documentation tests.

## What it is
Rustdoc ships with the standard Rust distribution. Its core job is to turn Rust API documentation into HTML, CSS, and JavaScript that users can browse and search.

Most projects invoke it through Cargo with `cargo doc` or `cargo doc --open`. Cargo chooses the crate name, output directory, dependency search paths, and other options for normal package documentation.

Rustdoc documents publicly reachable items by default. Private implementation details are normally omitted unless private-item documentation is explicitly requested.

## How it works
Documentation comments such as `///` and `//!` become `#[doc = "..."]` attributes. Rustdoc reads those attributes, item signatures, module structure, links, and Markdown content to build the output.

`cargo doc` writes generated documentation under `target/doc`, the Cargo-standard location for build artifacts. Direct `rustdoc src/lib.rs` usage writes to a `doc` directory unless configured otherwise.

Rustdoc can also test examples with `rustdoc --test src/lib.rs`, and Cargo includes library doctests as part of `cargo test`.

Rustdoc is a compiler client as well as a renderer. When it builds docs or tests examples, it needs
the crate edition, dependency search paths, cfg flags, and extern crates. Cargo supplies those for
packages, which is why direct `rustdoc` commands are best reserved for standalone files or debugging.

## Example
```rust
#![crate_name = "docs_demo"]

//! Utilities for small arithmetic examples.

/// Adds one to `value`.
///
/// # Examples
///
/// ```
/// let answer = docs_demo::add_one(5);
/// assert_eq!(answer, 6);
/// ```
pub fn add_one(value: i32) -> i32 {
    value + 1
}
```

## More realistic example
```rust
//! Small helpers for command-line parsing.
//!
//! # Examples
//!
//! ```
//! let verbose = docs_demo::is_verbose_flag("--verbose");
//! assert!(verbose);
//! ```

/// Returns `true` for the long verbose flag.
///
/// # Examples
///
/// ```
/// assert!(docs_demo::is_verbose_flag("--verbose"));
/// assert!(!docs_demo::is_verbose_flag("-v"));
/// ```
pub fn is_verbose_flag(value: &str) -> bool {
    value == "--verbose"
}
```

## Common errors
Running rustdoc directly on a Cargo package without the crate name or dependency paths can make
examples fail even though `cargo test` would configure them correctly.

```text
error[E0433]: failed to resolve: use of unresolved module or unlinked crate
```

Fix by using `cargo doc`, `cargo doc --open`, or `cargo test --doc` for package documentation. Use
direct `rustdoc` only when you also pass the necessary `--crate-name`, `--edition`, `-L`, and
`--extern` context.

## Best practice
- ✅ Use `cargo doc --open` during authoring to inspect the rendered result.
- ✅ Treat the crate root docs as the front page: explain purpose, first example, and major modules.
- ✅ Document public items enough that users do not need to read source for normal use.
- ✅ Use `#[doc(hidden)]` for public implementation details that must exist but should not be part of the guided API.
- ✅ Use intra-doc links such as ``[`Result`]`` and ``[`crate::parse`]`` so rustdoc can validate navigation.
- ✅ Keep the first paragraph of an item short because rustdoc reuses summaries in lists and search results.

## Pitfalls
- ⚠️ Assuming private items will appear in docs can hide useful user-facing APIs; make intended APIs public and documented.
- ⚠️ Writing examples that are not doctested lets docs drift; see [[Documentation Tests]] and [[Untested Documentation Examples]].
- ⚠️ Using rustdoc directly for Cargo packages is usually more error-prone than `cargo doc` because dependencies and crate names must be configured manually.
- ⚠️ Hiding public implementation details with `#[doc(hidden)]` does not make them private API; semver expectations may still apply if users can name them.

## See also
[[Documentation Comments]] · [[Documentation Tests]] · [[Testable Documentation Examples]] · [[Untested Documentation Examples]] · [[Public API Documentation]] · [[Cargo.toml Manifest]] · [[Publishing to crates.io]] · [[Test Harness and cargo test]] · [[Testing & Documentation]]

## Sources
- The rustdoc book, "What is rustdoc?" — [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/what-is-rustdoc.html
- The Rust Programming Language, ch. 14.2 "Making Useful Documentation Comments" — [[the-book]], https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#making-useful-documentation-comments
