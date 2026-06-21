---
type: concept
title: "Anatomy of a Cargo Project"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, project-structure, tooling]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[Cargo.toml Manifest]]", "[[Cargo.lock]]", "[[Packages and Crates]]", "[[Library and Binary Package Layout]]", "[[Crate Roots]]"]
sources: ["[[the-book]]", "[[command-line-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch01-03-hello-cargo.html", "https://doc.rust-lang.org/cargo/reference/cargo-targets.html", "https://doc.rust-lang.org/cargo/reference/manifest.html"]
rust_version: "edition 2024 / 1.85+"
---

# Anatomy of a Cargo Project

A Cargo project is a package directory organized around `Cargo.toml`, source files under `src/`, generated artifacts under `target/`, and conventional target locations that Cargo can discover automatically.

## What it is
The simplest generated binary package has this shape:

```text
hello_cargo/
  Cargo.toml
  Cargo.lock
  src/
    main.rs
  target/
```

`Cargo.toml` is the package manifest. `src/main.rs` is the crate root for the
default binary target. `Cargo.lock` records exact resolved dependency versions
after the first build that needs it. `target/` is generated build output and is
not source code.

## How it works
Cargo follows conventions so you do not have to list every source file manually.
A package can have a binary target at `src/main.rs`, a library target at
`src/lib.rs`, extra binaries under `src/bin/*.rs`, integration tests under
`tests/`, examples under `examples/`, and benchmarks under `benches/`.

The command-line book emphasizes splitting reusable application logic out of
`src/main.rs` into `src/lib.rs` when that logic should be tested directly or
shared by multiple binaries. That keeps `main` focused on input/output, argument
parsing, and process-level behavior while library functions hold domain logic.

Cargo's auto-discovery is target-based, not file-by-file magic. `src/main.rs`
and `src/lib.rs` are crate roots; submodules are reached through Rust's module
system from those roots. Files under `src/bin/` become separate binary crates.
Files under `tests/` become integration test crates that depend on the package's
public library API. Examples can be run with `cargo run --example name` and are
compiled by `cargo test` by default so examples do not silently rot.

## Example
```rust
pub fn greeting(name: &str) -> String {
    format!("Hello, {name}!")
}

fn main() {
    println!("{}", greeting("Cargo"));
}
```

## Worked example
A beginner CLI that is growing usually benefits from this shape:

```text
wordcount/
  Cargo.toml
  src/
    lib.rs
    main.rs
  tests/
    cli_smoke.rs
  examples/
    count_file.rs
```

`src/lib.rs` holds testable domain logic:

```rust
pub fn count_words(text: &str) -> usize {
    text.split_whitespace().count()
}

#[test]
fn counts_words() {
    assert_eq!(count_words("one two three"), 3);
}
```

`src/main.rs` stays small and calls the library:

```rust
fn main() {
    let count = wordcount::count_words("hello from Cargo");
    println!("{count}");
}
```

This layout lets `cargo test` exercise the library directly, while `cargo run`
still runs the binary.

## Common errors
Putting a file in `src/` does not automatically make it part of the crate:

```text
error[E0583]: file not found for module `parser`
```

Declare the module from a crate root or parent module with `mod parser;`, then
place it at `src/parser.rs` or `src/parser/mod.rs` according to the module
layout you chose. Cargo discovers crate roots; Rust resolves modules.

Trying to call private library functions from integration tests produces a
privacy error:

```text
error[E0603]: function `count_words` is private
```

Integration tests are separate crates. Expose the API with `pub` when it is
part of the package's public test surface, or move the test beside the private
code as a unit test.

## Best practice
- ✅ Put Rust source files under `src/`; reserve the package root for metadata
  such as `Cargo.toml`, README files, licenses, and configuration.
- ✅ Keep reusable logic in `src/lib.rs` once `src/main.rs` starts mixing
  command-line plumbing with testable behavior; see [[Keep Application Logic Testable]].
- ✅ Let Cargo discover conventional targets before adding custom manifest
  entries; conventional layouts are easier for Rust developers to scan.
- ✅ Ignore generated `target/` output in version control, but understand
  whether your package should commit [[Cargo.lock]].
- ✅ Use `src/bin/name.rs` for extra small binaries that share one package.
- ✅ Use `tests/` for black-box integration tests that should see only public
  API, and unit tests beside code for private details.
- ✅ Keep examples compiling; `cargo test` builds examples by default even when
  it does not run their `main` functions as tests.

## Pitfalls
- ⚠️ Treating `mod` as if it textually includes files; Rust modules are resolved
  by the module system, not by C-style includes. See [[Treating mod as include]].
- ⚠️ Putting all code forever in `src/main.rs`; the command-line book shows how
  that quickly makes tests and reuse harder.
- ⚠️ Editing generated files under `target/`; rebuilds can replace them at any
  time.
- ⚠️ Creating multiple binaries and then being surprised that plain `cargo run`
  needs `--bin` or a `default-run` manifest setting.
- ⚠️ Hiding all behavior in `main`; integration tests and other binaries can
  only reuse public library APIs.

## See also
[[Cargo Basics]] · [[Cargo.toml Manifest]] · [[Cargo.lock]] · [[Packages and Crates]] · [[Crate Roots]] · [[Library and Binary Package Layout]] · [[Splitting Modules into Files]] · [[Keep Application Logic Testable]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 1.3 "Hello, Cargo!" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-03-hello-cargo.html
- The Cargo Book, "Cargo Targets" — https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- The Cargo Book, "The Manifest Format" — https://doc.rust-lang.org/cargo/reference/manifest.html
