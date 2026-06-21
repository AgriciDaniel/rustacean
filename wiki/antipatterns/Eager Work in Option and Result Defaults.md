---
type: antipattern
title: "Eager Work in Option and Result Defaults"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, result, lazy-evaluation, antipattern, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[Lazy Evaluation]]", "[[Option Combinators]]", "[[Result Combinators]]", "[[Defaulting with unwrap_or Variants]]", "[[Fallback Chains with or_else]]", "[[Converting Option to Result with ok_or]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or", "https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or", "https://doc.rust-lang.org/std/result/enum.Result.html#method.map_or", "https://doc.rust-lang.org/std/result/enum.Result.html#method.unwrap_or"]
rust_version: "edition 2024 / 1.85+"
---

# Eager Work in Option and Result Defaults

The footgun is passing expensive or side-effecting fallback expressions to eager combinators such as `unwrap_or`, `or`, `ok_or`, and `map_or`.

## The mistake
Some combinators take fallback values directly.
Those fallback arguments are evaluated before the method call.
That means work happens even when the `Option` is `Some` or the `Result` is `Ok`.
This surprises people because the fallback branch is not logically needed.
The usual symptoms are unnecessary allocations, unnecessary formatting, duplicate logging, unexpected metrics, and wasted I/O.
The eager methods are still correct for cheap constants.
The mistake is using them with work that should happen only on the fallback path.
For `Option`, common eager methods include `unwrap_or`, `or`, `ok_or`, and `map_or`.
For `Result`, common eager methods include `unwrap_or`, `or`, and `map_or`.
The lazy alternatives end in `_else`: `unwrap_or_else`, `or_else`, `ok_or_else`, and `map_or_else`.

## Why it happens
Rust evaluates function and method arguments before calling the function or method.
`value.unwrap_or(make_default())` must call `make_default()` to pass its returned `T`.
The method then decides whether to use that already-created value.
By contrast, `value.unwrap_or_else(|| make_default())` passes a closure.
The method calls the closure only if it needs the fallback.
The same evaluation rule applies to `ok_or(format!(...))`.
The `format!` allocation happens even when the option is `Some`.
The same rule applies to `or(fallback_lookup())`.
The fallback lookup runs even when the primary value exists.
This is a normal Rust evaluation rule, not a special behavior of `Option` or `Result`.
Knowing which combinators are eager keeps pipelines cheap and predictable.

## Example
```rust
fn build_default(log: &mut Vec<&'static str>) -> String {
    log.push("built default");
    "fallback".to_string()
}

fn main() {
    let value = Some("actual".to_string());
    let mut log = Vec::new();

    let eager = value.clone().unwrap_or(build_default(&mut log));
    assert_eq!(eager, "actual");
    assert_eq!(log, vec!["built default"]);

    log.clear();

    let lazy = value.unwrap_or_else(|| build_default(&mut log));
    assert_eq!(lazy, "actual");
    assert!(log.is_empty());
}
```

## Best practice
- ✅ Use eager forms for cheap literals, constants, and already-computed values.
- ✅ Use `_else` forms for allocation, formatting, cloning, logging, I/O, locking, or parsing.
- ✅ Use `ok_or_else` when constructing a missing-value error.
- ✅ Use `or_else` when trying another optional or fallible source.
- ✅ Use `map_or_else` when both success and fallback branches produce a plain value.
- ✅ Keep side effects out of fallback expressions unless they must run unconditionally.
- ✅ In review, scan for `format!`, function calls, `.clone()`, and I/O inside eager fallback arguments.
- ✅ Benchmark only after choosing the semantically correct lazy/eager form.

## Pitfalls
- ⚠️ `unwrap_or(Default::default())` may be fine, but `unwrap_or(expensive_default())` is usually wrong.
- ⚠️ `ok_or(format!(...))` allocates on the success path; use `ok_or_else`.
- ⚠️ `or(fallback())` runs the fallback source even when the primary source succeeds.
- ⚠️ `map_or(expensive_default(), f)` runs the default even when mapping succeeds.
- ⚠️ Switching everything to `_else` can add noise for trivial copyable constants.
- ⚠️ Lazy closures can still hide side effects; make fallback policy explicit when it matters.

## See also
[[std: Option & Result Combinators]] ·
[[Lazy Evaluation]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Defaulting with unwrap_or Variants]] ·
[[Fallback Chains with or_else]] ·
[[Converting Option to Result with ok_or]] ·
[[Mapping Present Values with map]] ·
[[Unwrap and Expect Overuse]] ·
[[Needless Clone]] ·
[[Swallowing Errors]]

## Sources
- Rust standard library, `Option::unwrap_or`, `Option::ok_or`, and lazy alternatives — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html
- Rust standard library, `Result::unwrap_or`, `Result::map_or`, and lazy alternatives — [[std]],
  https://doc.rust-lang.org/std/result/enum.Result.html
