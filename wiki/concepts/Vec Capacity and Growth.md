---
type: concept
title: "Vec Capacity and Growth"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, vec, allocation, capacity, performance]
domain: "std: Vec, String & Slices"
difficulty: intermediate
related: ["[[Vec Methods Reference]]", "[[Capacity and Reallocation]]", "[[Reducing Heap Allocations]]", "[[Holding Collection Element References Across Mutation]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation", "https://doc.rust-lang.org/std/vec/struct.Vec.html#method.reserve"]
rust_version: "edition 2024 / 1.85+"
---

# Vec Capacity and Growth

Vector capacity is the currently allocated room for elements, and growth happens when a push or extend would make `len() > capacity()`.

## What it is
`len()` is the number of initialized elements.
`capacity()` is how many elements can fit without allocating again.
A newly created `Vec::new()` allocates nothing until elements are inserted.
`Vec::with_capacity(n)` asks for enough room for at least `n` elements.
The allocator may provide more capacity than requested.
Capacity is measured in elements, not bytes.
A vector's allocation is contiguous, so reallocation moves all elements to a new buffer when the old buffer cannot grow in place.
That move is why references, raw pointers, and indexes need different levels of care.

## How it works
`push` and `extend` grow length.
If spare capacity is available, the operation writes into existing allocation.
If spare capacity is not available, the vector reserves more allocation before inserting.
The exact growth strategy is intentionally unspecified.
`reserve(additional)` ensures capacity for at least `len() + additional` and may over-allocate to reduce future reallocations.
`reserve_exact(additional)` requests the minimum extra space but the allocator can still return more.
`try_reserve` and `try_reserve_exact` report allocation failure with `Result` instead of panicking or aborting.
`shrink_to_fit` asks to reduce capacity as much as possible.
`shrink_to(min_capacity)` asks to keep at least a chosen amount.
`clear` and `truncate` drop elements but keep allocation for reuse.
Use capacity deliberately for hot builders, parsers, and batch transforms; ignore it for small or one-off code.

## Example
```rust
fn main() {
    let input = ["red", "green", "blue"];
    let mut out = Vec::with_capacity(input.len());

    for item in input {
        out.push(item.len());
    }

    assert_eq!(out, vec![3, 5, 4]);
    assert!(out.capacity() >= out.len());

    out.clear();
    assert_eq!(out.len(), 0);
    assert!(out.capacity() >= input.len());

    out.try_reserve(10).expect("small reserve should succeed");
    assert!(out.capacity() >= 10);
}
```

## Best practice
- ✅ Use `Vec::with_capacity(n)` when `n` is a real estimate, such as `input.len()`.
- ✅ Use `reserve` before a known burst of appends.
- ✅ Prefer `try_reserve` in fallible, service-facing, or adversarial-input paths.
- ✅ Reuse a buffer with `clear` when repeated allocations dominate runtime.
- ✅ Treat capacity as an optimization detail, not as part of program correctness.
- ✅ Keep borrowed element references short-lived around operations that might grow the vector.
- ✅ Use `shrink_to_fit` only when memory pressure matters and reuse is unlikely.
- ✅ Benchmark before contorting code purely to reduce reallocations.

## Pitfalls
- ⚠️ Assuming a specific growth factor is non-portable; the standard library does not promise one.
- ⚠️ `with_capacity(0)` and `Vec::new()` allocate no buffer for normal non-zero-sized element types.
- ⚠️ `clear` does not free allocation; use `shrink_to_fit` or drop the vector if that matters.
- ⚠️ `shrink_to_fit` is a request, not a contractual exact capacity.
- ⚠️ Holding pointers across `reserve`, `push`, `insert`, or `extend` is invalid if reallocation occurs.
- ⚠️ `reserve_exact` can cause repeated allocations when called in a loop with small increments.
- ⚠️ Very large capacity requests can fail or panic; use fallible APIs when input controls size.
- ⚠️ Zero-sized element vectors have special capacity behavior; do not use capacity arithmetic as byte accounting.

## See also
[[std: Vec, String & Slices]] · [[Vec Methods Reference]] · [[Capacity and Reallocation]] · [[Reducing Heap Allocations]] · [[Holding Collection Element References Across Mutation]] · [[Borrowing Strings and Slices]] · [[String vs str Methods]] · [[Building Strings Efficiently]] · [[Index Panics vs get]]

## Sources
- Rust standard library, `Vec` capacity and reallocation — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation
- Rust standard library, `Vec::reserve` and `Vec::try_reserve` — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#method.reserve
