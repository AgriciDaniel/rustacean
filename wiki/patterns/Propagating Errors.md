---
type: pattern
title: "Propagating Errors"
aliases: ["Error Propagation"]
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, errors, propagation, result]
domain: "Error Handling"
difficulty: basic
related: ["[[Result]]", "[[The Question Mark Operator]]", "[[Custom Error Types]]", "[[Adding Error Context]]", "[[Returning Result from main]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#propagating-errors", "https://doc.rust-lang.org/std/result/", "https://doc.rust-lang.org/std/convert/trait.From.html"]
rust_version: "edition 2024 / 1.85+"
---

# Propagating Errors

Propagating errors means returning a failure to the caller instead of handling it locally, usually with `?`.

## What it is
When a function lacks enough context to recover, it should pass the error upward.
The caller may retry, substitute a default, show a message, log, or convert the error into an exit status.

This pattern is the everyday use of [[Result]] and [[The Question Mark Operator]].

## How it works
The function returns `Result<T, E>`.
Each fallible operation is followed by `?`.
On success, execution continues with the unwrapped value.
On failure, the function returns early with an error, converting it through `From` if the function's error type differs.

Add [[Adding Error Context]] where the current layer knows something the lower layer does not.
Propagation is a control-flow decision: "this layer cannot recover."
It should not be confused with ignoring the error or logging it everywhere.
The final handler, usually a CLI boundary, request handler, worker supervisor, or test assertion, decides how to report the chain.

## Example
```rust
use std::fs;
use std::io;

fn read_nonempty(path: &str) -> Result<String, io::Error> {
    let text = fs::read_to_string(path)?;
    if text.trim().is_empty() {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "file is empty"));
    }
    Ok(text)
}

fn main() {
    let result = read_nonempty("Cargo.toml");
    if let Err(error) = result {
        eprintln!("could not read file: {error}");
    }
}
```

## Second example
Propagate within a parser, but recover locally for one expected case.

```rust
use std::num::ParseIntError;

fn parse_line_numbers(text: &str) -> Result<Vec<u32>, ParseIntError> {
    let mut numbers = Vec::new();
    for line in text.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        numbers.push(trimmed.parse()?);
    }
    Ok(numbers)
}

fn main() {
    assert_eq!(parse_line_numbers("1\n\n2"), Ok(vec![1, 2]));
    assert!(parse_line_numbers("1\nx").is_err());
}
```

## Common errors
Using `?` before the function returns `Result` produces:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`
```

Fix it by changing the signature, mapping the error into the declared type, or handling the failure with `match`.
If the compiler says `From<SourceError>` is missing, add an intentional conversion or use `map_err`.

## Best practice
- ✅ Propagate when the current function cannot choose the right recovery behavior.
- ✅ Keep propagation signatures explicit so callers see the failure contract.
- ✅ Convert errors into a domain type when crossing an abstraction boundary; see [[Custom Error Types]].
- ✅ Attach context before propagating when the lower error alone is ambiguous.
- ✅ Handle narrow, expected exceptions locally and propagate the rest.
- ✅ Keep logging at the place where the error is actually handled.

## Pitfalls
- ⚠️ Propagating without context can yield messages like "not found" with no path; see [[Adding Error Context]].
- ⚠️ Propagating everything as `String` prevents callers from matching; see [[Stringly-Typed Errors]].
- ⚠️ Replacing `?` with `.unwrap()` converts propagation into a panic; see [[Unwrap and Expect Overuse]].
- ⚠️ Handling and then returning the same error can duplicate logs or messages.
- ⚠️ A catch-all conversion can erase whether a caller should retry, validate input, or report a bug.

## See also
[[Result]] · [[The Question Mark Operator]] · [[Returning Result from main]] · [[Custom Error Types]] · [[Adding Error Context]] · [[Application Errors with anyhow]] · [[Error Handling with thiserror]] · [[Swallowing Errors]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.2 "Propagating Errors" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#propagating-errors
- Rust standard library, `std::result` — https://doc.rust-lang.org/std/result/
