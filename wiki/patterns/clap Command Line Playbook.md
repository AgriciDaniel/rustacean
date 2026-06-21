---
type: pattern
title: "clap Command Line Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, clap, cli, arguments, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Command-Line Parsing]]", "[[Derive Macros]]", "[[Application Errors with anyhow]]", "[[Result Returning Tests]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[command-line-book]]", "[[tooling-project-hygiene]]", "docs.rs/clap"]
source_urls: ["https://docs.rs/clap/latest/clap/", "https://docs.rs/clap/latest/clap/_derive/", "https://docs.rs/clap/latest/clap/trait.Parser.html", "https://rust-cli.github.io/book/"]
rust_version: "edition 2024 / 1.85+"
---

# clap Command Line Playbook

Use clap derive for typed command-line interfaces whose help text, validation, defaults, and subcommands live next to the Rust types they populate.

## What it is
`clap` is the primary Rust ecosystem crate for parsing command-line arguments.
It can be used through a builder API or through derive macros.
For most applications, derive is the clearest route: define a struct for options, derive `Parser`, and let clap generate parsing, help, usage, and error messages.
Subcommands map naturally to enums.
Typed fields reduce stringly argument handling and keep validation close to the interface.

## How it works
`#[derive(Parser)]` reads attributes on a struct and its fields.
`#[arg(long)]` defines a long flag.
`#[arg(short)]` defines a short flag.
`#[arg(default_value_t = ...)]` provides typed defaults.
Fields such as `PathBuf`, `usize`, `bool`, `Option<T>`, and `Vec<T>` get common parsing behavior.
An enum with `#[derive(Subcommand)]` models command groups.
Use `try_parse_from` in tests so failures are values, not process exits.
Use `parse` in `main` when invalid arguments should print a message and exit.
Verify the latest clap version and derive feature name on docs.rs before editing dependencies.

## Example
```rust
use std::path::PathBuf;

use clap::Parser;

#[derive(Debug, Parser, PartialEq)]
#[command(name = "pack")]
struct Args {
    #[arg(long, default_value = ".")]
    input: PathBuf,

    #[arg(short, long)]
    verbose: bool,
}

fn main() {
    let args = Args::parse_from(["pack", "--input", "src", "--verbose"]);
    assert_eq!(args.input, PathBuf::from("src"));
    assert!(args.verbose);
}
```

Cargo dependency for this example:
```toml
[dependencies]
clap = { version = "4", features = ["derive"] }
```

## Best practice
- ✅ Prefer derive for small and medium CLIs because the Rust type is the interface contract.
- ✅ Use subcommand enums for distinct operations instead of many unrelated optional flags.
- ✅ Parse into `PathBuf`, numeric types, enums, and domain-specific value parsers rather than raw strings.
- ✅ Test representative parse cases with `try_parse_from`.
- ✅ Keep user-facing names stable; renaming a flag is a CLI breaking change.
- ✅ Use `ArgAction` or typed booleans instead of hand-counting flags.
- ✅ Route application failures through [[Application Errors with anyhow]] or a custom error type.
- ✅ Verify the latest clap version on docs.rs before updating examples or dependency features.

## Pitfalls
- ⚠️ Making every argument optional and validating the real command shape later.
- ⚠️ Calling `parse` inside library code or tests where process exit is surprising.
- ⚠️ Duplicating help text in README snippets instead of testing generated behavior.
- ⚠️ Treating CLI flag names as internal details; users script against them.
- ⚠️ Overusing positional arguments when named flags would be clearer.
- ⚠️ Hiding incompatible modes in ad hoc `if` chains instead of modeling subcommands.
- ⚠️ Pulling clap into a library crate's public API when only the binary needs it.

## See also
[[Ecosystem & Crate Playbooks]] · [[Command-Line Parsing]] · [[Derive Macros]] · [[Application Errors with anyhow]] · [[Result Returning Tests]] · [[Test Organization]] · [[Stringly-Typed Code]] · [[Making Invalid States Unrepresentable]] · [[Feature Flags]] · [[Choosing the Right Rust Crate]]

## Sources
- clap crate docs — https://docs.rs/clap/latest/clap/; verify the latest version before editing `Cargo.toml`.
- clap derive docs — https://docs.rs/clap/latest/clap/_derive/
- clap `Parser` trait docs — https://docs.rs/clap/latest/clap/trait.Parser.html
- Rust command-line book — [[command-line-book]], https://rust-cli.github.io/book/
