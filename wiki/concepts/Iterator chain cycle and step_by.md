---
type: concept
title: "Iterator chain cycle and step_by"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, adapter, chain, cycle, step-by]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator take skip and while bounds]]", "[[Iterator zip and enumerate]]", "[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Copy and Clone]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.chain", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.cycle", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.step_by"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator chain cycle and step_by

`chain` appends one iterator after another, `cycle` repeats a cloneable iterator forever, and `step_by` yields the first item and then advances by a fixed positive step.

## What it is
`Iterator::chain` creates a single iterator from two sources with the same item type.
It yields every item from the first source, then every item from the second.
The second argument only needs `IntoIterator`, so arrays and collections can be passed directly.
`Iterator::cycle` repeats an iterator from the beginning after it ends.
It requires the original iterator to implement `Clone`, because it needs a saved copy to restart.
If the original iterator is empty, the cycled iterator is empty.
`Iterator::step_by(step)` samples a stream at a fixed interval.
The first item is always yielded.
The `step` argument must be nonzero.
These adapters reshape traversal without changing item values.

## How it works
`chain` internally holds two iterators.
It polls the first until it is exhausted, then polls the second.
It does not interleave the sources.
`cycle` clones the original iterator to keep a restart point.
When the active iterator ends, it is replaced by a clone of the saved original.
This can produce an infinite iterator, so pair it with `take` when collecting.
`step_by(n)` yields an item, then skips ahead by `n - 1` items before yielding again.
The standard library does not guarantee exactly when skipped items are pulled from the underlying iterator.
For iterators with side effects in `next`, do not rely on precise skip timing beyond yielded values.
`step_by(0)` panics.
The first yielded item is unaffected by the step.

## Example
```rust
fn main() {
    let prefix = ["GET", "/index.html"];
    let suffix = ["HTTP/1.1"];

    let request_line = prefix
        .into_iter()
        .chain(suffix)
        .collect::<Vec<_>>()
        .join(" ");

    assert_eq!(request_line, "GET /index.html HTTP/1.1");
}
```

## Edge cases
```rust
fn main() {
    let repeated: Vec<_> = ["red", "green"]
        .into_iter()
        .cycle()
        .take(5)
        .collect();
    assert_eq!(repeated, ["red", "green", "red", "green", "red"]);

    let sampled: Vec<_> = (0..10).step_by(3).collect();
    assert_eq!(sampled, [0, 3, 6, 9]);
}
```

## Best practice
- ✅ Use `chain` instead of allocating a temporary vector just to append two streams.
- ✅ Use `std::iter::once(value)` with `chain` to add a single prefix or suffix item.
- ✅ Put `take` after `cycle` before collecting or otherwise requiring termination.
- ✅ Use `step_by` only with a positive step.
- ✅ Remember that `step_by` includes the first item.
- ✅ Keep side-effecting iterators away from assumptions about exactly when skipped items are consumed.
- ✅ Prefer `zip` when combining sources pairwise rather than sequentially.
- ✅ Prefer `chain` over nested conditionals when composing optional iterator fragments.

## Pitfalls
- ⚠️ Collecting a `cycle` without a bound never terminates.
- ⚠️ Calling `step_by(0)` panics.
- ⚠️ `chain` requires both sides to yield the same item type.
- ⚠️ `cycle` may be unavailable for iterators that are not `Clone`.
- ⚠️ `cycle` repeats the iterator, not necessarily cloned item values in isolation.
- ⚠️ `step_by` is sampling, not chunking.
- ⚠️ Relying on skipped-item side effects in a specific order is brittle.
- ⚠️ Chaining many different concrete iterator types can produce long types; return `impl Iterator`.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator take skip and while bounds]] · [[Iterator zip and enumerate]] · [[Iterator map and filter]] · [[Iterator collect and FromIterator]] · [[Iterator Adapters]] · [[Lazy Evaluation]] · [[Copy and Clone]] · [[Return Iterators Instead of Collecting]] · [[Unnecessary Collect]] · [[Iterating Collections]]

## Sources
- Rust standard library, `Iterator::chain` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.chain
- Rust standard library, `Iterator::cycle` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.cycle
- Rust standard library, `Iterator::step_by` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.step_by
