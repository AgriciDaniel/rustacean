---
type: concept
title: "IO Errors and io::Result"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, errors, result]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[The Read and Write Traits]]", "[[Files in std::fs]]", "[[Reading Standard Input]]", "[[Writing Standard Output]]", "[[The Question Mark Operator]]", "[[Recoverable vs Unrecoverable Errors]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/io/type.Result.html", "https://doc.rust-lang.org/std/io/struct.Error.html", "https://doc.rust-lang.org/std/io/enum.ErrorKind.html"]
rust_version: "edition 2024 / 1.85+"
---

# IO Errors and io::Result

`io::Result<T>` is the standard alias for fallible I/O operations, carrying either `T` or an `io::Error` that describes an operating-system or stream failure.

## What it is
I/O is inherently fallible.
Files can be missing.
Permissions can deny access.
Disks can fill.
Pipes can close.
Input can contain invalid UTF-8.
The standard library represents these failures with `std::io::Error`.
Most I/O APIs return `std::io::Result<T>`.
That alias means `Result<T, std::io::Error>`.
`io::ErrorKind` provides coarse categories such as `NotFound`, `PermissionDenied`, and `UnexpectedEof`.
The full error may also include platform-specific information and context.

## How it works
Use `?` to propagate I/O errors from functions that return `io::Result<T>`.
Return `io::Result<()>` from simple CLI `main` functions.
Match on `error.kind()` when a specific recovery path is expected.
Use `ErrorKind::NotFound` to create a file after an open fails, for example.
Avoid matching raw OS error codes unless platform-specific behavior is intended.
When adapting I/O errors into application errors, preserve the source error.
`io::Error::new(kind, error)` can wrap additional error data.
`io::Error::last_os_error()` captures the current OS error indicator after appropriate OS calls.
For std-only applications, `io::Result<T>` is often enough.
For larger applications, convert into a domain error type.

## Example
```rust
use std::fs::File;
use std::io::{self, ErrorKind, Read};

fn read_or_empty(path: &str) -> io::Result<String> {
    let mut file = match File::open(path) {
        Ok(file) => file,
        Err(error) if error.kind() == ErrorKind::NotFound => return Ok(String::new()),
        Err(error) => return Err(error),
    };

    let mut text = String::new();
    file.read_to_string(&mut text)?;
    Ok(text)
}

fn main() -> io::Result<()> {
    let text = read_or_empty("missing-example.txt")?;
    assert!(text.is_empty());
    Ok(())
}
```

## Example: return from main
```rust
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let mut out = io::stdout().lock();
    writeln!(out, "fallible output")?;
    Ok(())
}
```

## Best practice
- ✅ Use `io::Result<T>` for functions whose only error type is I/O.
- ✅ Use `?` to keep ordinary propagation clear.
- ✅ Match `ErrorKind` only when you can actually recover or change behavior.
- ✅ Preserve source errors when wrapping them in application errors.
- ✅ Include the path or operation in higher-level error context when possible.
- ✅ Return `Ok(())` explicitly from fallible `main`.
- ✅ Test error paths with missing files, directories, and invalid input.

## Pitfalls
- ⚠️ Swallowing I/O errors makes data loss hard to diagnose; see [[Swallowing Errors]].
- ⚠️ Treating all errors as `NotFound` hides permissions and encoding problems.
- ⚠️ `UnexpectedEof` is different from normal EOF after a partial protocol field.
- ⚠️ `ErrorKind` is intentionally broad; do not expect it to encode every OS detail.
- ⚠️ `unwrap()` turns recoverable I/O failures into panics.
- ⚠️ Adding path context manually is important because low-level errors may not include your intent.
- ⚠️ Checking existence before opening can race; handle the operation's result.

## See also
[[std IO & Formatting]] · [[The Read and Write Traits]] · [[Files in std::fs]] ·
[[Reading Standard Input]] · [[Writing Standard Output]] · [[Path and PathBuf]] ·
[[The Question Mark Operator]] · [[Result]] · [[Recoverable vs Unrecoverable Errors]] · [[Swallowing Errors]]

## Sources
- Rust Standard Library, `io::Result` — [[std]],
  https://doc.rust-lang.org/std/io/type.Result.html
- Rust Standard Library, `io::Error` — [[std]],
  https://doc.rust-lang.org/std/io/struct.Error.html
- Rust Standard Library, `ErrorKind` — [[std]],
  https://doc.rust-lang.org/std/io/enum.ErrorKind.html
