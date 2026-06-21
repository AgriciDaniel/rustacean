---
type: concept
title: "Crate Roots"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, crates, modules, crate-root]
domain: "Modules & Project Structure"
difficulty: basic
related: ["[[Packages and Crates]]", "[[Modules]]", "[[Module Paths]]", "[[Splitting Modules into Files]]", "[[Library and Binary Package Layout]]", "[[Visibility and Privacy]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html", "https://doc.rust-lang.org/reference/crates-and-source-files.html"]
rust_version: "edition 2024 / 1.85+"
---

# Crate Roots

A crate root is the source file where compilation starts and whose contents form the root module of that crate.

## What it is
Every crate has one root source file. For Cargo's conventional layout, that is
`src/lib.rs` for a library crate, `src/main.rs` for the default binary crate,
and each file under `src/bin/` for an additional binary crate.

The crate root creates the unnamed top-level module that Rust paths call
`crate`. All named modules, functions, structs, enums, traits, constants, and
imports are items in that root module or in descendants of it.

## How it works
When compiling a crate, Rust starts at the root file and reads its items.
A declaration such as `mod config;` tells the compiler to load another module
file into a specific place in the module tree. That loaded file does not choose
its own path; its path is determined by the `mod` declaration that loaded it.

Because crate roots are also modules, they are where public API design usually
begins. A library often keeps implementation modules private and exposes a
curated root API with `pub` items or [[Re-exporting with pub use]].

In a package with both a library and a binary, the binary crate root should
import the library by package name. That makes the binary a real client of the
library's public API.

## Example
```rust
mod config {
    pub const DEFAULT_PORT: u16 = 8080;
}

pub fn endpoint(host: &str) -> String {
    format!("{host}:{}", config::DEFAULT_PORT)
}

fn main() {
    assert_eq!(endpoint("127.0.0.1"), "127.0.0.1:8080");
}
```

This file is a crate root. The `config` module is a child of `crate`.

## Worked example
In a package with both `src/lib.rs` and `src/main.rs`, the two roots create two
separate module trees:

```rust
// src/lib.rs
mod parser {
    pub fn parse(input: &str) -> usize {
        input.len()
    }
}

pub use parser::parse;
```

```rust
// src/main.rs in package `text-tool`
fn main() {
    assert_eq!(text_tool::parse("rust"), 4);
}
```

The binary root does not see `parser` as a sibling module. It sees the library
crate only through the public path `text_tool::parse`.

## Common errors
When a root declares `mod config;`, the compiler searches relative to that
root's module location. If no matching file exists, the error is usually:

```console
error[E0583]: file not found for module `config`
  = help: to create the module `config`, create file "src/config.rs" or "src/config/mod.rs"
```

The fix is not to add `use config;`. Create the file at the searched location
or make the module inline with `mod config { ... }`.

## Deeper mechanics
`rustc` receives exactly one input source file for a crate. That file's items
become the anonymous root module addressed by `crate::`. Out-of-line child
modules are discovered only as the parser and name resolver encounter `mod`
items in that root or in descendants.

Crate-level inner attributes, such as `#![allow(...)]`, belong at the beginning
of the root source file. Inner module documentation with `//!` also documents
the containing module; in `src/lib.rs`, that means the crate-level rustdoc
front page.

## Best practice
- ✅ Keep crate roots readable: declare major modules, expose the public API, and avoid dumping all implementation code there.
- ✅ In libraries, use the crate root as the public front door for the crate.
- ✅ Use `crate::` paths from implementation code when the referenced item should remain stable if the caller module moves.
- ✅ Put `mod` declarations in the parent module that owns the child in the module tree.
- ✅ Put crate-level docs and lint configuration at the root so rustdoc and compiler settings have one obvious home.
- ✅ Keep binaries as clients of the library root; that catches accidental reliance on private implementation modules.
- ✅ Use root-level `pub use` for stable public names and private `mod` declarations for internal structure.

## Pitfalls
- ⚠️ Thinking a module file is compiled independently; Rust compiles crates, not loose module files.
- ⚠️ Declaring the same module from multiple places; one `mod` declaration should load a module into the tree once.
- ⚠️ Exposing internal folders as public modules just because they exist on disk; see [[Re-exporting with pub use]].
- ⚠️ Letting a binary crate become the only owner of reusable logic; see [[Library and Binary Package Layout]].
- ⚠️ Expecting a `use` in the crate root to be automatically available inside every child module.
- ⚠️ Moving a file without updating the parent `mod` declaration that gives the module its logical path.
- ⚠️ Treating `src/lib.rs` as a module named `lib`; it is the library crate root, not `crate::lib`.

## See also
[[Packages and Crates]] · [[Modules]] · [[Module Paths]] · [[The use Keyword]] · [[Splitting Modules into Files]] · [[Visibility and Privacy]] · [[Re-exporting with pub use]] · [[Library and Binary Package Layout]] · [[Treating mod as include]] · [[Cargo Workspaces]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Packages and Crates" — [[the-book]], https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html
- The Rust Reference, "Crates and source files" — [[the-reference]], https://doc.rust-lang.org/reference/crates-and-source-files.html
