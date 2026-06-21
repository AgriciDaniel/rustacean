---
type: concept
title: "Zero-Cost Abstractions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, iterators, abstractions]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Iterators]]", "[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Profiles and Optimization Settings]]", "[[Manual Index Loops for Speed]]", "[[While and For Loops]]"]
sources: ["[[the-book]]", "[[rust-performance-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/book/ch13-02-iterators.html"]
rust_version: "edition 2024 / 1.85+"
---

# Zero-Cost Abstractions

Zero-cost abstractions are high-level Rust constructs, including iterator pipelines, that compile to code with no inherent runtime penalty versus equivalent hand-written low-level code.

## What it is
For closures and iterators, "zero-cost" means the abstraction itself should not force extra dynamic
dispatch, allocation, or bounds checks merely because you wrote `map`, `filter`, and `sum`.

The Book's loop-versus-iterator benchmark shows similar performance for a manual search loop and
an iterator implementation. The broader lesson is not that every chain is magically optimal, but
that idiomatic iterator code is a sound default.

## How it works
Iterator chains are statically typed and usually monomorphized. The compiler can inline adapter
layers, remove unused structure, unroll loops, and often eliminate bounds checks because traversal
is encoded in the iterator.

Costs still come from what you ask the program to do: allocation in `collect`, cloning in
`cloned`, formatting, IO, cache misses, or an algorithmic mismatch. Measure those costs before
rewriting clear iterator code.

The claim is also profile-sensitive. Debug builds intentionally preserve debuggability and skip
many optimizations, so iterator-heavy code can look noisier there. Performance comparisons should
use release settings and representative inputs before drawing conclusions.

## Example
```rust
fn sum_even_squares(values: &[i32]) -> i32 {
    values
        .iter()
        .copied()
        .filter(|n| *n % 2 == 0)
        .map(|n| n * n)
        .sum()
}

fn main() {
    assert_eq!(sum_even_squares(&[1, 2, 3, 4]), 20);
}
```

This expresses the work at the level of the data transformation while staying friendly to the
optimizer.

## Worked example
```rust
fn first_match<'a>(haystack: &'a str, needle: &str) -> Option<&'a str> {
    haystack
        .lines()
        .find(|line| line.contains(needle))
}

fn count_ascii_digits(bytes: &[u8]) -> usize {
    bytes.iter().filter(|byte| byte.is_ascii_digit()).count()
}

fn main() {
    assert_eq!(first_match("alpha\nbeta\nrust\n", "ru"), Some("rust"));
    assert_eq!(count_ascii_digits(b"a1b22!"), 3);
}
```

Both functions express simple loops as iterator consumers. The absence of `collect` means there is
no intermediate allocation for the abstraction itself.

## Common errors
```rust
fn slow_shape(values: &[String]) -> Vec<String> {
    values.iter().map(|value| value.clone()).collect()
}
```

This is not slow because `map` is an adapter; it may be slow because every element is cloned and
the result vector allocates. When profiling shows a cost, identify the real operation before
rewriting the chain into indices.

## Best practice
- ✅ Write clear iterator code first, then profile if performance matters.
- ✅ Treat `collect`, `clone`, allocation, and formatting as more suspicious than adapter syntax itself.
- ✅ Use release builds and representative benchmarks when comparing loops and iterators.
- ✅ Prefer iterator shapes that expose bounds naturally, such as `zip`, `chunks_exact`, and slice iterators.
- ✅ Keep hot-path closures small enough for inlining, and move expensive setup outside repeated callbacks.

## Pitfalls
- ⚠️ Rewriting iterator chains into manual index loops solely because they look lower level. See [[Manual Index Loops for Speed]].
- ⚠️ Assuming "zero-cost" means "every possible chain is allocation-free"; consumers like `collect` allocate by design.
- ⚠️ Benchmarking debug builds, where optimizer conclusions are not meaningful. See [[Profiles and Optimization Settings]].
- ⚠️ Hiding algorithmic changes inside style comparisons; a one-pass iterator and a two-pass loop are not equivalent.
- ⚠️ Using dynamic dispatch (`Box<dyn Iterator>`) in a hot path without measuring; it can inhibit inlining compared with `impl Iterator`.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Lazy Evaluation]] · [[Manual Index Loops for Speed]] · [[Profiles and Optimization Settings]] · [[While and For Loops]] · [[Return Iterators Instead of Collecting]] · [[Unnecessary Collect]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
