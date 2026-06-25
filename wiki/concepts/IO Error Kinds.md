---
type: concept
title: "IO Error Kinds"
aliases: ["I/O Error Kinds"]
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, errors, errorkind]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[IO Errors and io::Result]]", "[[The Read and Write Traits]]", "[[Files in std::fs]]", "[[Seek and Cursor]]", "[[Reading Standard Input]]", "[[Recoverable vs Unrecoverable Errors]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/enum.ErrorKind.html", "https://doc.rust-lang.org/std/io/struct.Error.html", "https://doc.rust-lang.org/std/io/type.Result.html", "https://doc.rust-lang.org/std/io/index.html#ioresult"]
rust_version: "edition 2024 / 1.85+"
---

# IO Error Kinds

`io::ErrorKind` is the coarse, portable category attached to an `io::Error`; match it only when that category changes what your program should do.

## What it is
`std::io::Error` is the standard error type for Rust I/O.
`std::io::ErrorKind` classifies an `io::Error` into broad categories.
Common categories include `NotFound`, `PermissionDenied`, `AlreadyExists`, `InvalidInput`, `InvalidData`, `UnexpectedEof`, `Interrupted`, `WouldBlock`, `BrokenPipe`, and `Other`.
The full `io::Error` may also carry OS-specific data, a custom payload, or lower-level context.
The kind is intentionally portable and lossy.
It is useful for recovery decisions.
It is not a substitute for preserving the original error.
Use it with [[IO Errors and io::Result]] when an operation has a known alternate path.
For example, `NotFound` can mean "create the file".
`AlreadyExists` can mean "choose another path".
`UnexpectedEof` can mean "the file is truncated".
Other errors usually need to be propagated with context.

## How it works
Call `error.kind()` to inspect the category.
That returns an `ErrorKind`.
Compare it directly in a guard or match on it.
When matching, include a wildcard arm.
`ErrorKind` is not a closed application protocol.
New variants can be added by the standard library.
Some variants correspond closely to OS errors.
Others are produced by Rust adapters or validation code.
`InvalidInput` usually means the caller supplied an invalid argument before the operation was attempted.
`InvalidData` usually means bytes were read but did not satisfy the expected format, such as UTF-8 text APIs receiving invalid UTF-8.
`UnexpectedEof` means EOF arrived before a complete value was read.
Normal EOF from `Read::read` returning `Ok(0)` is not itself an error.
`Interrupted` often means the operation should be retried.
Higher-level methods may already handle retryable interruptions for you.
Always preserve the original `io::Error` when the caller needs diagnostics.

## Example
```rust
use std::fs;
use std::io::{self, ErrorKind};

fn read_config(path: &str) -> io::Result<String> {
    match fs::read_to_string(path) {
        Ok(text) => Ok(text),
        Err(error) if error.kind() == ErrorKind::NotFound => Ok(String::new()),
        Err(error) => Err(error),
    }
}

fn main() -> io::Result<()> {
    let text = read_config("missing-example.conf")?;
    assert!(text.is_empty());
    Ok(())
}
```

## Example: match with a wildcard
```rust
use std::io::{self, ErrorKind};

fn classify(error: &io::Error) -> &'static str {
    match error.kind() {
        ErrorKind::NotFound => "missing",
        ErrorKind::PermissionDenied => "permission",
        ErrorKind::UnexpectedEof => "truncated",
        _ => "other",
    }
}

fn main() {
    let error = io::Error::new(ErrorKind::UnexpectedEof, "short header");
    assert_eq!(classify(&error), "truncated");
}
```

## Best practice
- ✅ Match `ErrorKind` only when the branch has a specific recovery behavior.
- ✅ Propagate the original `io::Error` when you cannot recover.
- ✅ Include a wildcard arm when matching kinds.
- ✅ Treat `NotFound`, `AlreadyExists`, and `PermissionDenied` as distinct cases.
- ✅ Distinguish normal EOF from `UnexpectedEof`.
- ✅ Use `InvalidInput` for invalid arguments supplied to your I/O wrapper.
- ✅ Use `InvalidData` for malformed data read from an I/O source.
- ✅ Add path or operation context in higher-level application errors.

## Pitfalls
- ⚠️ Matching every kind just to print a different message duplicates standard diagnostics.
- ⚠️ Treating `Other` as impossible is incorrect.
- ⚠️ Dropping the original `io::Error` loses raw OS error codes and source context.
- ⚠️ Retrying every error can loop forever; retry only known transient cases such as `Interrupted`.
- ⚠️ Interpreting `UnexpectedEof` as normal end-of-file hides truncated records.
- ⚠️ Checking whether a file exists before opening it can race; handle the operation's error.
- ⚠️ Assuming variants cover every platform-specific case makes code brittle.

## See also
[[std IO & Formatting]] · [[IO Errors and io::Result]] · [[The Read and Write Traits]] ·
[[Files in std::fs]] · [[Seek and Cursor]] · [[Reading Standard Input]] ·
[[Writing Standard Output]] · [[Propagating Errors]] · [[Recoverable vs Unrecoverable Errors]] · [[Swallowing Errors]]

## Sources
- Rust Standard Library, `ErrorKind` — [[std]],
  https://doc.rust-lang.org/std/io/enum.ErrorKind.html
- Rust Standard Library, `io::Error` — [[std]],
  https://doc.rust-lang.org/std/io/struct.Error.html
- Rust Standard Library, `io::Result` — [[std]],
  https://doc.rust-lang.org/std/io/type.Result.html
- Rust Standard Library, `std::io` module overview — [[std]],
  https://doc.rust-lang.org/std/io/index.html#ioresult
