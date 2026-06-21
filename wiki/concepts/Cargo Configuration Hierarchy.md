---
type: concept
title: "Cargo Configuration Hierarchy"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, configuration, config, environment]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo Source Overrides]]", "[[Cargo Workspaces]]", "[[Cargo.toml Manifest]]", "[[Cargo.lock]]", "[[Profiles and Optimization Settings]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/config.html", "https://doc.rust-lang.org/cargo/reference/environment-variables.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo Configuration Hierarchy

Cargo configuration is layered from discovered `.cargo/config.toml` files, environment variables, and `--config` command-line overrides, with more specific or later sources taking precedence according to Cargo's merge rules.

## What it is
Cargo configuration is separate from the package manifest.
`Cargo.toml` describes the package and workspace.
`.cargo/config.toml` describes how Cargo should run: target directories, source replacement, registries, aliases, runners, linkers, network behavior, profile overrides, and similar operational settings.
Cargo supports both local project configuration and user-wide configuration.
This is why the hierarchy matters.
The same key can be present in a checked-in workspace config, a user's `$CARGO_HOME/config.toml`, an environment variable, and a one-shot `--config` flag.
Reviewing a build problem often means asking which layer actually supplied the value.

## How it works
When invoked in a directory, Cargo searches that directory and its parents for `.cargo/config.toml`.
For a command run in `/projects/foo/bar/baz`, Cargo probes:

```text
/projects/foo/bar/baz/.cargo/config.toml
/projects/foo/bar/.cargo/config.toml
/projects/foo/.cargo/config.toml
/projects/.cargo/config.toml
/.cargo/config.toml
$CARGO_HOME/config.toml
```

`$CARGO_HOME/config.toml` is the lowest-priority file.
On Unix it defaults to `$HOME/.cargo/config.toml`.
On Windows it defaults to `%USERPROFILE%\.cargo\config.toml`.
If a scalar key is specified in multiple discovered config files, the deeper project directory wins over ancestors and home config.
Arrays are joined, with higher-precedence items later in the merged array.
This can be surprising for flags, because the final command line may contain values from more than one config file.

When Cargo is invoked from a workspace root, it does not read `.cargo/config.toml` files inside individual member crates.
Put workspace-wide config at the workspace root in `.cargo/config.toml`.
Put personal defaults in `$CARGO_HOME/config.toml`.

Environment variables can set many config keys.
The key `net.git-fetch-with-cli` maps to `CARGO_NET_GIT_FETCH_WITH_CLI`.
Dashes and dots become underscores, and the name is uppercased.
Environment variables take precedence over TOML config files.

The `--config` option takes either a TOML `KEY=VALUE` snippet or a path to an extra config file.
Multiple `--config` options merge left to right.
Values from `--config` take precedence over environment variables and discovered files.

```console
cargo --config net.git-fetch-with-cli=true fetch
cargo --config 'build.rustflags = ["-Dwarnings"]' check
cargo --config .cargo/ci.toml test
```

Cargo also supports `include` in config files.
Included files are loaded first, left to right, then the including file's own values are merged on top.
Paths in config files are usually relative to the parent of the `.cargo` directory that contains the config file.
For example, in `/my/project/.cargo/config.toml`, `directory = "vendor"` resolves to `/my/project/vendor`.

## Example
```rust
use std::env;

fn cargo_target_dir() -> Option<String> {
    env::var("CARGO_TARGET_DIR").ok()
}

fn main() {
    match cargo_target_dir() {
        Some(path) => println!("Cargo target dir override: {path}"),
        None => println!("Cargo will use its configured/default target directory"),
    }
}
```

This program can observe one common environment override, but most Cargo configuration is consumed by Cargo before the crate is compiled.
A crate should not rely on arbitrary Cargo config being visible at runtime.

## Best practice
- ✅ Put reproducible project settings in the workspace root `.cargo/config.toml`.
- ✅ Keep user preferences, credentials, and machine-local paths out of the repository.
- ✅ Prefer `.cargo/config.toml` over legacy `.cargo/config`.
- ✅ Use `--config` for CI experiments and one-shot overrides that should be visible in the command log.
- ✅ Use environment variables for secret tokens in CI rather than committing them.
- ✅ Keep source replacement and registry settings easy to audit because they affect the dependency supply chain.

## Pitfalls
- ⚠️ Expecting member-crate `.cargo/config.toml` files to apply when commands are run from the workspace root.
- ⚠️ Forgetting that environment variables override files and `--config` overrides environment variables.
- ⚠️ Assuming arrays replace earlier arrays; Cargo joins arrays according to precedence.
- ⚠️ Committing personal absolute paths in project config.
- ⚠️ Putting registry tokens in `config.toml`; use credentials or environment mechanisms appropriate to the registry.
- ⚠️ Debugging a build without checking `$CARGO_HOME/config.toml`, especially on machines with long-lived Rust setups.

## See also
[[Cargo & Dependencies]] · [[Cargo Source Overrides]] · [[Cargo Workspaces]] · [[Cargo.toml Manifest]] · [[Cargo.lock]] · [[Profiles and Optimization Settings]] · [[Feature Resolver]] · [[cargo publish, yank and owners]] · [[Minimizing Dependencies]]

## Sources
- The Cargo Book, "Configuration" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/config.html
- The Cargo Book, "Environment Variables" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/environment-variables.html
