---
type: pattern
title: "Prefer Iterator Pipelines to Manual Indexing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, performance, idiom]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Iterators]]", "[[Iterator Adapters]]", "[[Consuming Adapters]]", "[[Zero-Cost Abstractions]]", "[[While and For Loops]]", "[[Manual Index Loops for Speed]]"]
sources: ["[[the-book]]", "[[rust-performance-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/book/ch13-02-iterators.html"]
rust_version: "edition 2024 / 1.85+"
---

# Prefer Iterator Pipelines to Manual Indexing

Prefer iterator pipelines when traversing collections because they express intent, avoid common indexing mistakes, and normally optimize as well as hand-written loops.

## What it is
This pattern replaces `for i in 0..values.len() { values[i] ... }` with iterator operations over
items, references, or paired sequences. The code describes what should happen to each element
rather than how to maintain an index.

It is especially strong for map/filter/reduce style transformations, searching, counting,
partitioning, and combining parallel sequences with `zip`.

## How it works
Iterators encode traversal bounds in the abstraction. That removes many manual opportunities for
off-by-one bugs and makes it easier for the compiler to see safe iteration patterns.

Manual indexing is still valid when the algorithm is truly index-oriented, but "for speed" is not
a sufficient reason by itself. The Book and performance guidance both support idiomatic iterators
as the default, with benchmarking for hot paths.

Iterator pipelines also encode ownership more directly. `iter_mut` proves each element is visited
through one mutable reference at a time, `zip` proves paired traversal stops safely, and `windows`
or `chunks` express shape constraints without exposing unchecked index arithmetic.

## Example
```rust
fn dot_product(left: &[i32], right: &[i32]) -> i32 {
    left.iter()
        .copied()
        .zip(right.iter().copied())
        .map(|(a, b)| a * b)
        .sum()
}

fn main() {
    assert_eq!(dot_product(&[1, 2, 3], &[4, 5, 6]), 32);
    assert_eq!(dot_product(&[1, 2], &[10, 20, 30]), 50);
}
```

`zip` naturally stops at the shorter input and removes the need to calculate an indexing limit.

## Worked example
```rust
fn moving_average3(values: &[f64]) -> Vec<f64> {
    values
        .windows(3)
        .map(|window| window.iter().sum::<f64>() / 3.0)
        .collect()
}

fn mark_large(values: &[i32], threshold: i32) -> Vec<(usize, i32)> {
    values
        .iter()
        .copied()
        .enumerate()
        .filter(|(_, value)| *value > threshold)
        .collect()
}

fn main() {
    assert_eq!(moving_average3(&[3.0, 6.0, 9.0, 12.0]), vec![6.0, 9.0]);
    assert_eq!(mark_large(&[4, 10, 2, 11], 9), vec![(1, 10), (3, 11)]);
}
```

`windows` expresses overlapping neighborhoods and `enumerate` keeps positions only where the
position is part of the result.

## Common errors
```rust
fn add_all(left: &[i32], right: &[i32]) -> Vec<i32> {
    let mut out = Vec::new();
    for i in 0..left.len() {
        out.push(left[i] + right[i]);
    }
    out
}
```

This panics if `right` is shorter. The iterator fix is `left.iter().zip(right).map(|(a, b)| a + b)`
when truncation is intended, or an explicit length check returning `Result` when equal lengths are
required.

## Best practice
- ✅ Use `iter`, `iter_mut`, `into_iter`, `enumerate`, and `zip` to express traversal shape.
- ✅ Benchmark before replacing clear iterator code with index arithmetic.
- ✅ Keep manual indexing for algorithms where positions are the domain concept, such as dynamic programming tables.
- ✅ Use `windows`, `chunks`, `chunks_exact`, or `split` variants when the traversal has structure beyond single items.
- ✅ Use `get` or checked length validation when indexing is genuinely required by the algorithm.

## Pitfalls
- ⚠️ Assuming manual indexing is faster because it looks closer to machine code. See [[Manual Index Loops for Speed]].
- ⚠️ Recomputing indices or lengths in complex loops when `zip`, `windows`, or `chunks` would encode the invariant.
- ⚠️ Collecting intermediate vectors between iterator steps. See [[Unnecessary Collect]].
- ⚠️ Using `zip` when mismatched lengths should be an error; `zip` truncates to the shorter input by design.
- ⚠️ Replacing a readable loop with a pipeline whose control flow is no longer obvious; iterators are a tool, not a contest.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Zero-Cost Abstractions]] · [[Manual Index Loops for Speed]] · [[While and For Loops]] · [[Unnecessary Collect]] · [[Index Panics vs get]] · [[Slices]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
