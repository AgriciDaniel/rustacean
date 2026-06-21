---
type: antipattern
title: "Speculative Micro-Optimization"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, micro-optimization, antipattern]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Avoiding Premature Optimization]]", "[[The inline Attribute]]", "[[Bounds-Check Elimination]]", "[[SmallVec for Inline Storage]]", "[[LTO and codegen-units]]", "[[Benchmarking with Criterion]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute", "https://doc.rust-lang.org/cargo/reference/profiles.html"]
rust_version: "edition 2024 / 1.85+"
---

# Speculative Micro-Optimization

Speculative micro-optimization is making tiny low-level changes for imagined speed before profiling proves the code is hot and benchmarking proves the change helps.

## The mistake
The mistake is not "small optimizations are bad."
The mistake is paying readability, portability, compile-time, or safety costs without evidence.
Common Rust examples include adding `#[inline(always)]`, replacing iterators with indexes, using `get_unchecked`, switching every small `Vec` to `SmallVec`, or enabling aggressive build flags without a benchmark.

Small changes can have non-small costs.
Inlining can bloat code.
Unsafe indexing creates a soundness obligation.
Specialized collections can leak implementation choices into public APIs.
Build flags can slow CI and release builds.
The right question is not "could this be faster?" but "did this measured change improve the measured bottleneck enough to justify the tradeoff?"

## Why it happens
Rust makes costs visible in types and APIs.
Seeing `Vec`, `String`, `clone`, bounds checks, or dynamic dispatch can trigger a reflex to remove them.
But the optimizer may already remove the abstraction, or the cost may be irrelevant next to I/O, allocation elsewhere, hashing, synchronization, or algorithmic complexity.
Micro-optimizations are also easy to cargo-cult because they are small enough to copy without copying the measurement context.
`#[inline(always)]` may have helped one crate on one target because of one call graph.
`SmallVec<[T; 8]>` may be excellent for one parser and worse for another where most values spill.
The local code shape is never the whole performance story.

Micro-optimization also suffers from local reasoning.
A change that reduces instructions in one function can hurt instruction cache behavior in the caller.
An inline attribute that helps one call path can make another worse.
An LTO setting that improves one binary can regress another.
Only measurement resolves those tradeoffs.
Rust version, target CPU, profile settings, dependencies, and data distribution all affect the result.
That is why "tiny" changes still need the same experiment discipline as bigger rewrites.

## Example
```rust
fn count_matches(haystack: &str, needle: &str) -> usize {
    haystack.lines().filter(|line| line.contains(needle)).count()
}

fn main() {
    let text = "rust\ntrust\nborrow\n";
    assert_eq!(count_matches(text, "rust"), 2);
}
```

There is no reason to replace this with manual byte scanning unless profiling shows this function dominates runtime and a benchmark proves the replacement wins on realistic input.
The iterator version delegates string search to the standard library and keeps the intent obvious.

## Worked example: a slower "clever" replacement
```rust
fn has_keyword(line: &str) -> bool {
    line.split_whitespace().any(|word| word == "unsafe")
}

fn main() {
    assert!(has_keyword("avoid unnecessary unsafe blocks"));
    assert!(!has_keyword("unsafely is a different word"));
}
```

A speculative rewrite might scan bytes manually to avoid iterator adapters.
That rewrite now owns Unicode boundary decisions, word-splitting semantics, and edge cases around punctuation.
If the standard-library version is not hot, the rewrite only adds bugs.
If it is hot, the benchmark should include realistic text, long lines, missing keywords, punctuation, and non-ASCII input before accepting a lower-level implementation.

## Common errors
Speculative micro-optimization often starts by adding attributes or unsafe calls in places where they are not valid:

```text
error: attribute should be applied to a function or closure
```

Move the attribute to a supported item or, more often, remove it until profiling justifies the annotation.

```text
error[E0133]: call to unsafe function `core::slice::<impl [T]>::get_unchecked` is unsafe and requires unsafe block
```

Do not treat this as a request to wrap a larger loop in `unsafe`.
The compiler is pointing out that you are taking responsibility for a bounds invariant; prove and document it or keep safe indexing.

## Best practice
- ✅ Treat tiny performance tweaks as experiments with a hypothesis, benchmark, and rollback path.
- ✅ Prefer algorithmic improvements and allocation reduction before unsafe or annotation-heavy changes.
- ✅ Keep public APIs ordinary unless a specialized type is part of the measured performance contract.
- ✅ Document why a non-obvious optimization exists and what benchmark protects it.
- ✅ Re-run benchmarks when upgrading Rust, changing target CPUs, or changing dependencies.
- ✅ Prefer reversible experiments: one commit, one hypothesis, one benchmark result.
- ✅ Measure code size and compile time when the tweak affects inlining, generics, or LTO.
- ✅ Remove the tweak if the improvement is within noise or only improves an unrealistic benchmark case.

## Pitfalls
- ⚠️ Adding `#[inline(always)]` everywhere fights the optimizer and can increase code size; see [[The inline Attribute]].
- ⚠️ Using `get_unchecked` to remove a check that was not hot risks undefined behavior for no measured gain.
- ⚠️ Replacing clear iterator code with indexes is often [[Manual Index Loops for Speed]].
- ⚠️ Switching to [[SmallVec for Inline Storage]] without data can make common moves larger and slower.
- ⚠️ Tuning `lto`, `codegen-units`, and `target-cpu` simultaneously hides what changed.
- ⚠️ Relying on one CPU architecture can mislead libraries used on different targets.
- ⚠️ Optimizing a public API around today's private benchmark can make tomorrow's correct design impossible without a breaking change.

## See also
[[Avoiding Premature Optimization]] · [[Profiling Rust Programs]] · [[Benchmarking with Criterion]] · [[The inline Attribute]] · [[Bounds-Check Elimination]] · [[SmallVec for Inline Storage]] · [[LTO and codegen-units]] · [[Manual Index Loops for Speed]] · [[Zero-Cost Abstractions]] · [[Performance & Optimization]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-04-performance.html
- The Rust Reference, "Code generation attributes: inline" — [[the-reference]],
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute
- The Cargo Book, "Profiles" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html
