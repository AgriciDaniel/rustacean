---
type: pattern
title: "Keep Application Logic Testable"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, testing, cli, cargo, design]
domain: "Tooling & Getting Started"
difficulty: intermediate
related: ["[[Anatomy of a Cargo Project]]", "[[Cargo Build Run Check Test]]", "[[Library and Binary Package Layout]]", "[[Returning Result from main]]", "[[Traits]]", "[[The Error Trait]]"]
sources: ["[[command-line-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/cargo-targets.html", "https://doc.rust-lang.org/cargo/commands/cargo-test.html", "https://doc.rust-lang.org/std/io/trait.Write.html"]
rust_version: "edition 2024 / 1.85+"
---

# Keep Application Logic Testable

Keep core application behavior in ordinary functions, and pass I/O dependencies as parameters when useful, so `cargo test` can exercise logic without driving the whole process manually.

## What it is
The command-line book shows this with a small grep-like tool. Printing matching
lines directly from `main` works, but it is awkward to unit test because the
logic is tangled with stdout. Extracting the search behavior into a function
makes the important behavior callable from tests.

The next improvement is passing a writer that implements `std::io::Write`.
That lets production code write to stdout while tests write to a memory buffer.
The code remains direct, but the boundary is testable.

## How it works
Rust's trait system lets functions accept behavior instead of one concrete I/O
destination. A parameter like `mut writer: impl std::io::Write` can be stdout, a
file, or a `Vec<u8>` in a test. `writeln!` writes to that destination and returns
an I/O result.

As the project grows, put reusable logic in `src/lib.rs` and keep `src/main.rs`
small. `main` parses arguments, reads external inputs, calls library functions,
prints output, and returns process-level errors. Tests can call the library
functions directly.

The mechanism is ordinary static dispatch when using `impl Write` in argument
position: the compiler monomorphizes the function for the concrete writer types
you call it with, such as `StdoutLock`, `File`, or `Vec<u8>`. If you need to
store mixed writers behind one value, use a trait object such as `&mut dyn
Write`, but most beginner code does not need that extra indirection.

Returning `io::Result<()>` keeps write failures visible. This matters for CLI
tools: stdout can fail when the downstream process closes a pipe. `println!`
panics on some output failures; `writeln!(writer, ...)?` lets the caller decide
the process policy.

## Example
```rust
use std::io::{self, Write};

fn write_match(mut out: impl Write, line: &str, pattern: &str) -> io::Result<()> {
    if line.contains(pattern) {
        writeln!(out, "{line}")?;
    }
    Ok(())
}

fn main() -> io::Result<()> {
    write_match(std::io::stdout(), "lorem ipsum", "lorem")
}
```

## Worked example
Make the core grep-like behavior testable without capturing global stdout:

```rust
use std::io::{self, Write};

pub fn find_matches(
    content: &str,
    pattern: &str,
    mut writer: impl Write,
) -> io::Result<()> {
    for line in content.lines() {
        if line.contains(pattern) {
            writeln!(writer, "{line}")?;
        }
    }
    Ok(())
}

#[test]
fn writes_only_matching_lines() {
    let mut output = Vec::new();

    find_matches("lorem ipsum\ndolor sit amet", "lorem", &mut output).unwrap();

    assert_eq!(output, b"lorem ipsum\n");
}
```

Production code passes stdout or a locked stdout handle. Tests pass a byte
buffer. The function's behavior is the same in both cases.

## Common errors
Forgetting to import the trait can make `writeln!` fail on custom writers:

```text
error[E0599]: cannot write into `Vec<u8>`
```

Bring `std::io::Write` into scope and pass a mutable writer when the call needs
to retain the buffer after writing.

Ignoring `writeln!`'s result triggers:

```text
warning: unused `Result` that must be used
```

Return `io::Result<()>` and use `?`, or deliberately handle the error at the
call site.

Asserting text against a byte buffer can cause type mismatches. A `Vec<u8>`
should be compared with a byte string (`b"..."`) or converted with
`String::from_utf8`.

## Best practice
- ✅ Extract logic from `main` when you want unit tests for it.
- ✅ Pass I/O abstractions such as `impl std::io::Write` when direct printing
  would hide observable behavior from tests.
- ✅ Return `Result` from functions that can fail instead of discarding write or
  read errors.
- ✅ Move shared logic into `src/lib.rs` when multiple binaries or tests need it.
- ✅ Keep `main` responsible for process concerns: parsing args, choosing files,
  opening stdout/stderr, and translating errors to exit status.
- ✅ Prefer returning data for pure transformations and passing writers for
  streaming output where collecting everything would change behavior.
- ✅ Lock or buffer stdout in output-heavy tools, then pass the handle down as
  the writer.

## Pitfalls
- ⚠️ Making every tiny beginner program highly abstract; testability should
  serve concrete behavior, not add ceremony for its own sake.
- ⚠️ Printing from deep logic and then struggling to assert output. Prefer a
  writer parameter or return data that the caller prints.
- ⚠️ Ignoring `writeln!` results; output can fail, especially in CLI tools that
  write to pipes.
- ⚠️ Hiding file reads, environment access, and global output inside deep logic;
  those choices make tests slow and brittle.
- ⚠️ Moving code to `src/lib.rs` but forgetting `pub` on the functions that
  integration tests or binaries need.

## See also
[[Anatomy of a Cargo Project]] · [[Cargo Build Run Check Test]] · [[Library and Binary Package Layout]] · [[Returning Result from main]] · [[Traits]] · [[The Error Trait]] · [[Result]] · [[Borrowed Parameter APIs]] · [[Tooling & Getting Started]]

## Sources
- Command Line Applications in Rust, "Making your code testable" — [[command-line-book]]
- The Cargo Book, "Cargo Targets" — https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- Standard library, `std::io::Write` — https://doc.rust-lang.org/std/io/trait.Write.html
