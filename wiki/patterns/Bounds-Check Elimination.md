---
type: pattern
title: "Bounds-Check Elimination"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, bounds-checks, slices]
domain: "Performance & Optimization"
difficulty: advanced
related: ["[[Iterator Performance]]", "[[Manual Index Loops for Speed]]", "[[Index Panics vs get]]", "[[Arrays]]", "[[Vec]]", "[[Slices]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-04-performance.html", "https://doc.rust-lang.org/std/primitive.slice.html#method.get_unchecked", "https://doc.rust-lang.org/reference/expressions/array-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Bounds-Check Elimination

Bounds-check elimination is the optimizer proving that slice or array indexing is in range, usually because your code expressed the range with iterators, slices, or explicit assertions.

## What it is
Rust checks indexing operations such as `slice[i]` at runtime and panics if the index is out of bounds.
That check is a safety feature, not a performance failure.
In optimized builds, many checks disappear when the compiler can prove the index is valid.
Bounds-check elimination is the practice of writing the code so that proof is easy.

The safe tools come first.
Iterate over items instead of indexes.
Use `zip` to pair collections by their common valid range.
Slice once before the hot loop.
Add an `assert!` that states a precondition the optimizer can use.
Reach for `unsafe { get_unchecked(...) }` only after measurement proves the safe version is too slow and the invariant is documented.

## How it works
The optimizer reasons better about local facts than about distant facts.
If a loop says `for x in slice`, each yielded `x` is valid by construction.
If a loop says `for i in 0..slice.len()`, `slice[i]` is also usually easy to prove.
If indexes come from another slice, a calculation, or a branch-heavy control flow, the compiler may keep checks unless you narrow the data first or assert the relationship.
Indexing syntax calls the slice indexing machinery, which must panic when the index is invalid.
The optimizer can remove that panic path only when it proves the invalid case cannot occur.
Short, local relationships such as `i < slice.len()` are easier to prove than relationships hidden behind helper functions, trait objects, or unrelated branches.

Assertions are useful because they are both runtime validation and optimization information.
If the assertion fails, the program panics before the loop.
If it passes, later code can be optimized under that known condition.
Slicing before a loop is often better than repeating arithmetic inside the loop.
Once `let data = &data[..n];` succeeds, the slice value itself carries the narrowed length.
Adapters such as `zip`, `chunks_exact`, and `windows` encode shape constraints in the iterator, which also avoids manual index math.
Unsafe `get_unchecked` removes the check by promising the invariant yourself; if the promise is wrong, the program has undefined behavior even if the reference is never visibly used for much.

## Example
```rust
fn dot_prefix(a: &[i32], b: &[i32], n: usize) -> i32 {
    assert!(n <= a.len());
    assert!(n <= b.len());

    a[..n]
        .iter()
        .zip(&b[..n])
        .map(|(left, right)| (*left) * (*right))
        .sum()
}

fn main() {
    let a = [1, 2, 3, 4];
    let b = [10, 20, 30, 40];

    assert_eq!(dot_prefix(&a, &b, 3), 140);
}
```

The function validates `n` once, slices to the valid prefix once, and then iterates over items.
No indexing is needed in the hot expression, so there are fewer checks for the optimizer to reason about.

## Worked example: chunking instead of index arithmetic
```rust
fn add_pairs(input: &[i32], output: &mut Vec<i32>) {
    output.clear();
    output.reserve(input.len() / 2);

    output.extend(input.chunks_exact(2).map(|pair| pair[0] + pair[1]));
}

fn main() {
    let input = [1, 2, 10, 20, 100];
    let mut sums = Vec::new();

    add_pairs(&input, &mut sums);
    assert_eq!(sums, [3, 30]);
}
```

`chunks_exact(2)` states that each yielded chunk has exactly two elements, and the remainder is ignored.
The indexing inside the closure is against a two-element chunk, not the original arbitrary slice.
If the remainder must be handled, call `chunks_exact(2).remainder()` after the loop and write that behavior explicitly.

## Common errors
Safe indexing panics on invalid input; unsafe indexing is worse because invalid input becomes undefined behavior.

```text
thread 'main' panicked at 'index out of bounds: the len is 3 but the index is 3'
```

Fix the precondition or use `get` when out-of-range input is expected and should be handled.
Do not replace the line with `get_unchecked(3)`; the slice documentation explicitly requires the index to be in bounds.

```text
error[E0133]: call to unsafe function `core::slice::<impl [T]>::get_unchecked` is unsafe and requires unsafe block
```

The fix is not merely adding `unsafe`.
First prefer iteration, slicing, or assertions.
If `unsafe` remains necessary, document the invariant immediately above the block and keep the unchecked access tiny.

## Best practice
- ✅ Prefer item iteration, `zip`, `chunks_exact`, and `windows` over manual indexing.
- ✅ Slice outside the hot loop when a loop operates on a known subrange.
- ✅ Add explicit `assert!` preconditions when they both document correctness and help optimization.
- ✅ Benchmark before changing safe indexing code; bounds checks may already be gone.
- ✅ Keep any unsafe indexing in a tiny, documented wrapper with tests for the invariant.
- ✅ Use `chunks_exact` when the loop works on fixed-size groups and has a clear remainder policy.
- ✅ Use `split_at` or range slicing to prove two subranges are valid before processing them.
- ✅ Inspect generated code only after a benchmark says the check matters; source-level guesses are unreliable.

## Pitfalls
- ⚠️ Replacing safe indexing with `get_unchecked` before measuring turns a possible nanosecond cost into a soundness obligation.
- ⚠️ Manual index loops written "for speed" are often [[Manual Index Loops for Speed]].
- ⚠️ Using `get()` everywhere for performance is confused; `get()` returns `Option` and changes control flow.
- ⚠️ Asserting the wrong relationship can make code panic earlier but still not prove the actual index is safe.
- ⚠️ Hiding indexing inside closures or helper functions may make the optimizer's proof harder unless inlining exposes the relationship.
- ⚠️ `get_unchecked(len)` is undefined behavior, not a nullable end pointer trick.
- ⚠️ Removing a bounds check can expose the next bottleneck; re-benchmark before keeping less clear code.

## See also
[[Iterator Performance]] · [[Manual Index Loops for Speed]] · [[Index Panics vs get]] · [[Arrays]] · [[Vec]] · [[Slices]] · [[The inline Attribute]] · [[Benchmarking with Criterion]] · [[Speculative Micro-Optimization]] · [[Performance & Optimization]]

## Sources
- The Rust Programming Language, ch. 13.4 "Comparing Performance: Loops vs. Iterators" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-04-performance.html
- Rust standard library, slice `get_unchecked` — [[the-reference]],
  https://doc.rust-lang.org/std/primitive.slice.html#method.get_unchecked
- The Rust Reference, "Array and index expressions" — [[the-reference]],
  https://doc.rust-lang.org/reference/expressions/array-expr.html
