---
type: concept
title: "Practice: Error Handling"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, errors]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Result]]", "[[The Question Mark Operator]]", "[[Recoverable vs Unrecoverable Errors]]", "[[Custom Error Types]]", "[[The Error Trait]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Error Handling

The error handling group teaches recoverable errors with `Result<T, E>` and when panics are inappropriate. The key idea is to return failures to the caller with enough type information or context to handle them.

## What it is
These exercises cover parsing errors, `Result`, `?`, `Box<dyn Error>`, custom error enums, and returning `Result` from `main`.

## How it works
`Result<T, E>` is `Ok(T)` on success or `Err(E)` on failure. The `?` operator returns early from the current function when it sees an error, converting the error type with `From` when applicable.

## Example
```rust
fn parse_positive(input: &str) -> Result<u32, String> {
    let n: u32 = input
        .parse()
        .map_err(|err| format!("not a number: {err}"))?;

    if n == 0 {
        Err(String::from("value must be positive"))
    } else {
        Ok(n)
    }
}

fn main() -> Result<(), String> {
    println!("{}", parse_positive("42")?);
    Ok(())
}
```

## Best practice
- ✅ Use `Result` for failures callers can reasonably handle.
- ✅ Add context when converting low-level errors into application errors.
- ✅ Let `?` express the straight-line success path.

## Pitfalls
- ⚠️ Do not `panic!` for ordinary invalid input.
- ⚠️ Do not throw away parse errors unless the caller truly does not need the cause.
- ⚠️ Remember that `?` requires a compatible return type.

## See also
[[Practice (Rustlings)]] · [[Result]] · [[The Question Mark Operator]] · [[Recoverable vs Unrecoverable Errors]] · [[Custom Error Types]] · [[The Error Trait]] · [[Propagating Errors]]

## Sources
- Rustlings `13_error_handling` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

