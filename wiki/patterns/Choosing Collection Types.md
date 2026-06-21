---
type: pattern
title: "Choosing Collection Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, design, data-structures]
domain: "Collections & Strings"
difficulty: intermediate
related: ["[[Vec]]", "[[VecDeque]]", "[[HashMap]]", "[[BTreeMap and BTreeSet]]", "[[String and str]]", "[[Capacity and Reallocation]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/index.html", "https://doc.rust-lang.org/book/ch08-00-common-collections.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/collections/struct.BTreeMap.html", "https://doc.rust-lang.org/std/collections/struct.VecDeque.html"]
rust_version: "edition 2024 / 1.85+"
---

# Choosing Collection Types

Choose the collection whose operations match the program's access pattern: sequence, queue, unordered lookup, ordered lookup, unique set, or owned text.

## What it is
Rust's standard collections overlap enough that many problems can be solved several ways.
The idiomatic choice is the one that makes the main operation cheap and the code's intent obvious.

Start with the question the data structure answers.
If the answer is "in this order," think `Vec`.
If it is "next item to process," think `VecDeque`.
If it is "value for this key," think `HashMap`.
If it is "keys in sorted order," think `BTreeMap`.
If it is "owned UTF-8 text," think `String`.

## How it works
`Vec<T>` is the default growable sequence.
It is compact, contiguous, and efficient for iteration and push/pop at the end.

`VecDeque<T>` trades physical contiguity for efficient operations at both ends.
`HashMap<K, V>` provides unordered key lookup.
`BTreeMap<K, V>` and `BTreeSet<T>` provide ordered traversal and range-style operations.

Use sets when the value itself is the key.
Use maps when each key carries associated data.
Use `String` for owned text and `&str` for borrowed text views.

The standard collections overview deliberately recommends starting with `Vec` or `HashMap` for many generic storage problems.
Move to a more specialized collection when its behavior is part of correctness or a measured performance need: front removal, sorted ranges, uniqueness, priority, or text ownership.

## Example
```rust
use std::collections::{BTreeMap, HashMap, VecDeque};

fn main() {
    let mut history = Vec::new();
    history.push("opened");
    history.push("saved");

    let mut queue = VecDeque::new();
    queue.push_back("parse");
    assert_eq!(queue.pop_front(), Some("parse"));

    let mut counts = HashMap::new();
    *counts.entry("warning").or_insert(0) += 1;

    let ordered = BTreeMap::from([("apple", 3), ("banana", 2)]);
    assert_eq!(ordered.keys().copied().collect::<Vec<_>>(), ["apple", "banana"]);
}
```

## More realistic example
```rust
use std::collections::{BTreeMap, HashMap, HashSet, VecDeque};

fn main() {
    let mut recent_errors = VecDeque::with_capacity(100);
    recent_errors.push_back("timeout");
    recent_errors.push_back("reset");

    let mut seen_hosts = HashSet::new();
    assert!(seen_hosts.insert("api-1"));
    assert!(!seen_hosts.insert("api-1"));

    let mut by_status = HashMap::new();
    *by_status.entry(500).or_insert(0) += 1;

    let timeline = BTreeMap::from([(10_u64, "start"), (20, "connect"), (30, "done")]);
    let visible: Vec<_> = timeline.range(10..=20).map(|(_, event)| *event).collect();

    assert_eq!(recent_errors.pop_front(), Some("timeout"));
    assert_eq!(by_status.get(&500), Some(&1));
    assert_eq!(visible, ["start", "connect"]);
}
```

This example uses four collections because the problem has four access patterns:
queueing, membership, keyed counting, and ordered range display.

## Common errors
```text
thread 'main' panicked at 'index out of bounds'
```

This is a symptom of forcing a sequence model onto uncertain keyed or optional data.
If the real question is "is this key present?" use a map or set; if it is "is this index valid?" use `get`.

```text
performance regression from repeated front removal
```

`Vec::remove(0)` is O(n) because all later elements shift.
Use `VecDeque` for sustained queue workloads.

## Best practice
- ✅ Default to `Vec<T>` for ordered, growable lists unless front operations or keyed lookup dominate.
- ✅ Use `VecDeque<T>` for queues and sliding windows.
- ✅ Use `HashMap<K, V>` for fast unordered lookup by key.
- ✅ Use `BTreeMap<K, V>` or `BTreeSet<T>` when sorted order or range traversal is required.
- ✅ Use `String` only for owned text; borrow as `&str` at API boundaries.
- ✅ Use `HashSet<T>` or `BTreeSet<T>` when membership is the data and there is no associated value.
- ✅ Use `BinaryHeap` for priority queues where only the next highest-priority item is needed.

## Pitfalls
- ⚠️ Do not use `Vec<(K, V)>` for frequent key lookup unless the collection is tiny or ordering by insertion is the point.
- ⚠️ Do not use `HashMap` when deterministic sorted output is part of correctness.
- ⚠️ Do not use `Vec::remove(0)` for queue workloads; use [[VecDeque]].
- ⚠️ Do not allocate owned strings for read-only APIs. See [[Borrowing Strings and Slices]].
- ⚠️ Do not choose a collection solely from asymptotic complexity; constants, cache locality, ordering, and clarity matter.
- ⚠️ Do not use `LinkedList` by reflex for insertion-heavy code; `Vec` or `VecDeque` is usually faster and simpler unless a specific linked-list operation is required.

## See also
[[Vec]] · [[VecDeque]] · [[HashMap]] · [[BTreeMap and BTreeSet]] · [[Set Collections with HashSet and BTreeSet]] · [[BinaryHeap Priority Queues]] · [[String and str]] · [[Capacity and Reallocation]] · [[Borrowing Strings and Slices]] · [[Collections & Strings]]

## Sources
- Standard library collections overview — [[std]], https://doc.rust-lang.org/std/collections/index.html
- The Rust Programming Language, ch. 8 "Common Collections" — [[the-book]], https://doc.rust-lang.org/book/ch08-00-common-collections.html
- Standard library `Vec<T>` docs — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html
- Standard library `HashMap` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Standard library `BTreeMap` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.BTreeMap.html
- Standard library `VecDeque` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.VecDeque.html
