---
type: antipattern
title: "Implementing Borrow for Partial Views"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, borrow, hashmap, api-design]
domain: "Idioms & API Design"
difficulty: advanced
related: ["[[Borrow for Equivalent Keys]]", "[[AsRef for Flexible Arguments]]", "[[Conversion Traits]]", "[[HashMap]]", "[[Stringly-Typed Code]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/borrow/trait.Borrow.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/hash/trait.Hash.html", "https://doc.rust-lang.org/std/cmp/trait.Eq.html"]
rust_version: "edition 2024 / 1.85+"
---

# Implementing Borrow for Partial Views

Implementing `Borrow` for one convenient field is wrong unless that field has exactly the same equality, ordering, and hashing behavior as the whole value.

## The mistake
Developers often see that `Borrow<str>` enables `HashMap<String, V>` lookup by `&str` and try to copy it for a richer struct.
For example, a `User { id, name }` might implement `Borrow<str>` by returning `name`.

That is only valid if the user's identity is exactly the same as the name string.
If equality or hashing includes `id`, then a borrowed `str` is not an equivalent key.

## Why it happens
The method signature of `Borrow` looks like [[AsRef for Flexible Arguments]].
Both return a borrowed view.
The difference is the semantic contract: `Borrow` is used by collections that require equivalent `Hash`, `Eq`, and `Ord` behavior.

The compiler cannot verify this contract.
Bad implementations can lead to failed lookups and confusing collection behavior.

`HashMap` stores entries according to the hash of the stored key.
Borrowed lookup hashes the borrowed query.
If `Hash` for the stored key includes `id` but `Hash` for the borrowed `str` includes only `name`, lookup starts in the wrong place.
That mismatch is a logic error in the key type's API, not a bug in `HashMap`.

Use a dedicated key type when the lookup identity is a field.
For example, store `HashMap<UserName, User>` if names are the lookup key, or store `HashMap<UserId, User>` if IDs are the lookup key.

## Example
```rust
#[derive(Debug, Hash, PartialEq, Eq)]
struct User {
    id: u64,
    name: String,
}

impl AsRef<str> for User {
    fn as_ref(&self) -> &str {
        &self.name
    }
}

fn greeting(name: impl AsRef<str>) -> String {
    format!("hello, {}", name.as_ref())
}

fn main() {
    let user = User { id: 1, name: String::from("Ferris") };
    assert_eq!(greeting(user), "hello, Ferris");
}
```

## Bad example
This implementation compiles but violates the `Borrow` contract because `User` equality and hashing include `id`.

```rust
use std::borrow::Borrow;
use std::collections::HashMap;

#[derive(Debug, Hash, PartialEq, Eq)]
struct User {
    id: u64,
    name: String,
}

impl Borrow<str> for User {
    fn borrow(&self) -> &str {
        &self.name
    }
}

fn main() {
    let mut users = HashMap::new();
    users.insert(User { id: 1, name: String::from("Ferris") }, "admin");

    assert_eq!(users.get("Ferris"), None);
}
```

The correct design is to key the map by `String`, `UserName`, or `UserId`, then store the full `User` as the value if needed.

## Common errors
There is usually no compiler error for this antipattern.
The common symptom is a test failure or production miss:

```text
assertion `left == right` failed
  left: None
 right: Some(...)
```

Fix the key model instead of trying to tweak hash implementations until one lookup passes.
The owned key and borrowed key must describe the same identity.

## Best practice
- ✅ Use `AsRef` when exposing a field or convenient borrowed representation.
- ✅ Implement [[Borrow for Equivalent Keys]] only when the borrowed view is the whole logical key.
- ✅ Test custom map-key lookup behavior if you implement `Borrow` manually.
- ✅ Prefer transparent [[Newtype Pattern]] wrappers for custom borrowed key implementations.
- ✅ Choose the map key type from the lookup operation you actually need most often.
- ✅ Use `AsRef` or a named accessor for display names, slugs, and other partial views.

## Pitfalls
- ⚠️ Do not implement `Borrow<str>` for a multi-field type whose equality includes more than that string.
- ⚠️ Do not assume successful compilation means the `Borrow` contract is valid.
- ⚠️ Do not use `Borrow` simply to make a function argument flexible.
- ⚠️ Do not make `Hash` ignore fields that `Eq` considers; equal keys must imply equal hashes, and mismatched semantics break collections.
- ⚠️ Do not use interior mutability to change the borrowed identity of a key while it is stored in a map.

## See also
[[Borrow for Equivalent Keys]] · [[AsRef for Flexible Arguments]] · [[Conversion Traits]] · [[HashMap]] · [[Newtype Pattern]] · [[Stringly-Typed Code]] · [[Hash and Eq Contracts]] · [[Collections & Strings]] · [[Idioms & API Design]]

## Sources
- `Borrow` - https://doc.rust-lang.org/std/borrow/trait.Borrow.html
- `HashMap` - https://doc.rust-lang.org/std/collections/struct.HashMap.html
- `Hash` - https://doc.rust-lang.org/std/hash/trait.Hash.html
- `Eq` - https://doc.rust-lang.org/std/cmp/trait.Eq.html
