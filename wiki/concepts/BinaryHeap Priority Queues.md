---
type: concept
title: "BinaryHeap Priority Queues"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, binaryheap, priority-queue, ordering]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[Choosing Standard Collections]]", "[[BTreeMap Ordering and Ranges]]", "[[VecDeque Ring Buffers]]", "[[The Iterator Trait]]", "[[Newtype Pattern]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html", "https://doc.rust-lang.org/std/collections/index.html#use-a-binaryheap-when"]
rust_version: "edition 2024 / 1.85+"
---

# BinaryHeap Priority Queues

`BinaryHeap` is Rust's standard priority queue: it efficiently returns the greatest item according to `Ord`, or the smallest item when values are wrapped in `Reverse`.

## What it is
`BinaryHeap<T>` stores many values but optimizes for repeatedly accessing the highest-priority value.
By default, it is a max-heap.
The item returned by `peek` or `pop` is the greatest item according to `Ord`.

Use it when:
- the next item is chosen by priority
- you do not need sorted iteration over all items
- pushes and pops are frequent
- a full sort after every insertion would be wasteful

Typical examples include schedulers, graph algorithms, top-k selection, and simulation events.

## How it works
A binary heap maintains a partial order.
The top item is always available.
The rest of the collection is not globally sorted.
Pushing and popping are O(log n).
Peeking is O(1).
Converting into a sorted vector consumes the heap and sorts by heap order.

Because it uses `Ord`, priority is part of the value's ordering.
For a min-heap, wrap values in `std::cmp::Reverse`.
For domain-specific priority, use a newtype or struct with derived or custom ordering.
When deriving `Ord` for a struct, field order matters.
Put the most important comparison field first, or implement ordering manually.

Like map and set keys, heap elements must not be mutated in a way that changes their ordering while stored.
Doing so is a logic error.

## Example
```rust
use std::collections::BinaryHeap;

fn main() {
    let mut jobs = BinaryHeap::new();
    jobs.push(3);
    jobs.push(10);
    jobs.push(1);

    assert_eq!(jobs.peek(), Some(&10));
    assert_eq!(jobs.pop(), Some(10));
    assert_eq!(jobs.pop(), Some(3));
    assert_eq!(jobs.pop(), Some(1));
    assert_eq!(jobs.pop(), None);
}
```

## Edge cases
```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

fn main() {
    let mut min_heap = BinaryHeap::new();
    for deadline in [30, 10, 20] {
        min_heap.push(Reverse(deadline));
    }

    assert_eq!(min_heap.pop(), Some(Reverse(10)));
    assert_eq!(min_heap.pop(), Some(Reverse(20)));
    assert_eq!(min_heap.pop(), Some(Reverse(30)));
}
```

## Best practice
- ✅ Use `BinaryHeap` when only the next highest-priority item matters.
- ✅ Use `Reverse<T>` to build a min-heap without custom types.
- ✅ Use a newtype when the natural `Ord` of the stored value is not the desired priority.
- ✅ Use `peek` to inspect the current top without removal.
- ✅ Use `VecDeque` for FIFO work and `BinaryHeap` for priority work.
- ✅ Use `BTreeMap` when you need sorted range queries or ordered traversal, not just the top item.
- ✅ Keep heap elements immutable with respect to their ordering while they are in the heap.

## Pitfalls
- ⚠️ Iterating a heap does not yield sorted order.
- ⚠️ `BinaryHeap` is a max-heap by default; use `Reverse` for smallest-first behavior.
- ⚠️ Deriving `Ord` on a struct may compare fields in an order that does not match the intended priority.
- ⚠️ Mutating an element's priority through interior mutability while it is in the heap is a logic error; see [[Mutating Collection Keys In Place]].
- ⚠️ Do not use `BinaryHeap` when you need fast lookup or removal by key; it is not a map.
- ⚠️ A `BTreeMap<Priority, Vec<Item>>` can be better when priorities group many items and range queries matter.

## See also
[[std: Collections Deep]] · [[Choosing Standard Collections]] · [[VecDeque Ring Buffers]] · [[BTreeMap Ordering and Ranges]] · [[Set Collections with HashSet and BTreeSet]] · [[Newtype Pattern]] · [[The Iterator Trait]] · [[Iterator Performance]] · [[Mutating Collection Keys In Place]] · [[Deriving Traits on Structs]]

## Sources
- Rust standard library, `BinaryHeap` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html
- Rust standard library, "Use a BinaryHeap when" - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#use-a-binaryheap-when
