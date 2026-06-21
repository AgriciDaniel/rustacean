---
type: concept
title: "rustup and Installation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustup, installation, tooling]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[The rustc Compiler]]", "[[Rust Editions]]", "[[rustfmt and Clippy]]", "[[Tooling & Getting Started]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch01-01-installation.html", "https://doc.rust-lang.org/book/appendix-04-useful-development-tools.html"]
rust_version: "edition 2024 / 1.85+"
---

# rustup and Installation

`rustup` is the standard installer and toolchain manager for Rust: it installs `rustc`, Cargo, standard tools, documentation, and lets you update or remove them from one command-line entry point.

## What it is
Rust development normally starts by installing the stable toolchain through `rustup`.
The toolchain includes the compiler (`rustc`), the package manager and build tool
(`cargo`), local standard-library documentation, and bundled developer tools such
as `rustfmt` and Clippy.

`rustup` is not the compiler itself. It manages compiler versions and components.
The compiler still lives behind `rustc`, and most project work goes through Cargo.
For a beginner, the important test is simple: `rustc --version` and
`cargo --version` should both print versions from the expected stable toolchain.

## How it works
On Unix-like systems, the Book installs Rust by piping the official `rustup`
install script into a shell. On Windows, the supported path is the official Rust
installer page, with Visual Studio build tools when the MSVC toolchain needs a
linker and native libraries.

Rust programs are ahead-of-time compiled, so your machine also needs a linker.
Many systems already have one. If linking fails, install the platform C build
tools: Xcode command-line tools on macOS, GCC or Clang packages on Linux, and the
Visual Studio tools on Windows.

`rustup update` moves installed toolchains forward. `rustup self uninstall`
removes Rust and `rustup`. `rustup doc` opens the local documentation, which is
especially useful for looking up standard-library APIs while offline.

`rustup` also owns *components* and *targets*. Components are tools such as
`rustfmt`, Clippy, and source documentation. Targets are compilation platforms
such as the host platform or a cross-compilation target. Beginners usually stay
on the default stable host toolchain, but knowing the distinction prevents
confusing "component missing" errors with Rust language errors.

The active toolchain is selected by the command context. A project can pin one
with a `rust-toolchain.toml` file, a shell can override one with `rustup
override`, and a one-off command can use `cargo +stable test` or `rustc +stable
--version`. When versions disagree between an editor and terminal, ask `rustup
show` which toolchain is active before changing code.

## Example
```rust
fn main() {
    let rustc_ok = "rustc --version prints the installed compiler";
    let cargo_ok = "cargo --version prints the installed build tool";

    println!("{rustc_ok}");
    println!("{cargo_ok}");
}
```

## Worked example
After installation, verify the complete beginner toolchain from a shell:

```text
$ rustup show
$ rustc --version
$ cargo --version
$ rustup component list --installed
$ cargo new smoke_test
$ cd smoke_test
$ cargo run
```

This checks toolchain selection, compiler availability, Cargo availability,
installed components, project creation, compilation, linking, and execution.
If `cargo run` reaches "Hello, world!", the installer, PATH, linker, and default
project layout are all working together.

For offline learning, prefetch tutorial dependencies before disconnecting:

```text
$ cargo new get-dependencies
$ cd get-dependencies
$ cargo add rand@0.8.5 trpl@0.2.0
```

The Book suggests this so later `cargo` commands can use cached dependencies
with `--offline`.

## Common errors
If the shell cannot find Rust, the issue is usually PATH configuration:

```text
rustc: command not found
```

Open a new terminal after installation, confirm the shell startup file sources
Cargo's environment, or inspect `PATH`. Do not debug Rust source code until
`rustc --version` and `cargo --version` work in the same terminal your editor
or CI uses.

Linker failures usually appear after compilation begins:

```text
error: linker `cc` not found
```

Install platform build tools: Xcode command-line tools on macOS, GCC or Clang
packages on Linux, or Visual Studio build tools for the Windows MSVC toolchain.
Crates with native dependencies may need those tools even when your own code is
pure Rust.

Missing tool components show up as Cargo subcommand failures:

```text
error: no such command: `clippy`
```

Install or repair the component with `rustup component add clippy rustfmt`, then
rerun the Cargo command.

## Best practice
- ✅ Install through `rustup` unless your operating system, company image, or CI
  environment has a deliberate toolchain-management policy.
- ✅ Verify both `rustc --version` and `cargo --version` after installation; most
  real projects use [[Cargo Basics]], not raw compiler invocations.
- ✅ Use `rustup doc` when you need local API documentation, especially for
  `std` types encountered in [[The Guessing Game Tutorial]].
- ✅ Install the platform linker early if build failures mention linking, native
  libraries, `cc`, `link.exe`, GCC, Clang, or Visual Studio tools.
- ✅ Use `rustup show` when debugging mismatched versions between terminal,
  editor, and CI; it reports the active toolchain and installed targets.
- ✅ Prefer stable for learning and production unless a dependency or experiment
  explicitly requires nightly; edition 2024 is stable on Rust 1.85+.

## Pitfalls
- ⚠️ Installing only `rustc` and then expecting dependency management, project
  layout, tests, and formatting to work automatically; those workflows come
  through [[Cargo Basics]] and [[rustfmt and Clippy]].
- ⚠️ Treating PATH problems as Rust syntax problems. If `rustc --version` fails,
  fix shell configuration before debugging source code.
- ⚠️ Mixing unrelated Rust installations without knowing which one your editor,
  terminal, and CI are using; that can look like an [[MSRV Policy]] or
  [[Rust Editions]] problem.
- ⚠️ Treating a linker or native-library error as a borrow-checker problem.
  Cargo invokes the platform linker after compiling Rust code.
- ⚠️ Pinning an old project toolchain and then assuming Book examples are wrong;
  check `rust-toolchain.toml` and [[Edition 2024]] before changing examples.

## See also
[[Cargo Basics]] · [[The rustc Compiler]] · [[Rust Editions]] · [[Edition 2024]] · [[rustfmt and Clippy]] · [[Cargo Build Run Check Test]] · [[The Guessing Game Tutorial]] · [[MSRV Policy]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 1.1 "Installation" — [[the-book]],
  https://doc.rust-lang.org/book/ch01-01-installation.html
- The Rust Programming Language, Appendix D "Useful Development Tools" — [[the-book]],
  https://doc.rust-lang.org/book/appendix-04-useful-development-tools.html
