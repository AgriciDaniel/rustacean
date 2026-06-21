---
type: pattern
title: "Reading Standard Input"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, stdin, cli]
domain: "std: I/O & Formatting"
difficulty: basic
related: ["[[Writing Standard Output]]", "[[The Read and Write Traits]]", "[[Buffered I/O with BufReader and BufWriter]]", "[[IO Errors and io::Result]]", "[[The Question Mark Operator]]", "[[Result]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/io/fn.stdin.html", "https://doc.rust-lang.org/std/io/struct.Stdin.html", "https://doc.rust-lang.org/std/io/trait.BufRead.html"]
rust_version: "edition 2024 / 1.85+"
---

# Reading Standard Input

Read standard input through `std::io::stdin()`, usually line-by-line for interactive CLI input or through the `Read` trait for byte streams.

## What it is
Standard input is the process input stream supplied by the shell, terminal, pipe, or parent process.
In Rust it is exposed by `std::io::stdin()`.
The returned `Stdin` handle can read a line directly with `read_line`.
For repeated reads, lock it with `stdin.lock()` to avoid taking the global lock on every operation.
For byte-oriented code, treat stdin as any other reader implementing [[The Read and Write Traits]].
For line-oriented code, use the `BufRead` methods available on `StdinLock`.
This pattern belongs with [[Writing Standard Output]] and [[IO Errors and io::Result]].
It is common in command-line tools, exercises, filters, and test harness helpers.

## How it works
`stdin().read_line(&mut String)` appends bytes up to and including the newline.
The returned `usize` is the number of bytes read.
A return of `0` means end of input.
`read_line` requires a mutable `String` because it appends instead of replacing.
Call `clear()` before reusing the same buffer for the next logical line.
The input must be valid UTF-8 when reading into `String`.
If arbitrary bytes are possible, read into `Vec<u8>` through `Read::read_to_end`.
The `?` operator works naturally when `main` or a helper returns `io::Result<()>`.
Interactive input often needs trimming because the newline is part of the line.
Use `trim_end()` when only the line ending should be removed.
Use `trim()` only when leading and trailing whitespace are intentionally ignored.

## Example
```rust
use std::io;

fn main() -> io::Result<()> {
    let mut name = String::new();

    io::stdin().read_line(&mut name)?;
    let name = name.trim_end();

    println!("hello, {name}");
    Ok(())
}
```

## Example: repeated lines
```rust
use std::io::{self, BufRead};

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let mut input = stdin.lock();
    let mut line = String::new();

    while input.read_line(&mut line)? != 0 {
        print!("read: {line}");
        line.clear();
    }

    Ok(())
}
```

## Best practice
- ✅ Return `io::Result<()>` from CLI `main` so input errors can use `?`.
- ✅ Lock stdin once when reading multiple lines.
- ✅ Reuse one `String` buffer in loops and call `clear()` between reads.
- ✅ Use `trim_end()` when removing only `\n` or `\r\n` from terminal input.
- ✅ Switch to byte buffers when stdin may contain non-UTF-8 data.
- ✅ Keep parsing separate from reading so the parser can be tested without a terminal.
- ✅ For filters, accept any `impl BufRead` in helper functions.

## Pitfalls
- ⚠️ `read_line` appends; forgetting `clear()` causes previous lines to remain.
- ⚠️ `trim()` removes meaningful leading spaces; use it only when whitespace is not data.
- ⚠️ Reading stdin directly in core logic makes tests awkward; depend on [[The Read and Write Traits]].
- ⚠️ `unwrap()` in CLI prototypes is common but poor for real tools; see [[Unwrap and Expect Overuse]].
- ⚠️ `read_to_string` can allocate the entire input; use streaming for large data.
- ⚠️ A terminal read can block forever if the user never sends a line or EOF.
- ⚠️ `String` input rejects invalid UTF-8; use `Vec<u8>` for binary protocols.

## See also
[[std IO & Formatting]] · [[Writing Standard Output]] · [[The Read and Write Traits]] ·
[[Buffered I/O with BufReader and BufWriter]] · [[IO Errors and io::Result]] · [[The Question Mark Operator]] ·
[[Result]] · [[String and str]] · [[Borrowing Strings and Slices]] · [[Unwrap and Expect Overuse]]

## Sources
- Rust Standard Library, `std::io::stdin` and `Stdin` — [[std]],
  https://doc.rust-lang.org/std/io/fn.stdin.html
- Rust Standard Library, `BufRead` — [[std]],
  https://doc.rust-lang.org/std/io/trait.BufRead.html
- Rust Standard Library, `std::io` module examples — [[std]],
  https://doc.rust-lang.org/std/io/index.html
