---
type: concept
title: "Packages and Crates"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, packages, crates, cargo]
domain: "Modules & Project Structure"
difficulty: basic
related: ["[[Crate Roots]]", "[[Modules]]", "[[Cargo.toml Manifest]]", "[[Cargo Workspaces]]", "[[Library and Binary Package Layout]]", "[[Workspace Project Structure]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html", "https://doc.rust-lang.org/reference/crates-and-source-files.html"]
rust_version: "edition 2024 / 1.85+"
---

# Packages and Crates

A crate is the compiler's unit of compilation; a package is the Cargo unit that contains one or more crates described by a `Cargo.toml`.

## What it is
A _crate_ is the smallest body of Rust code that `rustc` compiles at one time.
It can be a binary crate, which produces an executable and has `fn main`, or a
library crate, which exposes reusable functionality and has no `main`.

A _package_ is a Cargo bundle with a `Cargo.toml`. It can contain many binary
crates and at most one library crate. The package is the distribution and build
unit; the crate is the compilation and module-tree unit.

This distinction matters because [[Modules]] organize code inside a crate,
while [[Cargo.toml Manifest]] and [[Cargo Workspaces]] organize packages and
dependencies around crates.

## How it works
Cargo uses file conventions to discover crate roots. `src/main.rs` is the root
of a binary crate with the package name. `src/lib.rs` is the root of a library
crate with the package name. Files in `src/bin/*.rs` are additional binary
crate roots.

If a package has both `src/lib.rs` and `src/main.rs`, it contains a library
crate and a binary crate. They are separate crates, even though they live in
one package and usually share a name. The binary should call the library
through the library's public API, just as an external crate would.

`rustc` receives one crate root at a time. Additional source files are loaded
only because [[Crate Roots]] declare [[Modules]] with `mod`.

## Example
```rust
mod math {
    pub fn double(n: i32) -> i32 {
        n * 2
    }
}

fn main() {
    let answer = math::double(21);
    assert_eq!(answer, 42);
}
```

This single file can be a binary crate root. In a Cargo package, it would
usually live at `src/main.rs`.

## Worked example
For a package named `weather-cli`, this layout gives Cargo three crate roots:

```text
weather-cli/
├── Cargo.toml
└── src
    ├── lib.rs
    ├── main.rs
    └── bin
        └── import.rs
```

`src/lib.rs` is the library crate. `src/main.rs` is the default binary crate.
`src/bin/import.rs` is another binary crate. The binaries should call the
library through the package's library crate name, which Cargo exposes with
hyphens converted to underscores:

```rust
// In src/main.rs of package `weather-cli`.
use weather_cli::Forecast;

fn main() {
    let forecast = Forecast::new("clear");
    assert_eq!(forecast.summary(), "clear");
}
```

That import is not a module declaration. It is a dependency edge from one crate
in the package to the package's library crate.

## Common errors
Confusing a library crate with a module often produces duplicate definitions or
unresolved paths. This is the wrong shape in `src/main.rs`:

```rust
mod lib; // Do not load src/lib.rs as a child module of the binary.
```

Typical diagnostic:

```console
warning: found module declaration for lib.rs
  = note: lib.rs is the root of this crate's library target
  = help: to refer to it from other targets, use the library's name as the path
```

Fix it by removing `mod lib;` and importing the library crate by name, for
example `use weather_cli::Forecast;`.

## Deeper mechanics
Cargo package discovery is convention plus manifest configuration. By default,
Cargo infers `src/lib.rs`, `src/main.rs`, and `src/bin/*.rs`, but explicit
`[lib]` and `[[bin]]` sections in [[Cargo.toml Manifest]] can override names
or paths. After target discovery, Cargo invokes `rustc` separately for each
crate root, passing dependency metadata so one crate can link to another.

Because each crate is compiled as its own unit, `pub(crate)` means "visible
within this crate," not "visible anywhere in this package." A binary crate in
the same package cannot access the library crate's `pub(crate)` items. That is
why [[Library and Binary Package Layout]] is a useful API-design pressure.

## Best practice
- ✅ Treat the library crate as the reusable core of a package; keep the binary crate thin.
- ✅ Put additional command-line entry points in `src/bin/` instead of branching one large `main`.
- ✅ Use package boundaries when code needs separate dependency metadata, versioning, or publication.
- ✅ Use [[Workspace Project Structure]] when multiple packages evolve together.
- ✅ Name the package for publication and the library crate for Rust paths; remember `my-tool` becomes `my_tool`.
- ✅ Keep integration tests, examples, and binaries pointed at the library API so they test the same surface users get.
- ✅ Reach for explicit `[lib]` or `[[bin]]` only when conventions do not describe the intended target layout.

## Pitfalls
- ⚠️ Assuming one package means one crate; a package can contain a library plus many binaries.
- ⚠️ Putting reusable logic only in `src/main.rs`; that prevents tests, examples, and other crates from using it cleanly.
- ⚠️ Confusing [[Modules]] with crates; modules are inside a crate, not independently compiled packages.
- ⚠️ Splitting into packages before a real boundary exists; module boundaries are cheaper than package boundaries.
- ⚠️ Expecting `pub(crate)` in the library to be callable from the package's binary; the binary is a different crate.
- ⚠️ Treating the package name, crate name, and module name as interchangeable; they participate in different systems.
- ⚠️ Adding a workspace when one package with multiple targets would keep dependency and API management simpler.

## See also
[[Crate Roots]] · [[Modules]] · [[Splitting Modules into Files]] · [[Visibility and Privacy]] · [[The use Keyword]] · [[Module Paths]] · [[Library and Binary Package Layout]] · [[Workspace Project Structure]] · [[Cargo Workspaces]] · [[Cargo.toml Manifest]] · [[Dependencies and Version Requirements]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Packages and Crates" — [[the-book]], https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html
- The Rust Reference, "Crates and source files" — [[the-reference]], https://doc.rust-lang.org/reference/crates-and-source-files.html
