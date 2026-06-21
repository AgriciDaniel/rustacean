---
type: pattern
title: "Start Projects with cargo new"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, project-structure, getting-started]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[Anatomy of a Cargo Project]]", "[[Cargo.toml Manifest]]", "[[Packages and Crates]]", "[[rustup and Installation]]", "[[Using rustc Directly for Cargo-Sized Projects]]"]
sources: ["[[the-book]]", "[[command-line-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch01-03-hello-cargo.html", "https://doc.rust-lang.org/cargo/commands/cargo-new.html", "https://doc.rust-lang.org/cargo/commands/cargo-init.html"]
rust_version: "edition 2024 / 1.85+"
---

# Start Projects with cargo new

Start real Rust packages with `cargo new` or convert an existing directory with `cargo init` so the project gets Cargo's manifest, source layout, target discovery, and version-control defaults from the beginning.

## What it is
This pattern says: reach for Cargo before the project grows. `cargo new name`
creates a new package directory. `cargo init` adds Cargo metadata to an existing
directory. Both save beginners from inventing a layout that later fights the
standard tools.

The Book uses raw `rustc main.rs` only for the first "Hello, world!" lesson.
Immediately afterward, it moves to Cargo because Cargo is the workflow used by
normal Rust projects.

## How it works
For a binary application, `cargo new hello_cargo` creates `Cargo.toml` and
`src/main.rs`. Cargo may also initialize version-control files unless it detects
an existing repository or you choose a different `--vcs` option.

After creation, `cargo run` from the package directory should build and execute
the generated "Hello, world!" program. That quick run validates installation,
project layout, the compiler, and Cargo's ability to create artifacts under
`target/`.

`cargo new` creates a new directory; `cargo init` turns the current directory
into a package. Both write a manifest with the current default edition, create
the conventional source root, and may initialize version-control ignore rules.
The generated structure is intentionally boring because every Rust tool,
editor, CI template, and teammate knows how to navigate it.

For libraries, use `cargo new --lib name` or `cargo init --lib`. A library
package starts with `src/lib.rs` instead of `src/main.rs`, and later binary
targets can still be added under `src/bin/` when needed.

## Example
```rust
fn main() {
    println!("This file belongs in src/main.rs of a Cargo package.");
}
```

## Worked example
Create, inspect, run, and then grow a beginner package:

```text
$ cargo new hello_cargo
$ cd hello_cargo
$ cargo run
$ cargo test
```

The generated manifest starts like this on edition 2024 toolchains:

```toml
[package]
name = "hello_cargo"
version = "0.1.0"
edition = "2024"

[dependencies]
```

If you already created a directory with a README or prototype file, use:

```text
$ cd existing-project
$ cargo init
```

Then move Rust source into `src/` and let Cargo own builds under `target/`.

## Common errors
Running `cargo new` inside a directory that already exists as the target path
can fail:

```text
error: destination already exists
```

Use `cargo init` inside the existing directory, or choose a new package path.

Invalid package names are rejected before a manifest is generated:

```text
error: invalid character `.` in package name
```

Pick a Cargo package name that is also a reasonable Rust identifier for the
default crate target. Hyphens are allowed in package names, but the library
crate name is used with underscores in Rust paths.

If the generated binary cannot link, the project was created correctly but the
platform toolchain is incomplete; revisit [[rustup and Installation]].

## Best practice
- ✅ Use `cargo new app_name` for new packages and `cargo init` when you already
  have a directory.
- ✅ Keep source under `src/` and let Cargo generate the initial manifest before
  adding dependencies.
- ✅ Use `cargo new --help` when you need a library package, a specific VCS
  setting, or another generated shape.
- ✅ Run `cargo run` immediately after creation to prove the toolchain and
  project structure work.
- ✅ Choose names that can age into crate names, binary names, and import paths
  without awkward punctuation.
- ✅ Commit the generated `Cargo.toml` and source layout before large edits when
  starting a serious project; it gives future diffs a clean baseline.
- ✅ Use `--lib` when the primary artifact is reusable logic, even if a small
  binary will be added later.

## Pitfalls
- ⚠️ Building a multi-file or dependency-using project around direct `rustc`
  commands; see [[Using rustc Directly for Cargo-Sized Projects]].
- ⚠️ Creating source files in the package root and wondering why Cargo does not
  discover them; Cargo expects source under [[Anatomy of a Cargo Project]].
- ⚠️ Hand-writing a manifest before understanding [[Cargo.toml Manifest]]; the
  generated file is a better starting point.
- ⚠️ Running `cargo new` repeatedly inside nested directories and accidentally
  creating multiple unrelated packages instead of one workspace.
- ⚠️ Treating the generated "Hello, world!" as disposable noise before running
  it; that first run validates the whole toolchain.

## See also
[[Cargo Basics]] · [[Anatomy of a Cargo Project]] · [[Cargo.toml Manifest]] · [[Packages and Crates]] · [[Crate Roots]] · [[Library and Binary Package Layout]] · [[Cargo Build Run Check Test]] · [[rustup and Installation]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 1.3 "Creating a Project with Cargo" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-03-hello-cargo.html
- Cargo command docs, `cargo new` — https://doc.rust-lang.org/cargo/commands/cargo-new.html
