---
type: antipattern
title: "Unconsumed Iterator Adapters"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, lazy, footgun]
domain: "Closures & Iterators"
difficulty: basic
related: ["[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Consuming Adapters]]", "[[Iterators]]", "[[Closures]]", "[[Unnecessary Collect]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map"]
rust_version: "edition 2024 / 1.85+"
---

# Unconsumed Iterator Adapters

An unconsumed iterator adapter is a lazy chain like `iter.map(...)` whose result is ignored, so the closure never runs and the code has no effect.

## The mistake
The mistake is writing an adapter chain for its apparent side effects or transformation, then not
ending it with a consuming operation. Rust warns for many of these cases because lazy iterators do
nothing unless consumed.

This often appears as `values.iter().map(|x| do_something(x));` with no `collect`, `for_each`, or
`for` loop.

## Why it happens
In eager collection APIs from other languages, `map` may immediately apply a function. Rust's
iterator adapters are lazy. Creating `Map`, `Filter`, or similar adapter values only builds a
description of future work.

The correct alternative depends on intent: collect transformed values, use a search/aggregate
consumer, or use a loop for side effects.

The warning is powered by `#[must_use]` on iterator adapter types. Silencing it with `let _ = ...`
only says "I intentionally ignored this value"; it does not force evaluation. Evaluation requires
something that pulls from the iterator.

## Example
```rust
fn main() {
    let values = [1, 2, 3];

    let doubled: Vec<i32> = values.iter().copied().map(|n| n * 2).collect();
    assert_eq!(doubled, vec![2, 4, 6]);

    let mut total = 0;
    for n in values {
        total += n;
    }
    assert_eq!(total, 6);
}
```

The transformation is consumed with `collect`; the side effect uses a straightforward loop.

## Worked example
```rust
fn main() {
    let values = [1, 2, 3, 4];

    let total: i32 = values
        .iter()
        .copied()
        .inspect(|n| eprintln!("saw {n}"))
        .filter(|n| n % 2 == 0)
        .sum();

    assert_eq!(total, 6);
}
```

Here `sum` is the real consumer. `inspect` is acceptable for logging because the calculation does
not depend on its side effect.

## Common errors
```rust
fn main() {
    let mut out = Vec::new();
    [1, 2, 3].iter().map(|n| out.push(*n * 2));
    assert!(out.is_empty());
}
```

The compiler warns `unused Map that must be used` and notes that iterators are lazy. The fix is a
`for` loop for side effects, or `let out: Vec<_> = [1, 2, 3].iter().map(|n| n * 2).collect();`
when a transformed collection is the goal.

## Best practice
- ✅ End transformation chains with a consumer such as `collect`, `sum`, `count`, `find`, or `for_each`.
- ✅ Prefer a `for` loop when the primary purpose is side effects.
- ✅ Treat the compiler's unused iterator warning as a real bug unless you intentionally discard the value.
- ✅ Choose the cheapest correct consumer: `any`, `all`, `find`, and `position` can stop early.
- ✅ Use `for_each` when chaining with other iterator logic is clearer than opening a loop, not just to avoid braces.

## Pitfalls
- ⚠️ Using `map` for side effects and assuming the closure will run immediately.
- ⚠️ Adding `let _ = iter.map(...)` to silence the warning; that still discards the lazy work.
- ⚠️ Fixing every warning with `collect::<Vec<_>>()` even when a cheaper consumer exists. See [[Unnecessary Collect]].
- ⚠️ Hiding important side effects in `inspect`, which readers expect to be observational.
- ⚠️ Assuming tests covered a lazy branch when no consumer in the test actually pulled from it.

## See also
[[Closures & Iterators]] · [[Iterator Adapters]] · [[Lazy Evaluation]] · [[Consuming Adapters]] · [[Iterators]] · [[Closures]] · [[Unnecessary Collect]] · [[Return Iterators Instead of Collecting]] · [[Prefer Iterator Pipelines to Manual Indexing]] · [[Zero-Cost Abstractions]]

## Sources
- The Rust Programming Language, ch. 13.2 "Methods That Produce Other Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Rust standard library, `Iterator::map` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map
