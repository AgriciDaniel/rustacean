---
type: concept
title: "Iterator Performance"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, iterators, zero-cost-abstractions]
domain: "Performance & Optimization"
difficulty: basic
related: ["[[Iterators]]", "[[Iterator Adapters]]", "[[Zero-Cost Abstractions]]", "[[Prefer Iterator Pipelines to Manual Indexing]]", "[[Manual Index Loops for Speed]]", "[[Bounds-Check Elimination]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/book/ch13-02-iterators.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator Performance

Rust iterators are designed as zero-cost abstractions: idiomatic iterator chains commonly compile to code comparable to hand-written loops while removing many indexing mistakes.

## What it is
Iterator performance is the practical result of three Rust design choices.
First, iterators are lazy, so adapters such as `map` and `filter` describe work but do not run until consumed.
Second, iterator types are concrete and usually statically dispatched, so the compiler sees the adapter chain.
Third, iteration over slices and collections carries bounds information that manual indexing often obscures.

The Book's loop-vs-iterator comparison intentionally shows similar performance for an explicit loop and an iterator-based search.
The important lesson is not that every iterator pipeline is faster.
The lesson is that the default assumption should be "write the clear iterator code, then measure if performance matters."

## How it works
A `for` loop over a collection already uses `IntoIterator` under the hood.
Iterator adapters build small structs that the optimizer can inline and simplify.
For simple pipelines over slices, LLVM can often fuse the chain into a tight loop and remove temporary adapter objects.
Because an iterator yields valid items, it can also avoid repeated `v[i]` bounds checks that an index loop might need.
The laziness is important mechanically: `map`, `filter`, and similar adapters store the previous iterator plus a closure, but they do not allocate by themselves.
When a consuming adapter such as `sum`, `count`, `collect`, or a `for` loop pulls items, the chain becomes repeated calls to `next`.
With static dispatch and inlining, those `next` calls are often flattened into one loop over the original data.

This does not make every chain free.
Collecting into an intermediate `Vec`, allocating in a closure, dynamic dispatch through `Box<dyn Iterator>`, or doing expensive work inside the closure still costs what it costs.
Iterator style removes overhead only when the abstraction itself can disappear.
It cannot erase allocations, I/O, hashing, formatting, or algorithmic complexity.
`impl Iterator` preserves a concrete return type without naming it, so callers still get static dispatch.
`Box<dyn Iterator<Item = T>>` is useful when different branches must return different iterator types, but it normally adds a heap allocation and virtual calls unless the optimizer can see through the box.
For public APIs, the performance question and the API-stability question are separate: returning `impl Iterator` hides the exact adapter type but still commits to one concrete type per function body.

## Example
```rust
fn sum_even_squares(values: &[u32]) -> u32 {
    values
        .iter()
        .copied()
        .filter(|n| n % 2 == 0)
        .map(|n| n * n)
        .sum()
}

fn sum_even_squares_loop(values: &[u32]) -> u32 {
    let mut sum = 0;
    for &n in values {
        if n % 2 == 0 {
            sum += n * n;
        }
    }
    sum
}

fn main() {
    let values = [1, 2, 3, 4, 5, 6];
    assert_eq!(sum_even_squares(&values), 56);
    assert_eq!(sum_even_squares_loop(&values), 56);
}
```

Both functions express the same work.
The iterator version is often easier to audit because it names the data transformation directly.
If a benchmark shows a difference, inspect allocation, dispatch, and missed inlining before assuming "iterators are slow."

## Worked example: avoiding an intermediate collection
```rust
fn normalized_word_count(lines: &[&str]) -> usize {
    lines
        .iter()
        .flat_map(|line| line.split_whitespace())
        .filter(|word| !word.is_empty())
        .count()
}

fn main() {
    let lines = ["rust iterators", "  are lazy  ", ""];
    assert_eq!(normalized_word_count(&lines), 4);
}
```

This pipeline does not allocate a `Vec<&str>` of all words.
`flat_map` pulls words from each line as the final `count` consumes them.
If the next step genuinely needs random access or repeated traversal, collecting may be correct; if the next step is another single pass, collecting only adds memory traffic.

## Common errors
Iterator adapters are lazy, so an adapter chain that is not consumed does no work.
The compiler normally warns about this pattern:

```text
warning: unused `Map` that must be used
  = note: iterators are lazy and do nothing unless consumed
help: use `let _ = ...` to ignore the resulting value
```

The fix is to consume the iterator with a `for` loop, `collect`, `sum`, `count`, `any`, `find`, or another consuming adapter.
Use `let _ = ...` only when intentionally discarding the lazy adapter, which is rare.

## Best practice
- ✅ Prefer iterator pipelines when they make the transformation clearer; see [[Prefer Iterator Pipelines to Manual Indexing]].
- ✅ Return iterators when the caller can consume lazily; see [[Return Iterators Instead of Collecting]].
- ✅ Use `.iter()`, `.iter_mut()`, and `.into_iter()` deliberately so ownership and borrowing match the task.
- ✅ Benchmark the real workload before replacing iterator code with manual indexing.
- ✅ Use `zip`, `chunks_exact`, `windows`, and slice iteration to express shape constraints the optimizer can use.
- ✅ Prefer `impl Iterator` over `Box<dyn Iterator>` when one concrete iterator type can be returned.
- ✅ Keep expensive setup outside closures that run per item; a cheap-looking pipeline can hide repeated allocation or parsing.
- ✅ Use `by_ref()` when partially consuming an iterator and then continuing with the same iterator value.

## Pitfalls
- ⚠️ Assuming a manual index loop is faster is the [[Manual Index Loops for Speed]] antipattern.
- ⚠️ Calling `collect()` between adapters can allocate and block fusion; see [[Unnecessary Collect]].
- ⚠️ Forgetting that adapters are lazy produces no work; see [[Unconsumed Iterator Adapters]].
- ⚠️ Boxing an iterator for convenience can introduce dynamic dispatch and block inlining; prefer `impl Iterator` when possible.
- ⚠️ Hiding expensive work inside a closure can make the pipeline look cheap while the closure dominates the runtime.
- ⚠️ Using `flat_map` or `filter_map` to hide fallible parsing can make error handling disappear; choose clarity over clever chains.
- ⚠️ Calling `.inspect()` for required side effects is brittle; it is intended for observation/debugging, not core behavior.

## See also
[[Iterators]] · [[Iterator Adapters]] · [[The Iterator Trait]] · [[Lazy Evaluation]] · [[Zero-Cost Abstractions]] · [[Prefer Iterator Pipelines to Manual Indexing]] · [[Manual Index Loops for Speed]] · [[Bounds-Check Elimination]] · [[Unconsumed Iterator Adapters]] · [[Unnecessary Collect]] · [[Return Iterators Instead of Collecting]] · [[Performance & Optimization]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-02-iterators.html
