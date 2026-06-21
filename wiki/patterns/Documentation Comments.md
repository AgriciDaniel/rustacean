---
type: pattern
title: "Documentation Comments"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustdoc, documentation, comments]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Comments]]", "[[Functions]]", "[[Modules]]", "[[Testing]]", "[[Result]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#making-useful-documentation-comments", "https://doc.rust-lang.org/reference/comments.html#doc-comments", "https://doc.rust-lang.org/rustdoc/"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Public API Documentation"]
---

# Documentation Comments

Documentation comments are the idiomatic way to document Rust APIs because rustdoc turns them into searchable HTML and `cargo test` can run their examples.

## What it is
Use `///` before an item to document that item. Use `//!` near the top of a crate root or module file to document the containing crate or module.

Rustdoc expects Markdown inside doc comments. Common sections include `# Examples`, `# Panics`, `# Errors`, and `# Safety`, depending on what the API exposes.

The Reference specifies doc comments as syntax for `doc` attributes. `/// text` is equivalent in meaning to an outer `#[doc = "..."]` attribute.

## How it works
`cargo doc` builds HTML documentation. `cargo doc --open` builds it and opens it in a browser. Public crates should treat this output as part of their API surface.

Code blocks in documentation comments can be tested by `cargo test`. This keeps examples close to the API and helps catch stale documentation.

Inner doc comments such as `//!` apply to the item that contains them, so they are appropriate for module-level overviews. Outer doc comments such as `///` apply to the item that follows.

## Example
```rust
/// Adds one to `value`.
///
/// # Examples
///
/// ```
/// # fn add_one(value: i32) -> i32 { value + 1 }
/// assert_eq!(add_one(5), 6);
/// ```
pub fn add_one(value: i32) -> i32 {
    value + 1
}

fn main() {
    assert_eq!(add_one(1), 2);
}
```

## Common errors
Doctest examples are compiled as Rust code. If an example references setup code that is not shown or
hidden with `#`, `cargo test` fails.

```text
error[E0425]: cannot find function `add_one` in this scope
```

Fix by writing a complete example, importing the public item, or using hidden lines for necessary
setup that should not clutter the rendered docs.

## Best practice
- ✅ Document public functions, types, modules, and traits at the level callers need.
- ✅ Include a small `# Examples` section when usage is not completely obvious.
- ✅ Add `# Errors`, `# Panics`, or `# Safety` sections when those contracts exist.
- ✅ Prefer line doc comments for Markdown-heavy docs because block comments terminate at `*/`.

## Pitfalls
- ⚠️ Do not describe implementation details when callers need usage contracts.
- ⚠️ Do not let examples drift; run doc tests with `cargo test`.
- ⚠️ Do not use `//!` when you mean to document the next function; use `///`.
- ⚠️ Avoid promising behavior in docs that the type signature and tests do not support.

## See also
[[Comments]] · [[Functions]] · [[Modules]] · [[Rustdoc]] · [[Testing]] · [[Result]] · [[Untested Documentation Examples]] · [[Readable Generic APIs]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 14.2 "Making Useful Documentation Comments" — [[the-book]], https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#making-useful-documentation-comments
- The Rust Reference, "Doc comments" — [[the-reference]], https://doc.rust-lang.org/reference/comments.html#doc-comments
- The Rustdoc Book — https://doc.rust-lang.org/rustdoc/
