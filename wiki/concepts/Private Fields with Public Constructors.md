---
type: concept
title: "Private Fields with Public Constructors"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, privacy, constructors, api-design]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Functions]]", "[[Name Resolution]]", "[[Readable Generic APIs]]", "[[Ownership]]", "[[The Debug Trait]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[idiomatic-api-design]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/visibility-and-privacy.html"]
rust_version: "edition 2024 / 1.85+"
---

# Private Fields with Public Constructors

Keep struct fields private and expose constructors/methods so invariants hold and the layout can evolve without breaking callers.

## What it is
Private fields with public constructors is the Rust API pattern of making a type public while keeping
its representation private. Callers construct and inspect values through methods instead of directly
setting fields.

This is useful when a type has invariants: non-empty strings, normalized paths, bounded numbers,
sorted collections, validated IDs, or cached derived state.

The pattern also preserves future flexibility. You can add fields, rename fields, change storage, or
precompute caches without breaking callers who never built the struct literally.

## How it works
Rust privacy is module-based. A `pub struct UserName { value: String }` exposes the type name, but the
field remains private outside the defining module unless it is marked `pub`.

Associated functions such as `new`, `try_new`, and `from_parts` are ordinary functions in an `impl`
block. They can access private fields because they are defined in the same module as the type.

Use infallible constructors when all inputs are valid, and fallible constructors returning `Result` or
`Option` when validation can fail.

## Example
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UserName {
    value: String,
}

impl UserName {
    pub fn new(value: impl Into<String>) -> Result<Self, String> {
        let value = value.into();
        if value.trim().is_empty() {
            return Err("user name cannot be empty".into());
        }
        Ok(Self { value })
    }

    pub fn as_str(&self) -> &str {
        &self.value
    }
}

fn main() {
    let name = UserName::new("ferris").expect("valid name");
    assert_eq!(name.as_str(), "ferris");
    assert!(UserName::new("   ").is_err());
}
```

## Edge cases
Private fields let you add cached state without changing construction syntax for callers:

```rust
pub struct Slug {
    raw: String,
    normalized: String,
}

impl Slug {
    pub fn new(raw: &str) -> Self {
        Self {
            raw: raw.to_owned(),
            normalized: raw.trim().to_ascii_lowercase().replace(' ', "-"),
        }
    }

    pub fn normalized(&self) -> &str {
        &self.normalized
    }
}

fn main() {
    let slug = Slug::new(" Rust Notes ");
    assert_eq!(slug.normalized(), "rust-notes");
}
```

## Common errors
External callers cannot construct a public struct with private fields directly:

```rust
mod account {
    pub struct AccountId {
        value: u64,
    }
}

fn main() {
    // let id = account::AccountId { value: 7 };
}
```

Typical diagnostic:

```text
error[E0451]: field `value` of struct `AccountId` is private
```

Fix by exposing a constructor:

```rust
mod account {
    pub struct AccountId {
        value: u64,
    }

    impl AccountId {
        pub fn new(value: u64) -> Self {
            Self { value }
        }
    }
}
```

## Best practice
- ✅ Make fields private by default for public domain types.
- ✅ Use `new` for infallible construction and `try_new` when validation can fail.
- ✅ Provide borrowing accessors such as `as_str` or `as_slice` instead of cloning owned fields.
- ✅ Derive common traits only when they preserve the invariant and reveal acceptable information.
- ✅ Keep constructors small enough that their validation rules are auditable.

## Pitfalls
- ⚠️ Public fields freeze your representation into the public API.
- ⚠️ A constructor that does not enforce the invariant gives a false sense of safety.
- ⚠️ Getter methods that clone large fields by default undo ownership benefits.
- ⚠️ Over-validating in constructors can make tests and parsing code painful; separate raw and validated types when needed.
- ⚠️ Do not hide expensive I/O inside a constructor named `new`.

## See also
[[Functions]] · [[Name Resolution]] · [[Readable Generic APIs]] · [[Ownership]] · [[Borrowing]] · [[The Debug Trait]] · [[PartialEq]] · [[Result]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 5.1 "Defining and Instantiating Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Visibility and privacy" — [[the-reference]], https://doc.rust-lang.org/reference/visibility-and-privacy.html
- Idiomatic API design research — [[idiomatic-api-design]]
