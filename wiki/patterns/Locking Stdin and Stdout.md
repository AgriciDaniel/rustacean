---
type: pattern
title: "Locking Stdin and Stdout"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, stdin, stdout, locking, cli]
domain: "std: I/O & Formatting"
difficulty: basic
related: ["[[Reading Standard Input]]", "[[Writing Standard Output]]", "[[The Read and Write Traits]]", "[[Buffered I/O with BufReader and BufWriter]]", "[[IO Errors and io::Result]]", "[[Returning Result from main]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/struct.Stdin.html#method.lock", "https://doc.rust-lang.org/std/io/struct.Stdout.html#method.lock", "https://doc.rust-lang.org/std/io/struct.StdinLock.html", "https://doc.rust-lang.org/std/io/struct.StdoutLock.html", "https://doc.rust-lang.org/std/io/index.html#standard-input-and-output"]
rust_version: "edition 2024 / 1.85+"
---

# Locking Stdin and Stdout

Lock stdin and stdout once when doing repeated terminal I/O so each read or write uses the same guarded handle instead of repeatedly taking the global stream lock.

## What it is
`std::io::stdin()` and `std::io::stdout()` return handles to process-global standard streams.
Those handles coordinate access through locking.
For a single `println!`, the macro is usually fine.
For loops and mixed input/output code, explicit locks are clearer and cheaper.
`Stdin::lock()` returns a `StdinLock`.
`Stdout::lock()` returns a `StdoutLock`.
`StdinLock` implements `Read` and `BufRead`.
`StdoutLock` implements `Write`.
That means locked streams compose with [[The Read and Write Traits]].
The pattern is common in command-line tools, coding challenge solutions, filters, and REPL-style programs.
It also makes fallible output visible because `write!` and `writeln!` return results.
Keep the lock scope as small as the repeated I/O operation needs.

## How it works
Bind the stream handle, then lock it.
Pass the locked guard to helpers that accept `impl BufRead` or `impl Write`.
Use `read_line` on `StdinLock` for line input.
Use `writeln!` on `StdoutLock` for output.
Call `flush()` before waiting for input after printing a prompt without a newline.
The guard unlocks automatically when it is dropped.
This follows the same RAII shape as other guard-based APIs.
For stdout, explicit locking avoids repeatedly locking around every small write.
For stdin, the locked handle exposes buffered line-reading methods.
For testable code, keep parsing and formatting helpers generic over `BufRead` and `Write`.
That lets production call them with locked standard streams and tests call them with `Cursor` and `Vec<u8>`.

## Example
```rust
use std::io::{self, BufRead, Write};

fn echo_number(mut input: impl BufRead, mut output: impl Write) -> io::Result<()> {
    let mut line = String::new();
    input.read_line(&mut line)?;
    let number: i32 = line.trim().parse().unwrap_or(0);

    writeln!(output, "{}", number * 2)?;
    Ok(())
}

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let stdout = io::stdout();

    let input = stdin.lock();
    let output = stdout.lock();

    echo_number(input, output)
}
```

## Example: prompt before input
```rust
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let stdout = io::stdout();

    let mut out = stdout.lock();
    write!(out, "name: ")?;
    out.flush()?;

    let mut name = String::new();
    stdin.read_line(&mut name)?;

    writeln!(out, "hello, {}", name.trim_end())?;
    Ok(())
}
```

## Best practice
- ✅ Lock stdin once for repeated line reads.
- ✅ Lock stdout once for repeated writes.
- ✅ Use `writeln!(out, ...)` and propagate the result with `?`.
- ✅ Flush stdout before a prompt that does not end with `\n`.
- ✅ Keep core logic generic over `BufRead` and `Write`.
- ✅ Drop the lock before calling code that might also need long-running access to the same stream.
- ✅ Return `io::Result<()>` from `main` so stream failures are not ignored.
- ✅ Use `Cursor` and `Vec<u8>` in tests instead of real terminal streams.

## Pitfalls
- ⚠️ Ignoring output errors can hide broken pipes and failed writes; see [[Swallowing Errors]].
- ⚠️ Holding a stream lock across unrelated work can make interleaved output less predictable.
- ⚠️ Printing a prompt without `flush()` can leave the prompt buffered until after input is read.
- ⚠️ `println!` is convenient but not ideal for tight output loops.
- ⚠️ `read_line` appends to the buffer; clear it when reusing a `String`.
- ⚠️ `String` input requires valid UTF-8; use byte APIs for arbitrary input.
- ⚠️ `unwrap()` on terminal I/O turns ordinary environment failures into panics.

## See also
[[std IO & Formatting]] · [[Reading Standard Input]] · [[Writing Standard Output]] ·
[[The Read and Write Traits]] · [[Buffered I/O with BufReader and BufWriter]] · [[IO Errors and io::Result]] ·
[[Returning Result from main]] · [[Seek and Cursor]] · [[The Question Mark Operator]] · [[Swallowing Errors]]

## Sources
- Rust Standard Library, `Stdin::lock` — [[std]],
  https://doc.rust-lang.org/std/io/struct.Stdin.html#method.lock
- Rust Standard Library, `Stdout::lock` — [[std]],
  https://doc.rust-lang.org/std/io/struct.Stdout.html#method.lock
- Rust Standard Library, `StdinLock` — [[std]],
  https://doc.rust-lang.org/std/io/struct.StdinLock.html
- Rust Standard Library, `StdoutLock` — [[std]],
  https://doc.rust-lang.org/std/io/struct.StdoutLock.html
- Rust Standard Library, standard input and output overview — [[std]],
  https://doc.rust-lang.org/std/io/index.html#standard-input-and-output
