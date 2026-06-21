---
type: pattern
title: "Choosing Standard Collections"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, std, api-design, performance]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[Choosing Collection Types]]", "[[HashMap Method Families]]", "[[BTreeMap Ordering and Ranges]]", "[[VecDeque Ring Buffers]]", "[[BinaryHeap Priority Queues]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/index.html#when-should-you-use-which-collection", "https://doc.rust-lang.org/std/collections/index.html#performance"]
rust_version: "edition 2024 / 1.85+"
---

# Choosing Standard Collections

Choose the collection by the operation that defines correctness first, then by performance: `Vec` for sequences, `HashMap` for unordered lookup, `BTreeMap` for sorted keys, sets for membership, `VecDeque` for queues, and `BinaryHeap` for priority queues.

## What it is
Rust's standard library provides general-purpose collections.
The practical choice usually starts with the question "what operation must be efficient and correct?"
The standard documentation says `Vec` and `HashMap` cover many ordinary cases.
Other collections are specialized for specific behavior.

This note complements the existing [[Choosing Collection Types]] pattern with a deeper std-focused decision guide.

The main choices are:
- `Vec<T>` for contiguous sequences, stacks, and append-heavy arrays
- `VecDeque<T>` for efficient work at both ends
- `HashMap<K, V>` for unordered key-value lookup
- `BTreeMap<K, V>` for sorted keys and ranges
- `HashSet<T>` for unordered membership
- `BTreeSet<T>` for sorted membership
- `BinaryHeap<T>` for priority queues

## How it works
Correctness constraints narrow the field.
If order is part of output, use an ordered collection or sort before output.
If keys need range queries, use `BTreeMap`.
If only membership matters, use a set.
If every item has a priority and only the next item matters, use `BinaryHeap`.

Performance then refines the choice.
`Vec` is compact and cache-friendly.
`HashMap` has expected O(1) lookup but arbitrary order and hashing costs.
`BTreeMap` has O(log n) lookup but sorted iteration and range operations.
`VecDeque` has efficient front and back operations but is less simple than `Vec`.
`BinaryHeap` has efficient top-priority access but no sorted iteration.

Allocation behavior matters too.
Use capacity hints when you know approximate size.
Avoid shrinking repeatedly.
Prefer iterator adapters when you do not need an intermediate collection.

## Example
```rust
use std::collections::{BTreeMap, BinaryHeap, HashMap, VecDeque};

fn main() {
    let stack = vec!["parse", "check"];

    let mut queue = VecDeque::from(["read", "parse"]);
    queue.push_back("check");

    let counts: HashMap<_, _> = [("error", 2), ("warning", 5)].into_iter().collect();
    let sorted_counts: BTreeMap<_, _> = counts.iter().map(|(&k, &v)| (k, v)).collect();

    let priorities: BinaryHeap<_> = [3, 1, 8].into_iter().collect();

    assert_eq!(stack.last(), Some(&"check"));
    assert_eq!(queue.pop_front(), Some("read"));
    assert_eq!(sorted_counts.keys().copied().collect::<Vec<_>>(), ["error", "warning"]);
    assert_eq!(priorities.peek(), Some(&8));
}
```

## Best practice
- ✅ Start with `Vec` unless you need key lookup, membership, front removal, ordering, or priority behavior.
- ✅ Start with `HashMap` for general maps when deterministic order is not required.
- ✅ Use `BTreeMap` when sorted iteration or ranges are part of the task.
- ✅ Use `HashSet` or `BTreeSet` when there is no meaningful value associated with each key.
- ✅ Use `VecDeque` for FIFO queues and deques.
- ✅ Use `BinaryHeap` for priority queues.
- ✅ Add capacity hints when ingesting a known amount of data.
- ✅ Benchmark only after the operation mix is clear.

## Pitfalls
- ⚠️ Choosing `BTreeMap` only for deterministic tests may hide that production output should sort explicitly.
- ⚠️ Choosing `HashMap` for user-visible output without sorting can create unstable output; see [[HashMap Iteration Order Is Arbitrary]].
- ⚠️ Removing repeatedly from the front of a `Vec` is a queue smell; see [[VecDeque Ring Buffers]].
- ⚠️ Using `BinaryHeap` expecting sorted iteration is wrong; only the top is guaranteed.
- ⚠️ Using a map as a set adds noise and can obscure intent.
- ⚠️ Optimizing collection choice before profiling can become [[Avoiding Premature Optimization]].

## See also
[[std: Collections Deep]] · [[Choosing Collection Types]] · [[HashMap Method Families]] · [[BTreeMap Ordering and Ranges]] · [[Set Collections with HashSet and BTreeSet]] · [[VecDeque Ring Buffers]] · [[BinaryHeap Priority Queues]] · [[Capacity and Reallocation]] · [[Iterator Performance]] · [[Avoiding Premature Optimization]]

## Sources
- Rust standard library, choosing collections - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#when-should-you-use-which-collection
- Rust standard library, collection performance - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#performance
