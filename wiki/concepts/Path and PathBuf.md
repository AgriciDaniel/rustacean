---
type: concept
title: "Path and PathBuf"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, path, filesystem, osstr]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[Files in std::fs]]", "[[The Read and Write Traits]]", "[[IO Errors and io::Result]]", "[[String and str]]", "[[AsRef and AsMut Conversion Traits]]", "[[Stringly-Typed Code]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/path/struct.Path.html", "https://doc.rust-lang.org/std/path/struct.PathBuf.html", "https://doc.rust-lang.org/std/ffi/struct.OsStr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Path and PathBuf

`Path` is a borrowed filesystem path, and `PathBuf` is its owned, mutable counterpart; use them instead of treating paths as ordinary UTF-8 strings.

## What it is
Filesystem paths are not just Rust `String` values.
Different platforms have different path encodings, separators, prefixes, and normalization rules.
`std::path::Path` is to `PathBuf` roughly what `str` is to `String`.
`Path` is an unsized borrowed path slice, normally used as `&Path`.
`PathBuf` owns path storage and can be mutated.
Many filesystem APIs accept `impl AsRef<Path>`.
That lets callers pass `&str`, `String`, `&Path`, or `PathBuf`.
Internally, prefer `Path` and `PathBuf` once a value is semantically a path.
This avoids accidental string parsing and preserves non-UTF-8 paths.
It also makes APIs communicate intent clearly.

## How it works
`Path::new("Cargo.toml")` creates a borrowed path view from a string literal.
`PathBuf::from("target")` creates an owned path buffer.
`join` appends a path component in a platform-aware way.
`parent`, `file_name`, `extension`, and `file_stem` inspect components.
These methods often return `Option` because paths may lack the requested component.
`to_str` returns `Option<&str>` because a path may not be valid UTF-8.
`display()` returns a wrapper that formats a path lossily for humans.
`to_string_lossy()` is also explicitly lossy and should be used only when loss is acceptable.
Paths can be absolute, relative, normalized, or syntactically unusual.
The `Path` API does not generally hit the filesystem unless the called method says so.
Use `std::fs::canonicalize` when you need a filesystem-resolved absolute path.

## Example
```rust
use std::path::{Path, PathBuf};

fn cache_file(root: impl AsRef<Path>, name: &str) -> PathBuf {
    root.as_ref().join("cache").join(name)
}

fn main() {
    let path = cache_file("/tmp/app", "index.txt");

    assert!(path.ends_with(Path::new("cache/index.txt")));
    assert_eq!(path.file_name().and_then(|s| s.to_str()), Some("index.txt"));
}
```

## Example: display for humans
```rust
use std::path::Path;

fn main() {
    let path = Path::new("logs/app.log");
    let message = format!("writing {}", path.display());

    assert_eq!(message, "writing logs/app.log");
}
```

## Best practice
- ✅ Accept paths as `impl AsRef<Path>` in public functions.
- ✅ Store owned paths as `PathBuf`, not `String`.
- ✅ Use `join` instead of manually adding separators.
- ✅ Treat `to_str()` returning `None` as a real possibility.
- ✅ Use `display()` for messages meant for people.
- ✅ Use `Path` methods for component inspection.
- ✅ Keep path construction separate from file opening so both can be tested.

## Pitfalls
- ⚠️ Assuming all paths are valid UTF-8 breaks cross-platform code.
- ⚠️ String concatenation can produce the wrong separator or duplicate separators.
- ⚠️ `display()` may be lossy; do not use it as a stable serialization format.
- ⚠️ `extension()` is syntactic, not a content-type check.
- ⚠️ Checking a path and later opening it can race; handle [[IO Errors and io::Result]].
- ⚠️ `canonicalize` touches the filesystem and fails if the path does not exist.
- ⚠️ Paths do not prevent traversal attacks by themselves; validate components for security-sensitive roots.

## See also
[[std IO & Formatting]] · [[Files in std::fs]] · [[IO Errors and io::Result]] ·
[[The Read and Write Traits]] · [[String and str]] · [[AsRef and AsMut Conversion Traits]] ·
[[Stringly-Typed Code]] · [[Borrowing Strings and Slices]] · [[Option]] · [[Result]]

## Sources
- Rust Standard Library, `Path` — [[std]],
  https://doc.rust-lang.org/std/path/struct.Path.html
- Rust Standard Library, `PathBuf` — [[std]],
  https://doc.rust-lang.org/std/path/struct.PathBuf.html
- Rust Standard Library, `OsStr` — [[std]],
  https://doc.rust-lang.org/std/ffi/struct.OsStr.html
