---
type: concept
title: "Files in std::fs"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, fs, files]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[The Read and Write Traits]]", "[[Buffered I/O with BufReader and BufWriter]]", "[[Path and PathBuf]]", "[[IO Errors and io::Result]]", "[[Ownership]]", "[[RAII and Drop Guards]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/fs/index.html", "https://doc.rust-lang.org/std/fs/struct.File.html", "https://doc.rust-lang.org/std/fs/struct.OpenOptions.html"]
rust_version: "edition 2024 / 1.85+"
---

# Files in std::fs

`std::fs` provides filesystem operations, while `std::fs::File` is an owned file handle that implements `Read`, `Write`, and `Seek`.

## What it is
The `std::fs` module contains portable filesystem operations.
`File` represents an open file handle.
Opening a file acquires an operating-system resource.
Dropping `File` closes that resource.
This is a normal Rust ownership pattern, not a special cleanup mechanism.
`File::open` opens for reading.
`File::create` opens for writing, creating or truncating the file.
`OpenOptions` configures read, write, append, create, truncate, and related behavior.
Convenience functions such as `fs::read`, `fs::read_to_string`, and `fs::write` handle whole files.
Use [[Path and PathBuf]] for path values rather than stringly-typed path manipulation.

## How it works
`File` implements [[The Read and Write Traits]] depending on how it was opened.
A file opened read-only will fail when written.
A file opened write-only will fail when read.
Most filesystem operations return `io::Result<T>`.
That result contains `io::Error` when the OS rejects the operation.
Failure can come from missing paths, permissions, invalid names, full disks, or races.
`File` also implements `Seek`, so a file cursor can be moved.
For small files, whole-file helpers are clear and fine.
For large files, stream through `BufReader` or `BufWriter`.
For atomic application-level updates, write to a temporary file and rename.
The standard library does not make multi-step filesystem workflows race-free by default.

## Example
```rust
use std::fs::File;
use std::io::{self, Read, Write};

fn main() -> io::Result<()> {
    let path = "rustacean-example.txt";

    {
        let mut file = File::create(path)?;
        file.write_all(b"Ferris\n")?;
    }

    let mut file = File::open(path)?;
    let mut text = String::new();
    file.read_to_string(&mut text)?;

    assert_eq!(text, "Ferris\n");
    std::fs::remove_file(path)?;
    Ok(())
}
```

## Example: OpenOptions
```rust
use std::fs::OpenOptions;
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let path = "rustacean-log.txt";
    let mut log = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)?;

    writeln!(log, "started")?;
    std::fs::remove_file(path)?;
    Ok(())
}
```

## Best practice
- ✅ Use `fs::read_to_string` for simple small UTF-8 files.
- ✅ Use `BufReader<File>` for line-oriented or streaming reads.
- ✅ Use `BufWriter<File>` for many small writes.
- ✅ Use `OpenOptions` when the access mode matters.
- ✅ Return or propagate `io::Result<T>` instead of panicking.
- ✅ Treat filesystem state as changeable between checks and use operations that report failure.
- ✅ Use `Path` and `PathBuf` for APIs that accept paths.

## Pitfalls
- ⚠️ `File::create` truncates an existing file.
- ⚠️ `fs::read_to_string` fails on invalid UTF-8.
- ⚠️ `fs::read` and `read_to_end` can allocate huge memory for huge files.
- ⚠️ Checking existence before opening can race; handle the open error instead.
- ⚠️ Assuming paths are UTF-8 breaks on some platforms.
- ⚠️ Drop closes files, but explicit flushing may still matter for buffered writers.
- ⚠️ Ignoring write results can silently lose data; see [[Swallowing Errors]].

## See also
[[std IO & Formatting]] · [[Path and PathBuf]] · [[The Read and Write Traits]] ·
[[Buffered I/O with BufReader and BufWriter]] · [[IO Errors and io::Result]] · [[Ownership]] ·
[[The Drop Trait]] · [[RAII and Drop Guards]] · [[Stringly-Typed Code]] · [[Swallowing Errors]]

## Sources
- Rust Standard Library, `std::fs` — [[std]],
  https://doc.rust-lang.org/std/fs/index.html
- Rust Standard Library, `File` — [[std]],
  https://doc.rust-lang.org/std/fs/struct.File.html
- Rust Standard Library, `OpenOptions` — [[std]],
  https://doc.rust-lang.org/std/fs/struct.OpenOptions.html
