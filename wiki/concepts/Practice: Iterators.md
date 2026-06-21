---
type: concept
title: "Practice: Iterators"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, iterators]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Iterators]]", "[[The Iterator Trait]]", "[[Iterator Adapters]]", "[[Iterator map and filter]]", "[[Iterator collect and FromIterator]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Iterators

The iterators group teaches processing sequences through lazy adapter chains and explicit consumption. The key idea is that adapters describe work, and consumers like `collect`, `sum`, or `for` actually run it.

## What it is
These exercises cover `iter`, `into_iter`, `map`, `filter`, `collect`, `fold`, consuming adapters, and implementing logic without manual indexing.

## How it works
An iterator produces `Item` values one at a time. Most adapters are lazy and return another iterator; consumers pull items through the chain and produce a final value.

## Example
```rust
fn sum_squared_evens(values: &[i32]) -> i32 {
    values
        .iter()
        .copied()
        .filter(|n| n % 2 == 0)
        .map(|n| n * n)
        .sum()
}

fn main() {
    println!("{}", sum_squared_evens(&[1, 2, 3, 4]));
}
```

## Best practice
- ✅ Choose `iter`, `iter_mut`, or `into_iter` based on borrow versus ownership needs.
- ✅ Keep chains readable by naming intermediate results when logic gets dense.
- ✅ Use collection-specific methods only when they express the job better than adapters.

## Pitfalls
- ⚠️ Lazy adapters do nothing until consumed.
- ⚠️ Closure argument types differ between borrowed and owned iteration.
- ⚠️ Do not collect just to iterate again unless ownership or reuse requires it.

## See also
[[Practice (Rustlings)]] · [[Iterators]] · [[The Iterator Trait]] · [[Iterator Adapters]] · [[Iterator map and filter]] · [[Iterator collect and FromIterator]] · [[Consuming Adapters]]

## Sources
- Rustlings `18_iterators` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

