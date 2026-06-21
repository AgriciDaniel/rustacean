---
type: pattern
title: "Lending Iterators with GATs"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, gat, iterators, lifetimes, pattern]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Generic Associated Types]]", "[[Required Bounds on Generic Associated Types]]", "[[Iterators]]", "[[Lifetimes]]", "[[Higher-Ranked Trait Bounds]]", "[[Borrowing]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/associated-items.html#associated-types", "https://doc.rust-lang.org/reference/items/associated-items.html#required-where-clauses-on-generic-associated-types"]
rust_version: "edition 2024 / 1.85+"
---

# Lending Iterators with GATs

A lending iterator returns items that may borrow from the iterator itself, using a generic associated type to tie each item to the borrow of `self`.
Use this pattern when ordinary `Iterator::Item` is too detached to express borrowed views.

## What it is
The standard `Iterator` trait has one associated type: `type Item`.
That item type is fixed for the iterator and cannot depend on the lifetime of each `next` borrow.
A lending iterator changes the shape to `type Item<'a> where Self: 'a`.
Then `next<'a>(&'a mut self) -> Option<Self::Item<'a>>` can return a value borrowing from the iterator.
This is useful for windowing, streaming parsers, arena-backed traversals, and mutable view APIs.
The pattern is powered by [[Generic Associated Types]].
It is often paired with [[Required Bounds on Generic Associated Types]].
It is not a drop-in replacement for [[The Iterator Trait]] because many standard iterator adapters expect an ordinary `Iterator`.

## How it works
The borrow of `self` creates the lifetime used to instantiate the associated item.
Each call to `next` can lend a value whose lifetime is no longer than that borrow.
The caller must finish using the lent item before calling `next` again if the method needs `&mut self`.
That restriction is the point: it prevents two mutable or invalidated views from existing at once.
Unlike returning `&'a T` from a struct with a single lifetime parameter, the GAT lets each call create a fresh relationship.
Unlike HRTB-only callbacks, the lent value can be returned to the caller.
The design keeps unsafe lifetime tricks out of the implementation.
The tradeoff is lower compatibility with existing iterator combinators.

## Example
```rust
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct Lines<'data> {
    rest: &'data str,
}

impl<'data> LendingIterator for Lines<'data> {
    type Item<'a> = &'a str
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        let rest = self.rest;
        if rest.is_empty() {
            return None;
        }

        if let Some(index) = rest.find('\n') {
            let line = &rest[..index];
            self.rest = &rest[index + 1..];
            Some(line)
        } else {
            self.rest = "";
            Some(rest)
        }
    }
}

fn main() {
    let mut lines = Lines { rest: "a\nbb\nccc" };
    assert_eq!(lines.next(), Some("a"));
    assert_eq!(lines.next(), Some("bb"));
    assert_eq!(lines.next(), Some("ccc"));
    assert_eq!(lines.next(), None);
}
```

## Edge cases
```rust
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct One<T>(Option<T>);

impl<T> LendingIterator for One<T> {
    type Item<'a> = &'a mut T
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        self.0.as_mut()
    }
}

fn main() {
    let mut one = One(Some(3));
    *one.next().unwrap() += 1;
    assert_eq!(one.0, Some(4));
}
```

## Best practice
- ✅ Use a lending iterator when returned items borrow from the iterator's internal storage.
- ✅ Put `where Self: 'a` on the GAT and repeat it in impls.
- ✅ Name the trait differently from `Iterator` so callers know adapter compatibility is different.
- ✅ Keep lent items short-lived in examples; this teaches the borrowing model.
- ✅ Offer ordinary iterator adapters too when the data can be yielded by value or by independent shared borrow.
- ✅ Consider a callback API with [[Higher-Ranked Trait Bounds]] if callers do not need to keep the lent value.

## Pitfalls
- ⚠️ Trying to implement the standard `Iterator` trait for values that need to lend from `self`.
- ⚠️ Holding a lent item while calling `next` again on a `&mut self` lending iterator.
- ⚠️ Forgetting that many standard iterator combinators will not apply directly.
- ⚠️ Using unsafe lifetime extension instead of modeling the borrow with a GAT.
- ⚠️ Making the GAT bounds more restrictive than the methods require.

## See also
[[Advanced Type System]]
[[Generic Associated Types]]
[[Required Bounds on Generic Associated Types]]
[[Iterators]]
[[The Iterator Trait]]
[[Iterator Adapters]]
[[Lifetimes]]
[[Borrowing]]
[[Higher-Ranked Trait Bounds]]
[[Return Iterators Instead of Collecting]]

## Sources
- The Rust Reference, "Associated types with generics" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/associated-items.html#associated-types
- The Rust Reference, "Required where clauses on generic associated types" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/associated-items.html#required-where-clauses-on-generic-associated-types
