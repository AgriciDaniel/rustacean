---
type: pattern
title: "Borrow for Equivalent Keys"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, borrow, hashmap, api-design]
domain: "Idioms & API Design"
difficulty: advanced
related: ["[[Conversion Traits]]", "[[AsRef for Flexible Arguments]]", "[[HashMap]]", "[[Implementing Borrow for Partial Views]]", "[[Borrowing]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/borrow/trait.Borrow.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/hash/trait.Hash.html", "https://doc.rust-lang.org/std/cmp/trait.Eq.html"]
rust_version: "edition 2024 / 1.85+"
---

# Borrow for Equivalent Keys

`Borrow<T>` is for borrowed views that behave equivalently to the owned value for `Eq`, `Ord`, and `Hash`, which is why maps can look up `String` keys by `&str`.

## What it is
`Borrow<T>` also converts `&Self` to `&T`, but it carries a semantic contract beyond the type signature.
If a type implements `Borrow<Q>`, the borrowed `Q` must compare, order, and hash the same way as the owned type.

This is stricter than [[AsRef for Flexible Arguments]].
`AsRef` says "you can cheaply view me as this."
`Borrow` says "this borrowed view is the same key for collection behavior."

## How it works
Collections such as `HashMap<K, V>` use `Borrow<Q>` to support lookups with a borrowed key.
A `HashMap<String, V>` can be queried with `&str` because `String: Borrow<str>` and the hash/equality behavior is compatible.

Custom key types should implement `Borrow` only when the borrowed form represents the whole key identity.
If it is just a convenient view or a single display field, implement `AsRef` instead.

The important signature is on lookup methods such as `HashMap::get`: the stored key `K` must implement `Borrow<Q>`, and the queried `Q` must have compatible `Hash` and `Eq`.
The map hashes the borrowed query and searches buckets that were organized using the stored key's hash.
If the stored and borrowed forms disagree about equality or hashing, the algorithm can miss entries that "look" present to a human reader.

This is a logic contract, not an unsafe-code contract.
Violating it should not cause undefined behavior, but it can produce incorrect lookups, duplicate-looking keys, or surprising removals.

## Example
```rust
use std::borrow::Borrow;
use std::collections::HashMap;

#[derive(Debug, Hash, PartialEq, Eq)]
struct Name(String);

impl Borrow<str> for Name {
    fn borrow(&self) -> &str {
        &self.0
    }
}

fn main() {
    let mut scores = HashMap::new();
    scores.insert(Name(String::from("Ferris")), 10);

    assert_eq!(scores.get("Ferris"), Some(&10));
    assert_eq!(scores.get("Crab"), None);
}
```

## Edge case: case-insensitive keys
A case-insensitive key usually must not implement `Borrow<str>` because `str` hashing and equality are case-sensitive.
Expose `AsRef<str>` for display or diagnostics instead.

```rust
#[derive(Debug, Clone)]
struct CaseInsensitive(String);

impl PartialEq for CaseInsensitive {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq_ignore_ascii_case(&other.0)
    }
}

impl Eq for CaseInsensitive {}

impl AsRef<str> for CaseInsensitive {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

fn main() {
    let key = CaseInsensitive(String::from("Ferris"));
    assert_eq!(key.as_ref(), "Ferris");
    assert!(key == CaseInsensitive(String::from("ferris")));
}
```

## Common errors
Bad `Borrow` implementations compile because the compiler cannot compare your `Hash` and `Eq` semantics.
The symptom is usually a lookup that unexpectedly returns `None`:

```rust
use std::collections::HashMap;

fn main() {
    let mut map = HashMap::new();
    map.insert(String::from("Ferris"), 1);
    assert_eq!(map.get("Ferris"), Some(&1));
}
```

For custom keys, add tests like this for every borrowed lookup form.
If the borrowed form is not exactly the stored key's identity, remove the `Borrow` impl and use `AsRef` or a dedicated lookup method.

## Best practice
- ✅ Implement `Borrow` for transparent key wrappers where the borrowed target is the same logical key.
- ✅ Ensure `Hash`, `Eq`, and `Ord` for the owned type match the borrowed view.
- ✅ Use `AsRef` instead when you only need a convenient field or representation.
- ✅ Prefer standard implementations such as `String: Borrow<str>` when designing map APIs.
- ✅ Derive `Hash`, `Eq`, and `PartialEq` for transparent wrappers when the derived behavior really matches the borrowed target.
- ✅ Write lookup tests with both owned and borrowed keys before exposing a manual `Borrow` implementation.

## Pitfalls
- ⚠️ Do not implement `Borrow<str>` for a struct whose equality includes fields other than that `str`; see [[Implementing Borrow for Partial Views]].
- ⚠️ Do not assume the compiler checks the `Borrow` equality/hash contract; it is a library-level invariant.
- ⚠️ Avoid using `Borrow` merely to make function parameters more flexible; use [[AsRef for Flexible Arguments]].
- ⚠️ Do not implement `Borrow<str>` for case-insensitive text unless the borrowed query type has the same case-insensitive semantics.
- ⚠️ Do not mutate key identity through interior mutability while the key is stored in a map.

## See also
[[Conversion Traits]] · [[AsRef for Flexible Arguments]] · [[HashMap]] · [[Borrowing]] · [[Implementing Borrow for Partial Views]] · [[Newtype Pattern]] · [[Hash and Eq Contracts]] · [[Collections & Strings]] · [[Idioms & API Design]]

## Sources
- `Borrow` - https://doc.rust-lang.org/std/borrow/trait.Borrow.html
- `HashMap` - https://doc.rust-lang.org/std/collections/struct.HashMap.html
- `Hash` - https://doc.rust-lang.org/std/hash/trait.Hash.html
- `Eq` - https://doc.rust-lang.org/std/cmp/trait.Eq.html
