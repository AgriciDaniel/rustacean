---
type: concept
title: "Option Combinators"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option]]", "[[Result Combinators]]", "[[Mapping Present Values with map]]", "[[Chaining with and_then]]", "[[Fallback Chains with or_else]]", "[[Defaulting with unwrap_or Variants]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html", "https://doc.rust-lang.org/std/option/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Option Combinators

`Option` combinators are methods that transform, inspect, filter, default, or chain optional values without manually matching every `Some` and `None`.

## What it is
An `Option<T>` is either `Some(T)` or `None`.
Combinators are the method vocabulary for working with that shape directly.
They keep the absence path explicit while making the success path compact.
The most common groups are transformation, chaining, fallback, conversion, and predicates.
Transformation methods include `map`, `map_or`, `map_or_else`, and `inspect`.
Chaining methods include `and_then` and `filter`.
Fallback methods include `or`, `or_else`, `unwrap_or`, `unwrap_or_else`, and `unwrap_or_default`.
Conversion methods include `ok_or`, `ok_or_else`, `transpose`, and `flatten`.
Predicate methods include `is_some`, `is_none`, `is_some_and`, and `is_none_or`.
The methods are useful because they preserve the meaning of `None`: there is no value to transform.
They are also useful because many methods consume `self`, so ownership remains visible in the type.

## How it works
`map` runs a closure only for `Some`, returning `Option<U>`.
`and_then` runs a closure that itself returns `Option<U>`, avoiding nested `Option<Option<U>>`.
`filter` keeps a `Some` only when a predicate on `&T` returns true.
`or_else` computes a backup `Option<T>` only when the original is `None`.
`unwrap_or_else` computes a plain backup `T` only when the original is `None`.
`ok_or_else` converts absence into a lazy error, producing a `Result<T, E>`.
`transpose` flips `Option<Result<T, E>>` into `Result<Option<T>, E>`.
`flatten` removes one layer from `Option<Option<T>>`.
Use `as_ref` or `as_mut` before consuming combinators when you need to keep the original `Option`.
For example, `opt.as_ref().map(|s| s.len())` reads a contained `String` without moving it.
That ownership detail is often the difference between an ergonomic pipeline and a move error.

## Example
```rust
fn parse_score(input: Option<&str>) -> u32 {
    input
        .and_then(|text| text.trim().parse::<u32>().ok())
        .filter(|score| *score <= 100)
        .map(|score| score * 10)
        .unwrap_or_default()
}

fn main() {
    assert_eq!(parse_score(Some("8")), 80);
    assert_eq!(parse_score(Some("101")), 0);
    assert_eq!(parse_score(Some("nope")), 0);
    assert_eq!(parse_score(None), 0);

    let fallback = None
        .or_else(|| Some("guest"))
        .map(str::to_uppercase);

    assert_eq!(fallback.as_deref(), Some("GUEST"));
}
```

## Best practice
- ✅ Use `map` when a present value changes shape but absence remains absence.
- ✅ Use `and_then` when the next operation can also return `None`.
- ✅ Use `filter` for optional validation that should discard invalid present values.
- ✅ Use `ok_or_else` when absence needs to become a structured error.
- ✅ Use `as_ref` before `map`, `is_some_and`, or `inspect` when you want to keep the original owned value.
- ✅ Prefer lazy forms (`or_else`, `unwrap_or_else`, `ok_or_else`, `map_or_else`) when fallback work allocates, logs, reads, or formats.
- ✅ Keep pipelines short enough that the absence path is still obvious to the next reader.
- ✅ Switch to `match` when branches need names, logging, mutation, or different multi-step behavior.

## Pitfalls
- ⚠️ `unwrap_or`, `or`, `ok_or`, and `map_or` evaluate their fallback arguments eagerly; see [[Eager Work in Option and Result Defaults]].
- ⚠️ `opt.map(f)` consumes `opt`; use `opt.as_ref().map(f)` when the original must remain usable.
- ⚠️ `Result::ok` discards error information; prefer `ok_or_else` in the opposite direction when absence needs context.
- ⚠️ `is_some()` followed by `unwrap()` repeats the enum test and risks future panics; see [[Is Some Then Unwrap]].
- ⚠️ Long chains can hide the moment where domain meaning changes from "missing" to "invalid".
- ⚠️ `None` is not an error message; if callers need a reason, return `Result`.

## See also
[[std: Option & Result Combinators]] ·
[[Option]] ·
[[Result]] ·
[[Option vs Result]] ·
[[Result Combinators]] ·
[[Converting Between Option and Result]] ·
[[Converting Option to Result with ok_or]] ·
[[Defaulting with unwrap_or Variants]] ·
[[Mapping Present Values with map]] ·
[[Chaining with and_then]] ·
[[Fallback Chains with or_else]] ·
[[Predicate Checks with is_some_and and matches]] ·
[[Question Mark with Option]]

## Sources
- Rust standard library, `Option` enum and methods — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html
- Rust standard library, `std::option` module — [[std]],
  https://doc.rust-lang.org/std/option/index.html
