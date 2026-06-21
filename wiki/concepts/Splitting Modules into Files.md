---
type: concept
title: "Splitting Modules into Files"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, modules, files, project-structure]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[Modules]]", "[[Crate Roots]]", "[[Module Paths]]", "[[The use Keyword]]", "[[Treating mod as include]]", "[[Re-exporting with pub use]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-05-separating-modules-into-different-files.html", "https://doc.rust-lang.org/reference/items/modules.html#module-source-filenames"]
rust_version: "edition 2024 / 1.85+"
---

# Splitting Modules into Files

Splitting modules into files changes where code lives on disk, not where it lives in the module tree.

## What it is
Small modules can be written inline with `mod name { ... }`. Larger modules
are usually moved to their own `.rs` files and declared from the parent with
`mod name;`.

The filesystem layout mirrors the logical module path. A root child module
`crate::garden` can live at `src/garden.rs`. Its child
`crate::garden::vegetables` can live at `src/garden/vegetables.rs`.

## How it works
For a declaration `mod garden;` in `src/lib.rs` or `src/main.rs`, Rust looks
for `src/garden.rs` or the older supported `src/garden/mod.rs`. For a
declaration `mod vegetables;` inside `src/garden.rs`, Rust looks for
`src/garden/vegetables.rs` or `src/garden/vegetables/mod.rs`.

The modern `name.rs` plus `name/child.rs` convention is preferred because it
avoids many open editor tabs all named `mod.rs`. You cannot define the same
module with both `name.rs` and `name/mod.rs`.

`mod` declarations should appear once at the module's parent. Other code
refers to the module with [[Module Paths]] or [[The use Keyword]].

## Example
```rust
mod garden {
    pub mod vegetables {
        #[derive(Debug, PartialEq)]
        pub struct Asparagus;
    }
}

fn main() {
    let plant = garden::vegetables::Asparagus;
    assert_eq!(format!("{plant:?}"), "Asparagus");
}
```

This compiles as one file. It has the same module tree you would get after
moving `garden` and `vegetables` into separate files.

## Worked example
The same tree can be split like this:

```text
src/
├── lib.rs
├── garden.rs
└── garden
    └── vegetables.rs
```

```rust
// src/lib.rs
mod garden;

pub use garden::vegetables::Asparagus;
```

```rust
// src/garden.rs
pub mod vegetables;
```

```rust
// src/garden/vegetables.rs
#[derive(Debug, PartialEq)]
pub struct Asparagus;
```

The public path can still be `crate::Asparagus` because `lib.rs` re-exports
the type. The implementation path is `crate::garden::vegetables::Asparagus`.

## Common errors
Putting a child file at the wrong level produces E0583:

```rust
// src/garden.rs
mod vegetables;
```

Typical diagnostic if the file is accidentally at `src/vegetables.rs`:

```console
error[E0583]: file not found for module `vegetables`
  = help: to create the module `vegetables`, create file "src/garden/vegetables.rs" or "src/garden/vegetables/mod.rs"
```

Move the file under the parent module's directory, or change the parent module
where `mod vegetables;` is declared.

## Deeper mechanics
An out-of-line module declaration is an item in the parent module. Without a
`#[path = "..."]` attribute, the compiler derives the searched filename from
the logical module path, not from imports. The modern convention is
`parent.rs` plus `parent/child.rs`; the historical `parent/mod.rs` form remains
supported, but the two forms cannot define the same module at the same time.

The `#[path]` attribute can redirect module source filenames, but it is best
reserved for generated code or unusual layouts. For ordinary projects, letting
the filesystem mirror [[Module Paths]] keeps editor navigation, rustdoc, and
code review predictable.

## Best practice
- ✅ Declare a child module in its parent, then refer to it by path elsewhere.
- ✅ Prefer `foo.rs` plus `foo/bar.rs` over the older `foo/mod.rs` style for new code.
- ✅ Split files when navigation or review becomes harder, not because every item needs a file.
- ✅ Keep public API decisions separate from file layout decisions.
- ✅ Re-export important public types from stable facade modules when the physical layout is an implementation detail.
- ✅ Keep `mod` declarations near the top of the parent module so the tree is easy to scan.
- ✅ Move tests with the module they exercise, using child `mod tests` for private access when useful.

## Pitfalls
- ⚠️ Loading the same module file with multiple `mod` declarations; see [[Treating mod as include]].
- ⚠️ Putting a child module file at the wrong directory level and wondering why Rust cannot find it.
- ⚠️ Mixing `foo.rs` and `foo/mod.rs` for the same module; that is a compiler error.
- ⚠️ Assuming `use` affects which files are compiled; only `mod` declarations load module files.
- ⚠️ Reorganizing files and accidentally changing public paths because re-exports were not in place.
- ⚠️ Using `#[path]` to fight the module system instead of fixing the parent-child relationship.
- ⚠️ Creating one file per tiny item, which increases path noise without improving cohesion.

## See also
[[Modules]] · [[Crate Roots]] · [[Module Paths]] · [[The use Keyword]] · [[Re-exporting with pub use]] · [[Treating mod as include]] · [[Packages and Crates]] · [[Library and Binary Package Layout]] · [[Visibility and Privacy]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Separating Modules into Different Files" — [[the-book]], https://doc.rust-lang.org/book/ch07-05-separating-modules-into-different-files.html
- The Rust Reference, "Module source filenames" — [[the-reference]], https://doc.rust-lang.org/reference/items/modules.html#module-source-filenames
