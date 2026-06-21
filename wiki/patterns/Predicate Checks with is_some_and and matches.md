---
type: pattern
title: "Predicate Checks with is_some_and and matches"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, predicates, matches, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[The match Expression]]", "[[Match Guards]]", "[[Patterns]]", "[[Is Some Then Unwrap]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.is_some_and", "https://doc.rust-lang.org/std/option/enum.Option.html#method.is_none_or", "https://doc.rust-lang.org/std/result/enum.Result.html#method.is_ok_and", "https://doc.rust-lang.org/std/macro.matches.html"]
rust_version: "edition 2024 / 1.85+"
---

# Predicate Checks with is_some_and and matches

Use `is_some_and`, `is_ok_and`, and `matches!` for boolean checks that inspect enum contents without extracting them for later use.

## What it is
Predicate checks answer yes-or-no questions about enum shape and payload.
`Option::is_some_and` returns true only for `Some(value)` where the predicate is true.
`Option::is_none_or` returns true for `None` or for `Some(value)` where the predicate is true.
`Result::is_ok_and` returns true only for `Ok(value)` where the predicate is true.
`Result::is_err_and` returns true only for `Err(error)` where the predicate is true.
The `matches!` macro checks arbitrary patterns and optional guards.
These tools are for tests, guards, filters, assertions, and compact conditionals.
They are not extraction tools.
If the next line needs the contained value, use `if let`, `let else`, `match`, or combinators that keep the value.
That distinction avoids the `is_some` then `unwrap` antipattern.

## How it works
The `*_and` methods consume `self`.
Use `as_ref()` first when checking an owned payload that must remain available.
For example, `opt.as_ref().is_some_and(|s| s.len() > 3)` keeps `opt`.
The predicate receives the contained value by value for owned enums or by reference after `as_ref`.
`matches!(expr, pattern)` evaluates to a boolean.
`matches!(expr, Some(x) if x > 3)` supports a match guard.
`matches!` is often clearer for structural checks involving enum variants, ranges, or nested patterns.
`is_some_and` is often clearer for method-call predicates on a contained value.
Both styles should remain simple enough to read as a condition.
Use a full `match` when the logic grows beyond a predicate.

## Example
```rust
#[derive(Debug)]
enum State {
    Ready { code: u16 },
    Waiting,
}

fn main() {
    let name = Some("Ferris".to_string());
    let long = name.as_ref().is_some_and(|text| text.len() > 4);

    assert!(long);
    assert_eq!(name.as_deref(), Some("Ferris"));

    let parsed: Result<u16, _> = "204".parse();
    assert!(parsed.as_ref().is_ok_and(|code| (200..300).contains(code)));

    let state = Some(State::Ready { code: 204 });
    assert!(matches!(state, Some(State::Ready { code: 200..=299 })));

    let waiting = State::Waiting;
    assert!(matches!(waiting, State::Waiting));
}
```

## Best practice
- ✅ Use `is_some_and` for a compact predicate over a present optional value.
- ✅ Use `is_none_or` when missing means "passes" and present values must satisfy a predicate.
- ✅ Use `is_ok_and` and `is_err_and` for test assertions or simple guards on `Result`.
- ✅ Use `matches!` for structural patterns, ranges, nested enum checks, and guards.
- ✅ Use `as_ref` before predicate methods when the enum owns data you still need.
- ✅ Use `if let` or `match` when you need to bind and reuse the contained value.
- ✅ Prefer positive predicates that read directly.
- ✅ Keep side effects out of predicate closures.

## Pitfalls
- ⚠️ `is_some_and` consumes the option unless you borrow first.
- ⚠️ `is_some()` followed by `unwrap()` is a code smell; see [[Is Some Then Unwrap]].
- ⚠️ A complex `matches!` guard can become less clear than `match`.
- ⚠️ Predicate checks discard the value after answering the boolean question.
- ⚠️ `is_none_or` can hide validation by treating absence as acceptable; document that policy.
- ⚠️ Do not use predicate methods when callers need detailed failure reasons.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[The match Expression]] ·
[[Match Guards]] ·
[[Patterns]] ·
[[if let]] ·
[[let else]] ·
[[Is Some Then Unwrap]] ·
[[Option vs Result]] ·
[[Borrowing]]

## Sources
- Rust standard library, `Option::is_some_and` and `Option::is_none_or` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.is_some_and
- Rust standard library, `Result::is_ok_and` and `Result::is_err_and` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html#method.is_ok_and
- Rust standard library, `matches!` macro — [[std]],
  https://doc.rust-lang.org/std/macro.matches.html
