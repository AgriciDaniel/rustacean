---
type: concept
title: "Option"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, option, enums, null-safety]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Enums]]", "[[The match Expression]]", "[[if let]]", "[[let else]]", "[[Option vs Result]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum-and-its-advantages-over-null-values", "https://doc.rust-lang.org/std/option/enum.Option.html"]
rust_version: "edition 2024 / 1.85+"
---

# Option

`Option<T>` represents either one present `T` value (`Some(T)`) or no value (`None`) without using null.

## What it is
`Option<T>` is a standard library enum with two variants: `Some(T)` and `None`.
It is in the prelude, so most code can write `Some(value)` and `None` without importing them.
Use it when absence is expected and recoverable: missing config, an empty search result, or the first item of an empty slice.

`Option<T>` and `T` are different types.
That distinction forces code to handle absence before using the inner value.
It is the type-level alternative to nullable references.

## How it works
Pattern matching is the most explicit way to handle an option.
`Some(value)` binds the inner value.
`None` handles the absent case.

The standard library also provides many combinators such as `map`, `and_then`, `unwrap_or`, `ok_or`, and `is_some_and`.
Use a `match` when both branches have substantial logic.
Use [[if let]] when only the present case matters.
Use [[let else]] to keep the successful path unindented when absence should return early.

Many `Option` methods take `self` by value. For `Option<String>`, `map` consumes the option and moves
the string into the closure; call `as_ref()` or `as_mut()` first when you want `Option<&T>` or
`Option<&mut T>` instead. On stable 1.85+, `is_some_and`, `is_none_or`, `take`, `take_if`, `as_slice`,
and `transpose` cover common cases without manual matches, but a clear `match` is still best when the
branches carry domain meaning.

`Option<T>` also participates in niche optimization for many `T` values. For example, an absent
reference can often be represented by the same machine value as a null pointer, while safe Rust still
prevents you from treating `None` as `&T`.

## Example
```rust
fn first_even(numbers: &[i32]) -> Option<i32> {
    numbers.iter().copied().find(|number| number % 2 == 0)
}

fn describe(number: Option<i32>) -> String {
    match number {
        Some(value) => format!("found {value}"),
        None => String::from("no even number"),
    }
}

fn main() {
    assert_eq!(first_even(&[1, 3, 6, 9]), Some(6));
    assert_eq!(describe(first_even(&[1, 3, 5])), "no even number");
}
```

## Worked example
```rust
fn normalized_host(raw: Option<String>) -> Option<String> {
    raw.as_ref()
        .map(|host| host.trim())
        .filter(|host| !host.is_empty())
        .map(str::to_ascii_lowercase)
}

fn take_cached(cache: &mut Option<String>) -> String {
    let Some(value) = cache.take() else {
        return String::from("cache miss");
    };

    format!("cache hit: {value}")
}

fn main() {
    let raw = Some(String::from(" EXAMPLE.COM "));
    assert_eq!(normalized_host(raw), Some(String::from("example.com")));

    let mut cache = Some(String::from("token"));
    assert_eq!(take_cached(&mut cache), "cache hit: token");
    assert_eq!(cache, None);
}
```

## Common errors
Using `Option<T>` as though it were `T` fails because absence has not been handled:

```text
error[E0277]: cannot add `Option<i8>` to `i8`
```

Fix it by matching, using `?` in an `Option`-returning function, or choosing a combinator such as
`map`, `unwrap_or`, `ok_or_else`, or `and_then`. If a combinator moves the option unexpectedly, use
`as_ref()` or `as_mut()` before calling it.

## Best practice
- ✅ Return `Option<T>` when "not found" or "not present" is a normal outcome.
- ✅ Convert to `Result<T, E>` with `ok_or` or `ok_or_else` when the caller needs an error reason; see [[Option vs Result]].
- ✅ Prefer pattern matching or option combinators over checking `is_some()` and then unwrapping.
- ✅ Use `as_ref()`/`as_mut()` to inspect or edit an optional payload without consuming the container.
- ✅ Use `take()` to move a value out of `&mut Option<T>` while leaving `None` behind.

## Pitfalls
- ⚠️ Do not treat `None` as an exceptional error if a caller needs diagnostics; use [[Result]] instead.
- ⚠️ Do not write `if value.is_some() { value.unwrap() }`; see [[Is Some Then Unwrap]].
- ⚠️ Do not use sentinel values such as an empty string or `0` to mean absence; see [[Sentinel Values]].
- ⚠️ Do not use `unwrap_or(expensive())` when the default is costly; use `unwrap_or_else`.
- ⚠️ Do not collapse several absence reasons into `None` if the caller must distinguish them.

## See also
[[Enums]] · [[The match Expression]] · [[if let]] · [[let else]] · [[Option vs Result]] · [[Result]] · [[The Question Mark Operator]] · [[Is Some Then Unwrap]] · [[Unwrap and Expect Overuse]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.1 "The Option Enum and Its Advantages Over Null Values" - [[the-book]], https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum-and-its-advantages-over-null-values
- Standard library `Option` documentation - https://doc.rust-lang.org/std/option/enum.Option.html
