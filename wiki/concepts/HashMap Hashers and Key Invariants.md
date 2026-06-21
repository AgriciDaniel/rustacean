---
type: concept
title: "HashMap Hashers and Key Invariants"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashmap, hashing, hashers]
domain: "std: Collections Deep"
difficulty: advanced
related: ["[[HashMap]]", "[[HashMap Method Families]]", "[[Set Collections with HashSet and BTreeSet]]", "[[Borrow for Equivalent Keys]]", "[[Newtype Pattern]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/hash/trait.BuildHasher.html", "https://doc.rust-lang.org/std/hash/trait.Hash.html"]
rust_version: "edition 2024 / 1.85+"
---

# HashMap Hashers and Key Invariants

`HashMap` correctness depends on a stable key contract: equal keys must hash equally, and a key's `Hash` and `Eq` behavior must not change while the key is stored.

## What it is
Hashing is how `HashMap` and `HashSet` find buckets.
The standard map uses `RandomState` by default.
That default is randomly seeded to resist collision attacks.
The exact default hashing algorithm is not a stable API guarantee.

Keys must implement `Eq` and `Hash`.
The required invariant is:

```text
k1 == k2 -> hash(k1) == hash(k2)
```

This does not require unequal keys to hash differently.
Collisions are allowed.
But equal keys must have equal hashes.

## How it works
`HashMap` stores a hash table.
Lookup hashes the borrowed key, probes the table, and checks equality among candidates.
If equality and hashing disagree, lookup may miss existing entries or produce other incorrect behavior.
The standard library classifies this as a logic error.
It is not undefined behavior, but behavior is not specified beyond being contained to the observing map.

The key's hash and equality must also remain stable while the key is in the map.
This is normally automatic because keys are owned and not mutably accessible through the map.
The risk appears with interior mutability, global state, I/O-dependent comparisons, or unsafe code.

Custom hashers are possible through `with_hasher` and `with_capacity_and_hasher`.
They are advanced tools.
Replacing the default hasher can improve performance in controlled contexts.
It can also remove HashDoS resistance if the hasher is fixed or predictable.
For third-party hashers, cite docs.rs and verify the latest version before adopting one.

## Example
```rust
use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq, Hash)]
struct UserId(u64);

fn main() {
    let mut names = HashMap::new();
    names.insert(UserId(7), "Ferris");

    assert_eq!(names.get(&UserId(7)), Some(&"Ferris"));
    assert_eq!(names.insert(UserId(7), "Rustacean"), Some("Ferris"));
    assert_eq!(names.get(&UserId(7)), Some(&"Rustacean"));
}
```

## Edge cases
```rust
use std::collections::HashMap;
use std::hash::RandomState;

fn main() {
    let state = RandomState::new();
    let mut map = HashMap::with_hasher(state);
    map.insert("language", "Rust");

    assert_eq!(map.get("language"), Some(&"Rust"));
}
```

## Best practice
- ✅ Derive `PartialEq`, `Eq`, and `Hash` together when all fields define identity.
- ✅ Use a newtype when only a subset of fields should define map identity.
- ✅ Keep key equality and hashing pure, deterministic, and independent of mutable global state.
- ✅ Keep stored keys immutable with respect to their equality and hash behavior.
- ✅ Use the default `RandomState` for maps exposed to untrusted keys unless you have a measured reason.
- ✅ Treat alternative hashers as dependencies that need docs.rs review and latest-version verification.
- ✅ Use `Borrow`-compatible keys only when borrowed equality and hashing match owned-key behavior.

## Pitfalls
- ⚠️ Implementing `Eq` by one field and `Hash` by another breaks the map contract.
- ⚠️ Mutating key identity through `Cell`, `RefCell`, global state, or unsafe code is a logic error; see [[Mutating Collection Keys In Place]].
- ⚠️ A faster non-random hasher may be inappropriate for untrusted input.
- ⚠️ Assuming the default hasher is permanently SipHash is wrong; the algorithm is subject to change.
- ⚠️ `HashMap::with_hasher` can be `const` with a fixed hasher, but fixed hashers are not HashDoS resistant.
- ⚠️ If two keys compare equal, `insert` replaces the value but leaves the original stored key.

## See also
[[std: Collections Deep]] · [[HashMap]] · [[HashMap Method Families]] · [[Set Collections with HashSet and BTreeSet]] · [[Borrow for Equivalent Keys]] · [[Newtype Pattern]] · [[Deriving Traits on Structs]] · [[PartialEq]] · [[Mutating Collection Keys In Place]] · [[HashMap Iteration Order Is Arbitrary]]

## Sources
- Rust standard library, `HashMap` hashing and key requirements - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Rust standard library, `BuildHasher` - [[std]],
  https://doc.rust-lang.org/std/hash/trait.BuildHasher.html
- Rust standard library, `Hash` - [[std]],
  https://doc.rust-lang.org/std/hash/trait.Hash.html
