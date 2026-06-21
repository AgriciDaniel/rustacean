---
type: concept
title: "Iterator sum product and count"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, sum, product, count]
domain: "std: Iterator Adapter Catalog"
difficulty: basic
related: ["[[Iterator fold and reduce]]", "[[Consuming Adapters]]", "[[Integer Overflow]]", "[[Iterator collect and FromIterator]]", "[[Option]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.sum", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.product", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.count"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator sum product and count

`sum`, `product`, and `count` are consuming adapters for common totals: addition, multiplication, and number of yielded items.

## What it is
`Iterator::sum` consumes an iterator and adds all yielded items.
Its return type must implement `Sum<Self::Item>`.
An empty numeric iterator returns the additive identity for the requested type.
`Iterator::product` consumes an iterator and multiplies all yielded items.
Its return type must implement `Product<Self::Item>`.
An empty numeric iterator returns the multiplicative identity for the requested type.
`Iterator::count` consumes an iterator and returns how many items it yielded as `usize`.
These methods are clearer than spelling simple totals with `fold`.
They are terminal consumers, not lazy adapters.
They may need type annotations because several numeric result types can be valid.

## How it works
`sum` repeatedly combines items using the type's `Sum` implementation.
`product` repeatedly combines items using the type's `Product` implementation.
Primitive integer sums and products can overflow.
With overflow checks enabled, overflowing primitive integer arithmetic panics.
Without overflow checks, primitive integer overflow follows Rust's normal release behavior for those operations.
`Option` and `Result` also have standard summing and product behavior through trait implementations.
This can short-circuit on absent or failed values while accumulating present successes.
`count` repeatedly calls `next` until the iterator ends.
It must call `next` at least once even on an empty iterator.
Counting more than `usize::MAX` yielded items can overflow or panic.
On infinite iterators, `count`, `sum`, and `product` generally do not terminate.

## Example
```rust
fn main() {
    let values = [1, 2, 3, 4];

    let sum: i32 = values.iter().sum();
    let product: i32 = values.iter().product();
    let count = values.iter().filter(|n| **n % 2 == 0).count();

    assert_eq!(sum, 10);
    assert_eq!(product, 24);
    assert_eq!(count, 2);
}
```

## Edge cases
```rust
fn main() {
    let empty: [i32; 0] = [];
    assert_eq!(empty.into_iter().sum::<i32>(), 0);
    assert_eq!(empty.into_iter().product::<i32>(), 1);

    let checked: Option<i32> = [Some(2), Some(3), Some(4)].into_iter().sum();
    assert_eq!(checked, Some(9));

    let missing: Option<i32> = [Some(2), None, Some(4)].into_iter().product();
    assert_eq!(missing, None);
}
```

## Best practice
- ✅ Use `sum` for addition and `product` for multiplication instead of custom folds.
- ✅ Add a result type annotation for numeric totals.
- ✅ Use `count` after filters when you need the number of matches.
- ✅ Use checked arithmetic in a fold when overflow must be handled explicitly.
- ✅ Bound infinite iterators with `take` before total consumers.
- ✅ Prefer `any` or `find` when existence is enough and a full count is wasteful.
- ✅ Know whether `Option` or `Result` accumulation is preserving absence or errors as intended.
- ✅ Use `len` on exact collections when you already have the collection and need its size.

## Pitfalls
- ⚠️ `count` consumes the iterator and discards the items.
- ⚠️ `sum` and `product` over infinite iterators do not finish.
- ⚠️ Primitive integer totals can overflow; see [[Integer Overflow]].
- ⚠️ Counting more than `usize::MAX` items can overflow or panic.
- ⚠️ `count() > 0` may traverse more than needed; use `next().is_some()` or `any`.
- ⚠️ Type inference may not know whether `sum` should return `i32`, `usize`, or another type.
- ⚠️ Floating-point sums are order-sensitive due to rounding.
- ⚠️ Calling `collect` before `count` is usually an [[Unnecessary Collect]].

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator fold and reduce]] · [[Iterator predicate search adapters]] · [[Iterator take skip and while bounds]] · [[Iterator collect and FromIterator]] · [[Consuming Adapters]] · [[Integer Overflow]] · [[Option]] · [[Result]] · [[Type Inference]] · [[Unnecessary Collect]]

## Sources
- Rust standard library, `Iterator::sum` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.sum
- Rust standard library, `Iterator::product` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.product
- Rust standard library, `Iterator::count` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.count
