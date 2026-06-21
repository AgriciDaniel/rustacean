---
type: antipattern
title: "Manual Index Loops for Speed"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, performance, footgun]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Zero-Cost Abstractions]]", "[[Prefer Iterator Pipelines to Manual Indexing]]", "[[Iterators]]", "[[Iterator Adapters]]", "[[While and For Loops]]", "[[Index Panics vs get]]"]
sources: ["[[the-book]]", "[[rust-performance-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/book/ch13-02-iterators.html"]
rust_version: "edition 2024 / 1.85+"
---

# Manual Index Loops for Speed

Manual index loops are an antipattern when they replace clear iterator code solely from the assumption that indexing must be faster.

## The mistake
The mistake is writing `for i in 0..len { values[i] ... }` for ordinary traversal because it looks
lower level. That style adds index bookkeeping, can introduce bounds-check and off-by-one hazards,
and often does not outperform idiomatic iterator code in optimized builds.

Manual indexing is not wrong when the algorithm is genuinely about positions. It is wrong as a
reflexive performance rewrite without measurement.

## Why it happens
Developers coming from C-like loops may equate visible indices with speed. Rust's iterator
abstractions are designed to compile away in common cases, and the Book's loop-versus-iterator
comparison shows similar performance.

Iterator forms also communicate aliasing and bounds more directly to the compiler and to readers.
When bounds checks matter in a proven hot path, use safe iterator shapes, slicing, or assertions
before reaching for unsafe indexing.

Manual loops can also accidentally change semantics. `zip` truncates at the shorter input,
`chunks_exact` exposes remainders explicitly, and `get` returns `Option`; indexing with `[]`
panics on mismatch. Choosing one of those forms forces the length behavior to be visible.

## Example
```rust
fn add_scaled(output: &mut [i32], input: &[i32], scale: i32) {
    for (out, value) in output.iter_mut().zip(input.iter().copied()) {
        *out += value * scale;
    }
}

fn main() {
    let mut output = [10, 20, 30];
    let input = [1, 2, 3, 4];
    add_scaled(&mut output, &input, 5);
    assert_eq!(output, [15, 30, 45]);
}
```

`zip` expresses the shared traversal and naturally stops at the shorter slice.

## Worked example
```rust
fn pairwise_deltas(values: &[i32]) -> Vec<i32> {
    values
        .windows(2)
        .map(|pair| pair[1] - pair[0])
        .collect()
}

fn scale_in_place(values: &mut [i32], scale: i32) {
    values.iter_mut().for_each(|value| *value *= scale);
}

fn main() {
    assert_eq!(pairwise_deltas(&[3, 8, 10, 2]), vec![5, 2, -8]);

    let mut values = [1, 2, 3];
    scale_in_place(&mut values, 10);
    assert_eq!(values, [10, 20, 30]);
}
```

`windows(2)` makes the overlapping-pair invariant explicit. The in-place update uses one mutable
reference per element without exposing indices.

## Common errors
```rust
fn sum_pairs(left: &[i32], right: &[i32]) -> i32 {
    let mut total = 0;
    for i in 0..left.len() {
        total += left[i] * right[i];
    }
    total
}
```

This can panic at runtime when `right` is shorter than `left`. Use `left.iter().zip(right)` for
truncating pairwise work, or check `left.len() == right.len()` and return `Result` if mismatch is
invalid input.

## Best practice
- ✅ Start with iterator operations for ordinary traversal.
- ✅ Use `enumerate` when you need both position and item.
- ✅ Use profiling and release-mode benchmarks before replacing iterator code for speed.
- ✅ Use slice methods such as `windows`, `chunks`, `split_at`, and `get` to encode indexing invariants safely.
- ✅ Keep index loops when the index is the data, such as matrix coordinates, heap navigation, or dynamic programming transitions.

## Pitfalls
- ⚠️ Comparing debug-build performance and drawing conclusions about optimized code.
- ⚠️ Introducing panicking indexing where `zip`, `chunks`, `windows`, or `get` would encode safety. See [[Index Panics vs get]].
- ⚠️ Replacing one clear iterator chain with a longer loop whose invariants are harder to review.
- ⚠️ Using `unsafe get_unchecked` as a first response to bounds checks; prove the hot path and the invariant first.
- ⚠️ Forgetting that `for i in 0..vec.len()` can become stale if the loop mutates the collection length.

## See also
[[Closures & Iterators]] · [[Zero-Cost Abstractions]] · [[Prefer Iterator Pipelines to Manual Indexing]] · [[Iterators]] · [[Iterator Adapters]] · [[While and For Loops]] · [[Index Panics vs get]] · [[Profiles and Optimization Settings]] · [[Slices]] · [[Unnecessary Collect]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
