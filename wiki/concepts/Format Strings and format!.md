---
type: concept
title: "Format Strings and format!"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, fmt, formatting, macros]
domain: "std: I/O & Formatting"
difficulty: basic
related: ["[[Format Specifiers]]", "[[Implementing Display by Hand]]", "[[Writing Standard Output]]", "[[The Read and Write Traits]]", "[[Display and Debug Formatting Traits]]", "[[The Display Trait]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/fmt/index.html", "https://doc.rust-lang.org/std/macro.format.html", "https://doc.rust-lang.org/std/macro.format_args.html"]
rust_version: "edition 2024 / 1.85+"
---

# Format Strings and format!

Rust format strings are compiler-checked string literals that describe how values are converted into text by macros such as `format!`, `println!`, `write!`, and `format_args!`.

## What it is
Formatting is the standard way to turn values into human-readable text.
The `format!` macro returns a new `String`.
The `print!` and `println!` macros write formatted text to stdout.
The `write!` and `writeln!` macros write formatted text to a destination.
The `format_args!` macro produces a `fmt::Arguments` value without allocating a `String`.
All of these use the same formatting syntax from `std::fmt`.
The first argument to these macros must be a string literal.
That requirement lets the compiler validate placeholders and arguments.
The empty placeholder `{}` uses `Display`.
The debug placeholder `{:?}` uses `Debug`.

## How it works
Each `{}` in a format string consumes or references an argument.
Arguments can be implicit by position, explicit by numeric position, or named.
`format!("{} {}", 1, 2)` uses arguments in order.
`format!("{1} {0}", "a", "b")` chooses explicit positional arguments.
`format!("{name}", name = "Ferris")` uses a named argument.
When a name is not provided in the macro argument list, Rust can capture a local variable with that name.
Explicit argument references do not advance the implicit argument counter.
Unused format arguments are a compile-time error.
Literal braces are escaped as `{{` and `}}`.
For nontrivial width, precision, numeric base, and alignment, see [[Format Specifiers]].
For custom type output, see [[Implementing Display by Hand]].

## Example
```rust
fn main() {
    let language = "Rust";
    let edition = 2024;

    let label = format!("{language} edition {edition}");
    let debug = format!("{:?}", ("answer", 42));

    assert_eq!(label, "Rust edition 2024");
    assert_eq!(debug, "(\"answer\", 42)");
}
```

## Example: write without building a String
```rust
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let mut out = Vec::new();

    writeln!(&mut out, "id={:04}", 7)?;

    assert_eq!(out, b"id=0007\n");
    Ok(())
}
```

## Best practice
- ✅ Use `format!` when you need an owned `String`.
- ✅ Use `write!` or `writeln!` when you already have a writer.
- ✅ Prefer captured identifiers like `{name}` for readable format calls.
- ✅ Use `{:?}` for diagnostics and `{}` for user-facing display.
- ✅ Escape literal braces with `{{` and `}}`.
- ✅ Keep expensive formatting out of hot paths unless the result is needed.
- ✅ Use `format_args!` for logging-like APIs that can avoid allocation.

## Pitfalls
- ⚠️ Format strings must be literals; runtime strings are not accepted by these macros.
- ⚠️ `format!` allocates a new `String`; do not use it just to immediately write bytes.
- ⚠️ Mixed implicit and explicit positional arguments can be hard to read.
- ⚠️ `Debug` output is not a stable serialization format.
- ⚠️ `Display` is not automatically derived.
- ⚠️ Formatting is locale-independent; do not expect comma decimal separators.
- ⚠️ Supplying unused named arguments is a compile-time error.

## See also
[[std IO & Formatting]] · [[Format Specifiers]] · [[Implementing Display by Hand]] ·
[[Writing Standard Output]] · [[The Read and Write Traits]] · [[Display and Debug Formatting Traits]] ·
[[The Display Trait]] · [[The Debug Trait]] · [[Building Strings Efficiently]] · [[String and str]]

## Sources
- Rust Standard Library, `std::fmt` module — [[std]],
  https://doc.rust-lang.org/std/fmt/index.html
- Rust Standard Library, `format!` — [[std]],
  https://doc.rust-lang.org/std/macro.format.html
- Rust Standard Library, `format_args!` — [[std]],
  https://doc.rust-lang.org/std/macro.format_args.html
