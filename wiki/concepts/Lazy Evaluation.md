---
type: concept
title: "Lazy Evaluation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, closures, lazy]
domain: "Closures & Iterators"
difficulty: basic
related: ["[[Iterators]]", "[[Iterator Adapters]]", "[[Consuming Adapters]]", "[[Closures]]", "[[Unconsumed Iterator Adapters]]", "[[Return Iterators Instead of Collecting]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html"]
rust_version: "edition 2024 / 1.85+"
---

# Lazy Evaluation

Lazy evaluation means iterator work and lazy closure fallbacks run only when a consumer actually asks for the result.

## What it is
In Rust iterator code, methods like `map` and `filter` describe future work. They do not run their
closures immediately. The work happens when a consumer such as `collect`, `sum`, `find`, or a
`for` loop pulls items.

The same principle appears in closure-based APIs such as `unwrap_or_else`: the closure is evaluated
only on the branch that needs it.

## How it works
Lazy iterators form a pipeline of small state machines. Each call to `next` asks the pipeline for
one more item. This enables streaming, short-circuiting, and avoiding intermediate allocations.

Short-circuiting consumers are an important part of laziness. `any` can stop at the first `true`;
`find` can stop at the first match; `take(10)` can bound an otherwise long or infinite sequence.

Laziness is pull-based: the consumer asks for one item, each adapter asks its upstream iterator
for only as much as it needs, and closures run as part of that pull. This is why side effects in
`map` are fragile: they are tied to how much of the chain the eventual consumer decides to pull.

## Example
```rust
fn main() {
    let mut calls = 0;
    let first = (1..)
        .map(|n| {
            calls += 1;
            n * n
        })
        .find(|square| *square > 20);

    assert_eq!(first, Some(25));
    assert_eq!(calls, 5);
}
```

The infinite range is safe here because `find` stops once it sees `25`.

## Worked example
```rust
fn main() {
    let mut inspected = Vec::new();

    let result: Vec<i32> = (1..)
        .inspect(|n| inspected.push(*n))
        .filter(|n| n % 3 == 0)
        .take(3)
        .collect();

    assert_eq!(result, vec![3, 6, 9]);
    assert_eq!(inspected, vec![1, 2, 3, 4, 5, 6, 7, 8, 9]);
}
```

The chain only inspects values needed to produce three multiples of three. It does not evaluate
the rest of the infinite range.

## Common errors
```rust
fn main() {
    let mut seen = Vec::new();
    [1, 2, 3].iter().map(|n| seen.push(*n));
    assert!(seen.is_empty());
}
```

This compiles with an `unused Map that must be used` warning, and the assertion passes because
the closure never runs. Replace `map` with a `for` loop or add a real consumer.

## Best practice
- ✅ Use lazy chains to avoid temporary collections when data can flow directly to the final consumer.
- ✅ Use short-circuiting consumers for search and predicates.
- ✅ Return an iterator when callers can benefit from streaming or further composition.
- ✅ Bound infinite iterators with `take`, `take_while`, or a short-circuiting consumer before exhaustive operations.
- ✅ Prefer `unwrap_or_else` over `unwrap_or` when building the fallback is expensive or has side effects.

## Pitfalls
- ⚠️ Expecting `map` or `filter` side effects to run without a terminal consumer. See [[Unconsumed Iterator Adapters]].
- ⚠️ Calling `collect` too early and giving up laziness. See [[Unnecessary Collect]].
- ⚠️ Forgetting to bound infinite iterators before exhaustive consumers.
- ⚠️ Depending on the number of times a predicate runs unless the consumer's stopping behavior is part of the contract.
- ⚠️ Putting essential mutations in `inspect`; reserve it for observation and debugging.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Return Iterators Instead of Collecting]] · [[Unconsumed Iterator Adapters]] · [[Unnecessary Collect]] · [[Zero-Cost Abstractions]] · [[Closures]] · [[Fn, FnMut, FnOnce]]

## Sources
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Rust standard library, `Iterator` trait - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html
