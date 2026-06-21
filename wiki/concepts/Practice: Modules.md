---
type: concept
title: "Practice: Modules"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, modules]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Modules]]", "[[Module Paths]]", "[[The use Keyword]]", "[[Visibility and Privacy]]", "[[Name Resolution]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Modules

The modules group teaches Rust's namespace and privacy system. The key idea is that paths name where an item lives, while `pub` controls which module boundaries callers may cross.

## What it is
These exercises cover module definitions, nested modules, `use`, `super`, absolute and relative paths, and public visibility.

## How it works
Items are private to their parent module by default. Code can refer to items through paths like `crate::garden::vegetables::Asparagus`, and `use` can bring a path into local scope without changing ownership or visibility.

## Example
```rust
mod kitchen {
    pub mod tools {
        pub fn clean() -> &'static str {
            "clean knife"
        }
    }
}

use kitchen::tools;

fn main() {
    println!("{}", tools::clean());
}
```

## Best practice
- ✅ Keep modules organized around responsibilities, not just file count.
- ✅ Use `pub` sparingly; expose the API surface callers actually need.
- ✅ Prefer clear paths over overly broad glob imports in normal code.

## Pitfalls
- ⚠️ `use` does not make a private item public.
- ⚠️ Relative paths are resolved from the current module, not from the filesystem.
- ⚠️ Splitting modules into files changes layout, not the language's visibility rules.

## See also
[[Practice (Rustlings)]] · [[Modules]] · [[Module Paths]] · [[The use Keyword]] · [[Visibility and Privacy]] · [[Name Resolution]] · [[Splitting Modules into Files]]

## Sources
- Rustlings `10_modules` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

