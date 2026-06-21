---
type: concept
title: "Seek and Cursor"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, seek, cursor]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[The Read and Write Traits]]", "[[Buffered I/O with BufReader and BufWriter]]", "[[Files in std::fs]]", "[[IO Errors and io::Result]]", "[[I/O Error Kinds]]", "[[Borrowed Parameter APIs]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/trait.Seek.html", "https://doc.rust-lang.org/std/io/enum.SeekFrom.html", "https://doc.rust-lang.org/std/io/struct.Cursor.html", "https://doc.rust-lang.org/std/io/index.html#seek-and-bufread"]
rust_version: "edition 2024 / 1.85+"
---

# Seek and Cursor

`Seek` moves the read/write position inside a seekable byte stream, and `Cursor<T>` gives an in-memory buffer the same positioned I/O behavior.

## What it is
`std::io::Seek` is the standard trait for byte streams with a movable cursor.
Files usually support seeking.
Sockets, pipes, and standard input usually do not.
The position is the byte offset used by the next read or write.
`Seek` complements [[The Read and Write Traits]].
It does not replace them.
A type can implement `Read`, `Write`, and `Seek` together.
`std::io::Cursor<T>` wraps in-memory storage such as `Vec<u8>`, `&[u8]`, or `[u8; N]`.
That wrapper is useful for tests, parsers, binary formats, and examples.
It lets code written against `Read + Seek` run without a real file.
The `SeekFrom` enum describes how a new position is calculated.
It can seek from the start, from the current position, or from the end.

## How it works
`seek` takes a `SeekFrom` and returns the resulting absolute position.
`SeekFrom::Start(n)` moves to byte offset `n`.
`SeekFrom::Current(delta)` moves relative to the current position.
`SeekFrom::End(delta)` moves relative to the end of the stream.
The relative forms use signed offsets.
Seeking before byte zero is an error.
Seeking beyond the end may be allowed by the underlying object.
For a file, writing after seeking beyond the end can create a hole on platforms that support sparse files.
For a `Cursor<Vec<u8>>`, writing can extend the vector.
For a `Cursor` over fixed-size or borrowed storage, writes are constrained by the wrapped buffer.
`Cursor::position()` reports the current offset.
`Cursor::set_position()` changes the offset without returning an `io::Result`.
`Cursor::into_inner()` returns the wrapped buffer when the cursor is no longer needed.
When a buffered reader wraps a seekable object, coordinate seeking through the wrapper so its buffer stays consistent.

## Example
```rust
use std::io::{self, Cursor, Read, Seek, SeekFrom, Write};

fn patch_header(mut stream: impl Read + Write + Seek) -> io::Result<Vec<u8>> {
    let mut header = [0_u8; 4];
    stream.read_exact(&mut header)?;

    stream.seek(SeekFrom::Start(0))?;
    stream.write_all(b"DONE")?;

    stream.seek(SeekFrom::Start(0))?;
    let mut out = Vec::new();
    stream.read_to_end(&mut out)?;
    Ok(out)
}

fn main() -> io::Result<()> {
    let data = Cursor::new(Vec::from(&b"PEND body"[..]));
    let patched = patch_header(data)?;

    assert_eq!(patched.as_slice(), b"DONE body");
    Ok(())
}
```

## Example: seek from the end
```rust
use std::io::{self, Cursor, Read, Seek, SeekFrom};

fn main() -> io::Result<()> {
    let mut reader = Cursor::new(b"abcdef".to_vec());
    let mut tail = [0_u8; 2];

    reader.seek(SeekFrom::End(-2))?;
    reader.read_exact(&mut tail)?;

    assert_eq!(&tail, b"ef");
    Ok(())
}
```

## Best practice
- ✅ Use `Read + Seek` bounds when code needs both bytes and repositioning.
- ✅ Use `Cursor<Vec<u8>>` or `Cursor<&[u8]>` to test seekable I/O without temporary files.
- ✅ Prefer `SeekFrom::Start` for fixed binary-format offsets.
- ✅ Check the returned position when the exact offset matters.
- ✅ Keep seek offsets in bytes, not characters or display columns.
- ✅ Use `read_exact` after seeking to a fixed-size protocol field.
- ✅ Let `io::Result` propagate seek failures with `?`.
- ✅ Seek through `BufReader` or `BufWriter` itself when a buffered wrapper owns the stream.

## Pitfalls
- ⚠️ Not every reader is seekable; generic code should require `Seek` only when it really needs it.
- ⚠️ `SeekFrom::End(-n)` can fail if `n` is larger than the stream length.
- ⚠️ Seeking uses byte offsets, so it is not a safe way to index human text by character.
- ⚠️ Writing with a `Cursor<Vec<u8>>` starts at position 0 unless you move to the end first.
- ⚠️ Manually seeking the inner object behind a buffer can desynchronize buffered state.
- ⚠️ Treating a successful seek beyond EOF as proof that bytes exist can produce later read surprises.
- ⚠️ Mapping all seek failures to one case loses useful [[I/O Error Kinds]].

## See also
[[std IO & Formatting]] · [[The Read and Write Traits]] · [[Buffered I/O with BufReader and BufWriter]] ·
[[Files in std::fs]] · [[IO Errors and io::Result]] · [[I/O Error Kinds]] ·
[[Reading Standard Input]] · [[Writing Standard Output]] · [[Borrowed Parameter APIs]] · [[Result]]

## Sources
- Rust Standard Library, `Seek` — [[std]],
  https://doc.rust-lang.org/std/io/trait.Seek.html
- Rust Standard Library, `SeekFrom` — [[std]],
  https://doc.rust-lang.org/std/io/enum.SeekFrom.html
- Rust Standard Library, `Cursor` — [[std]],
  https://doc.rust-lang.org/std/io/struct.Cursor.html
- Rust Standard Library, `std::io` module overview — [[std]],
  https://doc.rust-lang.org/std/io/index.html#seek-and-bufread
