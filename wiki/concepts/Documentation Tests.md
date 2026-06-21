---
type: concept
title: "Documentation Tests"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, documentation, doctest]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Documentation Comments]]", "[[rustdoc]]", "[[Testable Documentation Examples]]", "[[Test Harness and cargo test]]", "[[Untested Documentation Examples]]", "[[Testing & Documentation]]"]
sources: ["[[the-book]]", "[[rustdoc-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests", "https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html"]
rust_version: "edition 2024 / 1.85+"
---

# Documentation Tests

Documentation tests are Rust code blocks in API docs that `rustdoc` extracts, compiles, and usually runs, keeping examples synchronized with the library.

## What it is
A doctest is a code example in a documentation comment or Markdown input that `rustdoc --test` treats as executable Rust. Running `cargo test` includes doctests for library documentation.

If a code block has no language tag, rustdoc assumes it is Rust. A normal doctest passes if it compiles and runs without panicking.

Doctests are both documentation and tests. They should show real public API usage while also containing enough hidden setup to remain compilable.

## How it works
Rustdoc preprocesses examples before testing. It adds common lint allowances, preserves leading crate attributes, may inject `extern crate <mycrate>;`, and wraps code in `fn main` if no `main` is present.

Lines beginning with `#` are hidden from rendered output but included during compilation. This lets examples use setup, imports, `fn main() -> Result`, or cleanup code without distracting readers.

Fence attributes change behavior: `should_panic` expects runtime panic, `no_run` compiles but skips execution, `compile_fail` expects compilation failure, and `edition2024` selects the edition for that sample.

Starting with edition 2024 behavior, rustdoc can merge compatible doctests before compiling them to
reduce overhead, while still running doctests in their own process. Use `standalone_crate` only for
examples that depend on crate-level line identity, exact compile diagnostics, or other isolation that
would be disturbed by merging.

## Example
```rust
/// Parses a decimal port number.
///
/// # Examples
///
/// ```
/// # fn main() -> Result<(), std::num::ParseIntError> {
/// let port = "8080".parse::<u16>()?;
/// assert_eq!(port, 8080);
/// # Ok(())
/// # }
/// ```
pub fn parse_port(text: &str) -> Result<u16, std::num::ParseIntError> {
    text.parse()
}
```

## More realistic example
```rust
/// Builds a normalized tag.
///
/// # Examples
///
/// ```
/// # use docs_demo::normalize_tag;
/// let tag = normalize_tag("  Rust DocTests  ");
/// assert_eq!(tag, "rust-doctests");
/// ```
///
/// Inputs containing only whitespace are rejected:
///
/// ```
/// # use docs_demo::normalize_tag;
/// assert_eq!(normalize_tag("   "), "");
/// ```
pub fn normalize_tag(input: &str) -> String {
    input.trim().to_lowercase().replace(' ', "-")
}
```

## Common errors
Using `?` in a doctest without giving rustdoc a `Result`-returning context produces a type mismatch
because the generated `main` returns `()` by default.

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`
```

Fix with hidden setup:

```rust
/// ```
/// # fn main() -> Result<(), std::num::ParseIntError> {
/// let n = "42".parse::<u32>()?;
/// assert_eq!(n, 42);
/// # Ok(())
/// # }
/// ```
pub fn example_anchor() {}
```

## Best practice
- ✅ Put runnable examples on public APIs, especially constructors, parsers, and common workflows.
- ✅ Use hidden `#` lines to make examples compile while keeping the rendered snippet focused.
- ✅ Prefer `no_run` for examples that should compile but would touch the network, filesystem, or infinite loop.
- ✅ Use `compile_fail` sparingly for type-system guarantees that are important to document.
- ✅ Use `text` for shell transcripts, TOML snippets, and other non-Rust blocks so rustdoc does not try to compile them as Rust.
- ✅ Keep doctest assertions small and stable; they are examples first, regression tests second.

## Pitfalls
- ⚠️ Marking examples `ignore` loses the synchronization benefit; see [[Untested Documentation Examples]].
- ⚠️ Using private APIs in doctests usually fails because doctests link against the public crate interface.
- ⚠️ Depending on exact doctest line numbers can be fragile in edition 2024 because compatible doctests may be merged; use `standalone_crate` if line identity matters.
- ⚠️ A code fence with no language tag is treated as Rust by rustdoc; mark non-Rust fences explicitly.

## See also
[[Documentation Comments]] · [[rustdoc]] · [[Testable Documentation Examples]] · [[Untested Documentation Examples]] · [[Test Harness and cargo test]] · [[Integration Tests]] · [[Assertion Macros in Tests]] · [[Result Returning Tests]] · [[Testing & Documentation]]

## Sources
- The Rust Programming Language, ch. 14.2 "Documentation Comments as Tests" — [[the-book]], https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests
- The rustdoc book, "Documentation tests" — [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
