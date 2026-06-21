---
type: pattern
title: "Workspace Project Structure"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, workspaces, project-structure, cargo]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[Cargo Workspaces]]", "[[Packages and Crates]]", "[[Crate Roots]]", "[[Library and Binary Package Layout]]", "[[Dependencies and Version Requirements]]", "[[Cargo.lock]]"]
sources: ["[[the-book]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html", "https://doc.rust-lang.org/cargo/reference/workspaces.html"]
rust_version: "edition 2024 / 1.85+"
---

# Workspace Project Structure

Use a Cargo workspace when a project has multiple related packages that should build, test, and resolve dependencies together.

## What it is
A workspace is a project-structure boundary above a package. It is useful when
one repository contains multiple crates with distinct package manifests, such
as an application crate, a core library crate, a proc-macro crate, and test
support crates.

This note focuses on when to choose a workspace as structure. For full Cargo
configuration details, see [[Cargo Workspaces]].

## How it works
The workspace root has a `Cargo.toml` with `[workspace]`, a shared
`Cargo.lock`, and one shared `target` directory. Each member remains its own
package and must declare its own dependencies. Cargo does not assume workspace
members depend on each other just because they live together.

Commands from the root can target all members or a specific package with `-p`.
That makes workspaces good for coordinated CI while preserving package-level
separation.

Use a workspace when package boundaries are real: different publication units,
different dependency sets, different crate types, or independent public APIs.
Use [[Modules]] inside one crate when the boundary is only organization.

## Example
```rust
pub fn member_label(package: &str, crate_name: &str) -> String {
    format!("{package}/{crate_name}")
}

fn main() {
    assert_eq!(member_label("api", "api"), "api/api");
}
```

The Rust code inside each workspace member is ordinary crate code; the
workspace changes how packages are coordinated by Cargo.

## Worked example
A typical edition-2024 virtual workspace root is manifest-only:

```toml
[workspace]
resolver = "3"
members = ["crates/api", "crates/domain", "crates/cli"]

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
serde = { version = "1", default-features = false, features = ["derive"] }
```

Each member opts into inherited metadata and dependencies:

```toml
[package]
name = "cli"
version = "0.1.0"
edition.workspace = true
rust-version.workspace = true
license.workspace = true

[dependencies]
domain = { path = "../domain" }
serde.workspace = true
```

The path dependency is still explicit. Workspace membership alone does not make
`core` available to `cli`.

## Common errors
Forgetting the dependency edge between members usually fails at name resolution:

```rust
fn main() {
    println!("{}", domain::version());
}
```

Typical diagnostic:

```console
error[E0433]: failed to resolve: use of unresolved module or unlinked crate `core`
```

Fix it by adding the member as a dependency in the consuming package's
`Cargo.toml`, commonly with `{ path = "../domain" }`.

## Deeper mechanics
A workspace is Cargo coordination, not a Rust module boundary. It gives members
one lockfile, one shared target directory, common package selection flags, and
optional inheritance for package metadata, dependencies, and lints. Each member
remains a package with its own crate roots and its own dependency declarations.

In edition 2024, resolver version 3 is the edition-default resolver for
packages, and virtual workspaces should set `resolver = "3"` explicitly because
there is no root package edition to infer from. Shared dependencies are
inherited with `.workspace = true`; features requested by members are additive.

## Best practice
- ✅ Start with one package plus [[Library and Binary Package Layout]] until separate package metadata is useful.
- ✅ Use workspaces for crates that evolve together and are commonly tested together.
- ✅ Keep dependency relationships explicit with path dependencies between members.
- ✅ Use `cargo test --workspace` for broad checks and `cargo test -p name` for focused checks.
- ✅ Put shared versions, edition, rust-version, lints, and common dependencies in workspace tables when many members use them.
- ✅ Use `default-members` when root commands should normally operate on a subset.
- ✅ Keep public API and release boundaries clear; publishing and semver decisions remain per package.

## Pitfalls
- ⚠️ Assuming every member can use every dependency declared elsewhere; each package needs its own dependency declaration.
- ⚠️ Creating a workspace to compensate for poorly organized [[Modules]].
- ⚠️ Forgetting that publishing is per package, even when packages live in one workspace.
- ⚠️ Treating the shared lockfile as a shared public API; it coordinates builds, not module paths.
- ⚠️ Forgetting `resolver = "3"` in a virtual edition-2024 workspace.
- ⚠️ Expecting `[patch]`, `[profile]`, or workspace-level settings in member manifests to behave like root settings.
- ⚠️ Centralizing dependencies but forgetting member-level feature choices are additive across the selected build graph.

## See also
[[Cargo Workspaces]] · [[Packages and Crates]] · [[Crate Roots]] · [[Modules]] · [[Library and Binary Package Layout]] · [[Dependencies and Version Requirements]] · [[Cargo.lock]] · [[Cargo.toml Manifest]] · [[Semantic Versioning]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Cargo Workspaces" — [[the-book]], https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
- The Cargo Book, "Workspaces" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/workspaces.html
