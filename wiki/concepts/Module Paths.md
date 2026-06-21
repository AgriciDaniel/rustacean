---
type: concept
title: "Module Paths"
aliases: ["Paths"]
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, paths, modules, name-resolution]
domain: "Modules & Project Structure"
difficulty: basic
related: ["[[Modules]]", "[[Crate Roots]]", "[[Visibility and Privacy]]", "[[The use Keyword]]", "[[Re-exporting with pub use]]", "[[Splitting Modules into Files]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html", "https://doc.rust-lang.org/reference/paths.html"]
rust_version: "edition 2024 / 1.85+"
---

# Module Paths

A module path names an item in the crate's module tree using `::`, either from the crate root or relative to the current module.

## What it is
Paths are how Rust code refers to modules and items such as functions,
structs, enums, traits, constants, and enum variants. In module code, a path is
usually either absolute or relative.

An absolute path starts from a crate root. For the current crate, it starts
with `crate`; for an external crate, it starts with that crate's name. A
relative path starts from the current module and may begin with `self`,
`super`, or an item name in scope.

## How it works
Each `::` segment descends through the module tree or selects an item. Rust
checks both name resolution and [[Visibility and Privacy]]. A path can point to
the right item and still fail to compile if any private module or item blocks
access from the current location.

`super` means the parent module, similar to `..` in a filesystem path. It is
useful when a child module calls a helper in its parent and both are likely to
move together.

In implementation code, absolute `crate::...` paths are often easier to move
because they do not depend on the current module's exact location. Relative
paths are useful for nearby sibling or parent relationships.

## Example
```rust
fn deliver_order() -> &'static str {
    "delivered"
}

mod kitchen {
    pub fn fix_order() -> &'static str {
        super::deliver_order()
    }
}

fn main() {
    assert_eq!(crate::kitchen::fix_order(), "delivered");
}
```

The call inside `kitchen` uses `super`; the call from `main` uses an absolute
`crate::` path.

## Worked example
Absolute paths are often better for cross-cutting helpers, while `super` fits
tight parent-child relationships:

```rust
mod telemetry {
    pub fn record(event: &str) -> String {
        format!("recorded:{event}")
    }
}

mod checkout {
    fn validate(total: u32) -> bool {
        total > 0
    }

    pub mod card {
        pub fn charge(total: u32) -> Option<String> {
            if super::validate(total) {
                Some(crate::telemetry::record("charge"))
            } else {
                None
            }
        }
    }
}

fn main() {
    assert_eq!(checkout::card::charge(10).as_deref(), Some("recorded:charge"));
}
```

`super::validate` says "the helper belongs to my parent." `crate::telemetry`
says "this is a crate-level service I should keep finding even if `card` moves."

## Common errors
A path can resolve syntactically but fail privacy:

```rust
mod api {
    mod internal {
        pub fn ping() {}
    }
}

fn main() {
    crate::api::internal::ping();
}
```

Typical diagnostic:

```console
error[E0603]: module `internal` is private
```

Fix the visibility chain (`pub mod internal`, a public wrapper, or preferably a
stable [[Re-exporting with pub use]] path) rather than changing the spelling of
the path.

## Deeper mechanics
Path resolution works segment by segment across namespaces. `crate` starts at
the current crate root; an external crate name starts at that dependency's
crate root; `self` starts at the current module; `super` climbs to an ancestor.
`super` may be repeated in leading segments, but `crate` can only appear as the
first segment.

For functions and constants, a resolved path can be an expression. For types,
traits, and modules, paths appear in type positions, imports, and qualified
syntax. [[Fully Qualified Syntax]] is the escape hatch when associated items
from traits or inherent implementations need disambiguation.

## Best practice
- ✅ Prefer `crate::...` for stable intra-crate references that should survive moving the calling module.
- ✅ Use `super::...` when the relationship to the parent module is the important part of the design.
- ✅ Keep public paths short and intentional with [[Re-exporting with pub use]].
- ✅ Remember that a path is valid only if the privacy chain permits access.
- ✅ Use external crate names at API boundaries so it is clear when code crosses a crate boundary.
- ✅ Import long, repeated paths with [[The use Keyword]] near the scope that uses them.
- ✅ Let public documentation show facade paths, not the deepest implementation paths.

## Pitfalls
- ⚠️ Assuming a correct spelling means accessible; private modules and private items still block the path.
- ⚠️ Using deep relative paths that break whenever a module moves.
- ⚠️ Repeating long paths everywhere instead of using [[The use Keyword]] locally.
- ⚠️ Exposing long internal paths as a public API, forcing users to depend on your folder structure.
- ⚠️ Starting ordinary paths with `::` as if it meant the current crate root; in edition 2024, use `crate::`.
- ⚠️ Reaching into sibling internals with `super::super::...` instead of designing a clearer shared parent API.
- ⚠️ Confusing module paths with filesystem paths after [[Splitting Modules into Files]].

## See also
[[Modules]] · [[Crate Roots]] · [[Visibility and Privacy]] · [[The use Keyword]] · [[Re-exporting with pub use]] · [[Splitting Modules into Files]] · [[Packages and Crates]] · [[Fully Qualified Syntax]] · [[Treating mod as include]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Paths for Referring to an Item in the Module Tree" — [[the-book]], https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
- The Rust Reference, "Paths" — [[the-reference]], https://doc.rust-lang.org/reference/paths.html
