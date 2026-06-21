---
type: antipattern
title: "Sentinel Values"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, option, result, invariants, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: basic
related: ["[[Option vs Result]]", "[[Result]]", "[[Enums]]", "[[Stringly-Typed Code]]", "[[Custom Error Types]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-00-enums.html", "https://doc.rust-lang.org/std/option/enum.Option.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Sentinel Values

Sentinel values encode absence or failure as ordinary data like `-1`, `""`, or `"unknown"`; Rust code should usually use `Option`, `Result`, or an enum instead.

## The mistake
A sentinel is a special value that means something outside the normal domain. It is common in C APIs and text protocols, but it is a poor internal representation when Rust's type system can represent the distinction directly.

The footgun is that callers can forget to check the sentinel, or a once-impossible sentinel can become valid after the domain changes.

## Why it happens
Primitive return values are quick to write. `usize::MAX` for "not found" or an empty string for "missing name" avoids defining a type, but it also hides absence from the function signature.

`Option<T>` means there may be no value. `Result<T, E>` means the operation can fail with a reason. Enums model multiple named states without overloading one primitive.

Rust's enums are designed for this. `Option<T>` and `Result<T, E>` are ordinary enums with pattern matching, combinators, and niche optimizations that often make `Option<&T>` or `Option<NonZeroUsize>` the same size as the raw value. You usually get clearer APIs without paying an extra runtime tax.

Sentinels are still common at FFI and wire-format boundaries. The important move is to convert them once at the boundary and keep typed representations inside the Rust core.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
enum LookupError {
    EmptyInput,
}

fn first_word(input: &str) -> Result<Option<&str>, LookupError> {
    if input.is_empty() {
        return Err(LookupError::EmptyInput);
    }

    Ok(input.split_whitespace().next())
}

fn main() {
    println!("{:?}", first_word("rust brain"));
    println!("{:?}", first_word("   "));
    println!("{:?}", first_word(""));
}
```

## Second example: convert legacy sentinels at the boundary
```rust
#[derive(Debug, PartialEq, Eq)]
enum LegacyError {
    NegativeCode,
}

fn decode_index(raw: i32) -> Result<Option<usize>, LegacyError> {
    match raw {
        -1 => Ok(None),
        n if n >= 0 => Ok(Some(n as usize)),
        _ => Err(LegacyError::NegativeCode),
    }
}

fn main() {
    println!("{:?}", decode_index(3));
    println!("{:?}", decode_index(-1));
    println!("{:?}", decode_index(-9));
}
```

The rest of the program should receive `Option<usize>`, not `-1`. That way any missing handling becomes a pattern-match or type problem instead of an unchecked magic number.

## Common errors
Unsigned sentinel bug:

```text
symptom: `usize::MAX` escapes into indexing or length arithmetic
```

Fix it by returning `Option<usize>` from search functions. If the value came from a C API, translate the sentinel immediately and keep the raw value out of ordinary logic.

Loss of failure reason:

```text
symptom: callers cannot tell "not found" from "input was invalid"
```

Fix it with `Result<Option<T>, E>` when absence is successful but malformed input is not, or with a custom enum when there are several domain states.

## Best practice
- ✅ Use `Option<T>` for expected absence.
- ✅ Use `Result<T, E>` when callers need an error reason.
- ✅ Use enums for domain states instead of magic numbers or strings.
- ✅ Convert sentinel-heavy external APIs at the boundary into typed Rust results.
- ✅ Use `NonZero*` integer types when zero is invalid and an `Option` around the value is useful.
- ✅ Name states in the type system when a value can be pending, absent, failed, or complete.

## Pitfalls
- ⚠️ `0`, `-1`, and empty strings often become valid values later.
- ⚠️ Sentinel values compose poorly; nested absence and failure become ambiguous.
- ⚠️ String sentinels are a form of [[Stringly-Typed Code]].
- ⚠️ Calling `.unwrap()` after converting a sentinel to `Option` reintroduces the panic path.
- ⚠️ `Result<T, ()>` can become a new sentinel if the caller needs to distinguish failures.
- ⚠️ Combining several sentinels in one field creates states the code never intended to handle.

## See also
[[Option vs Result]] · [[Result]] · [[Enums]] · [[Stringly-Typed Code]] · [[Custom Error Types]] · [[Recoverable vs Unrecoverable Errors]] · [[Unwrap and Expect Overuse]] · [[Index Panics vs get]] · [[Integer Overflow Assumptions]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 6 "Enums and Pattern Matching" — [[the-book]], https://doc.rust-lang.org/book/ch06-00-enums.html
- Standard library, `Option` — [[the-reference]], https://doc.rust-lang.org/std/option/enum.Option.html
- Standard library, `Result` — [[the-reference]], https://doc.rust-lang.org/std/result/enum.Result.html
