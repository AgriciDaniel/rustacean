---
type: concept
title: "Iterators"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, sequences, collections]
domain: "Closures & Iterators"
difficulty: basic
related: ["[[The Iterator Trait]]", "[[Iterator Adapters]]", "[[Consuming Adapters]]", "[[Lazy Evaluation]]", "[[Zero-Cost Abstractions]]", "[[While and For Loops]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterators

Iterators are Rust's standard abstraction for producing a sequence of items one at a time without exposing manual indexing or traversal state.

## What it is
An iterator owns the logic for moving through a sequence and deciding when the sequence is
finished. Vectors, slices, ranges, maps, strings, IO lines, and many custom types can provide
iterators.

Rust's `for` loop is built around iteration. In everyday code, `for item in collection` uses the
same iterator machinery as explicit calls to `.iter()`, `.iter_mut()`, or `.into_iter()`.

## How it works
Iterator values are lazy state machines. They produce items only when a consumer asks for the next
one. The required operation is [[The Iterator Trait]] method `next`, which returns
`Option<Self::Item>`.

Choose the iterator constructor by ownership:

`iter()` yields shared references. `iter_mut()` yields mutable references. `into_iter()` consumes
the source and yields owned items when the source type supports that behavior.

The `for` loop syntax desugars through `IntoIterator`, so it accepts collections, ranges, and
iterator values uniformly. Once an iterator exists, its progress is stored in the iterator value
itself; calling `next` mutates that state even when the underlying collection is only borrowed.

## Example
```rust
fn main() {
    let words = vec![String::from("rust"), String::from("is"), String::from("fast")];

    for word in words.iter() {
        println!("{word}");
    }

    let lengths: Vec<usize> = words.iter().map(|word| word.len()).collect();
    assert_eq!(lengths, vec![4, 2, 4]);

    let owned: Vec<String> = words.into_iter().filter(|word| word.len() > 2).collect();
    assert_eq!(owned, vec![String::from("rust"), String::from("fast")]);
}
```

The first two chains borrow `words`; the final chain consumes it and returns owned strings.

## Worked example
```rust
fn normalize_scores(scores: &mut [i32]) {
    for score in scores.iter_mut().filter(|score| **score < 0) {
        *score = 0;
    }
}

fn top_labels<'a>(labels: &'a [&'a str], scores: &'a [i32]) -> impl Iterator<Item = &'a str> {
    labels
        .iter()
        .copied()
        .zip(scores.iter().copied())
        .filter(|(_, score)| *score >= 90)
        .map(|(label, _)| label)
}

fn main() {
    let mut scores = [95, -3, 72, 100];
    normalize_scores(&mut scores);
    assert_eq!(scores, [95, 0, 72, 100]);

    let labels = ["a", "b", "c", "d"];
    assert_eq!(top_labels(&labels, &scores).collect::<Vec<_>>(), vec!["a", "d"]);
}
```

This uses mutable iteration for in-place cleanup and borrowed iteration plus `zip` for a lazy view
over related slices.

## Common errors
```rust
fn main() {
    let values = vec![1, 2, 3];
    let iter = values.iter();
    // assert_eq!(iter.next(), Some(&1));
}
```

Uncommenting the assertion gives `error[E0596]: cannot borrow iter as mutable` because `next`
requires `&mut self`. Declare `let mut iter = values.iter();`, or use a `for` loop when you do
not need manual stepping.

## Best practice
- ✅ Reach for iterators before manual index loops, especially for filtering, mapping, searching, and aggregation.
- ✅ Pick `iter`, `iter_mut`, or `into_iter` based on whether you need shared access, mutation, or ownership.
- ✅ Prefer clear iterator chains that express the data transformation directly.
- ✅ Use `by_ref()` when you need to partially consume an iterator and then keep using the same iterator value.
- ✅ Use `enumerate`, `zip`, `windows`, and `chunks` before writing index arithmetic.

## Pitfalls
- ⚠️ Creating an adapter chain and never consuming it. See [[Unconsumed Iterator Adapters]].
- ⚠️ Collecting into a `Vec` only to loop once over the result. See [[Unnecessary Collect]].
- ⚠️ Hand-writing index loops "for speed" without measuring. See [[Manual Index Loops for Speed]].
- ⚠️ Forgetting `filter` sees references to items; use `.copied()`, `.cloned()`, or explicit patterns when needed.
- ⚠️ Assuming all iterators are rewindable. Most are one-pass state machines unless you create a new iterator.

## See also
[[Closures & Iterators]] · [[The Iterator Trait]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Lazy Evaluation]] · [[Zero-Cost Abstractions]] · [[While and For Loops]] · [[Arrays]] · [[Slices]] · [[Unnecessary Collect]]

## Sources
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Rust standard library, `std::iter` - [[std]], https://doc.rust-lang.org/std/iter/index.html
