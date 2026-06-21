---
type: concept
title: "Iterator predicate search adapters"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, search, any, all, find, position]
domain: "std: Iterator Adapter Catalog"
difficulty: basic
related: ["[[Iterator map and filter]]", "[[Iterator zip and enumerate]]", "[[Iterator sum product and count]]", "[[Option]]", "[[Boolean Logic]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.any", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.all", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator predicate search adapters

`any`, `all`, `find`, and `position` are short-circuiting consumers that answer predicate questions without traversing more items than needed.

## What it is
`Iterator::any` returns `true` if at least one item satisfies a predicate.
It returns `false` for an empty iterator.
`Iterator::all` returns `true` if every item satisfies a predicate.
It returns `true` for an empty iterator.
That empty behavior is the usual logic of existential and universal quantification.
`Iterator::find` returns the first item whose predicate returns `true`.
It returns `Option<Self::Item>`.
`Iterator::position` returns the zero-based index of the first matching item.
It returns `Option<usize>`.
All four methods stop as soon as the final answer is known.
They consume items up to and including the decisive item.

## How it works
`any` takes `&mut self`.
It pulls items until one predicate call returns `true` or the iterator ends.
If it stops early, unconsumed items remain available through the same iterator variable.
`all` pulls items until one predicate call returns `false` or the iterator ends.
`find` passes a reference to each candidate item into the predicate.
This can create double-reference closure parameters when the iterator already yields references.
`position` passes items by value according to the upstream iterator and counts how many non-matching items have been seen.
The position is relative to the current iterator pipeline.
For example, after `skip(10)`, the first remaining item has position `0`.
For fallible predicate checks, stable Rust usually uses `try_fold` or explicit loops.

## Example
```rust
fn main() {
    let values = [3, 7, 10, 12];

    assert!(values.into_iter().any(|n| n % 2 == 0));
    assert!(!values.into_iter().all(|n| n < 10));

    let first_big = values.into_iter().find(|&n| n > 8);
    let first_big_index = values.into_iter().position(|n| n > 8);

    assert_eq!(first_big, Some(10));
    assert_eq!(first_big_index, Some(2));
}
```

## Edge cases
```rust
fn main() {
    let empty: [i32; 0] = [];
    assert!(!empty.into_iter().any(|n| n > 0));
    assert!(empty.into_iter().all(|n| n > 0));

    let data = [1, 2, 3, 4];
    let mut iter = data.into_iter();
    assert_eq!(iter.find(|&n| n == 2), Some(2));
    assert_eq!(iter.next(), Some(3));
}
```

## Best practice
- ✅ Use `any` for existence instead of `filter(...).count() > 0`.
- ✅ Use `all` for validation across a whole stream.
- ✅ Use `find` when you need the first matching item.
- ✅ Use `position` when you need the first matching index.
- ✅ Remember that `find` predicates receive references to candidate items.
- ✅ Use `find_map` when searching and transforming into `Option` at the same time.
- ✅ Treat returned `Option` values explicitly.
- ✅ Use these methods to avoid full traversal when short-circuiting is possible.

## Pitfalls
- ⚠️ Empty `all` returns `true`; this is correct but can surprise validation code.
- ⚠️ Empty `any` returns `false`.
- ⚠️ `position` indexes the adapted stream, not necessarily the original collection.
- ⚠️ `find` consumes through the matching item.
- ⚠️ Double references in `find` predicates can be confusing.
- ⚠️ Using `count` for existence wastes work.
- ⚠️ Calling `unwrap` on a missing `find` or `position` result is [[Unwrap and Expect Overuse]].
- ⚠️ `position` can overflow for more than `usize::MAX` non-matching items.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator map and filter]] · [[Iterator take skip and while bounds]] · [[Iterator zip and enumerate]] · [[Iterator sum product and count]] · [[Iterator collect and FromIterator]] · [[Option]] · [[Result]] · [[Boolean Logic]] · [[Unwrap and Expect Overuse]] · [[Lazy Evaluation]]

## Sources
- Rust standard library, `Iterator::any` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.any
- Rust standard library, `Iterator::all` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.all
- Rust standard library, `Iterator::find` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find
- Rust standard library, `Iterator::position` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position
