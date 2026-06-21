---
type: concept
title: "Result Combinators"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, result, errors, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Result]]", "[[Option Combinators]]", "[[Mapping Present Values with map]]", "[[Chaining with and_then]]", "[[Fallback Chains with or_else]]", "[[Propagating Errors]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/result/enum.Result.html", "https://doc.rust-lang.org/std/result/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Result Combinators

`Result` combinators are methods that transform success values, transform errors, chain fallible work, or recover from failures while preserving the `Ok`/`Err` contract.

## What it is
A `Result<T, E>` is either `Ok(T)` or `Err(E)`.
Combinators let you work with that branch structure without writing a `match` at every step.
They are especially common in parsing, I/O, validation, and API boundary code.
Success-side methods include `map`, `and_then`, `inspect`, `unwrap_or`, and `unwrap_or_else`.
Error-side methods include `map_err`, `or_else`, `inspect_err`, `err`, and the error closure of `map_or_else`.
Conversion methods include `ok`, `err`, and `transpose`; `Result::flatten` is available on newer stable Rust (1.89+), but `and_then(|inner| inner)` is the 1.85-compatible shape.
Predicate methods include `is_ok`, `is_err`, `is_ok_and`, and `is_err_and`.
Unlike `Option`, `Result` carries failure information, so combinators should preserve or improve that information by default.
When a pipeline throws away `E`, it should be a deliberate boundary decision.
The common reader expectation is that `Err` travels unchanged unless the method name says otherwise.

## How it works
`map` applies a closure to the `Ok` value and leaves `Err` untouched.
`map_err` applies a closure to the `Err` value and leaves `Ok` untouched.
`and_then` applies a closure returning another `Result`, which is how fallible steps are sequenced.
`or_else` applies a closure to the error and can return a recovered `Result`.
`unwrap_or_else` converts a `Result<T, E>` into `T` by mapping an error into a fallback value.
`map_or_else` also converts into a plain value, with one closure for `Err` and one for `Ok`.
`inspect` and `inspect_err` observe by reference and then return the original `Result`.
The `?` operator is usually clearer than a long `and_then` chain when every error should be propagated.
Combinators shine when one or two local transformations are attached to a fallible call.
For larger branch-specific behavior, `match` is often clearer and more debuggable.

## Example
```rust
fn parse_port(input: &str) -> Result<u16, String> {
    input
        .trim()
        .parse::<u16>()
        .map_err(|err| format!("invalid port: {err}"))
        .and_then(|port| {
            if port >= 1024 {
                Ok(port)
            } else {
                Err(format!("reserved port: {port}"))
            }
        })
}

fn main() {
    assert_eq!(parse_port("8080"), Ok(8080));
    assert_eq!(parse_port("80"), Err("reserved port: 80".to_string()));
    assert!(parse_port("abc").unwrap_err().starts_with("invalid port"));

    let display = parse_port("443").unwrap_or_else(|_| 8443);
    assert_eq!(display, 8443);
}
```

## Best practice
- ✅ Use `map` for pure success-value transformations.
- ✅ Use `map_err` to convert low-level error types into your function's error type.
- ✅ Use `and_then` when the next step is also fallible and uses the successful value.
- ✅ Use `?` for straight-line propagation when there is no local recovery.
- ✅ Use `or_else` for recovery that needs to inspect the error.
- ✅ Use `inspect_err` for logging or metrics that should not change the result.
- ✅ Preserve error context unless you are intentionally crossing into an optional or boolean API.
- ✅ Keep the error type stable across `and_then` chains, or convert with `map_err` at the boundary.

## Pitfalls
- ⚠️ `result.ok()` discards the error; see [[Converting Between Option and Result]] before using it in library code.
- ⚠️ `unwrap_or` eagerly evaluates its fallback value; see [[Eager Work in Option and Result Defaults]].
- ⚠️ `and_then` is not a replacement for `?` when the code is naturally sequential.
- ⚠️ `map_err(|_| "...")` can erase useful diagnostics; prefer adding context while keeping the cause where practical.
- ⚠️ `unwrap` and `expect` are not error handling in recoverable paths; see [[Unwrap and Expect Overuse]].
- ⚠️ Long combinator pipelines can make it hard to set breakpoints or inspect intermediate error values.

## See also
[[std: Option & Result Combinators]] ·
[[Result]] ·
[[Option]] ·
[[Recoverable vs Unrecoverable Errors]] ·
[[Propagating Errors]] ·
[[Custom Error Types]] ·
[[The Error Trait]] ·
[[Adding Error Context]] ·
[[Option Combinators]] ·
[[Mapping Present Values with map]] ·
[[Chaining with and_then]] ·
[[Fallback Chains with or_else]] ·
[[Transpose and Flatten]]

## Sources
- Rust standard library, `Result` enum and methods — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html
- Rust standard library, `std::result` module — [[std]],
  https://doc.rust-lang.org/std/result/index.html
