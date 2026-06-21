---
type: pattern
title: "Cancellation-Safe I/O"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, async, tokio, io, cancellation]
domain: "Async Rust"
difficulty: advanced
related: ["[[Cancellation Safety]]", "[[Non-Cancellation-Safe select! Branches]]", "[[Async Timeouts]]", "[[select!]]", "[[Futures]]", "[[Streams]]"]
sources: ["[[the-book]]", "[[04-async-rust]]"]
source_urls: ["https://doc.rust-lang.org/book/ch17-03-more-futures.html", "https://docs.rs/tokio/latest/tokio/io/trait.AsyncReadExt.html", "https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html", "https://tokio.rs/tokio/tutorial/io", "https://tokio.rs/tokio/tutorial/framing"]
rust_version: "edition 2024 / 1.85+"
---

# Cancellation-Safe I/O

Cancellation-safe I/O keeps partial read or write progress outside futures that may be dropped, so timeouts and `select!` branches cannot silently lose protocol state.

## What it is
Async I/O futures can be cancelled whenever they are dropped.

That happens when a `select!` branch loses, when a timeout expires, when a task is aborted, or when a parent future is dropped.

An I/O operation is cancellation-safe when dropping the in-flight future and trying again later does not lose data or corrupt the protocol state.

Tokio documents this method by method.

`AsyncReadExt::read` and `read_buf` are cancellation-safe.
If they lose a `select!` race, Tokio guarantees no data was read.

`AsyncReadExt::read_exact` is not cancellation-safe.
If it loses a race, some bytes may already have been read into the buffer.

`AsyncWriteExt::write` and `write_buf` are cancellation-safe in the same "no data was written if cancelled before completion" sense.

`AsyncWriteExt::write_all` is not cancellation-safe.
If it loses a race, some prefix may already have been written, and calling `write_all` again starts from the beginning of the slice.

## How it works
The key question is where progress lives.

If progress lives only inside the future, dropping the future drops the progress.

If progress lives in a buffer, cursor, frame decoder, or session struct owned outside the future, cancellation can stop one attempt without forgetting what already happened.

For reads, prefer one-attempt operations in cancellation boundaries:

- `read(&mut [u8])`
- `read_buf(&mut BytesMut)` when using bytes
- a parser that stores accumulated bytes in a connection object

For writes, prefer:

- `write(&bytes[pos..])` with `pos` stored outside
- `write_buf(&mut cursor)` where the buffer cursor advances after successful writes
- a dedicated writer task when messages must eventually be flushed

Exact helpers are still excellent outside cancellation boundaries.
`read_exact` is the right tool for a fixed header when the future will not be raced or timed out mid-operation.
The problem is using exact helpers in places where losing a race drops them halfway through.

## Example
```rust
use std::{io, time::Duration};
use tokio::io::{AsyncRead, AsyncReadExt};

struct HeaderReader {
    buf: [u8; 4],
    filled: usize,
}

impl HeaderReader {
    fn new() -> Self {
        Self { buf: [0; 4], filled: 0 }
    }

    async fn read_header<R>(&mut self, reader: &mut R) -> io::Result<Option<[u8; 4]>>
    where
        R: AsyncRead + Unpin,
    {
        while self.filled < self.buf.len() {
            let n = reader.read(&mut self.buf[self.filled..]).await?;
            if n == 0 {
                return Ok(None);
            }
            self.filled += n;
        }

        self.filled = 0;
        Ok(Some(self.buf))
    }
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let (mut client, mut server) = tokio::io::duplex(16);

    tokio::spawn(async move {
        let _ = tokio::io::AsyncWriteExt::write_all(&mut client, b"PING").await;
    });

    let mut headers = HeaderReader::new();

    let header = tokio::time::timeout(
        Duration::from_secs(1),
        headers.read_header(&mut server),
    )
    .await
    .map_err(|_| io::Error::new(io::ErrorKind::TimedOut, "header timeout"))??;

    assert_eq!(header, Some(*b"PING"));
    Ok(())
}
```

The reader stores `buf` and `filled` outside the individual `read` future.
If a timeout or `select!` branch cancels one call to `read`, no bytes were read for that cancelled attempt.
If a previous call completed with a short read, the byte count is preserved in `filled`.

## Write-side pattern
For writes, use an external cursor when a message may be interrupted:

```rust
use tokio::io::{self, AsyncWrite, AsyncWriteExt};

async fn write_with_progress<W>(writer: &mut W, bytes: &[u8]) -> io::Result<()>
where
    W: AsyncWrite + Unpin,
{
    let mut written = 0;

    while written < bytes.len() {
        let n = writer.write(&bytes[written..]).await?;
        if n == 0 {
            return Err(io::ErrorKind::WriteZero.into());
        }
        written += n;
    }

    Ok(())
}
```

If this function itself is cancelled, its local `written` counter is still dropped.
That means it is only cancellation-safe if the whole message may be abandoned.
When progress must survive cancellation, store the cursor in the caller's session object or use `write_buf` with a buffer object the caller retains.

## Best practice
- ✅ Check Tokio's "Cancel safety" docs before putting an I/O method in [[select!]] or [[Async Timeouts]].
- ✅ Use `read`/`read_buf` in cancellation boundaries and keep parsers or accumulators outside the future.
- ✅ Use `write`/`write_buf` with caller-owned progress for interruptible writes.
- ✅ Use `read_exact` and `write_all` only where the operation will be awaited to completion or abandonment is explicitly acceptable.
- ✅ Keep protocol framing state in a connection/session struct, not in branch-local variables.
- ✅ Treat retry behavior as part of the protocol design, especially for non-idempotent writes.

## Pitfalls
- ⚠️ Racing `read_exact` against shutdown and then retrying without knowing how many bytes were consumed.
- ⚠️ Racing `write_all` against a timeout and then sending the same buffer again, duplicating a prefix on the wire.
- ⚠️ Assuming a timeout error means no I/O happened; it only means the wrapped future did not complete.
- ⚠️ Storing progress in local variables of a helper future that is itself used in `select!`.
- ⚠️ Using high-level line or frame helpers without checking whether their cancellation contract preserves partial state.
- ⚠️ Forgetting that cancellation-safe operations still need normal EOF, `WriteZero`, and protocol-error handling.

## See also
[[Cancellation Safety]] · [[Non-Cancellation-Safe select! Branches]] · [[Async Timeouts]] · [[select!]] · [[Futures]] · [[Streams]] · [[The Tokio Runtime]] · [[Async Message Passing]] · [[Tasks and spawn]] · [[Async Rust]]

## Sources
- The Rust Programming Language, ch. 17.3 "Working With Any Number of Futures" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-03-more-futures.html
- Tokio tutorial, "I/O" — https://tokio.rs/tokio/tutorial/io
- Tokio tutorial, "Framing" — https://tokio.rs/tokio/tutorial/framing
- Tokio docs.rs `AsyncReadExt` cancel-safety sections — https://docs.rs/tokio/latest/tokio/io/trait.AsyncReadExt.html
- Tokio docs.rs `AsyncWriteExt` cancel-safety sections — https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
- `docs.rs/tokio/latest` points at the current published Tokio docs; verify the exact Tokio version against your project's `Cargo.lock`.
