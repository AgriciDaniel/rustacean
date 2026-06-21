---
type: concept
title: "Comments"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, comments, syntax, documentation]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Documentation Comments]]", "[[Functions]]", "[[Statements vs Expressions]]", "[[Modules]]", "[[Rustdoc]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-04-comments.html", "https://doc.rust-lang.org/reference/comments.html"]
rust_version: "edition 2024 / 1.85+"
---

# Comments

Rust comments are source text ignored by the compiler except for documentation comments, which are translated into `doc` attributes for rustdoc.

## What it is
Ordinary comments explain code to humans. The common form is a line comment starting with `//` and continuing to the end of the line.

Block comments use `/* ... */` and can nest in Rust, which is useful when temporarily commenting out code that already contains block comments.

Documentation comments use `///`, `//!`, `/** ... */`, or `/*! ... */` and have special meaning; see [[Documentation Comments]].

## How it works
The Book recommends placing ordinary comments on the line above the code they explain. End-of-line comments are valid, but they are best for short clarifications that do not interrupt scanning.

The Reference treats non-doc comments as whitespace. That means they separate tokens but do not change program semantics.

Doc comments are not just whitespace: outer doc comments apply to the item that follows, while inner doc comments apply to the containing item such as a module or crate.

## Example
```rust
fn main() {
    let base = 10;

    // Discount is represented as whole percentage points.
    let discount_percent = 15;

    let discounted = base * (100 - discount_percent) / 100;
    assert_eq!(discounted, 8);
}
```

## Edge cases
Nested block comments are valid Rust, but they are still usually a temporary editing tool rather than
committed documentation:

```rust
fn main() {
    /* outer
       /* inner */
       still in the outer comment
    */
    assert_eq!(2 + 2, 4);
}
```

Use line comments for normal explanations. Use doc comments when the text should become rustdoc
output or a doctest.

## Common errors
An unterminated block comment stops tokenization before type checking:

```text
error[E0758]: unterminated block comment
```

Fix by closing `/* ... */`, or prefer `//` comments when commenting out short snippets.

## Best practice
- ✅ Prefer comments that explain why code is shaped a certain way, not what obvious syntax does.
- ✅ Put longer comments above the code they describe.
- ✅ Use [[Documentation Comments]] for public APIs instead of ordinary comments.
- ✅ Remove stale comments when the code changes; an outdated comment is worse than no comment.

## Pitfalls
- ⚠️ Do not use comments to compensate for unclear names or oversized functions.
- ⚠️ Avoid leaving commented-out code in committed notes or examples; version control keeps history.
- ⚠️ Remember that `///` and `//!` are doc comments, not ordinary comments.
- ⚠️ Block doc comments can be awkward with Markdown containing `*/`; line doc comments are often safer.

## See also
[[Documentation Comments]] · [[Functions]] · [[Modules]] · [[Rustdoc]] · [[Statements vs Expressions]] · [[Testing]] · [[Untested Documentation Examples]] · [[Name Resolution]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.4 "Comments" — [[the-book]], https://doc.rust-lang.org/book/ch03-04-comments.html
- The Rust Reference, "Comments" — [[the-reference]], https://doc.rust-lang.org/reference/comments.html
