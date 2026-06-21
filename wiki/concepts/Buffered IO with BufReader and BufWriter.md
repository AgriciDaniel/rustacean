---
type: concept
title: "Buffered IO with BufReader and BufWriter"
aliases: ["Buffered I/O with BufReader and BufWriter"]
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, buffering, bufreader, bufwriter]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[The Read and Write Traits]]", "[[Reading Standard Input]]", "[[Writing Standard Output]]", "[[Files in std::fs]]", "[[IO Errors and io::Result]]", "[[Iterator Adapters]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/struct.BufReader.html", "https://doc.rust-lang.org/std/io/struct.BufWriter.html", "https://doc.rust-lang.org/std/io/trait.BufRead.html"]
rust_version: "edition 2024 / 1.85+"
---

# Buffered IO with BufReader and BufWriter

`BufReader` and `BufWriter` wrap readers and writers to reduce small system calls and enable convenient buffered operations like `read_line` and `lines`.

## What it is
Byte-by-byte I/O is often inefficient because every operation may cross into the operating system.
`BufReader<R>` keeps an internal read buffer around any `R: Read`.
`BufWriter<W>` keeps an internal write buffer around any `W: Write`.
The wrappers are generic, so they work with files, streams, child process pipes, and custom readers.
`BufReader` also participates in the `BufRead` trait.
`BufRead` adds line and delimiter-oriented methods.
`BufWriter` does not change the logical write interface.
It batches writes and flushes them later.
These types are most useful when many small reads or writes hit an unbuffered resource.
They are less useful around sources that are already buffered in a way that matches your workload.

## How it works
`BufReader::new(reader)` creates a reader with the default capacity.
`BufReader::with_capacity(capacity, reader)` lets you choose the buffer size.
`read_line` appends one line to a `String`.
`lines()` returns an iterator of `io::Result<String>`.
`fill_buf` exposes the currently buffered bytes without consuming them.
`consume(n)` tells the buffer that `n` bytes were handled.
`BufWriter::new(writer)` stores writes in memory until the buffer fills or is flushed.
`flush()` reports write errors immediately.
Dropping a `BufWriter` attempts to flush, but errors during drop cannot be usefully returned.
Call `flush()` explicitly when the data must be durable or visible before continuing.
Use `into_inner()` if you need the wrapped writer back and want flush errors reported.

## Example
```rust
use std::io::{self, BufRead, BufReader, Cursor};

fn main() -> io::Result<()> {
    let data = Cursor::new("alpha\nbeta\n");
    let reader = BufReader::new(data);

    let mut lines = Vec::new();
    for line in reader.lines() {
        lines.push(line?);
    }

    assert_eq!(lines, ["alpha", "beta"]);
    Ok(())
}
```

## Example: buffered writes
```rust
use std::io::{self, BufWriter, Write};

fn main() -> io::Result<()> {
    let mut bytes = Vec::new();
    {
        let mut writer = BufWriter::new(&mut bytes);
        writeln!(writer, "one")?;
        writeln!(writer, "two")?;
        writer.flush()?;
    }

    assert_eq!(bytes, b"one\ntwo\n");
    Ok(())
}
```

## Best practice
- ✅ Wrap `File` in `BufReader` for line-by-line reads.
- ✅ Wrap `File` or sockets in `BufWriter` for many small writes.
- ✅ Import `BufRead` when using `read_line`, `lines`, `split`, or `fill_buf`.
- ✅ Explicitly call `flush()` on `BufWriter` before you need the data observed.
- ✅ Propagate the `Result` from `lines()` items instead of unwrapping.
- ✅ Reuse one line buffer with `read_line` when allocation matters.
- ✅ Tune capacity only after profiling; the default is usually fine.

## Pitfalls
- ⚠️ Data can remain in a `BufWriter` until flush or drop.
- ⚠️ Drop-time flush errors are easy to miss; call `flush()` yourself.
- ⚠️ Creating multiple `BufReader`s over the same stream can lose buffered bytes.
- ⚠️ `lines()` allocates a new `String` for each line.
- ⚠️ `read_line` keeps the newline; `lines()` strips line endings.
- ⚠️ Buffering an already buffered source may add latency without benefit.
- ⚠️ Mixing direct reads from the inner reader with buffered reads can produce surprising order.

## See also
[[std IO & Formatting]] · [[The Read and Write Traits]] · [[Reading Standard Input]] ·
[[Writing Standard Output]] · [[Files in std::fs]] · [[IO Errors and io::Result]] ·
[[Iterator Adapters]] · [[Unnecessary Collect]] · [[Performance & Optimization]] · [[Result]]

## Sources
- Rust Standard Library, `BufReader` — [[std]],
  https://doc.rust-lang.org/std/io/struct.BufReader.html
- Rust Standard Library, `BufWriter` — [[std]],
  https://doc.rust-lang.org/std/io/struct.BufWriter.html
- Rust Standard Library, `BufRead` — [[std]],
  https://doc.rust-lang.org/std/io/trait.BufRead.html
