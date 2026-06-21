---
type: pattern
title: "let else"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, let-else, patterns, early-return]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Refutable and Irrefutable Patterns]]", "[[Option]]", "[[Result]]", "[[if let]]", "[[The match Expression]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-03-if-let.html#staying-on-the-happy-path-with-letelse", "https://doc.rust-lang.org/book/ch19-02-refutability.html"]
rust_version: "edition 2024 / 1.85+"
---

# let else

`let else` extracts values with a refutable pattern and sends the failure case out of the current flow immediately.

## What it is
`let PATTERN = expression else { ... };` is an early-exit pattern.
If the pattern matches, its bindings are available in the outer scope after the statement.
If the pattern fails, the `else` block must diverge, typically with `return`, `break`, `continue`, or `panic!`.

Use it to keep the happy path left-aligned.
It is especially clear when a function cannot continue without a `Some` or `Ok` value.

## How it works
Rust evaluates the expression and checks the pattern.
On success, bindings escape the `let else` statement and can be used by the following code.
On failure, the `else` block runs and must not fall through.

This differs from [[if let]], where bindings live only inside the `if` block.
It also differs from [[The match Expression]], which is better when both success and failure are equally meaningful branches.

The `else` block must diverge: it must leave the current flow with `return`, `break`, `continue`,
`panic!`, or another expression of the never type. That rule is what lets Rust make the successful
bindings available after the statement. If the `else` block could fall through, later code might use
bindings that were never initialized.

`let else` has the same ownership behavior as other patterns. It is excellent for extracting an owned
value you intend to consume. For read-only extraction from borrowed data, use `as_ref()`, `as_mut()`,
or match on a reference so the container remains usable.

## Example
```rust
fn first_char(input: Option<&str>) -> Option<char> {
    let Some(text) = input else {
        return None;
    };

    let Some(ch) = text.chars().next() else {
        return None;
    };

    Some(ch)
}

fn main() {
    assert_eq!(first_char(Some("rust")), Some('r'));
    assert_eq!(first_char(Some("")), None);
    assert_eq!(first_char(None), None);
}
```

## Worked example
```rust
fn parse_header(line: &str) -> Option<(&str, &str)> {
    let Some((name, value)) = line.split_once(':') else {
        return None;
    };

    let name = name.trim();
    let value = value.trim();

    let false = name.is_empty() || value.is_empty() else {
        return None;
    };

    Some((name, value))
}

fn main() {
    assert_eq!(parse_header("content-type: text/plain"), Some(("content-type", "text/plain")));
    assert_eq!(parse_header("missing separator"), None);
    assert_eq!(parse_header(": empty name"), None);
}
```

## Common errors
If the `else` block does not diverge, Rust rejects the statement:

```text
error[E0308]: `else` clause of `let...else` does not diverge
```

Fix it by returning, breaking, continuing, panicking, or changing the construct to `match` when both
branches should produce values.

## Best practice
- ✅ Use `let else` when the rest of the function is the success path.
- ✅ Keep the `else` block short and focused on exiting the current control flow.
- ✅ Prefer `?` when converting `Option` or `Result` failure directly is clearer; see [[The Question Mark Operator]].
- ✅ Use it for validating inputs step by step when each failed extraction has the same early-exit shape.
- ✅ Give the extracted binding a name that reads naturally in the following happy path.

## Pitfalls
- ⚠️ Do not use `let else` for patterns that always match; use normal `let`.
- ⚠️ Do not put large recovery logic in the `else` block; use `match` when both branches matter.
- ⚠️ Do not use `unwrap` when a short `let else` can make absence explicit; see [[Unwrap and Expect Overuse]].
- ⚠️ Do not force `let else` when `?` already communicates the exact propagation behavior.
- ⚠️ Watch ownership: `let Some(value) = option else { ... };` consumes `option`.

## See also
[[Refutable and Irrefutable Patterns]] · [[Option]] · [[Result]] · [[if let]] · [[The match Expression]] · [[The Question Mark Operator]] · [[Unwrap and Expect Overuse]] · [[Exhaustiveness]] · [[Destructuring]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.3 "Staying on the Happy Path with let...else" - [[the-book]], https://doc.rust-lang.org/book/ch06-03-if-let.html#staying-on-the-happy-path-with-letelse
- The Rust Programming Language, ch. 19.2 "Refutability" - [[the-book]], https://doc.rust-lang.org/book/ch19-02-refutability.html
