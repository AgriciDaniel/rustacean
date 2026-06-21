---
type: pattern
title: "Fallback Chains with or_else"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, fallback, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Defaulting with unwrap_or Variants]]", "[[Lazy Evaluation]]", "[[Eager Work in Option and Result Defaults]]", "[[Swallowing Errors]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.or_else", "https://doc.rust-lang.org/std/result/enum.Result.html#method.or_else"]
rust_version: "edition 2024 / 1.85+"
---

# Fallback Chains with or_else

Use `or_else` when an absent `Option` or failed `Result` should trigger another attempt that returns the same kind of enum.

## What it is
`or_else` is the lazy fallback combinator.
For `Option<T>`, it runs a closure only when the value is `None`.
For `Result<T, E>`, it runs a closure only when the value is `Err(E)`.
The closure returns another `Option<T>` or `Result<T, F>`.
That makes `or_else` a retry, recovery, or fallback-source pattern.
It differs from `unwrap_or_else`, which returns a plain `T`.
It differs from `or`, which receives an eagerly evaluated fallback enum.
Use `or_else` when the fallback might be expensive or should not happen on the happy path.
Use it for secondary config sources, cache misses, environment fallbacks, or error-specific recovery.
For `Result`, the error value is passed into the closure, so recovery can inspect it.

## How it works
`Some(value).or_else(f)` returns `Some(value)` and does not call `f`.
`None.or_else(f)` calls `f()` and returns its `Option<T>`.
`Ok(value).or_else(f)` returns `Ok(value)` and does not call `f`.
`Err(error).or_else(f)` calls `f(error)` and returns its `Result`.
`Option::or_else` preserves the same value type `T`.
`Result::or_else` preserves the success type `T` but may change the error type.
Because the fallback is a closure, it can read late-bound state.
Because it returns an enum, it can still fail or still be absent.
This is usually clearer than manually matching only to call another lookup.
However, an explicit `match` is clearer when recovery has several branches.

## Example
```rust
fn from_env() -> Option<String> {
    std::env::var("APP_NAME").ok()
}

fn from_file() -> Option<String> {
    Some("file-name".to_string())
}

fn parse_primary(input: &str) -> Result<u32, String> {
    input.parse::<u32>().map_err(|err| err.to_string())
}

fn main() {
    let name = from_env().or_else(from_file);
    assert_eq!(name.as_deref(), Some("file-name"));

    let port = parse_primary("not-a-port")
        .or_else(|_| parse_primary("8080"))
        .unwrap_or(3000);

    assert_eq!(port, 8080);
}
```

## Best practice
- ✅ Use `or_else` for fallbacks that should be lazy and may themselves fail.
- ✅ Use `or` only when the fallback enum is already cheap and available.
- ✅ Use `unwrap_or_else` when you want to end the chain with a plain value.
- ✅ For `Result`, inspect the error in the closure when recovery depends on the failure.
- ✅ Keep fallback order obvious: most preferred source first, least preferred last.
- ✅ Name fallback functions when they represent real configuration or recovery sources.
- ✅ Log or preserve important errors before trying a lossy fallback.
- ✅ Test both the primary-success path and the fallback path.

## Pitfalls
- ⚠️ `or(fallback())` calls `fallback()` even when the first value is present; see [[Eager Work in Option and Result Defaults]].
- ⚠️ A fallback chain can hide a real operational failure; see [[Swallowing Errors]].
- ⚠️ Repeated `or_else` calls can make precedence rules hard to audit.
- ⚠️ For `Result`, changing error types in recovery can surprise callers if not documented.
- ⚠️ If fallback is unconditional and cheap, `or_else` may be noisier than `or`.
- ⚠️ If recovery needs multiple decisions, use `match` instead of packing policy into closures.

## See also
[[std: Option & Result Combinators]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Defaulting with unwrap_or Variants]] ·
[[Lazy Evaluation]] ·
[[Eager Work in Option and Result Defaults]] ·
[[Swallowing Errors]] ·
[[Propagating Errors]] ·
[[Adding Error Context]] ·
[[Option vs Result]] ·
[[The match Expression]]

## Sources
- Rust standard library, `Option::or_else` — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html#method.or_else
- Rust standard library, `Result::or_else` — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html#method.or_else
