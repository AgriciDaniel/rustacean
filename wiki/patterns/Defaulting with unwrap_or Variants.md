---
type: pattern
title: "Defaulting with unwrap_or Variants"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, defaults, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Lazy Evaluation]]", "[[Eager Work in Option and Result Defaults]]", "[[Unwrap and Expect Overuse]]", "[[Default Implementations]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or", "https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or_else", "https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or_default", "https://doc.rust-lang.org/std/result/enum.Result.html#method.unwrap_or", "https://doc.rust-lang.org/std/result/enum.Result.html#method.unwrap_or_else", "https://doc.rust-lang.org/std/result/enum.Result.html#method.unwrap_or_default"]
rust_version: "edition 2024 / 1.85+"
---

# Defaulting with unwrap_or Variants

Use `unwrap_or`, `unwrap_or_else`, and `unwrap_or_default` to turn an `Option<T>` or `Result<T, E>` into a plain `T` when fallback is correct, not when errors should be handled.

## What it is
The `unwrap_or` family is a controlled extraction pattern.
It does not panic like `unwrap`.
It returns the contained value on the success or presence path.
It returns a fallback value on the absence or error path.
For `Option`, the fallback is used for `None`.
For `Result`, the fallback is used for `Err`.
`unwrap_or(default)` takes a fallback value directly.
`unwrap_or_else(closure)` computes the fallback lazily.
`unwrap_or_default()` uses `T::default()` as the fallback.
This pattern is appropriate when a fallback is semantically valid and losing the missing/error branch is acceptable.
It is not appropriate when the caller needs to know that a value was missing or invalid.

## How it works
`Option<T>::unwrap_or(default)` returns `T`.
`Result<T, E>::unwrap_or(default)` also returns `T`.
The direct default argument is evaluated before the method call.
`unwrap_or_else` calls its closure only for `None` or `Err`.
For `Option`, the closure receives no argument.
For `Result`, the closure receives the error value `E`, so it can recover based on the failure.
`unwrap_or_default` requires `T: Default`.
For numbers, the default is usually zero.
For `String`, `Vec`, and many collections, the default is empty.
Those defaults are convenient but not always domain-correct.
The method consumes the `Option` or `Result`; borrow first if you need to keep it.

## Example
```rust
fn display_name(primary: Option<String>, username: &str) -> String {
    primary.unwrap_or_else(|| username.to_string())
}

fn parsed_limit(input: &str) -> usize {
    input.parse::<usize>().unwrap_or_else(|_| 100)
}

fn main() {
    assert_eq!(
        display_name(Some("Ada".to_string()), "ada_l"),
        "Ada".to_string()
    );
    assert_eq!(display_name(None, "ada_l"), "ada_l".to_string());

    assert_eq!(parsed_limit("25"), 25);
    assert_eq!(parsed_limit("many"), 100);

    let missing_count: Option<u32> = None;
    assert_eq!(missing_count.unwrap_or_default(), 0);
}
```

## Best practice
- ✅ Use `unwrap_or` for cheap literal defaults such as `0`, `false`, or a static string reference.
- ✅ Use `unwrap_or_else` when the fallback allocates, formats, logs, reads state, or depends on the error.
- ✅ Use `unwrap_or_default` only when `Default::default()` is a valid domain value.
- ✅ Prefer `Result` propagation when fallback would hide an actionable failure.
- ✅ For `Result`, use the error argument in `unwrap_or_else` when recovery depends on the cause.
- ✅ Keep fallback choices visible near the call site.
- ✅ Consider naming fallback-producing functions when the fallback has business meaning.
- ✅ Add tests for both the present/success path and the fallback path.

## Pitfalls
- ⚠️ `unwrap_or(expensive())` runs `expensive()` even when the value is present; see [[Eager Work in Option and Result Defaults]].
- ⚠️ `unwrap_or_default()` can turn parse failures into zero, which may be a valid but wrong value.
- ⚠️ Defaulting a `Result` discards the error unless `unwrap_or_else` records or incorporates it.
- ⚠️ Replacing `unwrap` with `unwrap_or_default` can hide a bug instead of fixing it.
- ⚠️ A fallback can be less clear than returning `Option` or `Result` to the caller.
- ⚠️ `unwrap_or_else` is lazy, but the closure must still be side-effect safe when the fallback branch is taken.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Lazy Evaluation]] ·
[[Default Implementations]] ·
[[Unwrap and Expect Overuse]] ·
[[Eager Work in Option and Result Defaults]] ·
[[Propagating Errors]] ·
[[Option vs Result]] ·
[[Converting Option to Result with ok_or]] ·
[[The Question Mark Operator]]

## Sources
- Rust standard library, `Option::unwrap_or`, `Option::unwrap_or_else`, `Option::unwrap_or_default` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html
- Rust standard library, `Result::unwrap_or`, `Result::unwrap_or_else`, `Result::unwrap_or_default` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html
