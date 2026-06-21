---
type: concept
title: "Hash and Eq Contracts"
aliases: ["The Hash Trait"]
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, hash, eq, collections]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[The Hash Trait]]", "[[Equality Traits PartialEq and Eq]]", "[[HashMap]]", "[[BTreeMap and BTreeSet]]"]
sources: ["[[std]]", "[[the-reference]]", "[[api-guidelines]]"]
source_urls: ["https://doc.rust-lang.org/std/hash/trait.Hash.html", "https://doc.rust-lang.org/std/cmp/trait.Eq.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html"]
rust_version: "edition 2024 / 1.85+"
---

# Hash and Eq Contracts

`Hash` is only correct for hash-table keys when it agrees with equality: if two values are equal, they must feed equivalent hash data to the hasher.

## What it is
`Hash` lets a value feed bytes or typed pieces of data into a `Hasher`.
It is used by `HashMap`, `HashSet`, and other hash-based structures.
The required method is `fn hash<H: Hasher>(&self, state: &mut H)`.

The central rule is simple.
If `k1 == k2`, then `hash(k1) == hash(k2)` for the same hasher behavior.
Unequal values may collide.
Equal values must not diverge.

`Hash` does not promise portable or stable hash bytes.
Endianness, platform size, compiler version, and implementation details can affect what is fed into a hasher.
Do not serialize std hashes as stable data.

## How it works
`#[derive(Hash)]` hashes each field in declaration order.
When paired with `#[derive(PartialEq, Eq)]`, the equality/hash contract is upheld if all fields uphold it.

Manual `Hash` is needed when manual equality ignores fields.
For example, if users are equal by `id`, `hash` must hash only the same identity-relevant fields.
Hashing extra non-equality fields breaks lookup.

Implementations should be prefix-free.
The standard docs use strings as an example: `("ab", "c")` must not feed the same logical sequence as `("a", "bc")`.
When you hash structured fields by calling each field's `Hash`, the standard implementations usually handle boundaries appropriately.

`hash_slice` is a convenience method, not a universal substitute for repeated field hashing.
Use it only when the slice is treated as one equality unit.

## Example
```rust
use std::collections::HashSet;
use std::hash::{Hash, Hasher};

#[derive(Debug)]
struct User {
    id: u64,
    display_name: String,
}

impl PartialEq for User {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl Eq for User {}

impl Hash for User {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.id.hash(state);
    }
}

fn main() {
    let mut users = HashSet::new();
    users.insert(User { id: 1, display_name: "Ada".into() });
    users.insert(User { id: 1, display_name: "A. Lovelace".into() });
    assert_eq!(users.len(), 1);
}
```

## Best practice
- ✅ Derive `PartialEq`, `Eq`, and `Hash` together when fieldwise identity is correct.
- ✅ If equality is manual, implement `Hash` from the exact same identity fields.
- ✅ Treat hash behavior as an internal lookup mechanism, not a stable external representation.
- ✅ Test map/set behavior instead of hard-coding hash numbers.
- ✅ Keep hash-relevant fields immutable while a key is inside a hash table.

## Pitfalls
- ⚠️ Do not hash fields ignored by [[Equality Traits PartialEq and Eq]].
- ⚠️ Do not mutate a key's equality or hash identity while it is stored in `HashMap` or `HashSet`.
- ⚠️ Do not use `Hash` output for cryptographic identity.
- ⚠️ Do not assume `DefaultHasher` output is stable across Rust versions.

## See also
[[std: Core Trait Catalog]] · [[The Hash Trait]] · [[Equality Traits PartialEq and Eq]] · [[HashMap]] · [[BTreeMap and BTreeSet]] · [[Deriving Traits on Structs]] · [[Clone Semantics in std]] · [[Ordering Traits PartialOrd and Ord]] · [[Marker Traits]] · [[Custom Error Types]]

## Sources
- Rust standard library, `std::hash::Hash` - [[std]], https://doc.rust-lang.org/std/hash/trait.Hash.html
- Rust standard library, `std::cmp::Eq` - [[std]], https://doc.rust-lang.org/std/cmp/trait.Eq.html
- Rust standard library, `HashMap` - [[std]], https://doc.rust-lang.org/std/collections/struct.HashMap.html
