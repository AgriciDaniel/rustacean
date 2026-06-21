---
type: antipattern
title: "Glob Imports in Public Code"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, glob-imports, use, footgun]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[The use Keyword]]", "[[Re-exporting with pub use]]", "[[Module Paths]]", "[[Visibility and Privacy]]", "[[Modules]]", "[[Semantic Versioning]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html#importing-items-with-the-glob-operator", "https://doc.rust-lang.org/reference/items/use-declarations.html#glob-imports"]
rust_version: "edition 2024 / 1.85+"
---

# Glob Imports in Public Code

Glob imports make every importable public name from a path available, which can hide dependencies and make public APIs unstable.

## The mistake
`use some_module::*;` is convenient, but in ordinary library or application
code it makes it harder to see which names are in scope and where they came
from. In public API code, `pub use some_module::*;` is riskier because new
items added to `some_module` can silently become part of your public API.

Glob imports are not always wrong. They are common in tests, examples, and
intentional prelude modules. The mistake is using them where explicit imports
would document dependencies or protect an API boundary.

## Why it happens
Glob imports reduce typing when many names are used from one module. They also
feel natural for enum variants in small scopes.

The problem is that the set of imported names is open-ended. If a dependency
or internal module adds a public item, name resolution can change. The
Reference also specifies shadowing behavior around glob imports, so explicit
items may shadow globbed names in ways that are legal but surprising to
readers.

The correct alternative is explicit imports, or a carefully designed prelude
whose purpose is to be glob-imported by users.

## Example
```rust
mod colors {
    #[derive(Debug, PartialEq)]
    pub enum Color {
        Red,
        Blue,
    }
}

use colors::Color::{Blue, Red};

fn main() {
    let palette = [Red, Blue];
    assert_eq!(palette.len(), 2);
}
```

The variant imports are explicit, so the scope documents exactly which names
are used.

## More realistic failure
Two glob imports can be accepted until an ambiguous name is actually used:

```rust
mod text {
    pub struct Error;
}

mod network {
    pub struct Error;
}

use network::*;
use text::*;

fn main() {
    // let _ = Error; // ambiguous if uncommented
}
```

Typical diagnostic when `Error` is used:

```console
error[E0659]: `Error` is ambiguous
  = note: ambiguous because of multiple glob imports of a name in the same module
```

Fix it by importing explicitly, usually with aliases:

```rust
use network::Error as NetworkError;
use text::Error as TextError;

fn main() {
    let _ = NetworkError;
    let _ = TextError;
}
```

## Common errors
The public version is subtler:

```rust
pub mod internal {
    pub struct Client;
    pub struct Experimental;
}

pub use internal::*;
```

There may be no compiler error. The mistake is that `Experimental` has become
public API. Removing it later can be a semver-breaking change even if it was
never meant to be supported.

## Deeper mechanics
A glob import creates candidate bindings for all importable public names in the
target path. If two glob imports provide the same name, Rust can leave the
ambiguity latent until the name is used. A non-glob import can shadow a globbed
candidate, which is legal but easy to miss during review.

With `pub use module::*`, those candidates become re-exported public names.
That ties your public API to every public item in the target module, including
future additions. This is why glob re-exports belong only in deliberately
designed preludes or facades with API review.

## Best practice
- ✅ Prefer explicit imports in library and application modules.
- ✅ Limit enum variant glob imports to small scopes where the enum is obvious.
- ✅ Reserve `pub use module::*;` for intentional prelude/facade designs with review.
- ✅ In tests, `use super::*;` is acceptable when the test module intentionally exercises its parent.
- ✅ Alias repeated names such as `Error`, `Result`, or `Config` so the domain remains clear at call sites.
- ✅ Keep prelude modules small, documented, and semver-reviewed.
- ✅ Use explicit `pub use module::{Type, Trait};` for crate-root facades.

## Pitfalls
- ⚠️ Publishing accidental API surface with `pub use internal::*`.
- ⚠️ Losing track of a name's origin during code review.
- ⚠️ Being surprised when a dependency upgrade adds a conflicting name.
- ⚠️ Hiding missing module design behind a broad import instead of using [[Re-exporting with pub use]] deliberately.
- ⚠️ Assuming no diagnostic means no problem; public glob re-exports can compile while exposing the wrong API.
- ⚠️ Glob-importing dependency modules in library code, tying local name resolution to dependency releases.
- ⚠️ Using glob imports to avoid deciding which enum variants or extension traits a module actually needs.

## See also
[[The use Keyword]] · [[Re-exporting with pub use]] · [[Module Paths]] · [[Visibility and Privacy]] · [[Modules]] · [[Semantic Versioning]] · [[Publishing to crates.io]] · [[Treating mod as include]] · [[Crate Roots]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Importing Items with the Glob Operator" — [[the-book]], https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html#importing-items-with-the-glob-operator
- The Rust Reference, "Glob imports" — [[the-reference]], https://doc.rust-lang.org/reference/items/use-declarations.html#glob-imports
