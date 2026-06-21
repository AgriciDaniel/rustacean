---
type: pattern
title: "if let"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, if-let, patterns, option]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Option]]", "[[Patterns]]", "[[Refutable and Irrefutable Patterns]]", "[[The match Expression]]", "[[let else]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-03-if-let.html", "https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html#conditional-if-let-expressions"]
rust_version: "edition 2024 / 1.85+"
---

# if let

`if let` is the idiom for running code when one refutable pattern matches while intentionally ignoring the nonmatching cases.

## What it is
`if let PATTERN = expression { ... }` combines an `if` branch with pattern matching.
It is equivalent to a small `match` with one meaningful arm and a do-nothing fallback.
It can also have an `else` branch for the nonmatching case.

Use it when only one case is interesting.
Common examples include `Some(value)`, `Ok(value)`, or one enum variant with a payload.

## How it works
Rust evaluates the expression and compares it with the pattern.
If the pattern matches, any bindings in the pattern are available inside the block.
If the pattern does not match, the block is skipped or the `else` block runs.

The tradeoff is that `if let` does not check [[Exhaustiveness]].
That is the point when you truly mean "ignore the rest."
When every case matters, use [[The match Expression]] instead.

`if let` is syntax for one pattern test, not a separate kind of destructuring. The pattern has the
same binding and ownership behavior it would have in a `match` arm. Matching an owned
`Option<String>` with `if let Some(text) = value` moves the string; matching `value.as_ref()` gives
you `Option<&String>` and keeps the original option usable.

An `else` block handles all nonmatching cases as one group. If those cases are not equivalent, switch
to `match` so the compiler and the reader can see every branch.

## Example
```rust
fn print_limit(limit: Option<u8>) -> String {
    let mut message = String::from("no limit");

    if let Some(value) = limit {
        message = format!("limit is {value}");
    }

    message
}

fn main() {
    assert_eq!(print_limit(Some(3)), "limit is 3");
    assert_eq!(print_limit(None), "no limit");
}
```

## Worked example
```rust
enum Event {
    Connected { peer: String },
    Disconnected,
    Data(Vec<u8>),
}

fn maybe_peer(event: &Event) -> Option<&str> {
    if let Event::Connected { peer } = event {
        return Some(peer.as_str());
    }

    None
}

fn main() {
    let event = Event::Connected {
        peer: String::from("cache-1"),
    };

    assert_eq!(maybe_peer(&event), Some("cache-1"));
    assert_eq!(maybe_peer(&Event::Disconnected), None);
}
```

## Common errors
Moving a payload in `if let` can make the original value unavailable:

```text
error[E0382]: borrow of partially moved value
```

Fix it by matching a reference (`if let Some(text) = value.as_ref()`) or by using `ref` in the pattern
when you are deliberately matching the owned value but borrowing one field.

## Best practice
- ✅ Use `if let` for a single interesting success case with small branch logic.
- ✅ Use `else` only when the fallback is simple and directly paired with the pattern.
- ✅ Switch to `match` when there are several meaningful alternatives.
- ✅ Use `as_ref()` or `as_mut()` before `if let` when you want to inspect or mutate without consuming.
- ✅ Prefer [[let else]] when the nonmatching case should immediately exit and the success binding is needed afterward.

## Pitfalls
- ⚠️ Do not use `if let` when forgetting a case would be a bug; use [[The match Expression]] for [[Exhaustiveness]].
- ⚠️ Watch for shadowing introduced by pattern bindings; see [[Pattern Variable Shadowing]].
- ⚠️ Do not check `is_some()` before `if let`; the pattern already performs the test.
- ⚠️ Do not grow an `if let`/`else if let` ladder until it encodes a hidden state machine; use `match`.
- ⚠️ Avoid `if let Some(_) = option` when `option.is_some()` is the clearer predicate and no binding is needed.

## See also
[[Option]] · [[Patterns]] · [[Refutable and Irrefutable Patterns]] · [[The match Expression]] · [[let else]] · [[Exhaustiveness]] · [[Pattern Variable Shadowing]] · [[Match Guards]] · [[Catch-All and Wildcard Patterns]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.3 "Concise Control Flow with if let and let...else" - [[the-book]], https://doc.rust-lang.org/book/ch06-03-if-let.html
- The Rust Programming Language, ch. 19.1 "Conditional if let Expressions" - [[the-book]], https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html#conditional-if-let-expressions
