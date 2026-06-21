---
type: concept
title: "Name Resolution"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, names, paths, modules, imports]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Modules]]", "[[Shadowing]]", "[[Functions]]", "[[Pattern Matching]]", "[[Documentation Comments]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html", "https://doc.rust-lang.org/reference/names.html", "https://doc.rust-lang.org/reference/items/use-declarations.html"]
rust_version: "edition 2024 / 1.85+"
---

# Name Resolution

How Rust resolves paths and identifiers to items, using the module tree, `use` imports, and scoping rules.

## What it is
Name resolution is the compiler phase that decides what an identifier or path refers to: a local
binding, item, module, associated item, macro, lifetime, label, or other named entity.

Most Rust code relies on it through ordinary paths such as `std::fs::File`, relative paths such as
`self::helper`, imports with `use`, and local bindings introduced by `let`, function parameters, and
patterns.

Understanding resolution helps when an import appears unused, a local name shadows an item, or a
method call requires a trait to be in scope.

## How it works
Rust has multiple namespaces. Types, values, macros, lifetimes, labels, and tool attributes do not
all compete in the same bucket. For example, a struct name lives in the type namespace, while a
function name lives in the value namespace.

Paths are resolved relative to the current module unless they start with `crate`, `self`, `super`, or
an external crate name. `use` declarations create local aliases for paths; they do not copy items or
change item ownership.

Local bindings can shadow earlier local bindings and some imported names. The resolver works with the
module tree first and later type checking handles method lookup, trait bounds, and type-dependent
associated items.

## Example
```rust
mod metrics {
    pub fn record(name: &str) -> String {
        format!("metric:{name}")
    }
}

use crate::metrics::record as record_metric;

fn main() {
    let record = "requests";
    assert_eq!(record, "requests");
    assert_eq!(record_metric(record), "metric:requests");
}
```

The local binding `record` does not erase the imported function because the import was renamed to
`record_metric`.

## Edge cases
Single-segment names in patterns can be ambiguous until resolution decides whether the name is a new
binding or a path pattern. Constants used as patterns must resolve to constants, not new variables.

```rust
const MAX: u8 = 3;

fn classify(n: u8) -> &'static str {
    match n {
        0 => "zero",
        MAX => "max",
        _ => "other",
    }
}

fn main() {
    assert_eq!(classify(3), "max");
}
```

## Common errors
An unresolved path usually produces E0433 or E0425:

```rust
fn main() {
    // let value = collections::HashMap::new();
}
```

Typical diagnostic:

```text
error[E0433]: failed to resolve: use of undeclared crate or module `collections`
```

Fix the path or import the item:

```rust
use std::collections::HashMap;

fn main() {
    let value: HashMap<&str, i32> = HashMap::new();
    assert!(value.is_empty());
}
```

## Best practice
- ✅ Prefer explicit imports for common standard-library types used repeatedly.
- ✅ Use `crate::`, `self::`, and `super::` when relative position matters.
- ✅ Rename imports with `as` when a local domain name would otherwise collide.
- ✅ Keep glob imports mostly to tests and prelude-style modules where the exported surface is intentional.
- ✅ Let compiler suggestions guide missing imports, then choose the path that communicates ownership of the API.

## Pitfalls
- ⚠️ Shadowing an import with a local variable can make later code read differently than expected.
- ⚠️ Assuming `use` makes a dependency available; dependencies still come from `Cargo.toml`.
- ⚠️ Overusing `use super::*` in tests hides which items the test actually needs.
- ⚠️ Forgetting trait imports can make extension methods appear missing.
- ⚠️ Public re-exports are API commitments, not mere convenience aliases.

## See also
[[Modules]] · [[Paths]] · [[Shadowing]] · [[Functions]] · [[Pattern Matching]] · [[The Display Trait]] · [[The Debug Trait]] · [[Readable Generic APIs]] · [[Documentation Comments]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 7.3 "Paths for Referring to an Item in the Module Tree" — [[the-book]], https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
- The Rust Reference, "Names" — [[the-reference]], https://doc.rust-lang.org/reference/names.html
- The Rust Reference, "`use` declarations" — [[the-reference]], https://doc.rust-lang.org/reference/items/use-declarations.html
