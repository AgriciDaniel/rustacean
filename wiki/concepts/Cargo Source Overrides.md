---
type: concept
title: "Cargo Source Overrides"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, dependencies, overrides, vendoring]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.toml Manifest]]", "[[Dependencies and Version Requirements]]", "[[Cargo Configuration Hierarchy]]", "[[Cargo.lock]]", "[[Cargo Workspaces]]"]
sources: ["[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html", "https://doc.rust-lang.org/cargo/reference/source-replacement.html", "https://doc.rust-lang.org/cargo/commands/cargo-vendor.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cargo Source Overrides

Cargo source overrides are the mechanisms that make Cargo use a different source for dependency code, either by patching individual packages with `[patch]` or by replacing an entire source with an equivalent vendor or mirror source.

## What it is
Cargo has several override mechanisms, and they are not interchangeable.
Use `[patch]` when you need a different copy of a specific package, such as a local bug fix or an unpublished upstream branch.
Use `paths` overrides for short-lived local substitutions where the replacement has the same dependency graph.
Use source replacement when a whole source, such as `crates-io`, should be redirected to an equivalent mirror, local registry, or vendored directory.
The important boundary is identity.
`[patch]` may change where a package version comes from.
Source replacement assumes the replacement source contains the same crate code as the original source.
That makes source replacement suitable for vendoring and mirroring, not for private forks.

## How it works
The `[patch]` table is written in the root manifest of the package or workspace.
Its child table names the source being patched, usually `crates-io` or a git URL.
Each entry looks like a normal dependency specification.
When Cargo queries the patched source for available versions, it also considers the patch entries.
The patched crate's own `version` still matters because normal version resolution applies.

```toml
[dependencies]
uuid = "1.0"

[patch.crates-io]
uuid = { path = "../uuid" }
```

If the local `uuid` checkout has a version that satisfies `uuid = "1.0"`, Cargo can resolve to it.
If the lockfile already points at a registry version, you may need `cargo update -p uuid --precise <version>` so the lockfile records the patched package.
Patches apply transitively, but Cargo only reads them from the top-level manifest.
If a library depends on a patched crate, the final application or workspace may need to repeat the `[patch]`.

Path overrides are configured in `.cargo/config.toml`, not in `Cargo.toml`.
They are convenient for local experiments:

```toml
paths = ["../uuid"]
```

They cannot change the dependency graph.
The replacement package must have dependencies matching the package it replaces.
If the fork adds or removes dependencies, use `[patch]`.

Source replacement is also configured in `.cargo/config.toml`.
It redirects an entire source to another named source:

```toml
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
```

`cargo vendor` prints this kind of configuration after it creates the vendor directory.
Cargo treats vendored registry and git sources as read-only.
If you intend to edit dependency code, point `[patch]` or a path dependency at an editable checkout.

## Example
```rust
fn selected_source(kind: &str) -> &'static str {
    match kind {
        "patch" => "one dependency is replaced during resolution",
        "vendor" => "an equivalent source is used for the whole registry",
        "paths" => "a local same-graph package override is used",
        _ => "normal dependency source",
    }
}

fn main() {
    assert_eq!(
        selected_source("patch"),
        "one dependency is replaced during resolution"
    );
    println!("{}", selected_source("vendor"));
}
```

The Rust code above is deliberately ordinary.
The override behavior is controlled by Cargo metadata around the crate, not by APIs inside the crate.
That distinction is useful in reviews: source overrides affect the dependency graph before compilation begins.

## Best practice
- ✅ Prefer `[patch]` for local fixes, upstream pull requests, unpublished minor versions, and pre-publishing breaking changes.
- ✅ Keep `[patch]`, `[replace]`, and profile settings in the workspace root because member manifests are ignored for those sections.
- ✅ Use `cargo vendor` plus `[source]` replacement for reproducible offline or mirrored builds.
- ✅ Commit only project-wide source replacement config; keep personal experiments in local `.cargo/config.toml` or `--config`.
- ✅ After adding a patch, inspect `cargo tree` or build output to confirm the patched path or git source is actually selected.
- ✅ Remove temporary patches when the upstream version has been published and the dependency requirement can resolve normally.

## Pitfalls
- ⚠️ Treating source replacement as a fork mechanism. Replacement sources must be equivalent to the source they replace; use `[patch]` for changed code.
- ⚠️ Forgetting that the patched crate's `version` still participates in normal resolution.
- ⚠️ Defining `[patch]` in a dependency crate and expecting downstream users to inherit it automatically.
- ⚠️ Using deprecated `[replace]` in new work; Cargo recommends `[patch]` instead.
- ⚠️ Editing files under a vendored directory and expecting Cargo to track them like a local path crate.
- ⚠️ Publishing with unresolved path-only dependencies; published crates need registry-compatible dependency specifications. See [[Publishing to crates.io]].

## See also
[[Cargo & Dependencies]] · [[Cargo.toml Manifest]] · [[Dependencies and Version Requirements]] · [[Cargo Configuration Hierarchy]] · [[Cargo.lock]] · [[Cargo Workspaces]] · [[Feature Resolver]] · [[Workspace Dependency Inheritance]] · [[Publishing to crates.io]] · [[Minimizing Dependencies]]

## Sources
- The Cargo Book, "Overriding Dependencies" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- The Cargo Book, "Source Replacement" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- The Cargo Book, "cargo vendor" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
