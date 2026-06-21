---
type: antipattern
title: "Using rustc Directly for Cargo-Sized Projects"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustc, cargo, antipattern, tooling]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[Start Projects with cargo new]]", "[[Anatomy of a Cargo Project]]", "[[Cargo.toml Manifest]]", "[[Packages and Crates]]", "[[The rustc Compiler]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch01-02-hello-world.html", "https://doc.rust-lang.org/book/ch01-03-hello-cargo.html", "https://doc.rust-lang.org/cargo/"]
rust_version: "edition 2024 / 1.85+"
---

# Using rustc Directly for Cargo-Sized Projects

Using `rustc main.rs` is fine for the first single-file lesson, but it becomes a footgun once a project needs dependencies, multiple targets, tests, build profiles, or reproducible dependency resolution.

## The mistake
A beginner learns that `rustc main.rs` creates an executable, then keeps scaling
that command by hand: extra files, manual paths, custom shell scripts, copied
compiler flags, and improvised output locations. The project slowly recreates a
weaker version of Cargo.

The Book deliberately uses raw `rustc` only for the initial "Hello, world!"
program. The next section introduces Cargo because real projects need a package
model, manifest, dependency resolution, build cache, and conventional commands.

## Why it happens
Direct compiler invocation feels transparent. For one file with no dependencies,
it is transparent. The problem appears when the project needs `Cargo.toml`,
external crates, tests, release builds, examples, documentation, or standard
layout. At that point, Cargo is not extra complexity; it is the shared interface
to the Rust ecosystem.

Cargo still uses the compiler. Moving to Cargo does not hide Rust; it lets Cargo
coordinate all the inputs that a growing package needs.

The direct `rustc` command does not read `Cargo.toml`, resolve crates from
crates.io, apply Cargo profiles, build dependencies first, discover tests, set
feature flags, run build scripts, or maintain `Cargo.lock`. You can pass many of
those flags by hand, but at that point the command line has become a fragile,
local-only build system.

This antipattern is especially costly for beginners because errors become
misleading. `use rand::Rng;` fails under raw `rustc` even when the dependency is
correctly listed in `Cargo.toml`, because Cargo is the tool that resolves and
passes external crate metadata to the compiler.

## Example
```rust
fn main() {
    println!("Compile this with Cargo once it is part of a package.");
}
```

## Worked example
This is fine for the Book's first isolated file:

```text
$ rustc main.rs
$ ./main
```

But this is the right shape once the code needs a dependency, tests, or more
than one file:

```text
$ cargo new guessing_game
$ cd guessing_game
$ cargo add rand@0.8.5
$ cargo run
$ cargo test
```

Cargo still invokes `rustc`, but it also builds `rand`, passes dependency
metadata, selects the edition from the manifest, writes artifacts under
`target/`, and records exact versions in `Cargo.lock`.

## Common errors
Using an external crate with raw `rustc` commonly fails like this:

```text
error[E0432]: unresolved import `rand`
```

If the code is part of a Cargo package, run `cargo run`, `cargo build`, or
`cargo test` instead of manually invoking `rustc`.

Multi-file projects often hit module path confusion:

```text
error[E0583]: file not found for module `parser`
```

Fix the module declaration/layout, then let Cargo compile from the crate root.
Do not compile arbitrary leaf files directly; they are usually not crate roots.

Hand-built release commands also miss Cargo's profile settings:

```text
$ rustc -O src/main.rs
```

Use `cargo build --release` so optimization, dependencies, features, and target
layout are consistent.

## Best practice
- ✅ Use `rustc file.rs` for tiny isolated experiments and for understanding the
  compile/run distinction.
- ✅ Use [[Start Projects with cargo new]] when the code is becoming a package,
  application, library, or tutorial project.
- ✅ Put dependencies in [[Cargo.toml Manifest]] and let Cargo resolve, build,
  and lock them.
- ✅ Use [[Cargo Build Run Check Test]] instead of maintaining hand-written
  command sequences for ordinary development.
- ✅ Keep raw `rustc` knowledge for debugging compiler behavior, custom build
  systems, and tiny throwaway files; switch to Cargo as soon as package metadata
  matters.
- ✅ Use `cargo rustc` only when you deliberately need to pass extra flags
  through Cargo's package model.
- ✅ Prefer `cargo script`-style tooling or examples only when the project truly
  remains a single-file experiment.

## Pitfalls
- ⚠️ Forgetting transitive dependency setup because raw `rustc` does not read
  `[dependencies]`.
- ⚠️ Producing binaries beside source files and then confusing generated output
  with source state; Cargo writes artifacts under `target/`.
- ⚠️ Hand-rolling testing and release flags instead of using `cargo test` and
  `cargo build --release`.
- ⚠️ Compiling `src/foo.rs` directly when it is a module, not a crate root.
- ⚠️ Losing reproducibility because no lockfile records the resolved dependency
  graph.
- ⚠️ Teaching teammates a private shell incantation instead of the standard
  Cargo commands every Rust project expects.

## See also
[[Cargo Basics]] · [[Start Projects with cargo new]] · [[Anatomy of a Cargo Project]] · [[Cargo.toml Manifest]] · [[Packages and Crates]] · [[The rustc Compiler]] · [[Cargo Build Run Check Test]] · [[crates.io and Dependencies Intro]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 1.2 "Hello, World!" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-02-hello-world.html
- The Rust Programming Language, ch. 1.3 "Hello, Cargo!" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-03-hello-cargo.html
