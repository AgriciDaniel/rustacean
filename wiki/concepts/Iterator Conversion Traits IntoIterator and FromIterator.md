---
type: concept
title: "Iterator Conversion Traits IntoIterator and FromIterator"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, iterators, intoiterator, fromiterator]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[Iterators]]", "[[The Iterator Trait]]", "[[Iterator Adapters]]", "[[Consuming Adapters]]"]
sources: ["[[std]]", "[[the-book]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.IntoIterator.html", "https://doc.rust-lang.org/std/iter/trait.FromIterator.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.collect"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator Conversion Traits IntoIterator and FromIterator

`IntoIterator` turns a value into an iterator for `for` loops and iterator chains, while `FromIterator` builds a collection from an iterator and powers `collect()`.

## What it is
`IntoIterator` is the trait behind `for item in value`.
It defines an `Item` type and an `IntoIter` iterator type.
Its required method is `into_iter`.

`FromIterator<A>` builds `Self` from an iterator of `A`.
It is the trait behind `Iterator::collect`.
Most standard collections implement it.

Together, these traits define collection boundaries.
One side lets a collection be consumed or borrowed as a stream of items.
The other side lets a stream of items become a collection.

## How it works
Many types have multiple `IntoIterator` implementations.
`Vec<T>` by value yields `T`.
`&Vec<T>` yields `&T`.
`&mut Vec<T>` yields `&mut T`.
The same pattern appears on arrays, slices, maps, sets, and many custom collections.

`for` calls `IntoIterator::into_iter` implicitly.
Iterator methods often call it explicitly through bounds like `I: IntoIterator`.
This is why generic APIs commonly accept `impl IntoIterator<Item = T>`.

`collect()` chooses its output type from context.
Sometimes that context comes from an annotation.
Sometimes it comes from a turbofish like `collect::<Vec<_>>()`.

`FromIterator` can fail only by choosing an item type that carries failure, such as `Result<T, E>`.
The standard library provides useful collection behavior for iterators of `Result` and `Option`.

## Example
```rust
use std::collections::BTreeSet;

fn unique_sorted<I>(items: I) -> Vec<String>
where
    I: IntoIterator,
    I::Item: Into<String>,
{
    let set: BTreeSet<String> = items.into_iter().map(Into::into).collect();
    set.into_iter().collect()
}

fn main() {
    let words = unique_sorted(["pear", "apple", "pear"]);
    assert_eq!(words, vec!["apple".to_string(), "pear".to_string()]);

    let numbers = vec![1, 2, 3];
    let doubled: Vec<_> = numbers.iter().map(|&n| n * 2).collect();
    assert_eq!(doubled, vec![2, 4, 6]);
}
```

## Best practice
- ✅ Accept `impl IntoIterator` when callers should pass arrays, vectors, sets, or iterator pipelines.
- ✅ Be explicit about `Item` in public generic bounds.
- ✅ Use `collect::<Target<_>>()` when inference is unclear.
- ✅ Choose by-value, shared-reference, and mutable-reference iteration deliberately.
- ✅ Implement all three `IntoIterator` forms for custom collections when they make sense.

## Pitfalls
- ⚠️ Do not accidentally consume a collection when you meant to iterate by reference.
- ⚠️ Do not add unnecessary `Vec` parameters when an `IntoIterator` bound would be more flexible.
- ⚠️ Do not call `collect()` without giving the compiler enough target type information.
- ⚠️ Avoid [[Unnecessary Collect]] when a lazy iterator pipeline can continue directly.

## See also
[[std: Core Trait Catalog]] · [[Iterators]] · [[The Iterator Trait]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Iterating Collections]] · [[Unnecessary Collect]] · [[Return Iterators Instead of Collecting]] · [[Vec]] · [[BTreeMap and BTreeSet]]

## Sources
- Rust standard library, `std::iter::IntoIterator` - [[std]], https://doc.rust-lang.org/std/iter/trait.IntoIterator.html
- Rust standard library, `std::iter::FromIterator` - [[std]], https://doc.rust-lang.org/std/iter/trait.FromIterator.html
- Rust standard library, `Iterator::collect` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.collect
