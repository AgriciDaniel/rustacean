---
type: concept
title: "Iterator zip and enumerate"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, adapter, zip, enumerate]
domain: "std: Iterator Adapter Catalog"
difficulty: basic
related: ["[[Iterator partition and unzip]]", "[[Iterator Adapters]]", "[[Tuples]]", "[[Vec]]", "[[Iterator predicate search adapters]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.zip", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.enumerate"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator zip and enumerate

`zip` pairs items from two iterators until either side ends, while `enumerate` pairs each item with a zero-based `usize` counter.

## What it is
`Iterator::zip` combines two streams into one stream of tuples.
The left tuple value comes from the receiver.
The right tuple value comes from the argument.
The argument only needs to implement `IntoIterator`, so arrays, vectors, ranges, and iterators all work.
`Iterator::enumerate` is a specialized counter zip.
It yields `(usize, item)` pairs starting at index `0`.
Use `enumerate` when the index is the position in the current iterator pipeline.
Use `zip` with a range when you need a different starting value, step, or integer type.
Both are lazy adapters.
Both preserve item order.
`unzip` can split an iterator of pairs back into two collections.

## How it works
`zip` asks each side for the next item.
If both sides return `Some`, it yields `Some((left, right))`.
If either side returns `None`, the zipped iterator ends.
Extra items on the longer side are not yielded.
This truncating behavior is often correct for lockstep traversal, but it can hide mismatched lengths.
`enumerate` stores a `usize` counter inside the adapter.
It increments the counter after yielding each pair.
The count is over the adapted stream, not necessarily over the original collection before earlier filters or skips.
For extremely long iterators, `enumerate` can overflow `usize`.
In overflow-checking builds, that can panic.
For ordinary finite collections, it is the idiomatic index source.

## Example
```rust
fn main() {
    let names = ["Ada", "Linus", "Grace"];
    let scores = [10, 20, 30];

    let rows: Vec<String> = names
        .into_iter()
        .zip(scores)
        .enumerate()
        .map(|(index, (name, score))| format!("{index}:{name}={score}"))
        .collect();

    assert_eq!(rows, ["0:Ada=10", "1:Linus=20", "2:Grace=30"]);
}
```

## Edge cases
```rust
fn main() {
    let left = [1, 2, 3, 4];
    let right = ["a", "b"];

    let pairs: Vec<_> = left.into_iter().zip(right).collect();
    assert_eq!(pairs, [(1, "a"), (2, "b")]);

    let filtered: Vec<_> = [10, 11, 12]
        .into_iter()
        .filter(|n| n % 2 == 0)
        .enumerate()
        .collect();
    assert_eq!(filtered, [(0, 10), (1, 12)]);
}
```

## Best practice
- ✅ Use `enumerate` instead of manual index variables in iterator pipelines.
- ✅ Use `zip` when two inputs should be processed in lockstep.
- ✅ Validate lengths separately when dropping extra items would be a bug.
- ✅ Use `zip(start.., iter)` or `(start..).zip(iter)` when the counter should start somewhere else.
- ✅ Destructure tuple layers immediately to keep closures readable.
- ✅ Use `unzip` when a pair stream needs to become two collections again.
- ✅ Prefer `position` when only the first matching index is needed.
- ✅ Prefer direct indexing only when random access is central to the algorithm.

## Pitfalls
- ⚠️ `zip` truncates to the shorter iterator and does not report length mismatch.
- ⚠️ `enumerate` indexes after previous adapters, not before them.
- ⚠️ Nested tuples from repeated `zip` calls can become unreadable.
- ⚠️ Manual index loops are often noisier and more fragile; see [[Manual Index Loops for Speed]].
- ⚠️ Assuming `enumerate` uses `u32` or `i32` is wrong; its counter is `usize`.
- ⚠️ Very long enumeration can overflow `usize`.
- ⚠️ Mutating a collection while iterating paired references can violate borrowing rules.
- ⚠️ Zipping owned iterators consumes their inputs.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator partition and unzip]] · [[Iterator predicate search adapters]] · [[Iterator take skip and while bounds]] · [[Iterator Adapters]] · [[Iterating Collections]] · [[Tuples]] · [[Vec]] · [[Manual Index Loops for Speed]] · [[Index Panics vs get]] · [[The Slice Type]]

## Sources
- Rust standard library, `Iterator::zip` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.zip
- Rust standard library, `Iterator::enumerate` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.enumerate
