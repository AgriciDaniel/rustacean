---
type: concept
title: "Doctest Attributes"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustdoc, doctest, documentation]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Documentation Tests]]", "[[Testable Documentation Examples]]", "[[Untested Documentation Examples]]", "[[rustdoc]]", "[[Documentation Comments]]", "[[Testing & Documentation]]"]
sources: ["[[rustdoc-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html#attributes", "https://doc.rust-lang.org/rustdoc/write-documentation/the-doc-attribute.html#testattr", "https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests"]
rust_version: "edition 2024 / 1.85+"
---

# Doctest Attributes

Doctest attributes are rustdoc code-fence flags and crate-level `doc(test(...))` settings that tell rustdoc whether an example should run, only compile, fail to compile, panic, use a specific edition, or receive extra attributes.

## What it is
Rustdoc treats Rust code blocks in documentation as [[Documentation Tests]].
Code-fence attributes refine what "passes" means for a specific example.

The common stable attributes are:
`should_panic`, `no_run`, `compile_fail`, `ignore`, and edition selectors such as `edition2024`.
Rustdoc also supports `standalone_crate` for examples that must not be merged with other doctests.

At crate or module level, `#![doc(test(attr(...)))]` adds attributes to generated doctest crates.
`#![doc(test(no_crate_inject))]` disables rustdoc's default `extern crate <mycrate>;` injection.

These attributes are documentation behavior, not normal `#[test]` attributes.
They live in Markdown code fences or the `#[doc]` attribute system, and rustdoc interprets them
while extracting examples.

## How it works
A normal doctest passes if it compiles and runs without panicking.
`should_panic` inverts the runtime expectation: the code must compile and then panic.
`no_run` compiles the example but does not execute it.
`compile_fail` expects compilation to fail.
`ignore` skips the example and is usually weaker than the more precise alternatives.

Edition attributes such as `edition2024` tell rustdoc which edition to use for that code block.
This matters for examples embedded in older-edition crates or migration docs.

Starting with edition 2024 behavior, rustdoc may merge compatible doctests before compiling them
for performance, while still running doctests in their own process.
Use `standalone_crate` only when the example depends on crate-level isolation, exact line numbers,
or another property that merging would disturb.

Rustdoc warns by default for invalid code-block attributes through
`rustdoc::invalid_codeblock_attributes`.
A typo such as `should-panic` is not the same as `should_panic`.

## Example
```rust
/// Parses a decimal port number.
///
/// # Examples
///
/// Normal examples compile and run:
///
/// ```
/// # use docs_demo::parse_port;
/// assert_eq!(parse_port("8080"), Ok(8080));
/// ```
///
/// Invalid input returns an error:
///
/// ```
/// # use docs_demo::parse_port;
/// assert!(parse_port("not a port").is_err());
/// ```
///
/// Code that should compile but not run in doctests uses `no_run`:
///
/// ```no_run
/// # use docs_demo::parse_port;
/// let port = parse_port("8080").expect("valid port");
/// println!("binding to port {port}");
/// ```
pub fn parse_port(text: &str) -> Result<u16, std::num::ParseIntError> {
    text.parse()
}
```

The file above is ordinary Rust code with documentation comments.
When rustdoc tests it, the fenced examples are extracted and checked according to their attributes.

## Attribute choices
Use `no_run` for examples that should type-check but should not execute in CI:
network calls, infinite event loops, destructive filesystem operations, or examples needing a
service that is not part of the test environment.

Use `compile_fail` for examples whose point is that Rust rejects them.
Keep those examples narrow, because code that fails today might compile in a future Rust release if
the language gains new capabilities.
Nightly-only error-number annotations for `compile_fail` are not part of the stable 1.85+ contract.

Use `should_panic` when panic behavior is the documented contract.
For ordinary tests, prefer `#[should_panic(expected = "...")]` when possible; for doctests, keep the
example small enough that the intended panic is obvious.

Use `ignore` only when the example truly cannot be compiled by rustdoc.
If the code is not Rust, mark it as `text`, `console`, `toml`, or another non-Rust fence instead.

## Crate-level doctest attributes
```rust
#![doc(test(attr(deny(warnings))))]

/// Adds one to a number.
///
/// ```
/// # use docs_demo::add_one;
/// assert_eq!(add_one(1), 2);
/// ```
pub fn add_one(n: i32) -> i32 {
    n + 1
}
```

The crate-level `doc(test(attr(...)))` form adds attributes to generated doctest crates.
Use it sparingly.
Making doctests stricter can be valuable, but examples often contain intentionally small snippets
that would be noisy under the same lint policy as production code.

## Best practice
- ✅ Prefer normal runnable doctests for public API examples.
- ✅ Use `no_run` instead of `ignore` when compilation is still meaningful.
- ✅ Use `compile_fail` for type-system examples that must be rejected.
- ✅ Use `edition2024` when the example needs to state its edition explicitly.
- ✅ Use hidden `#` lines from [[Testable Documentation Examples]] before reaching for `ignore`.
- ✅ Enable strict doctest attributes only when the whole crate's examples can satisfy them.
- ✅ Let `rustdoc::invalid_codeblock_attributes` catch typos in code-fence attributes.

## Pitfalls
- ⚠️ `ignore` creates [[Untested Documentation Examples]] by skipping both compilation and execution.
- ⚠️ `compile_fail` examples can become stale when Rust accepts new syntax or improves inference.
- ⚠️ Misspelled attributes may change test behavior; use the exact spellings `should_panic`, `no_run`, and `compile_fail`.
- ⚠️ `standalone_crate` slows doctests if used everywhere; reserve it for examples that require isolation.
- ⚠️ Crate-level `doc(test(attr(...)))` settings can make simple examples noisy or brittle.

## See also
[[Documentation Tests]] · [[Testable Documentation Examples]] · [[Untested Documentation Examples]] ·
[[Documentation Comments]] · [[rustdoc]] · [[Test Harness and cargo test]] ·
[[Ignored Tests]] · [[Broad should_panic Tests]] · [[Edition 2024]] · [[Testing & Documentation]]

## Sources
- The rustdoc book, "Documentation tests / Attributes" — [[rustdoc-book]],
  https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html#attributes
- The rustdoc book, "`#[doc]` attribute / `test(attr(..))`" — [[rustdoc-book]],
  https://doc.rust-lang.org/rustdoc/write-documentation/the-doc-attribute.html#testattr
- The Rust Programming Language, ch. 14.2 "Documentation Comments as Tests" — [[the-book]],
  https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests
