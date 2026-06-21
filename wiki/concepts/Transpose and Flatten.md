---
type: concept
title: "Transpose and Flatten"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, transpose, flatten, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Converting Between Option and Result]]", "[[Chaining with and_then]]", "[[The Question Mark Operator]]", "[[Iterator Adapters]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.transpose", "https://doc.rust-lang.org/std/result/enum.Result.html#method.transpose", "https://doc.rust-lang.org/std/option/enum.Option.html#method.flatten", "https://doc.rust-lang.org/std/result/enum.Result.html#method.flatten"]
rust_version: "edition 2024 / 1.85+"
---

# Transpose and Flatten

Use `transpose` to flip mixed `Option`/`Result` nesting, and use `flatten` to remove one redundant `Option` layer; `Result::flatten` is current stable API but requires Rust 1.89+.

## What it is
`transpose` handles nested optional fallibility.
`Option<Result<T, E>>::transpose` produces `Result<Option<T>, E>`.
`Result<Option<T>, E>::transpose` produces `Option<Result<T, E>>`.
The first direction is the common one: optional input may be present, and if present it may fail to parse.
`flatten` handles nested sameness.
`Option<Option<T>>::flatten` produces `Option<T>`.
On Rust 1.89+, `Result<Result<T, E>, E>::flatten` produces `Result<T, E>`.
On the repository's 1.85 floor, use `nested.and_then(|inner| inner)` for the same one-level `Result` flattening.
Both methods remove boilerplate matches that only rearrange enum layers.
They also document intent better than manual branch reshuffling.
Use them when nesting is structural, not when each layer has separate domain meaning.

## How it works
For `Option<Result<T, E>>`, `None` becomes `Ok(None)`.
For `Option<Result<T, E>>`, `Some(Ok(t))` becomes `Ok(Some(t))`.
For `Option<Result<T, E>>`, `Some(Err(e))` becomes `Err(e)`.
That shape is ideal when an optional field should be skipped if absent but validated if present.
For `Option<Option<T>>`, `Some(Some(t))` becomes `Some(t)`.
For `Option<Option<T>>`, `Some(None)` and `None` both become `None`.
For `Result<Result<T, E>, E>`, the 1.85-compatible `and_then(|inner| inner)` maps `Ok(Ok(t))` to `Ok(t)`.
It maps `Ok(Err(e))` and `Err(e)` to `Err(e)`.
`flatten` removes only one level at a time.
Repeated nesting requires repeated `flatten` calls or a different design.

## Example
```rust
use std::num::ParseIntError;

fn parse_optional(raw: Option<&str>) -> Result<Option<u32>, ParseIntError> {
    raw.map(str::parse::<u32>).transpose()
}

fn main() {
    assert_eq!(parse_optional(Some("7")), Ok(Some(7)));
    assert_eq!(parse_optional(None), Ok(None));
    assert!(parse_optional(Some("bad")).is_err());

    let nested_option = Some(Some("value"));
    assert_eq!(nested_option.flatten(), Some("value"));

    let nested_result: Result<Result<u8, &str>, &str> = Ok(Ok(5));
    assert_eq!(nested_result.and_then(|inner| inner), Ok(5));
}
```

## Best practice
- ✅ Use `transpose` for optional fields that require fallible parsing or validation.
- ✅ Use `flatten` after `map` only when a nested enum is already the natural result.
- ✅ Use `Result::flatten` only when your MSRV is Rust 1.89 or newer; otherwise use `and_then(|inner| inner)`.
- ✅ Prefer `and_then` over `map(...).flatten()` for direct chains.
- ✅ Keep distinct meanings separate; do not flatten if outer and inner absence mean different things.
- ✅ Use type annotations around `transpose` examples when inference becomes hard for readers.
- ✅ Remember that `flatten` removes one layer, not all layers.
- ✅ Use `collect::<Result<Vec<_>, _>>()` for iterators of results; use `transpose` for a single mixed enum.
- ✅ Add tests for absent, present-success, and present-failure cases.

## Pitfalls
- ⚠️ `Some(None).flatten()` and `None.flatten()` both become `None`, which may lose distinction.
- ⚠️ `Result::flatten` requires Rust 1.89+ and compatible error types in the nested results.
- ⚠️ `transpose` can be directionally confusing; write the target type when clarity matters.
- ⚠️ Using `flatten` to hide accidental nesting may mask a wrong `map` where `and_then` was intended.
- ⚠️ Nightly-only reference flattening APIs are not part of the stable 1.85+ target.
- ⚠️ If each nesting layer has domain meaning, model it with a named enum instead.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Converting Between Option and Result]] ·
[[Mapping Present Values with map]] ·
[[Chaining with and_then]] ·
[[The Question Mark Operator]] ·
[[Iterator Adapters]] ·
[[Option vs Result]] ·
[[Type Aliases]] ·
[[Custom Error Types]]

## Sources
- Rust standard library, `Option::transpose` and `Option::flatten` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html
- Rust standard library, `Result::transpose` and `Result::flatten` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html
