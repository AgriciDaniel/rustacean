---
type: concept
title: "Intra-doc Links"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustdoc, documentation, links]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[rustdoc]]", "[[Documentation Comments]]", "[[Documentation Tests]]", "[[Public API Documentation]]", "[[Module Paths]]", "[[Testing & Documentation]]"]
sources: ["[[rustdoc-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html", "https://doc.rust-lang.org/rustdoc/lints.html#broken_intra_doc_links", "https://doc.rust-lang.org/rustdoc/lints.html#private_intra_doc_links"]
rust_version: "edition 2024 / 1.85+"
---

# Intra-doc Links

Intra-doc links are rustdoc-checked Markdown links to Rust items, letting API documentation link to types, functions, modules, methods, associated items, macros, and primitives by Rust path instead of hard-coded URLs.

## What it is
An intra-doc link is a documentation link such as ``[`Result`]``, ``[`crate::parse`]``,
``[`Self::new`]``, or ``[`Iterator::next`]`` that rustdoc resolves to an item page.

Use intra-doc links for public API navigation.
They are more robust than copied HTML paths because rustdoc understands Rust names, module scope,
re-exports, and external crate documentation when available.

Rustdoc strips the display backticks, so ``[`Option`]`` displays as code but links to `Option`.
Reference-style Markdown also works: `[parser][crate::parse]`.

Broken links are not just cosmetic.
They usually mean the docs refer to an API that was renamed, moved, made private, or never existed.
That makes intra-doc links a documentation test for API navigation.

## How it works
Rustdoc resolves links in the scope where the documented item is defined.
You can use ordinary paths, including `crate`, `self`, `super`, and `Self`.
Associated functions, methods, associated types, and associated constants are supported.

Rust has separate type, value, and macro namespaces.
When a link is ambiguous, rustdoc warns and suggests a disambiguator.
Common disambiguators include `struct@Name`, `enum@Name`, `trait@Name`, `fn@name`,
`method@Type::method`, `macro@name`, and `prim@str`.
Function links can often be disambiguated with `()`, and macro links with `!`.

Re-exports have a subtle rule.
Links in the original item's documentation are resolved in the original module's scope.
Additional documentation written on the re-export is resolved in the re-exporting module's scope.

Rustdoc warns by default for `rustdoc::broken_intra_doc_links`.
It also warns by default for `rustdoc::private_intra_doc_links`, because a public page linking to a
private item will produce broken public documentation unless private items are documented.

## Example
```rust
#![deny(rustdoc::broken_intra_doc_links)]

/// A token produced by [`parse()`].
#[derive(Debug, PartialEq, Eq)]
pub struct Token {
    text: String,
}

impl Token {
    /// Returns the token text as a [`str`] slice.
    pub fn as_str(&self) -> &str {
        &self.text
    }
}

/// Parses one token.
///
/// Use [`Token::as_str`] to inspect the result.
/// Invalid input is reported with [`ParseError`].
pub fn parse(input: &str) -> Result<Token, ParseError> {
    let text = input.trim();
    if text.is_empty() {
        Err(ParseError)
    } else {
        Ok(Token { text: text.to_owned() })
    }
}

/// Error returned by [`parse()`].
#[derive(Debug, PartialEq, Eq)]
pub struct ParseError;
```

This example is normal library code.
The links are checked when rustdoc builds documentation, and `deny` turns a broken intra-doc link
into a documentation build failure.

## Disambiguation examples
Use a disambiguator when names overlap:

```rust
/// Returns the default [`enum@Mode`].
pub fn default_mode() -> Mode {
    Mode::Fast
}

/// Selects an execution mode.
pub enum Mode {
    Fast,
}

/// A function intentionally sharing a name with [`enum@Mode`].
#[allow(non_snake_case)]
pub fn Mode() -> &'static str {
    "mode"
}
```

Without `enum@Mode`, a link to `Mode` could be ambiguous because a type and a value share the same
spelling.
Prefer unique names for public APIs, but use disambiguators when overlapping names are intentional
or inherited from existing APIs.

## Link shape
Good intra-doc links look like Rust paths:
``[`Vec<T>`]``, ``[`std::fmt::Display`]``, ``[`Self::new`]``, ``[`parse()`]``,
and ``[`println!`]``.

Links containing URL-like syntax or unsupported characters may be treated as ordinary Markdown links
instead of checked intra-doc links.
When you intend a Rust item link, use a clear Rust path and let rustdoc validate it.

Fully-qualified syntax such as `<Vec<T> as IntoIterator>::into_iter` is not generally the most
portable intra-doc-link form.
Prefer a simpler item path or link text with an explicit target, such as
``[`into_iter`](IntoIterator::into_iter)`` when rustdoc can resolve it.

## Best practice
- ✅ Use intra-doc links for every public type, trait, function, macro, and module mentioned as API.
- ✅ Prefer crate-relative paths like ``[`crate::parser::parse`]`` when local scope would be unclear.
- ✅ Use `Self::method` in impl docs when the method belongs to the documented type.
- ✅ Turn `rustdoc::broken_intra_doc_links` into `deny` in library crates with public API docs.
- ✅ Fix private-link warnings by linking to public API, re-exporting intentionally, or making the docs less specific.
- ✅ Use namespace disambiguators when rustdoc reports ambiguity.
- ✅ Keep re-export docs aware of the scope where links are resolved.

## Pitfalls
- ⚠️ Hard-coding generated HTML URLs inside crate docs breaks when item paths or rustdoc output change.
- ⚠️ Linking from public docs to private helpers triggers `rustdoc::private_intra_doc_links`.
- ⚠️ Assuming re-exported docs resolve in the new module can produce surprising links.
- ⚠️ Ambiguous names can link to the wrong namespace unless disambiguated.
- ⚠️ Broken links may be missed if documentation is not built in CI with rustdoc warnings treated seriously.

## See also
[[rustdoc]] · [[Documentation Comments]] · [[Documentation Tests]] · [[Testable Documentation Examples]] ·
[[Public API Documentation]] · [[Module Paths]] · [[Re-exporting with pub use]] ·
[[Visibility and Privacy]] · [[Crate Roots]] · [[Testing & Documentation]]

## Sources
- The rustdoc book, "Linking to items by name" — [[rustdoc-book]],
  https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html
- The rustdoc book, "`broken_intra_doc_links`" — [[rustdoc-book]],
  https://doc.rust-lang.org/rustdoc/lints.html#broken_intra_doc_links
- The rustdoc book, "`private_intra_doc_links`" — [[rustdoc-book]],
  https://doc.rust-lang.org/rustdoc/lints.html#private_intra_doc_links
