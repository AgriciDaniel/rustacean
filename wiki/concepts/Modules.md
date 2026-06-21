---
type: concept
title: "Modules"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, modules, scope, privacy]
domain: "Modules & Project Structure"
difficulty: basic
related: ["[[Crate Roots]]", "[[Module Paths]]", "[[Visibility and Privacy]]", "[[The use Keyword]]", "[[Splitting Modules into Files]]", "[[Treating mod as include]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-02-defining-modules-to-control-scope-and-privacy.html", "https://doc.rust-lang.org/reference/items/modules.html"]
rust_version: "edition 2024 / 1.85+"
---

# Modules

Modules are named containers for Rust items; they organize a crate into a tree and define the privacy boundary for those items.

## What it is
A module can contain functions, structs, enums, traits, constants, statics,
type aliases, other modules, and imports. The whole crate is a module tree
rooted at the crate root. Named modules are child nodes in that tree.

Modules are about logical structure first. The filesystem can mirror the
module tree through [[Splitting Modules into Files]], but moving a module to a
file does not change the module's path or privacy rules.

## How it works
You create an inline module with `mod name { ... }` or declare an out-of-line
module with `mod name;`. In the out-of-line form, the module body is loaded
from a file based on the parent module and the module name.

Items inside a child module are private from parent modules by default. Child
modules can access private items in their ancestor modules, but parents need
public child modules and public child items to look inward.

Modules also create namespaces. Two items with the same name cannot exist in
the same namespace in the same module, but the same name can appear in
different modules and be selected with [[Module Paths]].

## Example
```rust
mod inventory {
    pub struct Item {
        pub name: &'static str,
    }

    pub fn sample() -> Item {
        Item { name: "notebook" }
    }
}

fn main() {
    let item = inventory::sample();
    assert_eq!(item.name, "notebook");
}
```

The `inventory` module groups an `Item` type and a constructor function behind
one path.

## Worked example
Modules can also encode an internal/public split without changing files:

```rust
mod catalog {
    pub struct Product {
        name: String,
    }

    impl Product {
        pub fn name(&self) -> &str {
            &self.name
        }
    }

    pub fn product(name: &str) -> Product {
        Product { name: name.to_owned() }
    }
}

fn main() {
    let product = catalog::product("book");
    assert_eq!(product.name(), "book");
}
```

The `Product` type is public, but its field stays private. Callers use the
module's constructor and methods instead of constructing invalid values.

## Common errors
Making a module public does not make every child item public:

```rust
pub mod catalog {
    fn hidden() {}
}

fn main() {
    catalog::hidden();
}
```

Typical diagnostic:

```console
error[E0603]: function `hidden` is private
```

Fix it by deciding whether `hidden` belongs in the public API. If it does, make
the function `pub`; if not, expose a narrower public wrapper.

## Deeper mechanics
Modules live in the type namespace and introduce lexical scopes for items,
imports, and visibility. A module path is not derived from the text inside a
file; it is derived from the parent module that declared it. Inline and
out-of-line modules produce the same module tree once loaded.

Privacy is checked after paths resolve. That means a private module can still
contain `pub` items that are usable elsewhere in the same crate, while external
crates cannot name those items unless a public path or re-export exposes them.

## Best practice
- ✅ Use modules to name cohesive areas of the codebase, not just to shorten files.
- ✅ Keep implementation modules private unless callers need their names as part of the API.
- ✅ Let module names describe domain concepts or responsibilities: `parser`, `storage`, `auth`, `reporting`.
- ✅ Split a module into files when navigation suffers, while keeping the same logical tree.
- ✅ Put tests as child modules when they need private access to the module under test.
- ✅ Prefer a shallow public module tree with clear names over exposing every implementation layer.
- ✅ Use module boundaries to protect invariants before reaching for extra crates or workspace members.

## Pitfalls
- ⚠️ Treating modules as textual includes; `mod` declares a place in the module tree. See [[Treating mod as include]].
- ⚠️ Marking a parent module `pub` and expecting its contents to become public automatically.
- ⚠️ Mirroring every small type with a one-item module; too much nesting makes [[Module Paths]] noisy.
- ⚠️ Letting public modules expose internal organization that callers should not depend on.
- ⚠️ Assuming the directory tree is authoritative; the `mod` declarations define the module tree.
- ⚠️ Hiding unrelated responsibilities in a vague `utils` module instead of naming the actual abstraction.
- ⚠️ Forgetting that imports inside one module do not leak into sibling or child modules.

## See also
[[Crate Roots]] · [[Module Paths]] · [[Visibility and Privacy]] · [[The use Keyword]] · [[Splitting Modules into Files]] · [[Re-exporting with pub use]] · [[Treating mod as include]] · [[Glob Imports in Public Code]] · [[Packages and Crates]] · [[Private Fields with Public Constructors]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Defining Modules to Control Scope and Privacy" — [[the-book]], https://doc.rust-lang.org/book/ch07-02-defining-modules-to-control-scope-and-privacy.html
- The Rust Reference, "Modules" — [[the-reference]], https://doc.rust-lang.org/reference/items/modules.html
