---
type: antipattern
title: "Treating mod as include"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, modules, mod, footgun]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[Modules]]", "[[Splitting Modules into Files]]", "[[Crate Roots]]", "[[The use Keyword]]", "[[Module Paths]]", "[[Visibility and Privacy]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-05-separating-modules-into-different-files.html", "https://doc.rust-lang.org/reference/items/modules.html#module-source-filenames"]
rust_version: "edition 2024 / 1.85+"
---

# Treating mod as include

`mod` is not textual inclusion; it declares a module at one place in the module tree and may load that module's body from a file.

## The mistake
New Rust projects sometimes put `mod shared;` in every file that wants to use
`shared.rs`. That imports habits from languages where source files are
included textually.

In Rust, repeating `mod shared;` in multiple parent modules declares multiple
different modules with similar source bodies at different paths. It changes
identity, paths, privacy, type names, and trait implementations.

## Why it happens
The same keyword handles inline modules and out-of-line module files. A file
named `shared.rs` looks like something one might include from anywhere.

But Rust's compiler starts at the [[Crate Roots]] and follows module
declarations. A module file's logical path is assigned by the parent `mod`
declaration. Code elsewhere should use [[Module Paths]] or [[The use Keyword]]
to refer to that already-declared module.

The correct alternative is: declare the module once in its parent, make the
needed items visible, and import or path to those items from other modules.

## Example
```rust
mod shared {
    pub fn normalize(input: &str) -> String {
        input.trim().to_lowercase()
    }
}

mod handler {
    use crate::shared;

    pub fn handle(input: &str) -> String {
        shared::normalize(input)
    }
}

fn main() {
    assert_eq!(handler::handle(" Rust "), "rust");
}
```

`shared` is declared once. `handler` uses a path to reach it.

## More realistic failure
Imagine `src/shared.rs` defines a type:

```rust
pub struct UserId(pub u64);
```

This is wrong:

```rust
// src/a.rs
mod shared;
pub fn id() -> shared::UserId {
    shared::UserId(1)
}

// src/b.rs
mod shared;
pub fn take(_: shared::UserId) {}
```

Even though both modules loaded text from a file with the same name, they have
different logical types: `crate::a::shared::UserId` and
`crate::b::shared::UserId`. Passing one to the other can produce a mismatch
like:

```console
error[E0308]: mismatched types
  = note: `a::shared::UserId` and `b::shared::UserId` have similar names, but are actually distinct types
```

The fix is to declare `mod shared;` once in the common parent, usually
`src/lib.rs` or `src/main.rs`, then use `crate::shared::UserId` from both `a`
and `b`.

## Common errors
Using `mod` where an import is intended may also produce duplicate-name errors:

```rust
mod shared;
mod shared;
```

Typical diagnostic:

```console
error[E0428]: the name `shared` is defined multiple times
```

If the module is already declared, use `use crate::shared;` or a direct
`crate::shared::item` path instead of another `mod`.

## Deeper mechanics
The compiler starts at the [[Crate Roots]] and builds one module tree. A `mod`
item inserts a new module node into that tree. If the item has a semicolon, the
body is loaded from a file chosen by the module-source filename rules. The file
does not carry a global identity; the parent `mod` declaration gives the module
its identity.

That identity affects type names, trait implementations, privacy, statics, and
singletons. Two modules loaded from similar-looking source text are still two
modules, so their types are not interchangeable unless they are aliases or
re-exports of the same item.

## Best practice
- ✅ Declare each module from exactly one parent module in the tree.
- ✅ Use `use crate::shared;` or `crate::shared::item` from other modules.
- ✅ Treat module files as bodies for module declarations, not standalone import targets.
- ✅ Split modules with [[Splitting Modules into Files]] only after the logical tree is clear.
- ✅ Put shared modules under the nearest common parent so all consumers name the same item identity.
- ✅ Re-export shared public types from a facade when consumers should not depend on the internal module path.
- ✅ Check the logical paths in compiler diagnostics; they reveal whether duplicate module identities were created.

## Pitfalls
- ⚠️ Repeating `mod shared;` under multiple parents creates different module paths.
- ⚠️ Using `mod` where `use` is intended; `mod` declares, `use` binds a name.
- ⚠️ Debugging duplicate type errors caused by the same-looking code existing in two module identities.
- ⚠️ Moving files around without moving the parent `mod` declaration that gives them their path.
- ⚠️ Trying to fix unresolved names by adding more `mod` declarations in leaf files.
- ⚠️ Assuming `include!` and `mod` solve the same problem; `include!` is textual macro inclusion and is rarely the right tool for ordinary modules.
- ⚠️ Letting tests create a second copy of a support module instead of sharing it through a common test-support crate or module.

## See also
[[Modules]] · [[Splitting Modules into Files]] · [[Crate Roots]] · [[The use Keyword]] · [[Module Paths]] · [[Visibility and Privacy]] · [[Packages and Crates]] · [[Library and Binary Package Layout]] · [[Re-exporting with pub use]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Separating Modules into Different Files" — [[the-book]], https://doc.rust-lang.org/book/ch07-05-separating-modules-into-different-files.html
- The Rust Reference, "Module source filenames" — [[the-reference]], https://doc.rust-lang.org/reference/items/modules.html#module-source-filenames
