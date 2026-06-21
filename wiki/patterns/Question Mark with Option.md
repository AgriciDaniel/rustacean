---
type: pattern
title: "Question Mark with Option"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, option, question-mark, combinators]
domain: "std: Option & Result Combinators"
difficulty: intermediate
related: ["[[The Question Mark Operator]]", "[[Option Combinators]]", "[[Converting Between Option and Result]]", "[[Converting Option to Result with ok_or]]", "[[Result Combinators]]", "[[Propagating Errors]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/option/enum.Option.html", "https://doc.rust-lang.org/std/ops/trait.Try.html", "https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Question Mark with Option

Use `?` in an `Option`-returning function to return `None` early when a required optional step is missing.

## What it is
The `?` operator works with `Option` as well as `Result`.
Inside a function returning `Option<T>`, applying `?` to `Option<U>` unwraps `Some(U)` or returns `None`.
This is the optional-data version of early return.
It is ideal for lookup chains where every missing intermediate value means the whole answer is absent.
It often reads better than multiple nested `and_then` calls.
It also works well with `Result::ok()?` when a fallible operation should become optional.
However, `?` does not convert `None` into a `Result::Err` by itself.
In a `Result`-returning function, convert with `ok_or_else(...)?`.
The return type chooses the meaning of early exit.
Use that choice deliberately.

## How it works
When `value?` sees `Some(inner)`, evaluation continues with `inner`.
When it sees `None`, the enclosing `Option` function immediately returns `None`.
The operator relies on `Option`'s stable `Try` behavior.
It keeps code linear when each step depends on the previous one.
For `Result` inside an `Option` function, call `.ok()?` to discard the error intentionally.
For `Option` inside a `Result` function, call `.ok_or_else(...)?` to create an error.
That conversion boundary should be visible because it either loses or adds error information.
Use `?` when the early-return policy is uniform.
Use `match` when different missing steps need different behavior.
Use `and_then` when a compact expression pipeline is clearer than statements.

## Example
```rust
fn second_word(input: &str) -> Option<&str> {
    let mut words = input.split_whitespace();
    words.next()?;
    Some(words.next()?)
}

fn checked_label(input: &str) -> Option<String> {
    let n = input.parse::<u32>().ok()?;
    let doubled = n.checked_mul(2)?;
    Some(format!("value-{doubled}"))
}

fn main() {
    assert_eq!(second_word("hello rust"), Some("rust"));
    assert_eq!(second_word("hello"), None);

    assert_eq!(checked_label("21"), Some("value-42".to_string()));
    assert_eq!(checked_label("not a number"), None);
}
```

## Best practice
- ✅ Use `?` with `Option` when every missing step should make the whole function return `None`.
- ✅ Use `.ok()?` only when discarding a `Result` error is intentional.
- ✅ Use `.ok_or_else(...)?` when optional absence must become a `Result` error.
- ✅ Prefer statement form with `?` when a chain of `and_then` calls becomes hard to read.
- ✅ Keep the function return type honest: `Option` for absence, `Result` for diagnosed failure.
- ✅ Add names to intermediate values when they clarify the lookup or parse sequence.
- ✅ Use `let else` when the missing branch needs logging or a custom fallback.
- ✅ Test the earliest missing step and the latest missing step.

## Pitfalls
- ⚠️ `?` on `Option` cannot explain which step was missing.
- ⚠️ `.ok()?` throws away error details; see [[Swallowing Errors]].
- ⚠️ `?` on `Option` is not allowed directly in a `Result`-returning function without conversion.
- ⚠️ A function returning `Option` may be too weak for API boundaries that need diagnostics.
- ⚠️ Replacing all `and_then` chains with statements can make simple expressions verbose.
- ⚠️ Replacing all statements with chains can make debugging missing values harder.

## See also
[[std: Option & Result Combinators]] ·
[[The Question Mark Operator]] ·
[[Option Combinators]] ·
[[Result Combinators]] ·
[[Converting Between Option and Result]] ·
[[Converting Option to Result with ok_or]] ·
[[Chaining with and_then]] ·
[[Option vs Result]] ·
[[Propagating Errors]] ·
[[let else]] ·
[[Swallowing Errors]]

## Sources
- Rust standard library, `Option` and its `Try` implementation — [[std]],
  https://doc.rust-lang.org/std/option/enum.Option.html
- Rust standard library, `Try` trait documentation — [[std]],
  https://doc.rust-lang.org/std/ops/trait.Try.html
- The Rust Programming Language, recoverable errors and `?` — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html
