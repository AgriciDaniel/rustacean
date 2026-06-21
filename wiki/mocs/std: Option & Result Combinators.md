---
type: moc
title: "std: Option & Result Combinators"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, combinators, moc]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Option Combinators]]", "[[Result Combinators]]", "[[Converting Between Option and Result]]", "[[Transpose and Flatten]]", "[[Question Mark with Option]]", "[[Eager Work in Option and Result Defaults]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# std: Option & Result Combinators

This MOC collects the standard-library combinator vocabulary for transforming, chaining, defaulting, converting, and checking `Option` and `Result`.

## What it is
This domain is about the method-level control flow of Rust's two everyday sum types.
`Option` models presence and absence.
`Result` models success and diagnosed failure.
Combinators make those meanings composable without writing a `match` for every operation.
The notes here separate broad concepts from specific idioms and footguns.
The goal is to choose the method that matches the semantic transition in the code.
If a value is present and you want to transform it, reach for `map`.
If the next step can also fail or be absent, reach for `and_then`.
If a backup source should be tried lazily, reach for `or_else`.
If absence should become an error, reach for `ok_or_else`.
If a fallback plain value is correct, reach for the `unwrap_or` family.
If nested enum layers need rearranging, reach for `transpose` or `flatten`.

## Map
- [[Option Combinators]] is the overview of the `Option` method vocabulary.
- [[Result Combinators]] is the overview of the `Result` method vocabulary.
- [[Mapping Present Values with map]] covers success/presence transformations with `map` and `map_err`.
- [[Chaining with and_then]] covers fallible or optional dependent steps.
- [[Fallback Chains with or_else]] covers lazy secondary attempts.
- [[Defaulting with unwrap_or Variants]] covers converting to a plain value with a fallback.
- [[Converting Option to Result with ok_or]] covers adding an error to absence.
- [[Converting Between Option and Result]] covers `ok_or`, `ok`, `err`, and error-loss boundaries.
- [[Transpose and Flatten]] covers mixed and repeated enum nesting.
- [[Predicate Checks with is_some_and and matches]] covers boolean checks over enum contents.
- [[Question Mark with Option]] covers early `None` returns with `?`.
- [[Eager Work in Option and Result Defaults]] covers eager fallback evaluation.

## How it works
Most combinators encode one branch policy.
`map` says "if there is a good value, transform it."
`map_err` says "if there is an error, transform it."
`and_then` says "if there is a good value, run the next fallible or optional step."
`or_else` says "if the first attempt failed or was absent, lazily try another enum-producing step."
`unwrap_or_else` says "if the first attempt failed or was absent, lazily produce a plain fallback value."
`ok_or_else` says "if the optional value is absent, lazily construct an error."
`transpose` says "the optionality and fallibility are in the wrong order for the caller."
`flatten` says "one layer of nesting is accidental or structurally redundant."
`is_some_and` and `matches!` say "I need only a boolean answer."
The right method is usually the one whose sentence matches the domain behavior.
When no sentence is obvious, use `match` and make the branches explicit.

## Example
```rust
fn optional_port(raw: Option<&str>) -> Result<Option<u16>, String> {
    raw.map(|text| {
        text.parse::<u16>()
            .map_err(|err| format!("invalid port: {err}"))
            .and_then(|port| {
                if port >= 1024 {
                    Ok(port)
                } else {
                    Err(format!("reserved port: {port}"))
                }
            })
    })
    .transpose()
}

fn main() {
    assert_eq!(optional_port(Some("8080")), Ok(Some(8080)));
    assert_eq!(optional_port(None), Ok(None));
    assert_eq!(optional_port(Some("80")), Err("reserved port: 80".to_string()));
}
```

## Best practice
- ✅ Start from the type shape: `Option<T>`, `Result<T, E>`, `Option<Result<T, E>>`, or nested same-type enums.
- ✅ Use `Option` when absence is expected and needs no diagnostic.
- ✅ Use `Result` when failure should carry a reason.
- ✅ Prefer lazy fallback methods when fallback construction is nontrivial.
- ✅ Prefer `?` over long `Result` chains when errors simply propagate.
- ✅ Prefer `match` over clever chains when branches have different policies.
- ✅ Preserve errors until an API boundary intentionally chooses to discard them.
- ✅ Borrow with `as_ref` or `as_deref` before consuming combinators when ownership matters.

## Pitfalls
- ⚠️ Eager defaults can do work on the success path; see [[Eager Work in Option and Result Defaults]].
- ⚠️ `Result::ok` can hide useful error context; see [[Swallowing Errors]].
- ⚠️ `is_some` followed by `unwrap` is more fragile than direct extraction; see [[Is Some Then Unwrap]].
- ⚠️ `unwrap_or_default` can hide parse failures as zero or empty values.
- ⚠️ Nested `map` calls can produce nested enums; use [[Chaining with and_then]] or [[Transpose and Flatten]].
- ⚠️ Combinator chains that encode business policy can become harder to audit than `match`.

## See also
[[Option]] ·
[[Result]] ·
[[Option vs Result]] ·
[[The Question Mark Operator]] ·
[[Propagating Errors]] ·
[[Recoverable vs Unrecoverable Errors]] ·
[[Lazy Evaluation]] ·
[[Iterator Adapters]] ·
[[The match Expression]] ·
[[if let]] ·
[[let else]] ·
[[Unwrap and Expect Overuse]]

## Sources
- Rust standard library, `Option` enum and combinators — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html
- Rust standard library, `Result` enum and combinators — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html
