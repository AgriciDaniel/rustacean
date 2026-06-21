---
type: concept
title: "Iterator take skip and while bounds"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, adapter, take, skip]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator chain cycle and step_by]]", "[[Iterator predicate search adapters]]", "[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Borrowing]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.take", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.skip", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.take_while", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.skip_while"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator take skip and while bounds

`take` and `skip` bound an iterator by count, while `take_while` and `skip_while` bound it by an initial run of items matching a predicate.

## What it is
`Iterator::take(n)` yields at most the first `n` items.
It is the standard way to make a finite prefix from a longer or infinite iterator.
`Iterator::skip(n)` discards at most the first `n` items, then yields the rest.
`Iterator::take_while(predicate)` yields items only while the predicate returns `true`.
Once the first `false` appears, it stops permanently.
`Iterator::skip_while(predicate)` discards items only while the predicate returns `true`.
Once the first `false` appears, it yields that item and every remaining item.
The while adapters are prefix-oriented, not whole-stream filters.
Use `filter` when every item should be tested independently.
Use these methods for headers, prefixes, pagination, sentinels, and bounded sampling.

## How it works
`take` stores a remaining count.
Each successful `next` decrements the count until it reaches zero.
`skip` consumes from the upstream iterator until the skip count is exhausted or the upstream iterator ends.
Then it passes through later items.
`take_while` and `skip_while` receive predicates of type `FnMut(&Self::Item) -> bool`.
Like `filter`, this can produce `&&T` closure arguments when the upstream iterator yields references.
`take_while` must inspect the first failing item to know that it should stop.
For a consuming iterator, that failing item is consumed and not returned later.
`skip_while` yields the first item that fails the predicate.
All four adapters are lazy and preserve order.
They are often combined with `by_ref` when part of an iterator should be consumed and the rest reused.

## Example
```rust
fn main() {
    let mut words = ["header", "body", "body", "tail"].into_iter();

    let first_two: Vec<_> = words.by_ref().take(2).collect();
    let rest: Vec<_> = words.collect();

    assert_eq!(first_two, ["header", "body"]);
    assert_eq!(rest, ["body", "tail"]);
}
```

## Edge cases
```rust
fn main() {
    let values = [1, 2, 0, 3, 4];

    let before_zero: Vec<_> = values
        .into_iter()
        .take_while(|&n| n != 0)
        .collect();
    assert_eq!(before_zero, [1, 2]);

    let after_prefix: Vec<_> = [-2, -1, 0, -3]
        .into_iter()
        .skip_while(|n| *n < 0)
        .collect();
    assert_eq!(after_prefix, [0, -3]);
}
```

## Best practice
- ✅ Use `take` to cap infinite iterators before collecting.
- ✅ Use `skip` and `take` together for simple offset-limit pagination.
- ✅ Use `take_while` for a prefix that ends at a sentinel.
- ✅ Use `skip_while` for dropping a leading prefix only.
- ✅ Use `filter` when later matching items should still be considered.
- ✅ Use `by_ref` when you need to keep using the original iterator after a partial consume.
- ✅ Pattern-match predicate parameters to handle references clearly.
- ✅ Document whether the boundary item is kept or consumed for sentinel parsing.

## Pitfalls
- ⚠️ `take_while` consumes the first item that returns `false` on a consuming iterator.
- ⚠️ `skip_while` stops testing after the first `false`; later matching items are still yielded.
- ⚠️ `take(n)` on a shorter iterator just yields fewer items, with no error.
- ⚠️ `skip(n)` on a shorter iterator yields an empty iterator, with no error.
- ⚠️ Collecting a huge or infinite iterator before `take` defeats the point; see [[Unnecessary Collect]].
- ⚠️ Double-reference predicates can obscure intent.
- ⚠️ Using `skip` for large offsets on non-random-access iterators still advances through skipped items.
- ⚠️ Forgetting `by_ref` moves the iterator into the adapter and prevents later direct use.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator map and filter]] · [[Iterator predicate search adapters]] · [[Iterator chain cycle and step_by]] · [[Iterator flat_map and flatten]] · [[Iterator collect and FromIterator]] · [[Iterator Adapters]] · [[Lazy Evaluation]] · [[Borrowing]] · [[Unnecessary Collect]] · [[Iterating Collections]]

## Sources
- Rust standard library, `Iterator::take` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.take
- Rust standard library, `Iterator::skip` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.skip
- Rust standard library, `Iterator::take_while` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.take_while
- Rust standard library, `Iterator::skip_while` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.skip_while
