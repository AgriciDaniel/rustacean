---
type: moc
title: "std: Collections Deep"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, std, moc]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[Collections & Strings]]", "[[HashMap Method Families]]", "[[Choosing Standard Collections]]", "[[BTreeMap Ordering and Ranges]]", "[[HashMap Hashers and Key Invariants]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/index.html", "https://doc.rust-lang.org/std/collections/struct.HashMap.html", "https://doc.rust-lang.org/std/collections/struct.BTreeMap.html"]
rust_version: "edition 2024 / 1.85+"
---

# std: Collections Deep

This map links the standard-library collection notes for choosing, operating, and avoiding footguns in Rust's deeper collection APIs.

## What it is
This MOC is the hub for the "std: Collections Deep" domain.
It covers map methods, entry APIs, ordered maps, sets, queues, heaps, hashers, and collection-specific footguns.
The goal is practical recall: choose the right standard collection and use its methods without relying on unspecified behavior.

## Core notes
[[Choosing Standard Collections]] is the decision guide.
[[HashMap Method Families]] organizes the large `HashMap` API by use case.
[[Entry API for Accumulator Maps]] focuses on one-lookup conditional updates.
[[BTreeMap Ordering and Ranges]] explains sorted maps, ranges, and boundary methods.
[[Set Collections with HashSet and BTreeSet]] covers membership collections.
[[HashSet]] covers the standard unordered membership set directly.
[[VecDeque Ring Buffers]] covers queues and double-ended queues.
[[LinkedList]] covers the standard owned doubly linked list and why it is niche.
[[BinaryHeap Priority Queues]] covers priority-first work queues.
[[HashMap Hashers and Key Invariants]] explains hashers and key contracts.
[[try_reserve and Fallible Allocation]] covers recoverable capacity growth.
[[HashMap Iteration Order Is Arbitrary]] captures the determinism footgun.
[[Mutating Collection Keys In Place]] captures key and priority identity logic errors.

## Existing related notes
[[HashMap]] already covers the base map concept.
[[BTreeMap and BTreeSet]] already covers the standard ordered map and set pair.
[[VecDeque]] already covers the base deque concept.
[[The Entry API]] already covers the general entry idiom.
[[Choosing Collection Types]] already covers general collection selection.
[[Borrow for Equivalent Keys]] is important for lookup with borrowed forms.
[[Iterating Collections]] is the broader iterator pattern for collections.
[[Capacity and Reallocation]] is the broader allocation model.

## How it works
Start from the operation that defines correctness.
If you need arbitrary indexed or append-heavy sequence storage, begin with [[Vec]].
If you need FIFO behavior, go to [[VecDeque Ring Buffers]].
If you need unordered key-value lookup, go to [[HashMap Method Families]].
If you need sorted keys, go to [[BTreeMap Ordering and Ranges]].
If you need only membership, go to [[Set Collections with HashSet and BTreeSet]].
If you need priority-first retrieval, go to [[BinaryHeap Priority Queues]].
If you need conditional insertion or accumulation, go to [[Entry API for Accumulator Maps]].
If you are designing keys or changing hashers, go to [[HashMap Hashers and Key Invariants]].
If allocation failure should be recoverable, go to [[try_reserve and Fallible Allocation]].

## Example
```rust
use std::collections::{BTreeMap, BinaryHeap, HashMap, VecDeque};

fn main() {
    let mut counts = HashMap::new();
    for word in ["rust", "std", "rust"] {
        *counts.entry(word).or_insert(0) += 1;
    }

    let sorted: BTreeMap<_, _> = counts.iter().map(|(&k, &v)| (k, v)).collect();
    let mut queue = VecDeque::from(["read", "write"]);
    let priorities: BinaryHeap<_> = [2, 5, 1].into_iter().collect();

    assert_eq!(sorted.keys().copied().collect::<Vec<_>>(), ["rust", "std"]);
    assert_eq!(queue.pop_front(), Some("read"));
    assert_eq!(priorities.peek(), Some(&5));
}
```

## Best practice
- ✅ Prefer the standard collection whose semantics match the task before reaching for crates.
- ✅ Use `Vec` and `HashMap` as defaults only when their semantics really fit.
- ✅ Make ordering explicit: sort, use `BTreeMap`, or document arbitrary order.
- ✅ Use `entry` for accumulator maps and conditional map updates.
- ✅ Use sets when there is no meaningful value.
- ✅ Keep key identity stable while values are stored.
- ✅ Check collection-specific docs for complexity, panics, and allocation behavior.
- ✅ For third-party collection or hasher crates, cite docs.rs and verify the latest version.

## Pitfalls
- ⚠️ Do not depend on `HashMap` or `HashSet` iteration order.
- ⚠️ Do not mutate key identity in place.
- ⚠️ Do not use `Vec` front removal as a queue.
- ⚠️ Do not expect `BinaryHeap` iteration to be sorted.
- ⚠️ Do not replace the default hasher for untrusted input without understanding HashDoS tradeoffs.
- ⚠️ Do not use nightly-only APIs in stable 1.85+ notes unless explicitly marked.
- ⚠️ Do not use a map where a set would communicate intent better.
- ⚠️ Do not benchmark collection alternatives before identifying the real operation mix.

## See also
[[Collections & Strings]] · [[HashMap Method Families]] · [[Entry API for Accumulator Maps]] · [[BTreeMap Ordering and Ranges]] · [[Set Collections with HashSet and BTreeSet]] · [[HashSet]] · [[LinkedList]] · [[VecDeque Ring Buffers]] · [[BinaryHeap Priority Queues]] · [[try_reserve and Fallible Allocation]] · [[Choosing Standard Collections]] · [[HashMap Hashers and Key Invariants]] · [[HashMap Iteration Order Is Arbitrary]] · [[Mutating Collection Keys In Place]] · [[HashMap]] · [[The Entry API]]

## Sources
- Rust standard library, collections overview - [[std]],
  https://doc.rust-lang.org/std/collections/index.html
- Rust standard library, `HashMap` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html
- Rust standard library, `BTreeMap` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BTreeMap.html
