---
type: antipattern
title: "Avoiding Premature Optimization"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, optimization, antipattern]
domain: "Performance & Optimization"
difficulty: basic
related: ["[[Profiling Rust Programs]]", "[[Benchmarking with Criterion]]", "[[Iterator Performance]]", "[[Reducing Heap Allocations]]", "[[Speculative Micro-Optimization]]", "[[Manual Index Loops for Speed]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/book/ch14-01-release-profiles.html", "https://doc.rust-lang.org/cargo/reference/profiles.html"]
rust_version: "edition 2024 / 1.85+"
---

# Avoiding Premature Optimization

Avoiding premature optimization means writing clear Rust first, then optimizing only the measured bottleneck with a benchmarked change.

## The mistake
The mistake is treating performance anxiety as performance evidence.
A developer sees an iterator chain, a `clone`, a bounds check, or an allocation and rewrites the code before knowing whether that code is hot.
The result can be harder to read, harder to test, and not faster in the real program.

Rust makes this tempting because it exposes powerful low-level tools.
You can tune profiles, add `#[inline(always)]`, switch collections, use arenas, and write unsafe indexing.
Those tools are valuable when data points to them.
Used early, they often create complexity while the real cost remains in I/O, allocation elsewhere, a bad algorithm, or a different build profile.

## Why it happens
Performance work feels concrete, and Rust's type system makes low-level changes explicit.
But modern optimizers erase many obvious-looking abstractions.
The Book's iterator comparison shows that higher-level iterator code can have performance similar to lower-level loops.
Cargo release profiles also mean a debug-build intuition may not apply to production.
The mistake is especially easy in Rust because a lot of real costs are visible in source: ownership moves, `clone`, allocation types, bounds checks, and dispatch choices are all explicit.
Visibility is useful for reasoning, but it is not the same as ranking costs.
A visible `clone` in a cold path may matter less than an invisible cache miss pattern, a blocking syscall, or a quadratic algorithm elsewhere.

Premature optimization also hides opportunity cost.
The time spent hand-tuning a cold loop could have found the hot allocation site, replaced an O(n^2) algorithm, or added a benchmark that guards against regression.
The correct alternative is a measurement loop: baseline, profile, change one thing, benchmark, keep or revert.
The loop is intentionally conservative.
A baseline prevents "it feels faster" from becoming a claim.
A profile identifies where effort belongs.
A benchmark or application performance test decides whether the change survives.
Code review should ask for that evidence when an optimization makes code less direct.

## Example
```rust
fn readable_total(values: &[u64]) -> u64 {
    values.iter().copied().filter(|n| n % 2 == 0).sum()
}

fn main() {
    let values = [1, 2, 3, 4, 5, 6];
    assert_eq!(readable_total(&values), 12);
}
```

This code should not be rewritten into unsafe pointer arithmetic because it "looks high level."
If a profiler later proves this exact calculation is hot, benchmark targeted alternatives.
Until then, the iterator version is clear, safe, and consistent with Rust's zero-cost abstraction model.

## Worked example: the measured path is somewhere else
```rust
fn parse_ids(lines: &[&str]) -> Vec<u64> {
    lines
        .iter()
        .filter_map(|line| line.trim().parse::<u64>().ok())
        .collect()
}

fn main() {
    let lines = [" 1", "not an id", " 42 "];
    assert_eq!(parse_ids(&lines), [1, 42]);
}
```

It is possible to micro-optimize the iterator chain, pre-size the `Vec`, or replace parsing with a custom parser.
But if the real application spends most time reading files or waiting on a database, those changes are noise.
The first useful step is a profile of the real workflow, then a benchmark of the parsing function only if parsing is actually hot.

## Common errors
Premature optimization often introduces ordinary Rust errors because the rewrite fights ownership or lifetimes:

```text
error[E0502]: cannot borrow `values` as mutable because it is also borrowed as immutable
```

This can happen when a manual loop tries to mutate a collection while still holding references from an iterator over it.
The fix is usually to keep the clear two-phase code, use `retain`/`drain`/a separate output buffer, or prove with a benchmark that a more complex rewrite is worth designing carefully.

```text
error[E0133]: call to unsafe function `get_unchecked` is unsafe and requires unsafe block
```

Adding `unsafe` is not the performance fix.
The fix is to avoid unchecked indexing unless a benchmark shows safe bounds checks matter and the invariant is documented.

## Best practice
- ✅ Start with idiomatic, testable code that expresses ownership and data flow clearly.
- ✅ Use [[Profiling Rust Programs]] to find the hot path before changing code for speed.
- ✅ Use [[Benchmarking with Criterion]] or an application benchmark to confirm a measurable improvement.
- ✅ Prefer narrow changes such as pre-sizing a `Vec` before invasive rewrites.
- ✅ Stop once the performance target is met; every extra trick has maintenance cost.
- ✅ Keep the simplest code that meets the measured target; performance work is complete when the target is met, not when every possible trick is tried.
- ✅ Write down the benchmark or profile that justifies a non-obvious optimization so future maintainers can retest it.
- ✅ Prefer changes that improve both clarity and performance, such as removing unnecessary allocation or choosing a better algorithm.

## Pitfalls
- ⚠️ Replacing iterators with manual indexes without evidence is [[Manual Index Loops for Speed]].
- ⚠️ Adding `#[inline(always)]` because a function is small is [[Speculative Micro-Optimization]].
- ⚠️ Introducing `SmallVec`, arenas, or unsafe indexing before profiling makes APIs more complex without proof.
- ⚠️ Benchmarking only a toy input can justify a change that does not help real workloads.
- ⚠️ Optimizing debug builds ignores release-profile behavior.
- ⚠️ Treating Clippy suggestions, assembly snippets, or blog posts as workload evidence skips measurement.
- ⚠️ Keeping an optimization after it no longer wins is also premature for the current codebase; remove stale tricks when measurements change.

## See also
[[Profiling Rust Programs]] · [[Benchmarking with Criterion]] · [[Iterator Performance]] · [[Reducing Heap Allocations]] · [[Bounds-Check Elimination]] · [[The inline Attribute]] · [[Speculative Micro-Optimization]] · [[Manual Index Loops for Speed]] · [[Zero-Cost Abstractions]] · [[Performance & Optimization]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Programming Language, ch. 14.1 "Customizing Builds with Release Profiles" — [[the-book]],
  https://doc.rust-lang.org/book/ch14-01-release-profiles.html
- The Cargo Book, "Profiles" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html
