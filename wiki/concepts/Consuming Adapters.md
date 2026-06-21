---
type: concept
title: "Consuming Adapters"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, consumers, adapters]
domain: "Closures & Iterators"
difficulty: basic
related: ["[[Iterators]]", "[[The Iterator Trait]]", "[[Iterator Adapters]]", "[[Lazy Evaluation]]", "[[Ownership]]", "[[Unnecessary Collect]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.sum"]
rust_version: "edition 2024 / 1.85+"
---

# Consuming Adapters

Consuming adapters drive an iterator by repeatedly calling `next`, using up the iterator to produce a final value or side effect.

## What it is
Consuming adapters include `sum`, `product`, `count`, `collect`, `fold`, `reduce`, `find`, `any`,
`all`, `position`, `for_each`, and similar methods. They are terminal operations for iterator
chains.

They are called "consuming" because they take ownership of the iterator value. After a consuming
adapter runs, that iterator cannot be used again.

## How it works
An adapter chain is lazy until a consumer asks for items. The consuming method owns the iterator
and repeatedly calls `next` until it has enough information to return.

Some consumers exhaust the iterator, such as `sum` and `collect`. Others short-circuit, such as
`find`, `any`, and `all`.

Consumers differ in whether they take `self` by value or `&mut self`. Methods like `sum` and
`collect` take ownership of the iterator value. Methods such as `find`, `any`, and `all` take a
mutable receiver, so they can leave the iterator positioned after the point where they stopped.

## Example
```rust
fn main() {
    let numbers = [1, 2, 3, 4, 5];

    let total: i32 = numbers.iter().copied().sum();
    assert_eq!(total, 15);

    let first_large = numbers.iter().find(|&&n| n > 3);
    assert_eq!(first_large, Some(&4));

    let evens: Vec<i32> = numbers.iter().copied().filter(|n| *n % 2 == 0).collect();
    assert_eq!(evens, vec![2, 4]);
}
```

Each consumer determines how much of the iterator must be evaluated.

## Worked example
```rust
fn first_error_position(lines: &[&str]) -> Option<usize> {
    lines
        .iter()
        .position(|line| line.contains("ERROR"))
}

fn parse_all(input: &[&str]) -> Result<Vec<u32>, std::num::ParseIntError> {
    input.iter().map(|s| s.parse::<u32>()).collect()
}

fn main() {
    let logs = ["INFO boot", "WARN slow", "ERROR disk", "ERROR net"];
    assert_eq!(first_error_position(&logs), Some(2));

    assert_eq!(parse_all(&["10", "20"]).unwrap(), vec![10, 20]);
    assert!(parse_all(&["10", "nope", "30"]).is_err());
}
```

`position` short-circuits at the first match. `collect::<Result<Vec<_>, _>>()` drives the iterator
until the first parse error or until all values are collected.

## Common errors
```rust
fn main() {
    let values = [1, 2, 3];
    let iter = values.iter();
    let total: i32 = iter.copied().sum();
    // let count = iter.count();
}
```

Uncommenting the final line gives `error[E0382]: use of moved value: iter` because `copied()`
takes ownership of the iterator and `sum` consumes the chain. Create a new iterator or use
`by_ref()` when you intentionally want partial consumption.

## Best practice
- ✅ Pick the consumer that states the intent: `any` for existence, `find` for first match, `sum` for totals.
- ✅ Prefer short-circuiting consumers over collecting when you only need one answer.
- ✅ Annotate the target type for `collect` or `sum` when inference is ambiguous.
- ✅ Use `collect::<Result<Vec<_>, _>>()` or `collect::<Option<Vec<_>>>()` to stop on the first failure in fallible pipelines.
- ✅ Reach for `try_fold` or `try_for_each` when aggregation may fail and you want early exit.

## Pitfalls
- ⚠️ Trying to use the same iterator variable after `sum`, `collect`, or another consuming method.
- ⚠️ Calling `collect::<Vec<_>>()` when `count`, `any`, `find`, or `fold` would avoid allocation. See [[Unnecessary Collect]].
- ⚠️ Consuming an infinite iterator with `collect` or `count` without a bound such as `take`.
- ⚠️ Assuming `for_each` is clearer than a `for` loop for side effects; use the form that best communicates control flow.
- ⚠️ Forgetting short-circuit consumers may leave a borrowed iterator partially consumed rather than exhausted.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[The Iterator Trait]] · [[Iterator Adapters]] · [[Lazy Evaluation]] · [[Unnecessary Collect]] · [[Ownership]] · [[Zero-Cost Abstractions]] · [[Option vs Result]] · [[Error Propagation]]

## Sources
- The Rust Programming Language, ch. 13.2 "Methods That Consume the Iterator" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Rust standard library, `Iterator::sum` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.sum
