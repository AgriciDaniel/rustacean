---
type: concept
title: "Visibility and Privacy"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, visibility, privacy, pub]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[Modules]]", "[[Module Paths]]", "[[The use Keyword]]", "[[Re-exporting with pub use]]", "[[Private Fields with Public Constructors]]", "[[Glob Imports in Public Code]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html", "https://doc.rust-lang.org/reference/visibility-and-privacy.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Visibility"]
---

# Visibility and Privacy

Rust items are private by default; `pub` and restricted forms such as `pub(crate)` decide where a name can be used.

## What it is
Visibility answers: can this item be used from this location? Modules use
privacy to hide implementation details and expose only the API that other code
should rely on.

The default is private. The two major exceptions are associated items in a
public trait and variants in a public enum, which are public by default.
Public structs do not make their fields public; each field has its own
visibility.

## How it works
Rust allows access in two broad cases. A public item can be accessed from a
module if all ancestor modules on the path are accessible from that module. A
private item can be accessed by the module where it is defined and by that
module's descendants.

Visibility can be unrestricted with `pub`, crate-wide with `pub(crate)`,
limited to the parent with `pub(super)`, equivalent to private with
`pub(self)`, or limited to an ancestor path with `pub(in crate::some_module)`.
For edition 2024, `pub(in ...)` paths follow the 2018+ rule: start with
`crate`, `self`, or `super`.

`pub` on a module only makes the module name accessible. It does not make
every item inside the module public.

## Example
```rust
mod account {
    pub struct User {
        pub name: String,
        password_hash: String,
    }

    impl User {
        pub fn new(name: &str) -> Self {
            Self { name: name.to_owned(), password_hash: String::from("hash") }
        }

        pub(crate) fn has_password_hash(&self) -> bool {
            !self.password_hash.is_empty()
        }
    }
}

fn main() {
    let user = account::User::new("Ada");
    assert_eq!(user.name, "Ada");
    assert!(user.has_password_hash());
}
```

The type and `name` field are public to this module, while the stored hash
remains an implementation detail.

## Worked example
Restricted visibility is useful when sibling modules need a helper but external
callers should not see it:

```rust
mod pipeline {
    pub(in crate::pipeline) fn normalize(input: &str) -> String {
        input.trim().to_lowercase()
    }

    pub mod ingest {
        pub fn prepare(input: &str) -> String {
            super::normalize(input)
        }
    }

    pub mod report {
        pub fn label(input: &str) -> String {
            format!("report:{}", super::normalize(input))
        }
    }
}

fn main() {
    assert_eq!(pipeline::ingest::prepare(" Rust "), "rust");
    assert_eq!(pipeline::report::label(" Rust "), "report:rust");
}
```

`normalize` is visible inside `crate::pipeline` and its descendants, but it is
not part of the crate's public API.

## Common errors
Public structs do not make fields public:

```rust
mod account {
    pub struct User {
        name: String,
    }
}

fn main() {
    let user = account::User { name: String::from("Ada") };
}
```

Typical diagnostic:

```console
error[E0451]: field `name` of struct `User` is private
```

Fix it by providing a public constructor or intentionally marking the field
`pub`. Prefer constructors when the type has invariants.

## Deeper mechanics
Rust checks privacy for every item access: imports, path expressions, type
positions, patterns, and re-exports. A public item is accessible only when the
path used to reach it has accessible ancestor modules, unless a public
re-export creates a shorter accessible path.

Restricted visibility only narrows access; it cannot make an item reachable
through private ancestors. For `pub(in path)`, the path must name an ancestor
module directly, not an alias introduced by [[The use Keyword]]. In edition
2024, that path must begin with `crate`, `self`, or `super`, following the
2018+ rule.

## Best practice
- ✅ Start private and widen visibility only when a caller genuinely needs the item.
- ✅ Prefer `pub(crate)` for internal cross-module helpers that are not part of the crate API.
- ✅ Keep struct fields private when invariants matter; expose constructors and methods instead.
- ✅ Use [[Re-exporting with pub use]] to expose a clean API without making every internal module public.
- ✅ Use `pub(super)` for parent-only callbacks or registration helpers instead of exposing them crate-wide.
- ✅ Use `pub(in crate::module)` when a whole subsystem needs access but the rest of the crate should not.
- ✅ Treat every unrestricted `pub` in a library as semver-relevant API unless it is hidden behind crate visibility.

## Pitfalls
- ⚠️ Assuming `pub mod child` exposes all child contents; each item still needs the right visibility.
- ⚠️ Making fields public when future validation or invariants are likely.
- ⚠️ Depending on a public path through internal modules that the crate should be free to reorganize.
- ⚠️ Using `pub(in path)` with a path introduced by `use`; the path must resolve directly to an ancestor module.
- ⚠️ Using `pub(crate)` as a default for everything; crate-wide visibility is still a broad contract inside large crates.
- ⚠️ Forgetting public enum variants are public by default, while public struct fields are private by default.
- ⚠️ Making an implementation module public only to expose one type; use a re-exported type path instead.

## See also
[[Modules]] · [[Module Paths]] · [[The use Keyword]] · [[Re-exporting with pub use]] · [[Splitting Modules into Files]] · [[Private Fields with Public Constructors]] · [[Newtype Pattern]] · [[Cargo Workspaces]] · [[Semantic Versioning]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Exposing Paths with the pub Keyword" — [[the-book]], https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
- The Rust Reference, "Visibility and privacy" — [[the-reference]], https://doc.rust-lang.org/reference/visibility-and-privacy.html
