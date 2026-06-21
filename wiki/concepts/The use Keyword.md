---
type: concept
title: "The use Keyword"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, use, imports, paths]
domain: "Modules & Project Structure"
difficulty: basic
related: ["[[Module Paths]]", "[[Modules]]", "[[Visibility and Privacy]]", "[[Re-exporting with pub use]]", "[[Glob Imports in Public Code]]", "[[Fully Qualified Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html", "https://doc.rust-lang.org/reference/items/use-declarations.html"]
rust_version: "edition 2024 / 1.85+"
---

# The use Keyword

`use` creates a local name binding for a path so code can refer to an item with a shorter, clearer name in that scope.

## What it is
A `use` declaration is Rust's import mechanism. It does not load a source file
and it does not declare a module; it only binds a name in the current module or
block to something already reachable by a path.

`use` can import modules, types, traits, functions, enum variants, macros, and
other nameable items. A public `use` is a re-export; see
[[Re-exporting with pub use]].

## How it works
The binding created by `use` is scoped. A `use` at the crate root does not
automatically apply inside a child module. Put imports in the module or block
where the short name is used.

Rust's idiom is to import parent modules for functions, then call
`module::function()`, because that keeps the call site clear. For structs,
enums, traits, and common types, importing the item itself is idiomatic:
`use std::collections::HashMap;`.

Brace syntax groups imports with a shared prefix, `self` imports the parent in
a grouped import, and `as` renames a binding to avoid collisions.

## Example
```rust
use std::collections::HashMap;
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let mut counts = HashMap::new();
    counts.insert("modules", 1);

    let mut out = io::stdout();
    writeln!(out, "{}", counts["modules"])?;
    Ok(())
}
```

This imports a type directly, imports a module with `self`, and imports a trait
needed by the `writeln!` method call.

## Worked example
Block-scoped imports keep names close to uncommon uses:

```rust
use std::fmt;

fn render(rows: &[&str]) -> fmt::Result {
    let mut output = String::new();
    {
        use std::fmt::Write;
        for row in rows {
            writeln!(&mut output, "{row}")?;
        }
    }
    assert_eq!(output, "a\nb\n");
    Ok(())
}

fn main() {
    render(&["a", "b"]).unwrap();
}
```

The `Write` trait is imported only in the block where method resolution needs
it. Outside the block, the short name is not in scope.

## Common errors
A parent module import does not apply inside a child module:

```rust
mod service {
    pub fn start() {}
}

use crate::service;

mod cli {
    pub fn run() {
        service::start();
    }
}
```

Typical diagnostic:

```console
error[E0433]: failed to resolve: use of unresolved module or unlinked crate `service`
```

Fix it by adding `use crate::service;` inside `cli`, or by writing
`crate::service::start()` directly.

## Deeper mechanics
A `use` declaration creates one or more bindings in the item namespace,
possibly also binding names from other namespaces for the same target. It does
not evaluate code, load a file, or change ownership of the item. The target
path must already resolve and pass privacy checks.

Use trees can group shared prefixes, import the parent with `self`, rename with
`as`, and import all public names from a module with `*`. Public `use` changes
the binding's visibility and becomes [[Re-exporting with pub use]], which is API
surface rather than a local convenience.

## Best practice
- ✅ Import types and traits directly when the short name is conventional and unambiguous.
- ✅ Import modules for function-heavy APIs so calls still show the module owner.
- ✅ Use `as` aliases for legitimate name collisions, especially `Result` types.
- ✅ Use nested paths to keep related imports compact without hiding their source.
- ✅ Put imports in the smallest module or block where they improve readability.
- ✅ Import extension traits deliberately so method-call syntax has an obvious source.
- ✅ Prefer explicit imports over broad globs in production code and public modules.

## Pitfalls
- ⚠️ Expecting a parent module's `use` to apply in child modules; imports are scoped.
- ⚠️ Using glob imports outside tests or preludes; see [[Glob Imports in Public Code]].
- ⚠️ Thinking `use` makes an inaccessible private item accessible; privacy is still checked.
- ⚠️ Treating `use` as file inclusion; module loading is done by `mod`, not `use`.
- ⚠️ Importing functions directly when the call site becomes unclear; `fs::read_to_string` usually reads better than bare `read_to_string`.
- ⚠️ Hiding a public API decision inside `pub use`; public imports are re-exports and should be reviewed as API.
- ⚠️ Relying on root-level imports to define a crate-wide prelude; each module still chooses its own imports.

## See also
[[Module Paths]] · [[Modules]] · [[Visibility and Privacy]] · [[Re-exporting with pub use]] · [[Glob Imports in Public Code]] · [[Treating mod as include]] · [[Fully Qualified Syntax]] · [[Traits]] · [[Crate Roots]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Bringing Paths into Scope with the use Keyword" — [[the-book]], https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html
- The Rust Reference, "Use declarations" — [[the-reference]], https://doc.rust-lang.org/reference/items/use-declarations.html
