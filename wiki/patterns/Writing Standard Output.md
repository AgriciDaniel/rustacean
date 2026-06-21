---
type: pattern
title: "Writing Standard Output"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, stdout, formatting, cli]
domain: "std: I/O & Formatting"
difficulty: basic
related: ["[[Reading Standard Input]]", "[[The Read and Write Traits]]", "[[Format Strings and format!]]", "[[Format Specifiers]]", "[[IO Errors and io::Result]]", "[[Buffered I/O with BufReader and BufWriter]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/fn.stdout.html", "https://doc.rust-lang.org/std/macro.println.html", "https://doc.rust-lang.org/std/macro.write.html"]
rust_version: "edition 2024 / 1.85+"
---

# Writing Standard Output

Write user-facing output with `print!` and `println!`, and write fallible or high-volume output through `io::stdout().lock()` plus `write!` or `writeln!`.

## What it is
Standard output is the process stream used for normal program output.
Rust exposes convenience macros such as `print!` and `println!`.
It also exposes the byte-oriented `Stdout` handle from `std::io::stdout()`.
The macros use the same formatting language as [[Format Strings and format!]].
The handle implements `Write`, so it works with [[The Read and Write Traits]].
For many small programs, `println!` is exactly the right tool.
For command-line filters and libraries, use explicit writers so errors can be returned.
For repeated writes, lock stdout once.
For diagnostics, use stderr through `eprint!`, `eprintln!`, or `io::stderr()`.

## How it works
`println!` formats arguments and writes a newline to stdout.
`print!` does the same without adding a newline.
`write!` and `writeln!` write formatted text into an explicit destination.
When the destination is `StdoutLock`, the write can fail and returns `io::Result<()>`.
The standard library documentation notes that direct `stdout().write(...)` is less common than `println!`.
The distinction matters when output is piped.
For example, a Unix pipeline may close early, producing a broken pipe error.
If your program returns `io::Result<()>`, that error can be propagated or handled.
The output stream is global, so locking once reduces repeated synchronization.
Use `flush()` when a prompt must appear before waiting for input.

## Example
```rust
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let mut out = io::stdout().lock();

    writeln!(out, "count: {}", 3)?;
    write!(out, "ready> ")?;
    out.flush()?;

    Ok(())
}
```

## Example: output is injectable
```rust
use std::io::{self, Write};

fn write_report(mut out: impl Write, items: &[&str]) -> io::Result<()> {
    for item in items {
        writeln!(out, "- {item}")?;
    }
    Ok(())
}

fn main() -> io::Result<()> {
    write_report(io::stdout().lock(), &["alpha", "beta"])
}
```

## Best practice
- ✅ Use `println!` for simple program output.
- ✅ Use `writeln!(writer, ...)` inside reusable functions.
- ✅ Accept `impl Write` in functions that produce output.
- ✅ Lock stdout once for loops or reports.
- ✅ Flush prompts before reading from [[Reading Standard Input]].
- ✅ Write diagnostics to stderr, not stdout.
- ✅ Propagate output errors with `?` in real CLI tools.

## Pitfalls
- ⚠️ `print!` output may be buffered; prompts can be invisible until `flush()`.
- ⚠️ `println!` panics on some output failures; explicit `Write` lets you return errors.
- ⚠️ Building a `String` with `format!` just to write it adds an allocation; use `write!`.
- ⚠️ Mixing stdout and stderr can reorder messages because they are separate streams.
- ⚠️ Holding a stdout lock across slow work can block other output in the process.
- ⚠️ Ignoring `writeln!` results can hide broken pipes or full disks; see [[Swallowing Errors]].
- ⚠️ Do not use stdout for machine-readable data and logs at the same time.

## See also
[[std IO & Formatting]] · [[Reading Standard Input]] · [[The Read and Write Traits]] ·
[[Buffered I/O with BufReader and BufWriter]] · [[Format Strings and format!]] · [[Format Specifiers]] ·
[[Implementing Display by Hand]] · [[IO Errors and io::Result]] · [[Swallowing Errors]] · [[Result Returning Tests]]

## Sources
- Rust Standard Library, `std::io::stdout` — [[std]],
  https://doc.rust-lang.org/std/io/fn.stdout.html
- Rust Standard Library, `print!` and `println!` macros — [[std]],
  https://doc.rust-lang.org/std/macro.println.html
- Rust Standard Library, `write!` macro — [[std]],
  https://doc.rust-lang.org/std/macro.write.html
