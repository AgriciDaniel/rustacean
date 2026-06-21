---
type: concept
title: "Iterator collect and FromIterator"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, collect, fromiterator, collection]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Consuming Adapters]]", "[[Iterator map and filter]]", "[[Vec]]", "[[Result]]", "[[Type Inference]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.collect", "https://doc.rust-lang.org/std/iter/trait.FromIterator.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator collect and FromIterator

`collect` consumes an iterator into a target type chosen by `FromIterator`, so the destination type must be known from context or a turbofish.

## What it is
`Iterator::collect` is the standard terminal operation for materializing an iterator.
It consumes the iterator and builds a value `B` where `B: FromIterator<Self::Item>`.
The destination might be a `Vec<T>`, `String`, `HashSet<T>`, `Result<Vec<T>, E>`, `Option<Vec<T>>`, or another type implementing `FromIterator`.
`FromIterator` is the trait that teaches a type how to be built from an iterator.
Because many destination types may be possible, `collect` often needs a type hint.
The hint can be on the left side of `let`.
It can also be written with turbofish syntax like `.collect::<Vec<_>>()`.
`collect` is powerful, but it is also a common place where unnecessary allocation sneaks into iterator code.
Use it when you need ownership, storage, random access, or an API boundary.
Avoid it when the next operation can keep streaming.

## How it works
The iterator decides the item type.
The collection type decides how to receive those items.
For `Vec<T>`, collection pushes items into contiguous heap storage.
For `String`, collection accepts characters or string slices depending on trait implementations.
For `Result<Collection<T>, E>`, collection stops at the first `Err(E)` and returns that error.
For `Option<Collection<T>>`, collection stops at the first `None`.
That short-circuiting behavior is often the cleanest way to turn many fallible operations into one fallible result.
The standard docs also describe nightly-only collection helpers.
For edition 2024 / stable 1.85+ notes, prefer stable `collect` and `Extend::extend`.
`collect` consumes `self`, so the iterator is not available afterward unless you used `by_ref` before collecting a prefix.

## Example
```rust
fn main() {
    let input = ["1", "2", "3"];

    let numbers: Result<Vec<i32>, _> = input
        .into_iter()
        .map(str::parse::<i32>)
        .collect();

    assert_eq!(numbers, Ok(vec![1, 2, 3]));
}
```

## Edge cases
```rust
fn main() {
    let chars = ['R', 'u', 's', 't'];
    let word: String = chars.into_iter().collect();
    assert_eq!(word, "Rust");

    let doubled = [1, 2, 3]
        .iter()
        .map(|n| n * 2)
        .collect::<Vec<_>>();
    assert_eq!(doubled, [2, 4, 6]);

    let maybe_values: Option<Vec<_>> = [Some(1), Some(2)].into_iter().collect();
    assert_eq!(maybe_values, Some(vec![1, 2]));
}
```

## Best practice
- ✅ Add a destination type when using `collect`.
- ✅ Use `.collect::<Vec<_>>()` when the item type is obvious but the collection type is not.
- ✅ Use `collect::<Result<Vec<_>, _>>()` to preserve the first fallible error.
- ✅ Use `collect::<Option<Vec<_>>>()` when every optional item must be present.
- ✅ Keep pipelines lazy until a real ownership or storage boundary.
- ✅ Use `Extend::extend` when appending into an existing collection on stable Rust.
- ✅ Prefer `String` collection for character streams that really produce text.
- ✅ Consider returning `impl Iterator` from APIs that do not need to allocate.

## Pitfalls
- ⚠️ Type inference errors around `collect` usually mean the destination type is ambiguous.
- ⚠️ Collecting just to iterate again is often [[Unnecessary Collect]].
- ⚠️ Collecting a large or infinite iterator can exhaust memory or never terminate.
- ⚠️ Using `filter_map(Result::ok)` before collect discards errors.
- ⚠️ Assuming `collect` always returns `Vec` is wrong.
- ⚠️ Consuming an iterator with `collect` prevents later use of that iterator value.
- ⚠️ Repeated collection inside loops can create avoidable allocations.
- ⚠️ Exposing concrete collected containers in APIs can reduce flexibility.

## See also
[[std: Iterator Adapter Catalog]] · [[Consuming Adapters]] · [[Iterator map and filter]] · [[Iterator flat_map and flatten]] · [[Iterator partition and unzip]] · [[Iterator sum product and count]] · [[Vec]] · [[String and str]] · [[Result]] · [[Option]] · [[Type Inference]] · [[Unnecessary Collect]] · [[Return Iterators Instead of Collecting]]

## Sources
- Rust standard library, `Iterator::collect` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.collect
- Rust standard library, `FromIterator` - [[std]], https://doc.rust-lang.org/std/iter/trait.FromIterator.html
