---
type: antipattern
title: "Mutating Collection Keys In Place"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, hashmap, btreemap, invariants]
domain: "std: Collections Deep"
difficulty: advanced
related: ["[[HashMap Hashers and Key Invariants]]", "[[BTreeMap Ordering and Ranges]]", "[[Set Collections with HashSet and BTreeSet]]", "[[Interior Mutability]]", "[[RefCell]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/collections/struct.BTreeMap.html", "https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html"]
rust_version: "edition 2024 / 1.85+"
---

# Mutating Collection Keys In Place

Do not mutate a value's hash, equality, or ordering identity while it is stored in a `HashMap`, `HashSet`, `BTreeMap`, `BTreeSet`, or `BinaryHeap`; remove it, change it, and reinsert it instead.

## The mistake
The mistake is changing the identity of a stored key or heap element in place.
For hash collections, identity is `Hash + Eq`.
For tree collections and heaps, identity is `Ord`.
If that identity changes while the value is inside the collection, the collection's internal placement can become wrong.

Safe Rust normally prevents direct mutation of map keys.
The problem appears through:
- `Cell`
- `RefCell`
- `Mutex` or `RwLock` inside keys
- global state used by comparisons
- I/O-dependent comparisons
- unsafe code

The standard library calls this a logic error.
It is not undefined behavior.
The consequences are unspecified and contained to the collection that observed the error.

## Why it happens
Collections place entries based on identity at insertion time.
`HashMap` chooses buckets using the key's hash and equality.
`BTreeMap` positions entries according to key order.
`BinaryHeap` maintains heap structure according to item order.

If the identity changes after placement, lookup and ordering can no longer trust the structure.
A key may become impossible to find.
Iteration may appear inconsistent.
Operations may panic, loop, leak, or return incorrect results.

The correct model is to treat stored keys and heap priorities as immutable.
To change identity, remove the value, mutate it outside the collection, and insert it again.

## Example
```rust
use std::collections::BTreeSet;

fn main() {
    let mut ids = BTreeSet::from([1, 2, 3]);

    assert!(ids.remove(&2));
    let changed = 20;
    assert!(ids.insert(changed));

    assert_eq!(ids.into_iter().collect::<Vec<_>>(), [1, 3, 20]);
}
```

## Edge cases
```rust
use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq, Hash)]
struct UserKey {
    id: u64,
}

fn main() {
    let mut names = HashMap::new();
    names.insert(UserKey { id: 1 }, "Ada");

    let old_value = names.remove(&UserKey { id: 1 });
    names.insert(UserKey { id: 2 }, old_value.unwrap());

    assert_eq!(names.get(&UserKey { id: 2 }), Some(&"Ada"));
}
```

## Best practice
- ✅ Design key types so identity fields are immutable.
- ✅ Remove, modify, and reinsert when a key or priority must change.
- ✅ Keep mutable payload in the map value, not in the key.
- ✅ Use stable IDs as keys and store changing metadata as values.
- ✅ For priority changes, push a new heap entry and ignore stale entries when that pattern fits the algorithm.
- ✅ Use newtypes to make key identity explicit.
- ✅ Keep `Hash`, `Eq`, and `Ord` implementations pure and deterministic.

## Pitfalls
- ⚠️ Interior mutability inside keys can bypass the compiler's usual protection.
- ⚠️ Changing a field ignored by `Hash`, `Eq`, or `Ord` may be harmless, but it often signals a key design smell.
- ⚠️ Custom comparison that reads global state can make identity change without touching the key.
- ⚠️ Updating a value through `get_mut` is fine; updating key identity is not.
- ⚠️ `insert` with an equivalent key updates the value but keeps the old stored key.
- ⚠️ Heap priority changes require rebuilding, reinserting, or an algorithm that tolerates stale entries.

## See also
[[std: Collections Deep]] · [[HashMap Hashers and Key Invariants]] · [[BTreeMap Ordering and Ranges]] · [[Set Collections with HashSet and BTreeSet]] · [[BinaryHeap Priority Queues]] · [[Interior Mutability]] · [[RefCell]] · [[Cell]] · [[Newtype Pattern]] · [[HashMap Method Families]]

## Sources
- Rust standard library, `HashMap` key logic errors - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Rust standard library, `BTreeMap` key ordering logic errors - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BTreeMap.html
- Rust standard library, `BinaryHeap` priority logic errors - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html
