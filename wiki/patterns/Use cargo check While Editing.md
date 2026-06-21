---
type: pattern
title: "Use cargo check While Editing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, feedback-loop, tooling]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Build Run Check Test]]", "[[Cargo Basics]]", "[[rustfmt and Clippy]]", "[[Borrowing]]", "[[The rustc Compiler]]", "[[Lints and Lint Levels]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch01-03-hello-cargo.html", "https://doc.rust-lang.org/cargo/commands/cargo-check.html"]
rust_version: "edition 2024 / 1.85+"
---

# Use cargo check While Editing

Use `cargo check` as the fast inner loop while writing Rust because it catches type, borrow, and many compile errors without spending time producing a final executable.

## What it is
`cargo check` asks Cargo and `rustc` whether the current package compiles, but
skips the final code generation step that produces a binary. The Book highlights
it as a way to check work periodically while writing code.

This is a workflow pattern, not a replacement for builds or tests. It gives fast
compiler feedback during editing, then `cargo build`, `cargo run`, `cargo test`,
`cargo fmt`, and `cargo clippy` answer the other parts of "is this ready?"

## How it works
Cargo still resolves the package, reads the manifest, checks dependencies, and
type-checks the crate. Because it does not emit the final executable, it is often
noticeably faster than `cargo build` for frequent checks.

The best moment to run it is after a small coherent change: a new function
signature, a borrow-checker fix, a refactor of a loop, or a dependency import.
Short intervals make compiler diagnostics easier to map back to the code you
just touched.

Under the hood, `cargo check` asks `rustc` to stop before final code generation.
It still catches most language errors: missing names, bad types, invalid trait
bounds, move and borrow errors, macro expansion failures, and many lints. It
also writes metadata so later checks can reuse unchanged work.

The limitation is important: checks do not prove that linking succeeds, that a
binary runs, that tests pass, or that code-generation-only diagnostics are
absent. Treat it as the inner loop, then close the loop with build/test/lint
commands.

## Example
```rust
fn parse_port(text: &str) -> Result<u16, std::num::ParseIntError> {
    text.trim().parse()
}

fn main() {
    let port = parse_port("8080").expect("valid port");
    println!("{port}");
}
```

## Worked example
Run `cargo check` at boundaries where the compiler can give useful design
feedback:

```rust
fn normalize_name(input: &str) -> String {
    input.trim().to_lowercase()
}

fn greeting(name: &str) -> String {
    format!("Hello, {}!", normalize_name(name))
}

fn main() {
    println!("{}", greeting("  Rust  "));
}
```

After adding `normalize_name`, `cargo check` confirms the ownership boundary:
the function borrows input and returns an owned `String`. After wiring it into
`greeting`, another check confirms the caller still has a valid borrow-only API.

For workspaces or large packages, narrow the target:

```text
$ cargo check --lib
$ cargo check --tests
$ cargo check -p my_crate
```

This keeps fast feedback while still using Cargo's real package model.

## Common errors
Move and borrow diagnostics are exactly the kind of feedback to get early:

```text
error[E0382]: borrow of moved value
```

Fix the ownership boundary while the change is small: borrow the value, return
ownership, or clone deliberately when independent ownership is required.

Unresolved imports often mean either a typo or a missing dependency:

```text
error[E0432]: unresolved import `regex`
```

Check the module path first, then add the crate through
[[crates.io and Dependencies Intro]] if it is truly external.

Remember that success can still be followed by a linker error during build:

```text
error: linking with `cc` failed
```

Install platform build tools or native libraries; `cargo check` intentionally
did not perform that final stage.

## Best practice
- ✅ Run `cargo check` frequently during design and refactoring, before errors
  stack up into a confusing batch.
- ✅ Follow a clean `cargo check` with `cargo test` for behavior and `cargo run`
  when the binary's runtime behavior matters.
- ✅ Use compiler messages as design feedback; Rust errors often point to better
  ownership, borrowing, or type boundaries.
- ✅ Pair it with [[rustfmt and Clippy]] before review.
- ✅ Run it after changing function signatures, trait bounds, module paths, or
  dependency features.
- ✅ Use package and target selectors in workspaces instead of waiting for every
  member when you are focused on one crate.
- ✅ Follow a warning-free check with tests for behavior; type-correct code can
  still implement the wrong rule.

## Pitfalls
- ⚠️ Shipping after only `cargo check`; no executable was produced and no tests
  were run.
- ⚠️ Letting warnings pile up because the command "passed"; warnings are part of
  the feedback loop and often connect to [[Lints and Lint Levels]].
- ⚠️ Using check speed as an excuse to avoid small tests for parsing or core
  logic; see [[Keep Application Logic Testable]].
- ⚠️ Assuming `cargo check` exercises all optional features; pass `--features`,
  `--all-features`, or target flags when the changed code is behind them.
- ⚠️ Ignoring code generation and linking differences for FFI, build scripts, or
  native dependencies.

## See also
[[Cargo Build Run Check Test]] · [[Cargo Basics]] · [[rustfmt and Clippy]] · [[Borrowing]] · [[The rustc Compiler]] · [[Lints and Lint Levels]] · [[Ownership]] · [[crates.io and Dependencies Intro]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 1.3 "Building and Running a Cargo Project" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-03-hello-cargo.html
- Cargo command docs, `cargo check` — https://doc.rust-lang.org/cargo/commands/cargo-check.html
