---
type: concept
title: "Cargo Build Run Check Test"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, build, test, tooling]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[Use cargo check While Editing]]", "[[rustfmt and Clippy]]", "[[Profiles and Optimization Settings]]", "[[Cargo.lock]]", "[[Returning Result from main]]"]
sources: ["[[the-book]]", "[[command-line-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch01-03-hello-cargo.html", "https://doc.rust-lang.org/cargo/commands/cargo-build.html", "https://doc.rust-lang.org/cargo/commands/cargo-run.html", "https://doc.rust-lang.org/cargo/commands/cargo-check.html", "https://doc.rust-lang.org/cargo/commands/cargo-test.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo Build Run Check Test

`cargo check`, `cargo build`, `cargo run`, and `cargo test` are the beginner command loop: check fast, build artifacts when needed, run binaries during iteration, and test behavior before trusting changes.

## What it is
These commands answer different questions:

- `cargo check`: does the package type-check and compile far enough to report errors?
- `cargo build`: can Cargo produce the executable or library artifacts?
- `cargo run`: can Cargo build the selected binary and execute it?
- `cargo test`: do test functions and test targets pass?

They overlap, but they are not interchangeable. `check` is fast because it skips
final executable generation. `build` creates artifacts. `run` executes a binary.
`test` compiles the package in test mode and runs discovered tests.

## How it works
Cargo tracks source and dependency changes. If nothing changed, repeating
`cargo run` or `cargo build` can finish quickly because Cargo reuses previous
work. A debug build goes to `target/debug`; `cargo build --release` uses the
release profile and writes to `target/release`.

The command-line book adds the testing angle: Rust's built-in test harness
discovers functions marked with `#[test]`. Integration tests conventionally live
under `tests/`, while unit tests can live beside the code they exercise.

`cargo check` still runs much of the compiler pipeline: parsing, name
resolution, macro expansion, type checking, borrow checking, linting, and
metadata emission. It skips final code generation, so some diagnostics that only
appear during code generation or linking are left for `cargo build`, `cargo run`,
or `cargo test`.

`cargo test` builds special test executables with Rust's libtest harness. Unit
tests can access private items in their target. Integration tests are separate
crates and use the package's public API. Documentation tests for a library are
also run by default and are compiled by `rustdoc`.

## Example
```rust
fn double(n: i32) -> i32 {
    n * 2
}

fn main() {
    println!("{}", double(21));
}

#[test]
fn doubles_an_integer() {
    assert_eq!(double(21), 42);
}
```

## Worked example
Use the commands as a layered loop:

```text
$ cargo check
$ cargo fmt
$ cargo clippy
$ cargo test
$ cargo run -- input.txt --verbose
$ cargo build --release
```

The first command gives fast compiler feedback. Formatting and Clippy keep the
code reviewable. Tests prove behavior. `cargo run -- ...` passes arguments
after `--` to the binary rather than to Cargo. Release builds are reserved for
optimized artifacts or performance measurements.

Target flags narrow the work:

```text
$ cargo test parser
$ cargo test --lib
$ cargo test --test cli
$ cargo run --bin admin
$ cargo run --example count_file
```

These are Cargo selections, not different languages or compilers. They choose
which package targets Cargo asks `rustc` to compile and run.

## Common errors
Passing program arguments without `--` makes Cargo parse them:

```text
error: unexpected argument '--name' found
```

Use `cargo run -- --name ferris` so `--name ferris` reaches your binary.

A clean check can still fail at build or run time:

```text
error: linking with `cc` failed: exit status: 1
```

Install the platform linker or native libraries, then run `cargo build` again.
`cargo check` did its job; linking is a later stage.

Test filters and harness flags are split by `--`:

```text
cargo test parser -- --test-threads 1
```

`parser` filters test names. `--test-threads 1` is passed to libtest.

## Best practice
- ✅ Run `cargo check` frequently while editing; it is the fastest feedback loop
  for type errors and borrow-checker errors.
- ✅ Use `cargo run` for beginner binary projects and tutorials such as
  [[The Guessing Game Tutorial]].
- ✅ Run `cargo test` before considering behavior done, even when the program is
  small.
- ✅ Use `cargo build --release` when measuring runtime or producing optimized
  binaries, not for every edit-compile cycle.
- ✅ Use target selectors to keep feedback focused in larger packages and
  workspaces.
- ✅ Treat warnings as work to resolve, especially before publishing or merging.
- ✅ Use `cargo test --no-run` when you need to confirm test compilation without
  executing slow or environment-dependent tests.

## Pitfalls
- ⚠️ Benchmarking `target/debug` binaries; debug builds favor compilation speed
  and debuggability over runtime speed. See [[Profiles and Optimization Settings]].
- ⚠️ Confusing a clean `cargo check` with a tested program; it proves type-level
  validity, not behavior.
- ⚠️ Ignoring warnings from build output; warnings often identify code that
  [[rustfmt and Clippy]] or [[Lints and Lint Levels]] can make clearer.
- ⚠️ Assuming `cargo test` only runs unit tests; it also builds/runs integration
  tests and library doc tests by default.
- ⚠️ Forgetting that `cargo run` chooses one binary; multiple binaries need
  `--bin` or `default-run`.

## See also
[[Cargo Basics]] · [[Use cargo check While Editing]] · [[rustfmt and Clippy]] · [[Profiles and Optimization Settings]] · [[Returning Result from main]] · [[Panic Unwinding and Abort]] · [[Keep Application Logic Testable]] · [[Anatomy of a Cargo Project]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 1.3 "Hello, Cargo!" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-03-hello-cargo.html
- The Cargo Book command docs — https://doc.rust-lang.org/cargo/commands/cargo-check.html
