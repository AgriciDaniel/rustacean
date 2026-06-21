---
type: concept
title: "VecDeque"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, vecdeque, queue]
domain: "Collections & Strings"
difficulty: intermediate
related: ["[[Vec]]", "[[Choosing Collection Types]]", "[[Iterating Collections]]", "[[Capacity and Reallocation]]", "[[Ownership]]", "[[Index Panics vs get]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/collections/struct.VecDeque.html", "https://doc.rust-lang.org/std/collections/index.html", "https://doc.rust-lang.org/book/ch08-01-vectors.html"]
rust_version: "edition 2024 / 1.85+"
---

# VecDeque

`VecDeque<T>` is a growable ring-buffer queue optimized for pushing and popping at both the front and back.

## What it is
Use `VecDeque<T>` when the collection acts like a FIFO queue, double-ended queue, or sliding window.
Its default queue shape is `push_back` to enqueue and `pop_front` to dequeue.

It is still an owned homogeneous collection like `Vec<T>`, but its storage may wrap around internally.
That ring-buffer design makes front operations efficient without shifting every element.

`VecDeque` lives in `std::collections`.
It is less common than `Vec`, but it is the standard answer for frequent front removal.

## How it works
`push_front`, `push_back`, `pop_front`, and `pop_back` operate at the two logical ends.
Iteration goes from front to back, independent of the physical wrap inside the buffer.

Because elements may be split into two physical slices, some APIs expose this reality.
`as_slices` returns the two contiguous pieces.
If a single contiguous slice is required, `make_contiguous` rotates the internal buffer and returns `&mut [T]`.

Indexing by position is supported, but it should not be the main design reason to choose `VecDeque`.
For dense random access and back-only growth, [[Vec]] is usually simpler and more cache-friendly.

The logical front can move without moving every element.
When the buffer reaches the physical end of the allocation, new elements may wrap to the beginning.
That is the core difference from `Vec`: `VecDeque` spends a little more complexity to make both ends cheap.

## Example
```rust
use std::collections::VecDeque;

fn main() {
    let mut jobs = VecDeque::new();
    jobs.push_back("parse");
    jobs.push_back("typecheck");
    jobs.push_front("read");

    assert_eq!(jobs.pop_front(), Some("read"));
    assert_eq!(jobs.pop_front(), Some("parse"));

    jobs.push_back("codegen");
    assert_eq!(jobs.iter().copied().collect::<Vec<_>>(), ["typecheck", "codegen"]);
}
```

## More realistic example
```rust
use std::collections::VecDeque;

fn moving_sums(input: &[i32], window: usize) -> Vec<i32> {
    let mut queue = VecDeque::with_capacity(window);
    let mut sum = 0;
    let mut out = Vec::new();

    for &value in input {
        queue.push_back(value);
        sum += value;

        if queue.len() > window {
            sum -= queue.pop_front().expect("window just exceeded its size");
        }

        if queue.len() == window {
            out.push(sum);
        }
    }

    out
}

fn main() {
    assert_eq!(moving_sums(&[1, 2, 3, 4, 5], 3), [6, 9, 12]);
}
```

Sliding windows and breadth-first queues are the common cases where `VecDeque` is clearer and faster than repeatedly removing from the front of a `Vec`.

## Common errors
```text
thread 'main' panicked at 'index out of bounds'
```

`deque[i]` checks bounds just like vector indexing.
Use `deque.get(i)` when the index is derived from input or from a changing queue length.

```text
error[E0502]: cannot borrow `queue` as mutable because it is also borrowed as immutable
```

This appears when code borrows an element and then calls `push_*`, `pop_*`, or `make_contiguous` before the reference is no longer used.
Shorten the borrow, copy the value, or mutate first and borrow afterward.

## Best practice
- ✅ Use `VecDeque` for queues instead of `Vec::remove(0)`.
- ✅ Use `push_back` plus `pop_front` for clear FIFO code.
- ✅ Use `as_slices` when you can handle two contiguous regions.
- ✅ Use `make_contiguous` only when an API truly needs one slice.
- ✅ Prefer `Vec` when front operations are rare and contiguous memory is the main requirement.
- ✅ Use `with_capacity` for bounded queues and windows to avoid early reallocations.
- ✅ Prefer `pop_front` in processing loops so empty queues are handled with `Option` instead of manual length checks.

## Pitfalls
- ⚠️ Do not assume `VecDeque` is physically contiguous at all times; it is logically ordered but may wrap.
- ⚠️ `deque[i]` panics out of bounds; use `get` when an index can be invalid. See [[Index Panics vs get]].
- ⚠️ Avoid repeatedly converting a queue to `Vec` just to process it; consume with `pop_front` or iterate.
- ⚠️ Holding element references while mutating the deque can run into the same invalidation rules as other growable collections.
- ⚠️ Do not pass `as_slices().0` alone to an API unless you are sure the deque has not wrapped or you intentionally want only the first physical segment.
- ⚠️ Do not assume `make_contiguous` is free; it may rotate elements to restore a single slice.

## See also
[[Vec]] · [[Choosing Collection Types]] · [[Iterating Collections]] · [[Capacity and Reallocation]] · [[Index Panics vs get]] · [[Holding Collection Element References Across Mutation]] · [[BinaryHeap Priority Queues]] · [[Ownership]] · [[Collections & Strings]]

## Sources
- Standard library `VecDeque` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.VecDeque.html
- Standard library collections overview — [[std]], https://doc.rust-lang.org/std/collections/index.html
- The Rust Programming Language, ch. 8.1 for vector contrast — [[the-book]], https://doc.rust-lang.org/book/ch08-01-vectors.html
