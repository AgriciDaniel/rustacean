---
type: concept
title: "Recoverable vs Unrecoverable Errors"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, result, panic]
domain: "Error Handling"
difficulty: basic
related: ["[[Result]]", "[[panic!]]", "[[Propagating Errors]]", "[[Panicking in Libraries]]", "[[The Question Mark Operator]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-00-error-handling.html", "https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html", "https://doc.rust-lang.org/std/result/"]
rust_version: "edition 2024 / 1.85+"
---

# Recoverable vs Unrecoverable Errors

Rust models expected failures with `Result<T, E>` and broken-program states with `panic!`; choosing between them is part of your API contract.

## What it is
Recoverable errors are ordinary runtime outcomes the caller can respond to: missing files, invalid user input, parse failures, permission errors, and network timeouts.
They belong in [[Result]] because they are part of the function's normal control flow.

Unrecoverable errors are states where continuing would be wrong, insecure, or meaningless.
They belong in [[panic!]] only when an invariant, precondition, or internal assumption has been broken.

## How it works
`Result<T, E>` forces the caller to handle or propagate the error before the code compiles.
That is why [[The Question Mark Operator]] and [[Propagating Errors]] are the default style for fallible functions.

`panic!` stops the current path of execution.
With the default unwind strategy, Rust walks the stack and runs destructors; with `panic = "abort"`, the process terminates without stack cleanup.
Either way, panic is not a typed value the caller can pattern-match like `Err(E)`.
It is a control-flow escape for bugs and broken invariants, not a replacement for domain errors.

The practical rule from the Book is: return `Result` by default, and panic only when the caller or program has reached a bad state that should be fixed by a programmer.
When unsure, ask whether a correct caller could reasonably encounter the condition in production.
If yes, return `Result`; if no, document the invariant and consider whether a stronger type can make the invalid state impossible.

## Example
```rust
fn parse_port(input: &str) -> Result<u16, String> {
    let port: u16 = input
        .parse()
        .map_err(|_| format!("port must be a number: {input}"))?;

    if port == 0 {
        return Err("port must be nonzero".to_string());
    }

    Ok(port)
}

fn require_nonempty(items: &[u8]) -> u8 {
    if items.is_empty() {
        panic!("items must not be empty");
    }
    items[0]
}

fn main() {
    assert_eq!(parse_port("8080"), Ok(8080));
    assert!(parse_port("abc").is_err());
    assert_eq!(require_nonempty(&[7]), 7);
}
```

## Edge cases
Library constructors often sit on the boundary between the two categories.
A `Percent::new(150) -> Result<Percent, PercentError>` is right when the value comes from users, files, or networks.
A `Percent::new_unchecked` would be unsafe or private unless the caller can uphold the invariant.
An indexing operation such as `items[0]` panics on an empty slice because indexing promises a reference, not a recoverable lookup; `items.get(0)` returns `Option` when absence is expected.

## Common errors
The compiler cannot always know whether a failed operation is recoverable; it enforces the return type you wrote.
Trying to use `?` inside a non-fallible function usually produces:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`
```

Fix it by changing the signature to return `Result`, or handle the error locally with `match`.
Do not replace `?` with `.unwrap()` unless the failure would prove a real invariant violation.

## Best practice
- ✅ Return [[Result]] for failures the caller can reasonably report, retry, ignore, convert, or recover from.
- ✅ Use [[panic!]] for violated contracts only after considering whether the type system can encode the invariant.
- ✅ Document public panics so callers know which preconditions are enforced at runtime.
- ✅ Let application boundaries decide whether a recoverable error becomes a user-facing failure, retry, log entry, or process exit.
- ✅ Prefer total APIs (`get`, checked constructors, `try_from`) when invalid input is normal.
- ✅ Keep panic messages about invariants, not operational failures like paths or HTTP status codes.

## Pitfalls
- ⚠️ Treating malformed input as a panic turns routine user behavior into a crash; see [[Panicking in Libraries]].
- ⚠️ Using [[Unwrap and Expect Overuse]] in production paths erases the caller's ability to recover.
- ⚠️ Returning [[Stringly-Typed Errors]] makes failures recoverable in theory but hard to inspect in practice.
- ⚠️ Swallowing a recoverable error hides the real failure; see [[Swallowing Errors]].
- ⚠️ Mixing panic and `Result` for the same failure mode makes the API hard to reason about.

## See also
[[Result]] · [[panic!]] · [[The Question Mark Operator]] · [[Propagating Errors]] · [[Returning Result from main]] · [[Custom Error Types]] · [[Panicking in Libraries]] · [[Unwrap and Expect Overuse]] · [[Option vs Result]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9 "Error Handling" and "To `panic!` or Not to `panic!`" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-00-error-handling.html and https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html
- Rust standard library, `std::result` module — https://doc.rust-lang.org/std/result/
