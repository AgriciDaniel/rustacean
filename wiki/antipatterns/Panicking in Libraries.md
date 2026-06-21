---
type: antipattern
title: "Panicking in Libraries"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, panic, libraries, api-design]
domain: "Error Handling"
difficulty: intermediate
related: ["[[panic!]]", "[[Result]]", "[[Recoverable vs Unrecoverable Errors]]", "[[Custom Error Types]]", "[[Error Handling with thiserror]]", "[[Error Handling]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html", "https://doc.rust-lang.org/book/ch09-01-unrecoverable-errors-with-panic.html", "https://doc.rust-lang.org/std/macro.panic.html"]
rust_version: "edition 2024 / 1.85+"
---

# Panicking in Libraries

Panicking in libraries is wrong when the failure is expected and recoverable, because it takes the recovery decision away from downstream callers.

## The mistake
A library function sees malformed input, an IO error, a missing record, or a remote failure and calls [[panic!]].
That forces every application using the library into a crash or unwind path.

Library panics are appropriate for caller bugs and documented contract violations.
They are not appropriate for routine environmental failure.

## Why it happens
Panics are easy to write and sometimes feel like "the error cannot happen here".
But a library rarely knows the caller's policy.
One application may retry, another may show a validation message, and another may ignore a missing optional file.

Returning [[Result]] preserves that choice.
[[Error Handling with thiserror]] makes precise library errors cheap enough that panic is rarely justified for expected failures.
Panics also interact with the downstream binary's panic strategy.
A consumer may build with `panic = "abort"`, run in a plugin host, or cross FFI boundaries where unwinding is constrained.
Your library should not force those policies for ordinary invalid input or environmental failure.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
pub enum DecodeError {
    Empty,
    InvalidHex,
}

pub fn decode_byte(input: &str) -> Result<u8, DecodeError> {
    if input.is_empty() {
        return Err(DecodeError::Empty);
    }
    u8::from_str_radix(input, 16).map_err(|_| DecodeError::InvalidHex)
}

fn main() {
    assert_eq!(decode_byte("ff"), Ok(255));
    assert_eq!(decode_byte(""), Err(DecodeError::Empty));
}
```

## Second example
It is fine to panic for documented caller bugs, but offer fallible APIs for runtime data.

```rust
#[derive(Debug, PartialEq, Eq)]
pub struct NonEmptyName(String);

#[derive(Debug, PartialEq, Eq)]
pub struct EmptyName;

impl NonEmptyName {
    pub fn parse(input: String) -> Result<Self, EmptyName> {
        if input.trim().is_empty() {
            Err(EmptyName)
        } else {
            Ok(Self(input))
        }
    }

    pub fn from_static(input: &'static str) -> Self {
        assert!(!input.is_empty(), "static name must be nonempty");
        Self(input.to_string())
    }
}

fn main() {
    assert!(NonEmptyName::parse(String::new()).is_err());
    assert!(NonEmptyName::from_static("admin").0 == "admin");
}
```

## Common errors
The downstream symptom is a runtime panic outside the caller's control:

```text
thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: ...'
```

Fix the library by returning `Result` for expected failures and documenting the remaining panics as preconditions.
Inside the library, replace internal `unwrap` on fallible external data with `?` and a typed error variant.

## Best practice
- ✅ Return typed errors for expected library failures.
- ✅ Panic only for documented precondition violations, impossible internal states, or security-sensitive invalid states.
- ✅ Encode invariants in types when practical so invalid calls do not compile.
- ✅ Make error variants reflect caller action, not private implementation detail.
- ✅ Provide checked constructors for data that can come from users, files, or networks.
- ✅ Keep panic behavior explicit in rustdoc `# Panics` sections for public APIs.

## Pitfalls
- ⚠️ `unwrap` inside library code is often an undocumented panic path; see [[Unwrap and Expect Overuse]].
- ⚠️ Panicking for bad user input makes the application less robust.
- ⚠️ Catching a library's panic is a poor substitute for a typed error contract.
- ⚠️ Public APIs that sometimes panic and sometimes return errors need especially clear documentation.
- ⚠️ Relying on unwinding for recovery breaks for consumers that build or deploy with aborting panics.

## See also
[[panic!]] · [[Result]] · [[Recoverable vs Unrecoverable Errors]] · [[Custom Error Types]] · [[Error Handling with thiserror]] · [[Panic Unwinding and Abort]] · [[Unwrap and Expect Overuse]] · [[Error Handling]]

## Sources
- The Rust Programming Language, ch. 9.3 "Guidelines for Error Handling" — [[the-book]],
  https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html
- Rust standard library, `panic!` — https://doc.rust-lang.org/std/macro.panic.html
