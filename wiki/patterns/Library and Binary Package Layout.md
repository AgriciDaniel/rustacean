---
type: pattern
title: "Library and Binary Package Layout"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, binary-crate, library-crate, package-layout]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[Packages and Crates]]", "[[Crate Roots]]", "[[Modules]]", "[[Visibility and Privacy]]", "[[The use Keyword]]", "[[Cargo.toml Manifest]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#best-practices-for-packages-with-a-binary-and-a-library", "https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html", "https://doc.rust-lang.org/reference/crates-and-source-files.html"]
rust_version: "edition 2024 / 1.85+"
---

# Library and Binary Package Layout

Put reusable behavior in `src/lib.rs` and keep `src/main.rs` as a thin executable entry point.

## What it is
A package can contain both a library crate and one or more binary crates. The
library crate is the reusable core. The binary crate parses process-level
inputs, calls the library, and handles process-level outputs.

This layout makes the binary a client of the library. That pressure improves
API design because the binary can only use what the library publicly exposes.

## How it works
With Cargo conventions, `src/lib.rs` is the library crate root and `src/main.rs`
is the default binary crate root. Both usually share the package name, but they
are compiled as separate crates.

Inside `src/main.rs`, import the library by the package crate name, not with
`mod lib;`. Additional binaries under `src/bin/` should do the same. Shared
logic stays in the library, so tests and future binaries do not duplicate it.

The library uses [[Modules]], [[Visibility and Privacy]], and
[[Re-exporting with pub use]] to expose a small API. The binary should not
depend on private implementation modules.

## Example
```rust
mod app {
    pub fn greeting(name: &str) -> String {
        format!("hello, {name}")
    }
}

fn main() {
    let message = app::greeting("Rust");
    assert_eq!(message, "hello, Rust");
}
```

In a real package, `app::greeting` would live in `src/lib.rs`, and `main` would
call it through the library crate name.

## Worked example
A practical command-line package usually has this split:

```rust
// src/lib.rs
pub struct Config {
    pub name: String,
}

pub fn run(config: Config) -> String {
    format!("hello, {}", config.name)
}
```

```rust
// src/main.rs in package `hello-tool`
use hello_tool::{run, Config};

fn main() {
    let name = std::env::args().nth(1).unwrap_or_else(|| String::from("Rust"));
    println!("{}", run(Config { name }));
}
```

The binary owns process concerns: arguments, stdout, exit behavior. The library
owns reusable behavior and can be tested without spawning the executable.

## Common errors
The common mistake is loading the library root as a module:

```rust
// src/main.rs
mod lib;
```

Typical diagnostic:

```console
warning: found module declaration for lib.rs
  = help: to refer to it from other targets, use the library's name as the path
```

Fix it by deleting `mod lib;` and importing the package library crate by name,
for example `use hello_tool::run;`.

## Deeper mechanics
Cargo passes `src/lib.rs` and `src/main.rs` to `rustc` as different crate
roots. The binary crate links the library crate the same way an integration
test, example, or external dependent would. That means privacy is real:
`pub(crate)` in the library is not visible to the binary crate.

This separation is a useful design constraint. If `main` cannot express its
work through the library's public API, the API probably needs a better
function, type, or error boundary. The answer is usually not to make internal
modules public; it is to add a deliberate facade.

## Best practice
- ✅ Keep `main` focused on argument parsing, environment setup, logging, exit codes, and calling library code.
- ✅ Put business logic, parsing logic, and reusable types in the library crate.
- ✅ Test the library directly; use binary tests only for command behavior.
- ✅ Use `src/bin/*.rs` for multiple executables that share one library.
- ✅ Return data or rich errors from the library; translate them to process exit codes and messages in the binary.
- ✅ Let examples and integration tests use the same library API as the binary.
- ✅ Use feature flags or separate binaries for alternate frontends only after the library boundary is clear.

## Pitfalls
- ⚠️ Declaring `mod lib;` from `main.rs`; that treats library code as a child module of the binary, not as the package library crate.
- ⚠️ Hiding all logic inside `main`, which makes reuse and unit testing awkward.
- ⚠️ Letting the binary reach into private modules instead of calling the library's public API.
- ⚠️ Splitting into a workspace before one package with library plus binaries has stopped fitting.
- ⚠️ Printing or exiting deep inside library functions, which makes tests and alternate binaries harder to write.
- ⚠️ Assuming same-package binaries can use library internals; they are separate crates.
- ⚠️ Copying shared logic into each `src/bin/*.rs` file instead of keeping it in `src/lib.rs`.

## See also
[[Packages and Crates]] · [[Crate Roots]] · [[Modules]] · [[Visibility and Privacy]] · [[The use Keyword]] · [[Re-exporting with pub use]] · [[Workspace Project Structure]] · [[Cargo.toml Manifest]] · [[Module Paths]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Best Practices for Packages with a Binary and a Library" — [[the-book]], https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#best-practices-for-packages-with-a-binary-and-a-library
- The Rust Programming Language, "Packages and Crates" — [[the-book]], https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html
- The Rust Reference, "Crates and source files" — [[the-reference]], https://doc.rust-lang.org/reference/crates-and-source-files.html
