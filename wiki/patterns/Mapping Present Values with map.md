---
type: pattern
title: "Mapping Present Values with map"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, map, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Chaining with and_then]]", "[[Borrowing]]", "[[Move Semantics]]", "[[Iterator Adapters]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.map", "https://doc.rust-lang.org/std/result/enum.Result.html#method.map", "https://doc.rust-lang.org/std/result/enum.Result.html#method.map_err"]
rust_version: "edition 2024 / 1.85+"
---

# Mapping Present Values with map

Use `map` to transform only the present or successful value while leaving `None` or `Err` unchanged.

## What it is
`map` is the basic transformation combinator for both `Option` and `Result`.
For `Option<T>`, it turns `Some(T)` into `Some(U)` and leaves `None` as `None`.
For `Result<T, E>`, it turns `Ok(T)` into `Ok(U)` and leaves `Err(E)` unchanged.
The closure runs only on the contained success or presence value.
It is the right method when the operation cannot fail.
If the operation can fail, use `and_then`.
For `Result`, use `map_err` to transform the error side.
For observing without transforming, use `inspect` or `inspect_err`.
For converting to a plain value, use `map_or` or `map_or_else`.
For borrowed inspection, call `as_ref` before `map`.

## How it works
`Option::map` has the shape `Option<T> -> Option<U>`.
`Result::map` has the shape `Result<T, E> -> Result<U, E>`.
`Result::map_err` has the shape `Result<T, E> -> Result<T, F>`.
All of these methods consume `self`.
That means `Option<String>::map` moves the `String` into the closure.
If you only need a borrowed view, use `as_ref().map(...)` or `as_deref().map(...)`.
The closure implements `FnOnce`, so it may consume captured values.
Because `map` does not flatten nested enums, a closure returning `Option<U>` produces `Option<Option<U>>`.
That nested shape is usually a signal to use `and_then`.
The same principle applies to `Result<Result<U, E>, E>`.
Use `flatten` only when the nested shape already exists and one layer should be removed.

## Example
```rust
fn main() {
    let name = Some("Ferris".to_string());
    let length = name.as_ref().map(|text| text.len());

    assert_eq!(length, Some(6));
    assert_eq!(name.as_deref(), Some("Ferris"));

    let parsed = "21"
        .parse::<u32>()
        .map(|n| n * 2)
        .map_err(|err| format!("bad number: {err}"));

    assert_eq!(parsed, Ok(42));

    let bad = "x"
        .parse::<u32>()
        .map(|n| n * 2)
        .map_err(|err| format!("bad number: {err}"));

    assert!(bad.unwrap_err().starts_with("bad number"));
}
```

## Best practice
- ✅ Use `map` for pure, infallible transformations on present values.
- ✅ Use `map_err` to adapt a low-level error into the surrounding error vocabulary.
- ✅ Use `as_ref`, `as_mut`, or `as_deref` before `map` when you want to avoid moving the payload.
- ✅ Prefer method references such as `str::len` or `ToString::to_string` when they improve clarity.
- ✅ Keep `map` closures small and expression-oriented.
- ✅ Use `and_then` when the closure returns `Option` or `Result`.
- ✅ Use `inspect` for logging or metrics that should not change the value.
- ✅ Use `map_or_else` when you need to end with a plain value and lazy fallback.

## Pitfalls
- ⚠️ `map` consumes the enum; accidental moves are common with `String`, `Vec`, and custom types.
- ⚠️ Returning an `Option` from `Option::map` creates nesting; use [[Chaining with and_then]].
- ⚠️ Returning a `Result` from `Result::map` creates nesting; use `and_then` or `?`.
- ⚠️ `map_err` can erase source errors if it formats them into strings too early.
- ⚠️ Long `map` chains can be harder to read than a named helper function.
- ⚠️ Do not use `map` only for side effects; use `inspect` or an explicit `if let`.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Chaining with and_then]] ·
[[Transpose and Flatten]] ·
[[Borrowing]] ·
[[Move Semantics]] ·
[[Iterator Adapters]] ·
[[Lazy Evaluation]] ·
[[Needless Clone]] ·
[[Result Type Aliases]]

## Sources
- Rust standard library, `Option::map` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.map
- Rust standard library, `Result::map` and `Result::map_err` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html#method.map
