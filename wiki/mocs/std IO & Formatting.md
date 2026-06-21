---
type: moc
title: "std IO & Formatting"
aliases: ["std: I/O & Formatting"]
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, io, formatting, moc]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[The Read and Write Traits]]", "[[Format Strings and format!]]", "[[Files in std::fs]]", "[[IO Errors and io::Result]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/io/index.html", "https://doc.rust-lang.org/std/fmt/index.html", "https://doc.rust-lang.org/std/fs/index.html", "https://doc.rust-lang.org/std/path/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# std IO & Formatting

This MOC maps the standard-library I/O and formatting surface: byte streams, buffered readers and writers, files, paths, format strings, specifiers, `Display`, and I/O errors.

## What belongs here
This domain covers `std::io`, `std::fmt`, `std::fs`, and `std::path` as they are used together in ordinary Rust programs.
It is about reading bytes, writing bytes, converting values to text, and naming filesystem locations.
It is not a full operating-system programming map.
It is not an async I/O map.
It is not a serialization format map.
It focuses on stable Rust edition 2024 / 1.85+.
The core idea is simple: make I/O generic through traits, make text formatting compiler-checked, and make errors explicit.

## Core notes
- [[The Read and Write Traits]] — byte-stream abstraction for sources and sinks.
- [[Buffered I/O with BufReader and BufWriter]] — batching reads and writes and using `BufRead`.
- [[Files in std::fs]] — file handles and filesystem helpers.
- [[Path and PathBuf]] — borrowed and owned filesystem paths.
- [[OsStr and OsString]] — operating-system string storage used by paths and process APIs.
- [[Seek and Cursor]] — positioned byte-stream I/O and in-memory seekable buffers.
- [[IO Errors and io::Result]] — standard I/O error handling.
- [[I/O Error Kinds]] — portable categories for recoverable I/O decisions.
- [[Format Strings and format!]] — checked formatting macros and argument capture.
- [[Format Specifiers]] — width, precision, alignment, fill, base, and trait selection.
- [[Implementing Display by Hand]] — custom `{}` output for your own types.
- [[Reading Standard Input]] — line and stream input from stdin.
- [[Writing Standard Output]] — stdout output with macros and explicit writers.

## Reading path
Start with [[The Read and Write Traits]].
Then read [[Reading Standard Input]] and [[Writing Standard Output]] for terminal workflows.
Move to [[Buffered I/O with BufReader and BufWriter]] once loops or large streams appear.
Read [[Files in std::fs]] before doing real filesystem work.
Read [[Path and PathBuf]] before designing any API that accepts paths.
For user-facing text, start with [[Format Strings and format!]].
Then use [[Format Specifiers]] for layout and numeric output.
Use [[Implementing Display by Hand]] when your own type needs `{}` output.
Keep [[IO Errors and io::Result]] open while wiring these pieces together.

## Patterns
- [[Reading Standard Input]] keeps input fallible and testable.
- [[Locking Stdin and Stdout]] keeps repeated terminal I/O efficient and explicitly fallible.
- [[Writing Standard Output]] separates presentation from where bytes go.
- [[Implementing Display by Hand]] turns domain values into clear user-facing text.
- [[Borrowed Parameter APIs]] supports `impl AsRef<Path>` and `impl Write` style APIs.
- [[Propagating Errors]] complements `io::Result<T>` and `?`.
- [[Returning Result from main]] is the natural shape for small CLI programs.
- [[Building Strings Efficiently]] helps choose between `format!`, `write!`, and mutation.
- [[Use a Newtype to Implement Foreign Traits]] helps when formatting foreign types.

## Concepts
- [[The Read and Write Traits]]
- [[Buffered I/O with BufReader and BufWriter]]
- [[Files in std::fs]]
- [[Path and PathBuf]]
- [[OsStr and OsString]]
- [[Seek and Cursor]]
- [[IO Errors and io::Result]]
- [[I/O Error Kinds]]
- [[Format Strings and format!]]
- [[Format Specifiers]]
- [[Display and Debug Formatting Traits]]
- [[The Display Trait]]
- [[The Debug Trait]]
- [[The Question Mark Operator]]
- [[Result]]

## Antipatterns
- [[Swallowing Errors]] — especially dangerous for writes and buffered flushes.
- [[Unwrap and Expect Overuse]] — turns recoverable I/O errors into panics.
- [[Stringly-Typed Code]] — especially common with paths.
- [[Panicking From Implementations]] — relevant to `Display` and `Debug` implementations.
- [[Unnecessary Collect]] — common when line streams are collected too early.
- [[Untested Documentation Examples]] — I/O examples should compile and handle errors.
- [[Overgeneric Public APIs]] — do not genericize beyond useful `Read`, `Write`, and `AsRef<Path>` boundaries.
- [[Avoiding Premature Optimization]] — tune buffer sizes only after measurement.

## Boundary decisions
Use `Read` and `Write` when the operation is about bytes.
Use `BufRead` when the operation is about lines or delimiters.
Use `Path` and `PathBuf` when the value is a filesystem path.
Use `format!` when an owned `String` is the real result.
Use `write!` or `writeln!` when the result should go directly to a writer.
Use `Display` for a stable user-facing representation.
Use `Debug` for developer diagnostics.
Use `io::Result<T>` when the only error family is standard I/O.
Use a richer application error type when I/O errors need domain context.

## Sources
- Rust Standard Library, `std::io` — [[std]],
  https://doc.rust-lang.org/std/io/index.html
- Rust Standard Library, `std::fmt` — [[std]],
  https://doc.rust-lang.org/std/fmt/index.html
- Rust Standard Library, `std::fs` — [[std]],
  https://doc.rust-lang.org/std/fs/index.html
- Rust Standard Library, `std::path` — [[std]],
  https://doc.rust-lang.org/std/path/index.html
