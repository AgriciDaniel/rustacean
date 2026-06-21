---
type: concept
title: "OsStr and OsString"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, ffi, osstr, strings, paths]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[Path and PathBuf]]", "[[String and str]]", "[[Bytes Chars and Unicode]]", "[[Stringly-Typed Code]]", "[[Borrowing Strings and Slices]]", "[[Borrowed Parameter APIs]]"]
sources: ["[[std]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/ffi/struct.OsStr.html", "https://doc.rust-lang.org/std/ffi/struct.OsString.html", "https://doc.rust-lang.org/std/path/struct.Path.html", "https://doc.rust-lang.org/reference/tokens.html#string-literals"]
rust_version: "edition 2024 / 1.85+"
---

# OsStr and OsString

`OsStr` and `OsString` store operating-system string data that may not be valid Rust UTF-8, especially path and process-argument text.

## What it is
`std::ffi::OsStr` is a borrowed operating-system string slice.
`std::ffi::OsString` is the owned, mutable counterpart.
They are to OS strings roughly what `str` and `String` are to UTF-8 text.
The difference is that OS strings preserve platform-native string data.
That matters for paths, command-line arguments, environment variables, and process APIs.
Rust `String` is always valid UTF-8.
An OS path or argument is not guaranteed to be valid UTF-8 on every platform.
`Path` and `PathBuf` are built on this idea.
For example, `Path::file_name()` returns an `Option<&OsStr>`.
Use `OsStr` at boundaries where the operating system, not Rust text processing, defines the bytes or code units.
Use `String` only after validating that the value is valid UTF-8.

## How it works
String literals can be viewed as `OsStr` with `OsStr::new`.
Owned values can be built with `OsString::from`.
Borrowing an `OsString` as `&OsStr` avoids allocation.
`to_str()` returns `Option<&str>` because conversion can fail.
`to_string_lossy()` returns text for display, replacing invalid data when needed.
That lossy result is appropriate for diagnostics but not for round-tripping identifiers.
`OsString::push` appends another OS string segment.
The internal representation is platform-specific and intentionally not a portable serialization format.
On Unix and Windows, extension traits expose platform-specific conversions for code that deliberately opts into them.
Most application code should stay with `Path`, `PathBuf`, `OsStr`, and `OsString` instead.
When designing APIs, accept `impl AsRef<OsStr>` only when the input is truly an OS string.
For filesystem paths, prefer `impl AsRef<Path>`.

## Example
```rust
use std::ffi::{OsStr, OsString};
use std::path::Path;

fn display_name(name: &OsStr) -> String {
    match name.to_str() {
        Some(valid_utf8) => valid_utf8.to_owned(),
        None => name.to_string_lossy().into_owned(),
    }
}

fn main() {
    let mut owned = OsString::from("report");
    owned.push(".txt");

    let path = Path::new(&owned);
    let file_name = path.file_name().unwrap_or_else(|| OsStr::new("<missing>"));

    assert_eq!(display_name(file_name), "report.txt");
}
```

## Example: keep paths as paths
```rust
use std::ffi::OsStr;
use std::path::Path;

fn has_extension(path: &Path, expected: &str) -> bool {
    path.extension() == Some(OsStr::new(expected))
}

fn main() {
    assert!(has_extension(Path::new("logs/app.log"), "log"));
}
```

## Best practice
- ✅ Use `Path` and `PathBuf` for filesystem paths, and let their component APIs return `OsStr`.
- ✅ Use `OsStr` or `OsString` for process arguments and environment-like OS data.
- ✅ Call `to_str()` when UTF-8 is required and handle `None`.
- ✅ Use `to_string_lossy()` only for human-facing diagnostics.
- ✅ Preserve `OsString` values when passing them back to OS APIs.
- ✅ Prefer borrowed parameters such as `&OsStr` or `impl AsRef<OsStr>` when ownership is unnecessary.
- ✅ Keep Unicode text processing on `str` after explicit conversion.
- ✅ Use platform extension traits only inside platform-specific modules.

## Pitfalls
- ⚠️ Assuming every path or argument is a valid `String` breaks non-UTF-8 inputs.
- ⚠️ `to_string_lossy()` can replace data, so it is not a stable serialization or lookup key.
- ⚠️ OS string ordering and normalization are not portable text semantics.
- ⚠️ `OsStr` is not a C string; use `CString`/`CStr` for nul-terminated C FFI.
- ⚠️ Manually splitting paths as strings duplicates work already handled by [[Path and PathBuf]].
- ⚠️ Exposing `String` in path APIs invites [[Stringly-Typed Code]].
- ⚠️ Platform-specific raw conversions should not leak into cross-platform public APIs.

## See also
[[std IO & Formatting]] · [[Path and PathBuf]] · [[String and str]] ·
[[Bytes Chars and Unicode]] · [[Borrowing Strings and Slices]] · [[Borrowed Parameter APIs]] ·
[[Stringly-Typed Code]] · [[Files in std::fs]] · [[Format Strings and format!]] · [[Display and Debug Formatting Traits]]

## Sources
- Rust Standard Library, `OsStr` — [[std]],
  https://doc.rust-lang.org/std/ffi/struct.OsStr.html
- Rust Standard Library, `OsString` — [[std]],
  https://doc.rust-lang.org/std/ffi/struct.OsString.html
- Rust Standard Library, `Path` — [[std]],
  https://doc.rust-lang.org/std/path/struct.Path.html
- The Rust Reference, string literals are UTF-8 source text — [[the-reference]],
  https://doc.rust-lang.org/reference/tokens.html#string-literals
