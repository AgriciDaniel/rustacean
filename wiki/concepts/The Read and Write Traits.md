---
type: concept
title: "The Read and Write Traits"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, traits, read, write]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[Reading Standard Input]]", "[[Writing Standard Output]]", "[[Buffered I/O with BufReader and BufWriter]]", "[[Files in std::fs]]", "[[IO Errors and io::Result]]", "[[Traits]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/trait.Read.html", "https://doc.rust-lang.org/std/io/trait.Write.html", "https://doc.rust-lang.org/std/io/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Read and Write Traits

`std::io::Read` and `std::io::Write` are byte-stream traits: `Read` pulls bytes from a source, and `Write` pushes bytes into a sink.

## What it is
The `std::io` module is centered on `Read` and `Write`.
They abstract over files, network streams, memory buffers, standard streams, and custom adapters.
A value that implements `Read` is often called a reader.
A value that implements `Write` is often called a writer.
This is the main reason Rust I/O APIs can be generic without depending on a concrete source.
`File`, `TcpStream`, `StdinLock`, `StdoutLock`, `Vec<u8>`, and `Cursor<T>` participate in this ecosystem.
The traits are byte-oriented, not text-oriented.
Text handling is layered on top through UTF-8 conversion, `String`, and `BufRead`.
For seekable streams, `Seek` adds cursor movement.
For buffered line-oriented input, `BufRead` builds on `Read`.

## How it works
`Read::read(&mut self, &mut [u8])` fills part or all of the supplied buffer.
It returns the number of bytes read.
It can return fewer bytes than the buffer length.
It returns `0` at EOF for finite streams.
`read_exact` keeps reading until the buffer is full or an error occurs.
`read_to_end` and `read_to_string` allocate or grow a destination until EOF.
`Write::write(&mut self, &[u8])` attempts to write bytes and returns how many were accepted.
It can write fewer bytes than requested.
`write_all` repeats until all bytes are written or an error occurs.
`flush` asks the writer to push buffered data to its underlying destination.
The extension methods are available when the traits are in scope.
Use `use std::io::{Read, Write};` when calling trait methods directly.

## Example
```rust
use std::io::{self, Read, Write};

fn copy_uppercase(mut input: impl Read, mut output: impl Write) -> io::Result<()> {
    let mut text = String::new();
    input.read_to_string(&mut text)?;

    for ch in text.chars() {
        write!(output, "{}", ch.to_ascii_uppercase())?;
    }

    Ok(())
}

fn main() -> io::Result<()> {
    let input = "rust".as_bytes();
    let mut output = Vec::new();
    copy_uppercase(input, &mut output)?;
    assert_eq!(output, b"RUST");
    Ok(())
}
```

## Example: exact bytes
```rust
use std::io::{self, Cursor, Read};

fn main() -> io::Result<()> {
    let mut reader = Cursor::new([1_u8, 2, 3, 4]);
    let mut header = [0_u8; 2];

    reader.read_exact(&mut header)?;
    assert_eq!(header, [1, 2]);

    Ok(())
}
```

## Best practice
- ✅ Use `impl Read` and `impl Write` at API boundaries when a concrete file is unnecessary.
- ✅ Prefer `read_exact` when a protocol requires a fixed-size field.
- ✅ Prefer `write_all` when all bytes must be written.
- ✅ Use `BufRead` for line-oriented input instead of manually scanning bytes.
- ✅ Keep `Read` and `Write` imports local to modules that call their methods.
- ✅ Return `io::Result<T>` from functions whose failures are ordinary I/O failures.
- ✅ Test I/O code with `Cursor`, byte slices, and `Vec<u8>`.

## Pitfalls
- ⚠️ A successful `read` or `write` may process only part of the buffer.
- ⚠️ `read_to_string` requires UTF-8 and reads until EOF.
- ⚠️ `write!` to an `io::Write` returns an I/O result; do not discard it.
- ⚠️ Calling `read` in a loop without handling `0` can spin at EOF.
- ⚠️ Assuming text APIs for binary data leads to invalid UTF-8 failures.
- ⚠️ Generic I/O code that hard-codes `File` is harder to test.
- ⚠️ Use buffering for many small reads or writes; see [[Buffered I/O with BufReader and BufWriter]].

## See also
[[std IO & Formatting]] · [[Reading Standard Input]] · [[Writing Standard Output]] ·
[[Buffered I/O with BufReader and BufWriter]] · [[Files in std::fs]] · [[IO Errors and io::Result]] ·
[[Traits]] · [[Trait Bounds]] · [[Result]] · [[The Question Mark Operator]]

## Sources
- Rust Standard Library, `Read` — [[std]],
  https://doc.rust-lang.org/std/io/trait.Read.html
- Rust Standard Library, `Write` — [[std]],
  https://doc.rust-lang.org/std/io/trait.Write.html
- Rust Standard Library, `std::io` module overview — [[std]],
  https://doc.rust-lang.org/std/io/index.html
