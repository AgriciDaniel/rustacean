---
type: pattern
title: "Testable Documentation Examples"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, documentation, doctest, examples]
domain: "Testing & Documentation"
difficulty: intermediate
related: ["[[Documentation Tests]]", "[[Documentation Comments]]", "[[rustdoc]]", "[[Untested Documentation Examples]]", "[[Assertion Macros in Tests]]", "[[Testing & Documentation]]"]
sources: ["[[rustdoc-book]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html#hiding-portions-of-the-example", "https://doc.rust-lang.org/rustdoc/write-documentation/what-to-include.html#examples"]
rust_version: "edition 2024 / 1.85+"
---

# Testable Documentation Examples

Write examples that users can read as minimal public API demonstrations and rustdoc can compile as tests, using hidden setup lines when necessary.

## What it is
A testable documentation example is a doc comment code block that remains small for readers but complete for the compiler. It shows the public API in realistic use and contains assertions that protect the documented behavior.

Rustdoc's hidden-line feature is the key tool. Lines beginning with `#` are compiled but not rendered, so setup, imports, result-returning `main`, and cleanup can stay out of the visible example.

This pattern is especially useful for examples using `?`, traits that need imports, or code where the visible teaching point is only a few lines inside a larger compilable program.

## How it works
Rustdoc extracts each Rust code block, preprocesses it, compiles it, and normally runs it. Hidden lines participate in that process.

For `?`, either write a hidden `fn main() -> Result<..., ...>` or end with a hidden `Ok::<(), E>(())` expression so type inference knows the error type.

Choose fence attributes precisely. `no_run` still compiles, `should_panic` documents expected panic behavior, and `compile_fail` documents code that must be rejected.

Rustdoc also treats an untagged code block as Rust, so examples should be explicit when the block is
not Rust code. Use `text`, `console`, or another non-Rust fence for command output and configuration
snippets; otherwise the doctest runner may try to compile prose.

## Example
```rust
/// Reads a decimal count from text.
///
/// # Examples
///
/// ```
/// # fn main() -> Result<(), std::num::ParseIntError> {
/// let count = "42".parse::<u32>()?;
/// assert_eq!(count + 1, 43);
/// # Ok(())
/// # }
/// ```
pub fn parse_count(text: &str) -> Result<u32, std::num::ParseIntError> {
    text.parse()
}
```

## More realistic example
```rust
/// Parses a comma-separated pair.
///
/// # Examples
///
/// ```
/// # use docs_demo::split_pair;
/// let (left, right) = split_pair("name=value").expect("pair should split");
/// assert_eq!(left, "name");
/// assert_eq!(right, "value");
/// ```
///
/// Invalid input returns `None`:
///
/// ```
/// # use docs_demo::split_pair;
/// assert_eq!(split_pair("missing separator"), None);
/// ```
pub fn split_pair(input: &str) -> Option<(&str, &str)> {
    input.split_once('=')
}
```

## Common errors
A doctest that uses `?` without a hidden `Result` context fails even though the visible code looks
reasonable:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`
```

Fix with `# fn main() -> Result<..., ...> { ... # Ok(()) # }` or the hidden
`# Ok::<(), ErrorType>(())` form when no explicit `main` is needed.

## Best practice
- ✅ Show the smallest useful public API usage, then hide only mechanical scaffolding.
- ✅ Include assertions in examples when a stable result is part of the lesson.
- ✅ Prefer `no_run` over `ignore` for examples that should compile but should not execute in CI.
- ✅ Use `compile_fail` for intentional non-compiling examples, and describe what contract they demonstrate.
- ✅ Prefer public imports in hidden lines so the example exercises the same path users will copy.
- ✅ Use two leading hashes (`##`) when a visible line itself must begin with `#`, such as shell prompts or literal strings.

## Pitfalls
- ⚠️ Hiding too much can make an example appear magical; visible code should still teach the real usage.
- ⚠️ Using private items in examples fights rustdoc's public-API model.
- ⚠️ Marking examples `ignore` by default creates [[Untested Documentation Examples]].
- ⚠️ Leaving examples assertion-free can let them keep compiling after they stop demonstrating the documented result.

## See also
[[Documentation Tests]] · [[Documentation Comments]] · [[rustdoc]] · [[Untested Documentation Examples]] · [[Assertion Macros in Tests]] · [[Public API Documentation]] · [[Result Returning Tests]] · [[Test Harness and cargo test]] · [[Testing & Documentation]]

## Sources
- The rustdoc book, "Hiding portions of the example" — [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html#hiding-portions-of-the-example
- The rustdoc book, "Examples" — [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/write-documentation/what-to-include.html#examples
