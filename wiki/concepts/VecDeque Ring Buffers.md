---
type: concept
title: "VecDeque Ring Buffers"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, vecdeque, queues, sequences]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[VecDeque]]", "[[Vec]]", "[[Choosing Standard Collections]]", "[[Capacity and Reallocation]]", "[[Iterating Collections]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.VecDeque.html", "https://doc.rust-lang.org/std/collections/index.html#use-a-vecdeque-when"]
rust_version: "edition 2024 / 1.85+"
---

# VecDeque Ring Buffers

`VecDeque` is a growable ring buffer for queues and double-ended queues, giving efficient push and pop operations at both the front and the back.

## What it is
`VecDeque<T>` is the standard double-ended queue.
It is useful when a sequence needs efficient work at both ends.
It fills the gap between `Vec` and specialized queue structures.

Use `VecDeque` for:
- FIFO queues
- sliding windows
- breadth-first traversal frontiers
- producer-consumer buffers
- deques where both ends are active

Use `Vec` when the sequence mostly grows and shrinks at the end.
The standard docs explicitly note that `Vec` is often faster when both choices are otherwise tied.

## How it works
`VecDeque` stores elements in a growable ring buffer.
The logical start of the sequence may be in the middle of the allocation.
Pushing at the front can move the start backward.
Pushing at the back can move the end forward.
When either side reaches the allocation boundary, indexing wraps around.

This is why `VecDeque` can push and pop at both ends efficiently.
It is also why its contents are not always one contiguous slice.
Methods such as `as_slices` expose the two physical slices.
`make_contiguous` can rotate elements so the logical sequence is one slice.

Common methods include:
- `new`
- `with_capacity`
- `push_back`
- `push_front`
- `pop_back`
- `pop_front`
- `front`
- `back`
- `rotate_left`
- `rotate_right`
- `make_contiguous`

## Example
```rust
use std::collections::VecDeque;

fn main() {
    let mut queue = VecDeque::new();
    queue.push_back("parse");
    queue.push_back("typecheck");
    queue.push_front("read");

    assert_eq!(queue.pop_front(), Some("read"));
    assert_eq!(queue.front(), Some(&"parse"));
    assert_eq!(queue.pop_front(), Some("parse"));
    assert_eq!(queue.pop_front(), Some("typecheck"));
    assert_eq!(queue.pop_front(), None);
}
```

## Edge cases
```rust
use std::collections::VecDeque;

fn main() {
    let mut window: VecDeque<i32> = VecDeque::from([1, 2, 3]);
    window.push_back(4);
    window.pop_front();

    let contiguous = window.make_contiguous();
    contiguous.sort_unstable();

    assert_eq!(window.into_iter().collect::<Vec<_>>(), [2, 3, 4]);
}
```

## Best practice
- ✅ Use `VecDeque` for FIFO queues instead of repeatedly removing `Vec[0]`.
- ✅ Use `push_back` plus `pop_front` for ordinary queue behavior.
- ✅ Use `with_capacity` when a queue has a known upper bound or expected size.
- ✅ Use `front` and `back` to peek without removing.
- ✅ Use `make_contiguous` only when an API needs a single slice or you want to sort the deque.
- ✅ Prefer `Vec` for append-only sequences, stacks, and dense random access workloads.
- ✅ Prefer `BinaryHeap` when the next item is selected by priority rather than arrival order.

## Pitfalls
- ⚠️ Treating `VecDeque` storage as always contiguous is wrong; use `as_slices` or `make_contiguous`.
- ⚠️ Removing from the front of a `Vec` repeatedly is O(n) per removal; use `VecDeque`.
- ⚠️ Assuming `VecDeque` beats `Vec` for all sequence workloads ignores cache locality and simpler layout.
- ⚠️ Holding references into a deque while pushing or popping can conflict with mutation; see [[Holding Collection Element References Across Mutation]].
- ⚠️ `make_contiguous` may move elements inside the allocation, so avoid calling it in a hot loop without need.
- ⚠️ A deque is not a priority queue; see [[BinaryHeap Priority Queues]].

## See also
[[std: Collections Deep]] · [[VecDeque]] · [[Vec]] · [[Choosing Standard Collections]] · [[BinaryHeap Priority Queues]] · [[Capacity and Reallocation]] · [[Iterating Collections]] · [[Holding Collection Element References Across Mutation]] · [[Stale Slice Indices]] · [[Iterator Performance]]

## Sources
- Rust standard library, `VecDeque` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.VecDeque.html
- Rust standard library, "Use a VecDeque when" - [[std]],
  https://doc.rust-lang.org/std/collections/index.html#use-a-vecdeque-when
