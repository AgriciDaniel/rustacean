---
type: concept
title: "Iterator flat_map and flatten"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, adapter, flatten, flat-map]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator map and filter]]", "[[Iterator collect and FromIterator]]", "[[Iterator Adapters]]", "[[Option]]", "[[Result]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.flat_map", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.flatten"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator flat_map and flatten

`flat_map` maps each item into something iterable and removes one nesting layer, while `flatten` removes one nesting layer that is already present.

## What it is
`Iterator::flat_map` is `map` followed by `flatten` in one adapter.
Its closure returns a value implementing `IntoIterator`.
The resulting iterator yields all inner items in order.
`Iterator::flatten` applies when the original iterator already yields iterable things.
It removes exactly one layer of nesting.
Common inputs include `Vec<Vec<T>>`, arrays of arrays, iterators of ranges, `Option<T>`, and `Result<T, E>`.
For `Option`, flattening skips `None` and yields values from `Some`.
For `Result`, flattening skips `Err` and yields values from `Ok`.
Use that behavior only when discarding failures is the desired semantics.
For fallible pipelines that must preserve errors, prefer `collect::<Result<Vec<_>, _>>()`.

## How it works
Both methods rely on `IntoIterator`.
`flat_map` calls the closure for each outer item.
Then it drives each returned inner iterator until it is exhausted.
Only then does it request the next outer item.
`flatten` does the same inner-then-outer traversal without an explicit mapping closure.
Neither method recursively flattens all levels.
If the item type is nested twice, two `flatten` calls remove two layers.
The adapters are lazy, so an inner iterator is not produced until the outer item is reached.
This makes them useful for expanding ranges, splitting strings, traversing child collections, and dropping absent optional values.
Because the result type can become complex, public APIs often return `impl Iterator<Item = T>` rather than naming the adapter type.

## Example
```rust
fn main() {
    let words = ["ab", "cd"];

    let chars: Vec<char> = words
        .iter()
        .flat_map(|word| word.chars())
        .collect();

    assert_eq!(chars, ['a', 'b', 'c', 'd']);
}
```

## Edge cases
```rust
fn main() {
    let nested = vec![vec![1, 2], vec![], vec![3]];
    let values: Vec<_> = nested.into_iter().flatten().collect();
    assert_eq!(values, [1, 2, 3]);

    let optional = [Some("rust"), None, Some("std")];
    let present: Vec<_> = optional.into_iter().flatten().collect();
    assert_eq!(present, ["rust", "std"]);

    let ranges: Vec<_> = [0..2, 4..6].into_iter().flatten().collect();
    assert_eq!(ranges, [0, 1, 4, 5]);
}
```

## Best practice
- ✅ Use `flat_map` when each input item expands into zero or more output items.
- ✅ Use `flatten` when the nested iterable already exists.
- ✅ Remember that only one layer is removed per `flatten` call.
- ✅ Use `filter_map` instead of `flat_map` when each item becomes zero or one output via `Option`.
- ✅ Preserve errors with `Result` collection when an `Err` is meaningful.
- ✅ Return `impl Iterator` from functions instead of exposing long adapter names.
- ✅ Keep expansion closures small enough to read.
- ✅ Combine with `take` when flattening potentially unbounded inner iterators.

## Pitfalls
- ⚠️ Flattening `Result` values silently discards `Err` values because `Result` implements `IntoIterator`.
- ⚠️ Expecting recursive flattening leads to one layer still remaining.
- ⚠️ Collecting nested data before flattening can be an [[Unnecessary Collect]].
- ⚠️ Capturing mutable state in a `flat_map` closure can be harder to understand than `scan`.
- ⚠️ Expanding to infinite inner iterators can prevent later outer items from ever being reached.
- ⚠️ Using `flat_map` for one-to-one mapping obscures intent compared with `map`.
- ⚠️ Cloning inner collections before flattening may be a [[Needless Clone]].
- ⚠️ Returning borrowed inner iterators from temporaries can run into lifetime errors.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator map and filter]] · [[Iterator collect and FromIterator]] · [[Iterator take skip and while bounds]] · [[Iterator scan and peekable]] · [[Iterator Adapters]] · [[Lazy Evaluation]] · [[Option]] · [[Result]] · [[Return Iterators Instead of Collecting]] · [[Unnecessary Collect]] · [[Needless Clone]]

## Sources
- Rust standard library, `Iterator::flat_map` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.flat_map
- Rust standard library, `Iterator::flatten` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.flatten
