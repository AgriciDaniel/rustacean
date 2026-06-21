---
type: pattern
title: "Reducing Heap Allocations"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, allocation, collections]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Capacity and Reallocation]]", "[[Vec]]", "[[String and str]]", "[[Needless Clone]]", "[[SmallVec for Inline Storage]]", "[[Arena Allocation]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html#method.with_capacity", "https://doc.rust-lang.org/std/string/struct.String.html#method.with_capacity", "https://doc.rust-lang.org/book/ch13-02-iterators.html#removing-a-clone-using-an-iterator"]
rust_version: "edition 2024 / 1.85+"
---

# Reducing Heap Allocations

Reducing heap allocations means reusing, pre-sizing, borrowing, or changing data flow so hot paths do less allocator work without changing program behavior.

## What it is
Heap allocation is not free.
Allocators manage metadata, may synchronize between threads, and may ask the operating system for more memory.
In Rust, many allocations are explicit in types such as `Vec`, `String`, `Box`, `Arc`, and collection maps, but they can also hide behind `clone`, `format!`, `to_string`, `collect`, and trait-object boxing.

Allocation reduction is often one of the highest-value Rust optimizations because it can improve CPU time, memory footprint, and cache behavior at the same time.
It should still be driven by measurement.
Some allocations are outside hot paths, some make APIs simpler, and some are required to own data safely.

## How it works
The common allocation fixes are simple.
Use `with_capacity` when a collection's approximate size is known.
Move buffers outside loops and call `clear()` to reuse the allocation.
Borrow with `&str` or `&[T]` when a function does not need ownership.
Move owned values out of an iterator instead of cloning from a borrowed slice.
Avoid intermediate `collect()` calls when a lazy iterator can flow directly to the consumer.
These fixes work because `Vec` and `String` separate length from capacity.
Length is the initialized, visible data; capacity is the currently allocated storage.
Pushing beyond capacity may allocate a larger buffer and move existing elements or bytes.
`clear()` drops elements or truncates bytes to length zero while keeping the allocation available for the next iteration.

Capacity and length are different.
`clear()` drops elements and sets length to zero, but keeps capacity for reuse.
`shrink_to_fit()` may reduce memory, but it is usually the opposite of what a hot loop wants.
Pre-sizing is a performance hint; correctness must not depend on capacity.
For fallible or adversarial sizes, prefer `try_reserve` over blindly reserving untrusted input sizes.
For strings, capacity is measured in bytes, not Unicode scalar values or grapheme clusters.
For `Vec<()>`, capacity behaves specially because zero-sized values need no allocation; do not use it as a proxy for real allocator behavior.

## Example
```rust
fn csv_line(fields: &[&str], output: &mut String) {
    output.clear();

    for (i, field) in fields.iter().enumerate() {
        if i > 0 {
            output.push(',');
        }
        output.push_str(field);
    }
}

fn main() {
    let rows = [
        ["Ada", "Lovelace", "1815"],
        ["Grace", "Hopper", "1906"],
    ];

    let mut line = String::with_capacity(64);
    for row in rows {
        csv_line(&row, &mut line);
        assert!(line.contains(','));
    }
}
```

The buffer is allocated once, then reused for each row.
The function takes `&mut String` because it needs scratch storage, not ownership of a fresh string every time.

## Worked example: collect once, extend many times
```rust
fn append_even_numbers(input: &[u32], output: &mut Vec<u32>) {
    output.clear();
    output.reserve(input.len() / 2);

    output.extend(input.iter().copied().filter(|n| n % 2 == 0));
}

fn main() {
    let input = [1, 2, 3, 4, 5, 6, 7, 8];
    let mut scratch = Vec::with_capacity(input.len());

    append_even_numbers(&input, &mut scratch);
    assert_eq!(scratch, [2, 4, 6, 8]);

    append_even_numbers(&[10, 11, 12], &mut scratch);
    assert_eq!(scratch, [10, 12]);
}
```

This keeps ownership of the reusable allocation at the caller.
`reserve` is deliberately a lower-bound hint; if the estimate is wrong, `Vec` still grows correctly.
Use `reserve_exact` only when the exact capacity matters enough to trade away the allocator's growth strategy.

## Common errors
A frequent optimization attempt is returning a borrowed scratch buffer created inside the function:

```text
error[E0515]: cannot return reference to local variable `buf`
```

The fix is to return an owned `String`/`Vec`, or pass scratch storage in from the caller as `&mut String` or `&mut Vec<T>`.
Another common error is trying to mutate a collection while iterating over borrowed items from it:

```text
error[E0502]: cannot borrow `items` as mutable because it is also borrowed as immutable
```

Use a separate output buffer, iterate by index only when justified, or restructure with `drain`, `retain`, or `mem::take` depending on ownership.

## Best practice
- ✅ Use `Vec::with_capacity` and `String::with_capacity` when the expected size is known or cheaply estimated.
- ✅ Reuse `Vec` and `String` buffers across loop iterations with `clear()`.
- ✅ Accept borrowed inputs such as `&str` and `&[T]` when ownership is unnecessary.
- ✅ Remove hot-path `.clone()` calls by moving values, borrowing, or changing iterator ownership.
- ✅ Use [[SmallVec for Inline Storage]] or [[Arena Allocation]] only after profiling shows ordinary allocation is a bottleneck.
- ✅ Use `try_reserve` when the requested capacity comes from user input or a file format and allocation failure should be handled.
- ✅ Prefer writing into an existing `String` with `write!` or `push_str` over repeated `format!` in hot loops.
- ✅ Keep scratch buffers local to the worker/thread that uses them; shared scratch can introduce locking that costs more than allocation.

## Pitfalls
- ⚠️ Cloning to satisfy the borrow checker can hide repeated allocations; see [[Needless Clone]].
- ⚠️ Calling `collect()` just to iterate again allocates unnecessarily; see [[Unnecessary Collect]].
- ⚠️ Reusing a buffer without `clear()` appends stale data and changes behavior.
- ⚠️ Over-reserving huge capacity can increase memory footprint and cache pressure.
- ⚠️ Optimizing allocations in cold startup code while ignoring hot runtime allocation is [[Avoiding Premature Optimization]].
- ⚠️ Calling `shrink_to_fit()` after every operation usually creates allocator churn instead of reducing it.
- ⚠️ Exposing scratch-buffer parameters in a public API can leak an internal optimization into callers; prefer it where the performance contract is explicit.

## See also
[[Capacity and Reallocation]] · [[Vec]] · [[String and str]] · [[Needless Clone]] · [[Unnecessary Collect]] · [[SmallVec for Inline Storage]] · [[Arena Allocation]] · [[Profiling Rust Programs]] · [[Benchmarking with Criterion]] · [[Ownership]] · [[Borrowing]] · [[Performance & Optimization]]

## Sources
- Rust standard library, `Vec::with_capacity` — [[the-book]],
  https://doc.rust-lang.org/std/vec/struct.Vec.html#method.with_capacity
- Rust standard library, `String::with_capacity` — [[the-book]],
  https://doc.rust-lang.org/std/string/struct.String.html#method.with_capacity
- The Rust Programming Language, ch. 13.2 "Removing a clone using an iterator" — [[the-book]],
  https://doc.rust-lang.org/book/ch13-02-iterators.html#removing-a-clone-using-an-iterator
