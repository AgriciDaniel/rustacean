---
type: pattern
title: "SmallVec for Inline Storage"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, allocation, smallvec]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Reducing Heap Allocations]]", "[[Capacity and Reallocation]]", "[[Vec]]", "[[Choosing Collection Types]]", "[[Arena Allocation]]", "[[Avoiding Premature Optimization]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html", "https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html", "https://docs.rs/smallvec/latest/smallvec/struct.SmallVec.html"]
rust_version: "edition 2024 / 1.85+"
---

# SmallVec for Inline Storage

`SmallVec` is a collection strategy for values that are usually short: store a fixed number of elements inline and spill to heap allocation only when that inline capacity is exceeded.

## What it is
`SmallVec` is not part of the Rust standard library.
It is an external crate commonly used when profiling shows that many short `Vec` allocations dominate a hot path.
The idea is simple: reserve space for `N` elements inside the collection value itself, then allocate like a normal `Vec` only for larger cases.
For the stable 1.x `smallvec` crate line, the common type spelling is `SmallVec<[T; N]>`.
Crate APIs can evolve, so check the project's locked dependency version before exposing this type in public API.

This is a good fit for data that is overwhelmingly small but not statically bounded.
Examples include a syntax node with usually one or two children, a temporary list of short matches, or a parser path with a common small case.
It is a poor fit when the collection is usually large, when the element type is huge, or when the extra branch and larger struct size hurt more than allocation removal helps.

## How it works
The inline capacity is part of the type.
For example, `SmallVec<[u8; 8]>` can hold up to eight bytes inline before spilling.
That means choosing `N` is a performance decision.
Too small and the code still allocates frequently.
Too large and every collection value becomes bulky, increasing stack size and move cost.

Treat `SmallVec` as a targeted replacement for `Vec`, not as a default collection.
First confirm with profiling that allocations are hot.
Then choose an inline capacity from real data distribution, not from guesswork.
Finally benchmark both the common case and the spill case.
Mechanically, a `SmallVec` value must store enough metadata to know whether its elements are inline or spilled.
Operations such as push and drop therefore have an extra state distinction compared with a plain `Vec`.
When inline, moving the `SmallVec` moves the inline storage as part of the value; when spilled, it behaves more like moving a `Vec` pointer/length/capacity triple.
That is why large inline capacities or large element types can make the "optimization" slower.

## Example
```rust
use smallvec::SmallVec;

fn ascii_digits(input: &str) -> SmallVec<[u8; 8]> {
    let mut digits = SmallVec::new();
    for byte in input.bytes() {
        if byte.is_ascii_digit() {
            digits.push(byte);
        }
    }
    digits
}

fn main() {
    let digits = ascii_digits("room 204");
    assert_eq!(&digits[..], b"204");
}
```

This example is minimal for a crate that depends on `smallvec`.
The call sites can use slices of the result just like they would with a `Vec`.
The optimization only pays when results usually fit within the inline capacity.

## Worked example: keep the optimization private
```rust
use smallvec::SmallVec;

pub fn first_ascii_digits(input: &str, limit: usize) -> Vec<u8> {
    let mut digits: SmallVec<[u8; 16]> = SmallVec::new();

    for byte in input.bytes().filter(u8::is_ascii_digit).take(limit) {
        digits.push(byte);
    }

    digits.into_vec()
}

fn main() {
    assert_eq!(first_ascii_digits("a1b2c3", 2), b"12");
}
```

The function uses `SmallVec` internally but returns `Vec<u8>`.
That keeps the dependency and inline capacity out of the public contract.
If returning a `SmallVec` is part of the performance API, document the capacity choice and treat changing it as an API-affecting decision.

## Common errors
The most common setup error is forgetting that `SmallVec` is an external dependency:

```text
error[E0432]: unresolved import `smallvec`
```

Add the crate to `[dependencies]` with a version appropriate for the project.
Another common mistake is copying examples from a different major-version line:

```text
error[E0107]: struct takes 1 generic argument but 2 generic arguments were supplied
```

For current stable `smallvec` 1.x, use the array form such as `SmallVec<[u8; 8]>`.
Do not assume examples for an alpha 2.x line apply to a 1.x dependency.

## Best practice
- ✅ Use `SmallVec` after [[Profiling Rust Programs]] shows many small `Vec` allocations in a hot path.
- ✅ Choose the inline capacity from observed data, such as percentiles from production or benchmark inputs.
- ✅ Keep element types small enough that inline storage does not bloat the stack or parent structs.
- ✅ Benchmark the inline case and the spill case with [[Benchmarking with Criterion]].
- ✅ Prefer ordinary [[Vec]] when allocation is not hot or the collection is usually large.
- ✅ Hide `SmallVec` behind module-private implementation details unless callers benefit from the exact storage policy.
- ✅ Include pathological spill-heavy inputs in benchmarks; the uncommon case can still dominate tail latency.
- ✅ Revisit the capacity when production data changes; a once-good percentile can become stale.

## Pitfalls
- ⚠️ Using `SmallVec` everywhere speculatively is [[Speculative Micro-Optimization]].
- ⚠️ Oversized inline capacity can make moves and stack frames more expensive.
- ⚠️ Assuming no allocation ever happens is wrong; spilling still allocates.
- ⚠️ Exposing `SmallVec` in a public API can force downstream users to depend on that crate and capacity choice.
- ⚠️ Replacing algorithmic fixes with collection tweaks is a form of [[Avoiding Premature Optimization]].
- ⚠️ Using `SmallVec<[Large; N]>` can make each collection value expensive to move or store inside parent structs.
- ⚠️ Treating inline storage as stack-only is imprecise; a `SmallVec` embedded in a heap allocation stores its inline buffer there.

## See also
[[Reducing Heap Allocations]] · [[Capacity and Reallocation]] · [[Vec]] · [[Choosing Collection Types]] · [[Arena Allocation]] · [[Benchmarking with Criterion]] · [[Profiling Rust Programs]] · [[Speculative Micro-Optimization]] · [[Avoiding Premature Optimization]] · [[Performance & Optimization]]

## Sources
- Rust standard library, `Vec` — [[the-book]],
  https://doc.rust-lang.org/std/vec/struct.Vec.html
- The Cargo Book, "Specifying dependencies" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- The Rust Programming Language, ch. 14.2 "Publishing a Crate to Crates.io" — [[the-book]],
  https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html
- `smallvec` crate documentation, `SmallVec`,
  https://docs.rs/smallvec/latest/smallvec/struct.SmallVec.html
