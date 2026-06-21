---
type: concept
title: "Iterator rev and last"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, rev, last, double-ended-iterator]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator take skip and while bounds]]", "[[Iterator chain cycle and step_by]]", "[[Consuming Adapters]]", "[[The Iterator Trait]]", "[[VecDeque]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.rev", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.last", "https://doc.rust-lang.org/std/iter/trait.DoubleEndedIterator.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator rev and last

`rev` reverses traversal for double-ended iterators, while `last` consumes any finite iterator to return the final item it yields.

## What it is
`Iterator::rev` is an adapter.
It changes iteration direction from the back toward the front.
It is available only when the iterator implements `DoubleEndedIterator`.
That bound means the iterator can produce items from both ends.
Slices, vectors, ranges, and many standard adapters support this.
Some iterators do not have a known or reachable back end and cannot be reversed.
`Iterator::last` is a consuming method on ordinary iterators.
It advances until the iterator returns `None` and returns the most recent item.
It does not require `DoubleEndedIterator`.
Because `last` walks through the iterator, it can be linear.
For double-ended iterators, `next_back` or `rev().next()` can express "take from the back" directly.

## How it works
`rev` wraps a double-ended iterator in `Rev`.
Calls to `next` on `Rev` call `next_back` on the underlying iterator.
Calls to `next_back` on `Rev` call `next` on the underlying iterator.
It remains lazy and does not allocate.
`last` repeatedly calls `next`.
It stores the newest item it has seen.
When iteration ends, it returns that stored item as `Some(item)`.
If no item was seen, it returns `None`.
On infinite iterators, `last` does not terminate and may be documented as able to panic for some implementations.
Do not use `last` to mean "back element" when a collection has direct back access.
Use collection APIs such as `slice.last()` or `VecDeque::back()` when you already have a collection reference.

## Example
```rust
fn main() {
    let values = [1, 2, 3];

    let reversed: Vec<_> = values.into_iter().rev().collect();
    assert_eq!(reversed, [3, 2, 1]);

    let final_item = [10, 20, 30].into_iter().last();
    assert_eq!(final_item, Some(30));
}
```

## Edge cases
```rust
fn main() {
    let empty: [i32; 0] = [];
    assert_eq!(empty.into_iter().last(), None);

    let after_filter = [1, 2, 3, 4]
        .into_iter()
        .filter(|n| n % 2 == 1)
        .last();
    assert_eq!(after_filter, Some(3));

    let from_back = [1, 2, 3].into_iter().rev().next();
    assert_eq!(from_back, Some(3));
}
```

## Best practice
- ✅ Use `rev` when the iterator is double-ended and reverse traversal is the goal.
- ✅ Use `last` when you need the last item yielded by the current pipeline.
- ✅ Use collection methods like `slice.last()` when you already have a slice and only need a reference.
- ✅ Use `next_back` when working directly with a mutable double-ended iterator.
- ✅ Remember that `last` consumes the entire remaining iterator.
- ✅ Bound infinite iterators before calling `last`.
- ✅ Place `rev` after filters or maps according to the order you actually want to reverse.
- ✅ Prefer clear method order over clever pipelines when combining `rev`, `skip`, and `take`.

## Pitfalls
- ⚠️ `rev` is unavailable unless the iterator implements `DoubleEndedIterator`.
- ⚠️ `last` on an infinite iterator does not finish.
- ⚠️ `last` is not always an O(1) back lookup.
- ⚠️ `iter.rev().last()` returns the original first item, not the original last item.
- ⚠️ Reversing after `enumerate` keeps original indices paired with items but reverses pair order.
- ⚠️ Reversing before `enumerate` creates new indices in reversed order.
- ⚠️ Consuming with `last` discards all earlier items.
- ⚠️ Assuming every adapter preserves double-ended behavior can lead to trait-bound errors.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator take skip and while bounds]] · [[Iterator chain cycle and step_by]] · [[Iterator zip and enumerate]] · [[Iterator predicate search adapters]] · [[Iterator sum product and count]] · [[Consuming Adapters]] · [[The Iterator Trait]] · [[Iterators]] · [[VecDeque]] · [[The Slice Type]]

## Sources
- Rust standard library, `Iterator::rev` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.rev
- Rust standard library, `Iterator::last` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.last
- Rust standard library, `DoubleEndedIterator` - [[std]], https://doc.rust-lang.org/std/iter/trait.DoubleEndedIterator.html
