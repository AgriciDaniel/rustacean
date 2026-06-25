---
type: pattern
title: "Chaining with and_then"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, and_then, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Mapping Present Values with map]]", "[[The Question Mark Operator]]", "[[Transpose and Flatten]]", "[[Propagating Errors]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then", "https://doc.rust-lang.org/std/result/enum.Result.html#method.and_then"]
rust_version: "edition 2024 / 1.85+"
---

# Chaining with and_then

Use `and_then` when the next step depends on the contained value and may itself return `Option` or `Result`.

## What it is
`and_then` is the flattening chain combinator.
For `Option`, it turns `Option<T>` plus `T -> Option<U>` into `Option<U>`.
For `Result`, it turns `Result<T, E>` plus `T -> Result<U, E>` into `Result<U, E>`.
It is the method form of "continue only if the previous step succeeded or had a value."
It avoids nested `Option<Option<T>>` and `Result<Result<T, E>, E>`.
It is often called `flat_map` in other ecosystems.
In Rust, `and_then` is especially common with indexed lookups, checked arithmetic, parsing, and validation.
For straight-line `Result` propagation, `?` is often clearer.
For a short local chain, `and_then` keeps the dependency between steps close.
The closure runs only when the enum is `Some` or `Ok`.

## How it works
`Option::and_then` skips the closure for `None`.
`Result::and_then` skips the closure for `Err`.
The closure receives the contained success value by value.
The closure must return the same enum family.
For `Result::and_then`, the returned error type must match the original `E`.
If the next function returns a different error type, convert with `map_err` or use `?` with `From`.
`and_then` consumes the original enum, so borrow first if necessary.
Use `map` instead when the closure returns a plain value.
Use `flatten` when you already have a nested enum value.
Use `transpose` when the nesting mixes `Option` and `Result`.

## Example
```rust
fn grid_cell<'a>(grid: &[Vec<&'a str>], row: usize, col: usize) -> Option<&'a str> {
    grid.get(row)
        .and_then(|line| line.get(col))
        .copied()
}

fn checked_square(input: &str) -> Result<u32, String> {
    input
        .parse::<u32>()
        .map_err(|err| err.to_string())
        .and_then(|n| n.checked_mul(n).ok_or_else(|| "overflow".to_string()))
}

fn main() {
    let grid = vec![vec!["a0", "a1"], vec!["b0", "b1"]];
    assert_eq!(grid_cell(&grid, 1, 0), Some("b0"));
    assert_eq!(grid_cell(&grid, 3, 0), None);

    assert_eq!(checked_square("12"), Ok(144));
    assert_eq!(checked_square("1000000"), Err("overflow".to_string()));
}
```

## Best practice
- ✅ Use `and_then` when the closure returns `Option` or `Result`.
- ✅ Use `map` when the closure returns a plain value.
- ✅ Use `ok_or_else` inside a `Result` chain to turn an optional sub-step into an error.
- ✅ Use `?` when a sequence of `Result` operations reads better as statements.
- ✅ Keep `and_then` closures small; extract a named function for multi-step work.
- ✅ Convert error types before `and_then` if the chain needs one stable error type.
- ✅ Use `copied` or `cloned` intentionally after lookup chains that produce references.
- ✅ Consider `let else` or `match` when the missing/error branch needs custom behavior.

## Pitfalls
- ⚠️ Using `map` with a closure that returns `Option` or `Result` creates a nested enum.
- ⚠️ `Result::and_then` requires compatible error types; mismatches often mean the boundary is in the wrong place.
- ⚠️ A long `and_then` chain can obscure which step returned `None` or `Err`.
- ⚠️ Converting every `None` to the same generic error can erase useful context.
- ⚠️ `and_then` consumes the success value, so use references when you need to keep ownership.
- ⚠️ Do not use `and_then` for side effects only; use `inspect`, `if let`, or explicit control flow.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Mapping Present Values with map]] ·
[[Converting Option to Result with ok_or]] ·
[[The Question Mark Operator]] ·
[[Question Mark with Option]] ·
[[Transpose and Flatten]] ·
[[Propagating Errors]] ·
[[let else]] ·
[[if let]]

## Sources
- Rust standard library, `Option::and_then` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then
- Rust standard library, `Result::and_then` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html#method.and_then
