---
type: concept
title: "Iterator fold and reduce"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, fold, reduce, accumulator]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Consuming Adapters]]", "[[Iterator sum product and count]]", "[[Iterator scan and peekable]]", "[[Option]]", "[[Integer Overflow]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.fold", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.reduce"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator fold and reduce

`fold` consumes an iterator into an explicit accumulator, while `reduce` consumes it by using the first item as the initial accumulator and returning `None` for an empty iterator.

## What it is
`Iterator::fold` is the general "turn many items into one value" consumer.
It takes an initial accumulator and a closure `FnMut(acc, item) -> acc`.
The accumulator type may differ from the iterator item type.
That makes `fold` useful for building strings, maps, statistics, state machines, and custom summaries.
`Iterator::reduce` is a narrower consumer.
It requires the accumulator and item to be the same type.
It uses the first item as the starting accumulator.
Because an iterator may be empty, `reduce` returns `Option<Self::Item>`.
Both methods consume the iterator.
Neither is an adapter that yields more items.
They belong with [[Consuming Adapters]] rather than purely lazy adapters.

## How it works
`fold(init, f)` starts with `init`.
For each item, it calls `f(current_accumulator, item)`.
The return value becomes the accumulator for the next item.
When the iterator ends, `fold` returns the final accumulator.
This is left-associative for forward iterators.
For non-associative operations like subtraction or string formatting, order matters.
`reduce(f)` first calls `next`.
If there is no first item, it returns `None`.
If there is a first item, it folds the remaining items with that first item as the accumulator.
For simple arithmetic, prefer the specialized consumers `sum` and `product` when they express the intent.
For fallible accumulation on stable Rust, use `try_fold` or collect `Result` values.
On infinite iterators, `fold` and `reduce` usually do not terminate.

## Example
```rust
fn main() {
    let words = ["rust", "is", "precise"];

    let sentence = words.iter().fold(String::new(), |mut acc, word| {
        if !acc.is_empty() {
            acc.push(' ');
        }
        acc.push_str(word);
        acc
    });

    assert_eq!(sentence, "rust is precise");
}
```

## Edge cases
```rust
fn main() {
    let values = [3, 5, 2];

    let max = values.into_iter().reduce(|left, right| left.max(right));
    assert_eq!(max, Some(5));

    let empty: [i32; 0] = [];
    assert_eq!(empty.into_iter().reduce(i32::max), None);

    let total = [1, 2, 3].into_iter().fold(10, |acc, n| acc + n);
    assert_eq!(total, 16);
}
```

## Best practice
- ✅ Use `fold` when you need an explicit identity value or a different accumulator type.
- ✅ Use `reduce` when the first item is the only valid initial value.
- ✅ Use `sum`, `product`, `min`, or `max` when those names express the operation directly.
- ✅ Remember that `reduce` returns `Option`; handle the empty case intentionally.
- ✅ Keep accumulator updates cheap and clear; a small `for` loop can be more readable for complex mutation.
- ✅ Use `try_fold` for fallible or short-circuiting accumulation on stable Rust.
- ✅ Watch order when the operation is not associative.
- ✅ Give the accumulator a concrete type when inference becomes unclear.

## Pitfalls
- ⚠️ Using `reduce(...).unwrap()` on possibly empty input recreates [[Unwrap and Expect Overuse]].
- ⚠️ Folding an infinite iterator without a short-circuiting method will not finish.
- ⚠️ Choosing `fold` for simple addition can hide intent compared with `sum`.
- ⚠️ Performing repeated `format!` in a fold can allocate on every step.
- ⚠️ Assuming left and right folds give the same answer is wrong for non-associative operations.
- ⚠️ Ignoring integer overflow in an accumulator can cause panics in debug and wrapping in release; see [[Integer Overflow]].
- ⚠️ Mutating external state in the closure can make a fold harder to reason about than a loop.
- ⚠️ Returning borrowed data from inside the closure has the same lifetime limits as any closure.

## See also
[[std: Iterator Adapter Catalog]] · [[Consuming Adapters]] · [[Iterator sum product and count]] · [[Iterator scan and peekable]] · [[Iterator collect and FromIterator]] · [[Option]] · [[Result]] · [[Integer Overflow]] · [[Closures]] · [[Fn, FnMut, FnOnce]] · [[Unwrap and Expect Overuse]]

## Sources
- Rust standard library, `Iterator::fold` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.fold
- Rust standard library, `Iterator::reduce` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.reduce
