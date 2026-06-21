---
type: concept
title: "LinkedList"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, linkedlist, sequence]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[Vec]]", "[[VecDeque]]", "[[Choosing Standard Collections]]", "[[Capacity and Reallocation]]", "[[Ownership]]", "[[Iterating Collections]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.LinkedList.html", "https://doc.rust-lang.org/std/collections/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# LinkedList

`LinkedList<T>` is Rust's standard owned doubly linked list, useful mainly when you truly need list splitting, whole-list appending, or non-amortized end operations.

## What it is
`LinkedList<T>` stores elements in individually allocated nodes linked forward and backward.
It supports efficient push and pop at both ends, and it can append one whole list to another without moving every element.
It is part of `std::collections`.

Most programs should still start with [[Vec]] or [[VecDeque]].
The standard collections overview explicitly treats `LinkedList` as a niche choice.
Its per-node allocation, pointer chasing, and poor cache locality often make it slower than contiguous collections even when big-O notation looks attractive.

Use it only when the operation mix is genuinely list-shaped:
you maintain separate lists and splice them with `append`, split off suffixes, or need predictable end insertion without a growable contiguous buffer.

## How it works
Each node owns one `T` and links to neighboring nodes.
The list owns the chain, so dropping the list drops every element.
`push_front`, `push_back`, `pop_front`, and `pop_back` operate at the ends.
`front`, `back`, `front_mut`, and `back_mut` borrow end elements without removing them.

`append(&mut other)` moves all nodes from `other` to the back of `self`.
Afterward, `other` is empty.
This is the strongest standard-library reason to choose `LinkedList`: moving a whole list can be constant-time at the list level.

`split_off(at)` returns the suffix starting at `at` and leaves the prefix in the original list.
Finding the split position still requires walking nodes, so it is not random access.
Index-like work is a smell; use [[Vec]] for dense indexing and [[VecDeque]] for queues.

Iteration visits elements from front to back.
`into_iter` consumes the list and yields owned elements, while `iter` and `iter_mut` borrow.

## Example
```rust
use std::collections::LinkedList;

fn main() {
    let mut work = LinkedList::from(["parse", "typecheck", "codegen"]);

    assert_eq!(work.pop_front(), Some("parse"));
    work.push_back("link");

    let mut later = work.split_off(1);
    assert_eq!(work.into_iter().collect::<Vec<_>>(), vec!["typecheck"]);

    later.push_front("borrow-check");
    assert_eq!(
        later.into_iter().collect::<Vec<_>>(),
        vec!["borrow-check", "codegen", "link"]
    );
}
```

## Worked example
Whole-list append is the case where `LinkedList` can express intent directly.
The source list is drained into the destination list without cloning elements.

```rust
use std::collections::LinkedList;

fn merge_batches(mut ready: LinkedList<u32>, mut delayed: LinkedList<u32>) -> LinkedList<u32> {
    ready.append(&mut delayed);
    assert!(delayed.is_empty());
    ready
}

fn main() {
    let ready = LinkedList::from([1, 2]);
    let delayed = LinkedList::from([3, 4]);

    let merged = merge_batches(ready, delayed);
    assert_eq!(merged.into_iter().collect::<Vec<_>>(), vec![1, 2, 3, 4]);
}
```

If the program is repeatedly popping from the front and pushing at the back of one queue, [[VecDeque]] is usually the better choice.
If the program is collecting items and iterating them, [[Vec]] is usually better.

## Common operations
- `push_front(value)` and `push_back(value)` insert at the two ends.
- `pop_front()` and `pop_back()` remove from the two ends and return `Option<T>`.
- `front()` and `back()` borrow the end elements.
- `front_mut()` and `back_mut()` mutably borrow the end elements.
- `append(&mut other)` moves all elements from `other` to the back of `self`.
- `split_off(at)` moves the suffix into a new `LinkedList`.
- `clear()` removes all elements.
- `iter()`, `iter_mut()`, and `into_iter()` provide borrowed, mutable, and owning traversal.

## Best practice
- ✅ Prefer [[Vec]] for compact storage, random access, sorting, and append-at-end workloads.
- ✅ Prefer [[VecDeque]] for FIFO queues and double-ended queues.
- ✅ Choose `LinkedList` only when whole-list append or splitting is a central operation.
- ✅ Keep list APIs at the list level; avoid designing around numeric indexes.
- ✅ Use `pop_front` and `pop_back` to model empty-list handling with `Option`.
- ✅ Consume with `into_iter` when the list is no longer needed and elements should move out.
- ✅ Benchmark before replacing a contiguous collection with `LinkedList` for performance.
- ✅ Document why `LinkedList` is the right collection when it appears in production code.

## Pitfalls
- ⚠️ Do not choose `LinkedList` just because insertion in the middle sounds O(1); reaching the middle is still a traversal.
- ⚠️ Do not expect better performance than `Vec` or `VecDeque` for ordinary queues or sequences.
- ⚠️ Do not use it for random access; it has no efficient indexing model.
- ⚠️ Do not forget that each node is a separate allocation with pointer overhead.
- ⚠️ Do not rely on unstable cursor or removal APIs in stable 1.85+ notes.
- ⚠️ Do not clone elements to merge lists; use `append` when list ownership can move.
- ⚠️ Do not keep long-lived mutable element borrows while trying to mutate the list structure.
- ⚠️ Do not use a linked list as a default teaching answer for Rust collections; the standard docs recommend `Vec` or `HashMap` for most storage.

## See also
[[Vec]] · [[VecDeque]] · [[VecDeque Ring Buffers]] · [[Choosing Standard Collections]] ·
[[Choosing Collection Types]] · [[Iterating Collections]] · [[Capacity and Reallocation]] ·
[[Ownership]] · [[The Drop Trait]] · [[Index Panics vs get]] · [[std: Collections Deep]]

## Sources
- Rust standard library, `LinkedList` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.LinkedList.html
- Rust standard library, collections overview - [[std]],
  https://doc.rust-lang.org/std/collections/index.html
