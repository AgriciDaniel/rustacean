---
type: concept
title: "Iterator Adapters"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, adapters, lazy]
domain: "Closures & Iterators"
difficulty: basic
related: ["[[Iterators]]", "[[The Iterator Trait]]", "[[Consuming Adapters]]", "[[Lazy Evaluation]]", "[[Closures]]", "[[Unconsumed Iterator Adapters]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator Adapters

Iterator adapters are lazy `Iterator` methods that transform one iterator into another without doing work until a consumer asks for items.

## What it is
Adapters include methods such as `map`, `filter`, `take`, `skip`, `enumerate`, `zip`, `chain`,
`rev`, and `flat_map`. They compose traversal behavior without allocating intermediate
collections by default.

Many adapters take closures, which makes [[Closures]] and [[Fn, FnMut, FnOnce]] central to
idiomatic iterator code.

## How it works
Calling an adapter returns a new iterator value. That returned value stores the previous iterator
and any closure or configuration it needs. No element is transformed or filtered at the moment the
adapter is created.

Work begins when a consuming adapter, a `for` loop, or a direct `next` call pulls items through
the chain. Each requested item flows through the adapter pipeline.

Most adapter types are zero-sized or small wrappers plus stored closures and configuration. The
large-looking concrete type of a chain is normally optimized away after monomorphization, but it
still exists at the type level, which is why public APIs usually return `impl Iterator` instead
of spelling the adapter type.

## Example
```rust
fn main() {
    let numbers = [1, 2, 3, 4, 5, 6];

    let doubled_evens: Vec<i32> = numbers
        .iter()
        .copied()
        .filter(|n| *n % 2 == 0)
        .map(|n| n * 2)
        .collect();

    assert_eq!(doubled_evens, vec![4, 8, 12]);
}
```

`filter` and `map` describe the transformation; `collect` consumes the chain and produces the
vector.

## Worked example
```rust
fn parse_ids(input: &str) -> impl Iterator<Item = u64> + '_ {
    input
        .split(',')
        .map(str::trim)
        .filter(|part| !part.is_empty())
        .filter_map(|part| part.parse::<u64>().ok())
}

fn main() {
    let ids: Vec<u64> = parse_ids("10, bad, 20, , 30").collect();
    assert_eq!(ids, vec![10, 20, 30]);

    let first = parse_ids("x, 99, 100").next();
    assert_eq!(first, Some(99));
}
```

The parser streams through the input and skips invalid fields without allocating a temporary
`Vec<&str>`.

## Common errors
```rust
fn main() {
    let values = [1, 2, 3];
    values.iter().map(|n| *n + 1);
}
```

Rust warns `unused Map that must be used` and notes that iterators are lazy. Add a terminal
consumer such as `.collect::<Vec<_>>()`, `.sum::<i32>()`, or use a `for` loop for side effects.

## Best practice
- ✅ Chain adapters when each step has a clear, named transformation role.
- ✅ Use `.copied()` or `.cloned()` intentionally when turning references into values.
- ✅ End the chain with a consumer such as `collect`, `sum`, `count`, `find`, or a `for` loop.
- ✅ Prefer `filter_map` when filtering and mapping through `Option` are one conceptual step.
- ✅ Use `inspect` only for debugging or observation; do not make it carry essential side effects.

## Pitfalls
- ⚠️ Forgetting the terminal consumer, leaving the adapter chain unused. See [[Unconsumed Iterator Adapters]].
- ⚠️ Using `map` only for side effects; prefer `for_each` or a `for` loop when the point is an effect.
- ⚠️ Adding `collect` between every adapter step. See [[Unnecessary Collect]].
- ⚠️ Building chains so clever that the data flow becomes harder to review; a named helper or loop can be clearer.
- ⚠️ Accidentally cloning large items with `.cloned()` where borrowing or `.copied()` for small `Copy` values was intended.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[The Iterator Trait]] · [[Consuming Adapters]] · [[Lazy Evaluation]] · [[Closures]] · [[Unconsumed Iterator Adapters]] · [[Unnecessary Collect]] · [[Return Iterators Instead of Collecting]] · [[Zero-Cost Abstractions]]

## Sources
- The Rust Programming Language, ch. 13.2 "Methods That Produce Other Iterators" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Rust standard library, `Iterator::map` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map
