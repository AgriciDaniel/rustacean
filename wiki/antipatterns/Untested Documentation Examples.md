---
type: antipattern
title: "Untested Documentation Examples"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, documentation, doctest]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Documentation Tests]]", "[[Testable Documentation Examples]]", "[[Documentation Comments]]", "[[rustdoc]]", "[[Public API Documentation]]", "[[Testing & Documentation]]"]
sources: ["[[rustdoc-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html#attributes", "https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests"]
rust_version: "edition 2024 / 1.85+"
---

# Untested Documentation Examples

Untested documentation examples are examples marked `ignore` or written as non-Rust text when they could be compiled; they drift from the API and teach broken usage.

## The mistake
The easiest way to silence a failing doctest is to mark the code block `ignore`. Rustdoc warns that this is almost never what you want because it gives up compile-time checking.

Another form is omitting assertions or using prose-only examples for code that could be shown as a runnable snippet. The docs may still look polished, but `cargo test` no longer protects them.

The result is documentation that can become stale exactly where users are most likely to copy code.

## Why it happens
Examples often need setup that feels distracting: imports, a `main`, error handling, feature flags, or external resources. Without knowing rustdoc's hidden lines and fence attributes, authors reach for `ignore`.

Rustdoc provides narrower tools. `no_run` checks compilation without execution, `compile_fail` asserts rejection, `should_panic` asserts panic behavior, and hidden `#` lines keep setup out of rendered docs.

For code that is not Rust, use `text` or a custom class intentionally. For Rust API examples, keep them as doctests whenever practical.

The cost of untested examples is highest for public APIs because rustdoc examples are often copied
directly into user projects. A stale example is not just bad prose; it is executable misinformation
that normal unit tests may never see.

## Example
```rust
#![crate_name = "docs_demo"]

/// Converts text to uppercase.
///
/// # Examples
///
/// ```
/// let value = docs_demo::shout("rust");
/// assert_eq!(value, "RUST");
/// ```
pub fn shout(input: &str) -> String {
    input.to_uppercase()
}
```

## Better alternatives to `ignore`
```rust
/// Sends a request.
///
/// This example should compile, but it is not run during doctests because it
/// would require a live service:
///
/// ```no_run
/// # use docs_demo::send_request;
/// # fn main() -> Result<(), Box<dyn std::error::Error>> {
/// send_request("https://example.com")?;
/// # Ok(())
/// # }
/// ```
///
/// This example documents an intentional type error:
///
/// ```compile_fail
/// let value: u32 = "not a number";
/// ```
pub fn send_request(_url: &str) -> Result<(), Box<dyn std::error::Error>> {
    Ok(())
}
```

## Common errors
Rustdoc warns about misspelled doctest attributes, which can accidentally turn a special fence into a
normal Rust test:

```text
warning: unknown attribute `should-panic`. Did you mean `should_panic`?
```

Fix the attribute spelling and prefer known fence attributes: `should_panic`, `no_run`,
`compile_fail`, `edition2024`, and target-specific `ignore-*` when truly needed.

## Best practice
- ✅ Prefer normal runnable Rust code blocks for public API examples.
- ✅ Use hidden `#` setup lines to keep examples both readable and compilable.
- ✅ Use `no_run` when running would require network, credentials, infinite loops, or destructive side effects.
- ✅ Use `compile_fail` for examples whose purpose is to show rejected code.
- ✅ Use `text` for command output, shell transcripts, and configuration snippets that are not Rust.
- ✅ Add assertions to examples that promise a result, so the doctest checks more than syntax.

## Pitfalls
- ⚠️ `ignore` skips both compilation and execution, so API changes can silently break the example.
- ⚠️ Using `text` for real Rust examples hides them from doctesting.
- ⚠️ Examples without assertions can compile while no longer demonstrating the promised result.
- ⚠️ A doctest using private APIs may force authors toward `ignore`; instead, rewrite the example through the public API.

## See also
[[Documentation Tests]] · [[Testable Documentation Examples]] · [[Documentation Comments]] · [[rustdoc]] · [[Assertion Macros in Tests]] · [[Public API Documentation]] · [[Ignored Tests]] · [[Test Harness and cargo test]] · [[Testing & Documentation]]

## Sources
- The rustdoc book, "Attributes" for documentation tests — [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html#attributes
- The Rust Programming Language, ch. 14.2 "Documentation Comments as Tests" — [[the-book]], https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests
