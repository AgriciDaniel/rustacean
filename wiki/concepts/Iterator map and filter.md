---
type: concept
title: "Iterator map and filter"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, adapter, map, filter]
domain: "std: Iterator Adapter Catalog"
difficulty: basic
related: ["[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Closures]]", "[[Fn, FnMut, FnOnce]]", "[[Iterator collect and FromIterator]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter_map"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator map and filter

`map` transforms each iterator item, while `filter` keeps only items whose predicate returns `true`; both are lazy adapters that do no work until the iterator is consumed.

## What it is
`Iterator::map` is the standard adapter for changing item shape.
It takes a closure `FnMut(Self::Item) -> B`.
The returned iterator yields one `B` for each input item.
It is the right tool for field projection, parsing after validation, formatting, numeric conversion, and building domain values.
`Iterator::filter` is the standard adapter for selection.
It takes a closure `FnMut(&Self::Item) -> bool`.
The returned iterator yields the original item, unchanged, when the predicate returns `true`.
Together they express the common "select then transform" and "transform then select" pipelines.
`filter_map` combines both when the mapping itself can fail or choose to skip.
These adapters are part of [[Iterator Adapters]] and inherit [[Lazy Evaluation]].

## How it works
The closure passed to `map` receives the item by value according to the upstream iterator.
If the upstream iterator yields `T`, the closure receives `T`.
If it yields `&T`, the closure receives `&T`.
The closure passed to `filter` receives a reference to the item that would be yielded.
That means `slice.iter().filter(...)` often has a `&&T` predicate argument.
Use pattern matching in closure parameters to make this readable.
`filter` does not clone, move into a new collection, or allocate by itself.
It just stores the predicate and asks the upstream iterator for values as needed.
`map` also does not allocate by itself.
Allocations appear only if the closure allocates or a consumer such as `collect::<Vec<_>>()` builds storage.
Because both adapters are lazy, an unused `map` or `filter` pipeline has no observable effect.
Use a consumer like `collect`, `sum`, `for_each`, `find`, or a `for` loop to drive it.

## Example
```rust
fn main() {
    let numbers = [1, 2, 3, 4, 5, 6];

    let labels: Vec<String> = numbers
        .into_iter()
        .filter(|n| n % 2 == 0)
        .map(|n| format!("even:{n}"))
        .collect();

    assert_eq!(labels, ["even:2", "even:4", "even:6"]);
}
```

## Edge cases
```rust
fn main() {
    let words = ["7", "nope", "11", ""];

    let parsed: Vec<i32> = words
        .iter()
        .filter_map(|word| word.parse::<i32>().ok())
        .collect();

    assert_eq!(parsed, [7, 11]);

    let data = [1, 2, 3];
    let found = data.iter().filter(|&&n| n > 1).next();
    assert_eq!(found, Some(&2));
}
```

## Best practice
- ✅ Put cheap filters before expensive maps when filtering can avoid unnecessary work.
- ✅ Use `filter_map` when the map closure naturally returns `Option<T>`.
- ✅ Use `Result` plus `collect::<Result<Vec<_>, _>>()` when failures must be reported.
- ✅ Prefer closure argument patterns such as `|&x|` or `|&&x|` over unclear dereference chains.
- ✅ Keep side effects in `for` loops or `for_each`; keep `map` for value transformation.
- ✅ Let type inference work, then add a `collect::<Vec<_>>()` or left-side type annotation only where needed.
- ✅ Preserve borrowing with `.iter()` when the original collection should remain usable.
- ✅ Use `.into_iter()` when consuming owned items is simpler and intended.

## Pitfalls
- ⚠️ Calling `map` only for side effects usually does nothing because the adapter is lazy; see [[Unconsumed Iterator Adapters]].
- ⚠️ Forgetting that `filter` receives `&Self::Item` leads to confusing `&&T` predicates.
- ⚠️ Writing `.map(...).filter(|x| x.is_some()).map(|x| x.unwrap())` is noisier than `filter_map`.
- ⚠️ Collecting after every small adapter step creates needless allocation; see [[Unnecessary Collect]].
- ⚠️ Cloning before filtering can copy data that will be discarded; see [[Needless Clone]].
- ⚠️ Using `filter` to validate fallible parsing loses the error unless that is intentional.
- ⚠️ Returning references to temporary values created inside `map` cannot work; see [[Returning References to Locals]].
- ⚠️ Assuming the closure has run before a consumer is attached misunderstands [[Lazy Evaluation]].

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator Adapters]] · [[The Iterator Trait]] · [[Iterators]] · [[Lazy Evaluation]] · [[Closures]] · [[Fn, FnMut, FnOnce]] · [[Iterator collect and FromIterator]] · [[Iterator predicate search adapters]] · [[Unconsumed Iterator Adapters]] · [[Unnecessary Collect]] · [[Needless Clone]]

## Sources
- Rust standard library, `Iterator::map` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map
- Rust standard library, `Iterator::filter` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter
- Rust standard library, `Iterator::filter_map` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter_map
