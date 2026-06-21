---
type: concept
title: "HashMap"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashmap, map]
domain: "Collections & Strings"
difficulty: basic
related: ["[[The Entry API]]", "[[BTreeMap and BTreeSet]]", "[[Choosing Collection Types]]", "[[Ownership]]", "[[Borrowing Strings and Slices]]", "[[Iterating Collections]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-03-hash-maps.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html"]
rust_version: "edition 2024 / 1.85+"
---

# HashMap

`HashMap<K, V>` stores one value per unique key and is the default unordered associative collection for fast key-based lookup.

## What it is
A hash map maps keys of one type to values of one type.
Use it when the program asks "given this key, what value is associated with it?" rather than "what is at index 7?"

`HashMap` is not in the prelude, so bring it into scope with `use std::collections::HashMap;`.
Keys must be hashable and comparable for equality.
Values can be any single type.

The standard `HashMap` has intentionally arbitrary iteration order.
If stable sorted order matters, choose [[BTreeMap and BTreeSet]].

## How it works
Insertion moves owned keys and values into the map unless they are `Copy`.
The map then owns those entries.
Lookups typically borrow a key with `get`, returning `Option<&V>`.

Calling `insert` for an existing key replaces the previous value and returns it as `Option<V>`.
Calling `entry` lets you insert or update based on whether the key is already present without writing separate lookup and mutation logic.

The default hasher is chosen for general-purpose resistance to adversarial inputs, not raw maximum throughput.
Only switch hashers when profiling shows hashing is a real bottleneck and the input trust model allows it.

Lookup can often avoid allocation even when the stored key is owned.
For example, a `HashMap<String, V>` can be queried with `map.get("name")` because `String` supports borrowed lookup by `str`.
This relies on the key's `Hash` and `Eq` behavior being compatible between the owned and borrowed forms.

The equality and hash contract is non-negotiable: if two keys compare equal, they must hash the same way.
Violating that contract is a logic error that can make entries unreachable or duplicated from the map's point of view.

## Example
```rust
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    let team = String::from("Blue");
    let blue_score = scores.get(&team).copied().unwrap_or(0);
    assert_eq!(blue_score, 10);

    let old = scores.insert(String::from("Blue"), 25);
    assert_eq!(old, Some(10));
    assert_eq!(scores.get("Blue"), Some(&25));
}
```

## More realistic example
```rust
use std::collections::HashMap;

fn group_by_extension(paths: &[&str]) -> HashMap<String, Vec<String>> {
    let mut groups = HashMap::new();

    for path in paths {
        let extension = path.rsplit_once('.').map_or("none", |(_, ext)| ext);
        groups
            .entry(extension.to_owned())
            .or_insert_with(Vec::new)
            .push((*path).to_owned());
    }

    groups
}

fn main() {
    let groups = group_by_extension(&["main.rs", "lib.rs", "README", "Cargo.toml"]);

    assert_eq!(groups.get("rs").map(Vec::len), Some(2));
    assert_eq!(groups.get("none").map(Vec::len), Some(1));
    assert!(groups.contains_key("toml"));
}
```

This pattern stores owned strings because the result outlives the input slice.
Inside the function, `entry` avoids a second lookup and cleanly creates each `Vec` on demand.

## Common errors
```text
error[E0599]: the method `insert` exists for struct `HashMap<K, V>`, but its trait bounds were not satisfied
```

The usual cause is that the key type does not implement both `Eq` and `Hash`.
Derive them for simple key structs with `#[derive(PartialEq, Eq, Hash)]`, or implement them consistently by hand.

```text
thread 'main' panicked at 'no entry found for key'
```

Indexing with `map[&key]` is intentionally panicking access.
Use `get`, `get_mut`, or `entry` when absence is part of normal control flow.

## Best practice
- ✅ Use `get` and pattern matching, `copied`, `cloned`, or `unwrap_or` to make missing-key behavior explicit.
- ✅ Use [[The Entry API]] for "insert if absent" and "update based on old value" operations.
- ✅ Use borrowed lookup forms such as `map.get("key")` when the key type supports it, avoiding temporary owned keys.
- ✅ Choose [[BTreeMap and BTreeSet]] when deterministic sorted iteration is part of the requirement.
- ✅ Treat iteration order as unspecified for program behavior and tests.
- ✅ Derive or implement `Eq` and `Hash` together so equal keys always hash equally.
- ✅ Consider `with_capacity` for large maps when the approximate number of entries is already known.

## Pitfalls
- ⚠️ `map[key]` panics if the key is absent; `get` returns `None` instead. See [[Index Panics vs get]].
- ⚠️ Do not write `contains_key` followed by `insert` for entry-style updates; it can duplicate lookup work and fight the borrow checker.
- ⚠️ Do not assume printed or iterated hash map order will remain the same between runs, platforms, or Rust versions.
- ⚠️ Storing references in a map requires the referents to outlive the map; owned `String` or other owned keys are often simpler.
- ⚠️ Do not mutate key state through interior mutability in a way that changes equality or hashing while the key is stored.
- ⚠️ Do not swap in a faster hasher for untrusted keys without understanding HashDoS tradeoffs.

## See also
[[The Entry API]] · [[BTreeMap and BTreeSet]] · [[Set Collections with HashSet and BTreeSet]] · [[Choosing Collection Types]] · [[Iterating Collections]] · [[Ownership]] · [[Borrowing Strings and Slices]] · [[Index Panics vs get]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.3 "Storing Keys with Associated Values in Hash Maps" — [[the-book]], https://doc.rust-lang.org/book/ch08-03-hash-maps.html
- Standard library `HashMap` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Standard library hash map `Entry` docs — [[std]], https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html
