---
type: pattern
title: "The Entry API"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashmap, entry]
domain: "Collections & Strings"
difficulty: intermediate
related: ["[[HashMap]]", "[[BTreeMap and BTreeSet]]", "[[Iterating Collections]]", "[[Ownership]]", "[[Borrowing Strings and Slices]]", "[[Unnecessary Collect]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-03-hash-maps.html#updating-a-value-based-on-the-old-value", "https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html", "https://doc.rust-lang.org/std/collections/btree_map/enum.Entry.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry"]
rust_version: "edition 2024 / 1.85+"
---

# The Entry API

The Entry API turns "look up a key, maybe insert, then mutate" into one map operation that returns a live handle to the value slot.

## What it is
`entry(key)` exists on `HashMap` and `BTreeMap`.
It returns an enum representing either an occupied key or a vacant key.

Most code uses helper methods such as `or_insert`, `or_insert_with`, `and_modify`, and `or_default`.
These methods let you express map updates without a separate `contains_key` or `get_mut` branch.

The pattern is especially important for counting, grouping, caching defaults, and "insert if absent" logic.

## How it works
`entry` takes ownership of the key because it may need to insert that key into the map.
If the key is already present, the map can discard the provided key and return access to the existing value.

`or_insert(value)` inserts `value` only if vacant and returns `&mut V`.
`or_insert_with(f)` computes the default lazily only if vacant.
`and_modify(f)` mutates an occupied value and passes through the entry so it can be followed by `or_insert`.

The returned mutable reference borrows the map mutably.
Keep that reference's scope small so the map can be used again afterward.

The key passed to `entry` is owned because a vacant entry may need to store it.
For an occupied entry, the provided key is not inserted.
If constructing the key is expensive and many lookups hit existing entries, consider whether `get_mut` plus a separate insertion path is clearer or cheaper for that specific case.

## Example
```rust
use std::collections::HashMap;

fn main() {
    let text = "red blue red green blue red";
    let mut counts: HashMap<&str, usize> = HashMap::new();

    for word in text.split_whitespace() {
        counts
            .entry(word)
            .and_modify(|count| *count += 1)
            .or_insert(1);
    }

    assert_eq!(counts.get("red"), Some(&3));
    assert_eq!(counts.get("green"), Some(&1));
}
```

## More realistic example
```rust
use std::collections::HashMap;

#[derive(Debug, Default, PartialEq)]
struct UserStats {
    logins: usize,
    last_ip: String,
}

fn record_login(stats: &mut HashMap<String, UserStats>, user: &str, ip: &str) {
    stats
        .entry(user.to_owned())
        .and_modify(|entry| {
            entry.logins += 1;
            entry.last_ip.clear();
            entry.last_ip.push_str(ip);
        })
        .or_insert_with(|| UserStats {
            logins: 1,
            last_ip: ip.to_owned(),
        });
}

fn main() {
    let mut stats = HashMap::new();
    record_login(&mut stats, "ada", "10.0.0.1");
    record_login(&mut stats, "ada", "10.0.0.2");

    assert_eq!(stats["ada"].logins, 2);
    assert_eq!(stats.get("ada").map(|stat| stat.last_ip.as_str()), Some("10.0.0.2"));
}
```

`and_modify(...).or_insert_with(...)` keeps the occupied and vacant cases adjacent and avoids building the default value on hits.

## Common errors
```text
error[E0382]: borrow of moved value
```

`map.entry(key)` may move `key` into the map.
If the original key is needed afterward, pass a clone intentionally, use a borrowed lookup first, or restructure so the moved key is no longer needed.

```text
error[E0499]: cannot borrow `map` as mutable more than once at a time
```

The `&mut V` returned by `or_insert`, `or_default`, or occupied-entry methods keeps the whole map mutably borrowed.
Finish using that reference before inserting, removing, or looking up other entries through the same map.

## Best practice
- ✅ Use `*map.entry(key).or_insert(0) += 1` for straightforward counters.
- ✅ Use `or_insert_with` when the default value is expensive to build.
- ✅ Use `or_default` when `V: Default` and the default is exactly what you need.
- ✅ Use `and_modify(...).or_insert(...)` when occupied and vacant behavior differ.
- ✅ Keep the `&mut V` returned by entry methods inside the smallest useful scope.
- ✅ Prefer `or_insert_with` over `or_insert` when creating the fallback allocates, clones, reads files, or performs nontrivial computation.
- ✅ Use the same pattern on `BTreeMap` when ordered output or range queries are also required.

## Pitfalls
- ⚠️ Avoid `if !map.contains_key(&key) { map.insert(key, value); }` when `entry` expresses the operation directly.
- ⚠️ Remember that `entry(key)` may move `key`; clone only if you really need to keep using the original. See [[Needless Clone]].
- ⚠️ Do not mutate the same map again while holding the returned `&mut V`.
- ⚠️ Do not use `or_insert(expensive())` when the value is rarely needed; `or_insert_with(expensive)` avoids eager work.
- ⚠️ Do not use `entry` when you only need a read-only lookup; `get` communicates that no insertion can occur.
- ⚠️ Do not hide complex business logic inside a long chain if a small `match map.entry(key)` is clearer.

## See also
[[HashMap]] · [[BTreeMap and BTreeSet]] · [[Iterating Collections]] · [[Borrowing Strings and Slices]] · [[Ownership]] · [[Needless Clone]] · [[Unnecessary Collect]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.3 Entry examples — [[the-book]], https://doc.rust-lang.org/book/ch08-03-hash-maps.html#updating-a-value-based-on-the-old-value
- Standard library hash map `Entry` docs — [[std]], https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html
- Standard library B-tree map `Entry` docs — [[std]], https://doc.rust-lang.org/std/collections/btree_map/enum.Entry.html
- Standard library `HashMap::entry` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry
