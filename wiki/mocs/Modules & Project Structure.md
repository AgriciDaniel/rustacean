---
type: moc
title: "Modules & Project Structure"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, modules, project-structure, moc]
domain: "Modules & Project Structure"
difficulty: basic
related: ["[[Packages and Crates]]", "[[Modules]]", "[[Module Paths]]", "[[Visibility and Privacy]]", "[[The use Keyword]]", "[[Splitting Modules into Files]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html", "https://doc.rust-lang.org/reference/items/modules.html", "https://doc.rust-lang.org/reference/items/use-declarations.html", "https://doc.rust-lang.org/reference/visibility-and-privacy.html"]
rust_version: "edition 2024 / 1.85+"
---

# Modules & Project Structure

Rust project structure is a layered system: packages contain crates, crates contain module trees, paths name items, and visibility controls the public API.

## Concepts
- [[Packages and Crates]]
- [[Crate Roots]]
- [[Modules]]
- [[Module Paths]]
- [[Visibility and Privacy]]
- [[The use Keyword]]
- [[Splitting Modules into Files]]

## Patterns
- [[Re-exporting with pub use]]
- [[Library and Binary Package Layout]]
- [[Workspace Project Structure]]

## Antipatterns
- [[Treating mod as include]]
- [[Glob Imports in Public Code]]

## Example
```rust
mod api {
    pub fn version() -> &'static str {
        "1.0"
    }
}

pub use api::version;

fn main() {
    assert_eq!(version(), "1.0");
}
```

This tiny crate shows the stack: a module owns implementation, `pub` exposes an
item, and `pub use` presents a short public path.

## Best practice
- ✅ Choose the smallest useful boundary: module before crate, crate before workspace.
- ✅ Keep crate roots as readable API and module declarations, not as dumping grounds.
- ✅ Use visibility to protect invariants and make public paths intentional.
- ✅ Re-export stable public concepts instead of exposing incidental internal folders.

## Pitfalls
- ⚠️ Confusing Cargo package layout with Rust module layout.
- ⚠️ Treating files as modules without understanding the parent `mod` declaration.
- ⚠️ Making everything `pub` to quiet privacy errors instead of designing the API.
- ⚠️ Using broad glob imports where explicit imports would make dependencies clearer.

## See also
[[Packages and Crates]] · [[Crate Roots]] · [[Modules]] · [[Module Paths]] · [[Visibility and Privacy]] · [[The use Keyword]] · [[Splitting Modules into Files]] · [[Re-exporting with pub use]] · [[Library and Binary Package Layout]] · [[Workspace Project Structure]] · [[Cargo Workspaces]] · [[Cargo.toml Manifest]]

## Sources
- The Rust Programming Language, "Managing Growing Projects with Packages, Crates, and Modules" — [[the-book]], https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html
- The Rust Reference, "Modules" — [[the-reference]], https://doc.rust-lang.org/reference/items/modules.html
- The Rust Reference, "Use declarations" — [[the-reference]], https://doc.rust-lang.org/reference/items/use-declarations.html
- The Rust Reference, "Visibility and privacy" — [[the-reference]], https://doc.rust-lang.org/reference/visibility-and-privacy.html
