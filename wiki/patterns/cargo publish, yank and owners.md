---
type: pattern
title: "cargo publish, yank and owners"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, publishing, crates-io, release]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Publishing to crates.io]]", "[[Cargo.toml Manifest]]", "[[Semantic Versioning]]", "[[Cargo.lock]]", "[[Dependencies and Version Requirements]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/publishing.html", "https://doc.rust-lang.org/cargo/commands/cargo-publish.html", "https://doc.rust-lang.org/cargo/commands/cargo-yank.html", "https://doc.rust-lang.org/cargo/commands/cargo-owner.html"]
rust_version: "edition 2024 / 1.85+"
---

# cargo publish, yank and owners

`cargo publish`, `cargo yank`, and `cargo owner` are the operational commands for releasing crates, preventing new resolutions of broken releases, and managing who may publish or yank a crate.

## What it is
Publishing uploads a specific package version to a registry such as crates.io.
For crates.io, a published version is permanent: the version cannot be overwritten and the code cannot be deleted through normal Cargo commands.
Yanking marks a version so Cargo will not choose it for new lockfiles, but it does not delete the code and does not break existing lockfiles.
Owner management controls who can publish or yank versions, and for named owners, who can add or remove other owners.
These commands form the release safety boundary for public Rust packages.

## How it works
Before publishing to crates.io, the package needs metadata such as `license` or `license-file`, `description`, repository or homepage information where appropriate, and a version that follows SemVer expectations.
Authentication is normally set up with `cargo login`, which stores credentials in Cargo's credentials file.
Tokens are secrets and should be revoked immediately if leaked.

`cargo publish` packages and uploads:

```console
cargo publish --dry-run
cargo package --list
cargo publish
```

The dry run performs the packaging and verification steps without upload.
`cargo package --list` shows which files will be included.
This matters because crates.io has size limits and because accidentally included files remain part of the published archive.
The `package.publish` manifest field can restrict which registries a package may be published to or disable publishing with `publish = false`.

`cargo yank` is for exceptional release mistakes:

```console
cargo yank --version 1.0.1 my-crate
cargo yank --version 1.0.1 --undo my-crate
```

A yank removes the version from normal future resolution.
It does not remove the archive.
Existing projects with `Cargo.lock` entries can continue to build.
If a compatible fixed version can be published first, do that before yanking so dependents are less likely to be stranded with no resolvable version.
For security advisories, RustSec or registry policy channels may be more appropriate than yanking alone.
For leaked credentials or secrets, revoke the credentials; yanking cannot ensure the published data disappears.

`cargo owner` manages owners:

```console
cargo owner --list my-crate
cargo owner --add github-handle my-crate
cargo owner --remove github-handle my-crate
cargo owner --add github:org:team my-crate
```

Named owners can publish, yank, and change the owner set.
Team owners can publish and yank but cannot add or remove owners.
Only grant named owner rights to people trusted to administer the crate.

## Example
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct Release {
    name: String,
    version: String,
}

impl Release {
    fn tag(&self) -> String {
        format!("{}-v{}", self.name, self.version)
    }
}

fn main() {
    let release = Release {
        name: "my-crate".to_string(),
        version: "1.2.3".to_string(),
    };
    assert_eq!(release.tag(), "my-crate-v1.2.3");
}
```

The Rust code is only the artifact being released.
The release behavior is governed by Cargo metadata, registry policy, and authenticated Cargo commands.

## Best practice
- ✅ Run `cargo publish --dry-run` before every publish.
- ✅ Inspect `cargo package --list` before the first publish and whenever packaging rules change.
- ✅ Publish SemVer-compatible fixes before yanking a broken compatible version when possible.
- ✅ Treat API tokens as secrets; use environment-backed credentials in CI and revoke leaked tokens immediately.
- ✅ Prefer team owners for organizations when available because team owners cannot alter the owner set.
- ✅ Tag the published commit and keep a changelog entry for each public release.
- ✅ Use `publish = false` for workspace members that must never be uploaded.

## Pitfalls
- ⚠️ Publishing is permanent. Do not assume a bad upload can be overwritten.
- ⚠️ Yanking is not deletion and is not a secret-removal mechanism.
- ⚠️ Yanking the only compatible version can break new dependents that do not already have a lockfile.
- ⚠️ Granting named owner rights too broadly gives those owners full control over the crate's owner set.
- ⚠️ Publishing with accidental files included in the package archive.
- ⚠️ Depending on local path-only crates in a package intended for crates.io; published dependencies must be registry-compatible.

## See also
[[Cargo & Dependencies]] · [[Publishing to crates.io]] · [[Cargo.toml Manifest]] · [[Semantic Versioning]] · [[Dependencies and Version Requirements]] · [[Cargo.lock]] · [[Cargo Configuration Hierarchy]] · [[Cargo Source Overrides]] · [[Workspace Dependency Inheritance]]

## Sources
- The Cargo Book, "Publishing on crates.io" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/publishing.html
- The Cargo Book, "cargo publish" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- The Cargo Book, "cargo yank" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/commands/cargo-yank.html
- The Cargo Book, "cargo owner" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/commands/cargo-owner.html
