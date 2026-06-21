---
type: concept
title: "crates.io and Dependencies Intro"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, dependencies, crates-io]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[Cargo.toml Manifest]]", "[[Cargo.lock]]", "[[Dependencies and Version Requirements]]", "[[Packages and Crates]]", "[[Semantic Versioning]]"]
sources: ["[[the-book]]", "[[command-line-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html", "https://doc.rust-lang.org/cargo/reference/resolver.html", "https://doc.rust-lang.org/cargo/commands/cargo-add.html"]
rust_version: "edition 2024 / 1.85+"
---

# crates.io and Dependencies Intro

crates.io is Cargo's default public registry, and a dependency entry in `Cargo.toml` tells Cargo which external crate versions your package is allowed to resolve, download, build, and lock.

## What it is
A crate is a compilation unit of Rust code. Some crates are binaries you run;
others are libraries your code uses. crates.io is the default registry where
open source Rust crates are published for Cargo to resolve and download.

In the guessing game, `rand` is introduced as the first external library crate.
The dependency declaration gives Cargo a package name and version requirement.
Cargo then resolves a compatible version and any transitive dependencies needed
by that crate.

## How it works
In `Cargo.toml`, dependencies normally live under `[dependencies]`:

```toml
[dependencies]
rand = "0.8.5"
```

The Book explains that `0.8.5` is shorthand for a compatible-version
requirement, allowing updates that stay below the next incompatible release for
that pre-1.0 series. Cargo records the exact resolved versions in [[Cargo.lock]]
after a build. Future builds reuse those exact versions until you intentionally
change requirements or run update commands.

`cargo add rand@0.8.5` is the command-line way to add the same dependency
without hand-editing the table. `cargo doc --open` builds local documentation
for your crate and its dependencies so you can inspect APIs such as `rand::Rng`.

Dependency resolution is constraint solving. Cargo combines your direct version
requirements, transitive requirements, selected features, target constraints,
the registry index, yanked releases, and the existing `Cargo.lock` when present.
It generally prefers the highest compatible version, but edition 2024's resolver
version 3 also prefers versions compatible with declared `rust-version` when it
can.

The lockfile matters because a version requirement like `"1.2"` is a range, not
one exact release. `Cargo.toml` says what is allowed; `Cargo.lock` records what
was actually chosen. `cargo update` changes locked versions within the allowed
requirements, while editing `Cargo.toml` changes the requirements themselves.

## Example
```rust
fn main() {
    let dependency = "rand";
    let registry = "crates.io";
    println!("Cargo can resolve {dependency} from {registry}.");
}
```

## Worked example
Adding a dependency creates both a manifest change and, after resolution, a
lockfile change:

```text
$ cargo add rand@0.8.5
$ cargo tree
```

```toml
[dependencies]
rand = "0.8.5"
```

The requirement permits compatible `0.8.x` releases. Cargo resolves `rand` plus
its transitive dependencies, writes exact package versions to `Cargo.lock`, and
`cargo tree` shows the resulting graph. If two crates require incompatible major
versions of the same dependency, Cargo may build both versions; `cargo tree -d`
helps find duplicates.

For a dependency used only by tests or examples, use a development dependency:

```toml
[dev-dependencies]
pretty_assertions = "1"
```

This keeps normal library/binary builds from depending on test-only crates.

## Common errors
Using a dependency in code before declaring it produces an unresolved import:

```text
error[E0432]: unresolved import `rand`
```

Add the dependency with `cargo add rand@0.8.5` or edit `[dependencies]`, then
rerun Cargo so the resolver can update `Cargo.lock`.

A lockfile conflict in CI often appears as:

```text
error: the lock file needs to be updated but --locked was passed
```

Regenerate `Cargo.lock` locally with the intended manifest changes and commit it
when project policy requires a lockfile.

A yanked or incompatible version may require changing the version requirement or
running a targeted update:

```text
$ cargo update -p rand
```

## Best practice
- ✅ Add dependencies deliberately and read their docs before leaning on an API;
  Cargo can build local docs with `cargo doc --open`.
- ✅ Prefer exact tutorial versions when following tutorial code that names a
  version, then update consciously after finishing the lesson.
- ✅ Commit or preserve [[Cargo.lock]] according to package type and policy so
  builds are reproducible where they need to be.
- ✅ Learn [[Dependencies and Version Requirements]] before widening or pinning
  version ranges in shared packages.
- ✅ Prefer `cargo add` when available because it resolves the package name and
  writes valid manifest syntax.
- ✅ Use `[dev-dependencies]` for test/example helpers and `[build-dependencies]`
  only for build scripts.
- ✅ Inspect the resolved graph with `cargo tree` when compile time, duplicate
  versions, or features become confusing.

## Pitfalls
- ⚠️ Assuming the newest crates.io release is always API-compatible with tutorial
  code; SemVer requirements matter.
- ⚠️ Editing [[Cargo.lock]] by hand instead of changing [[Cargo.toml Manifest]] or
  using Cargo commands.
- ⚠️ Adding dependencies for tiny standard-library tasks; see
  [[Minimizing Dependencies]] when a dependency is optional.
- ⚠️ Using `*` or overly broad requirements in application code; they make
  reproducibility and review harder.
- ⚠️ Forgetting that dependency features are unified; enabling a feature in one
  target can affect how that dependency is compiled elsewhere in the build.

## See also
[[Cargo Basics]] · [[Cargo.toml Manifest]] · [[Cargo.lock]] · [[Dependencies and Version Requirements]] · [[Packages and Crates]] · [[Semantic Versioning]] · [[Minimizing Dependencies]] · [[Cargo Workspaces]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 2 "Increasing Functionality with a Crate" — [[the-book]],
  https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html
- The Cargo Book, "Specifying Dependencies" — https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
