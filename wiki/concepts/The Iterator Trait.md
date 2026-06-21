---
type: concept
title: "The Iterator Trait"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, traits, associated-types]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Iterators]]", "[[Iterator Adapters]]", "[[Consuming Adapters]]", "[[Associated Types]]", "[[Traits]]", "[[Option vs Result]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Iterator"]
---

# The Iterator Trait

The `Iterator` trait is the standard contract for lazy sequences: define an `Item` type and a `next` method that returns `Some(item)` until it returns `None`.

## What it is
`Iterator` is a trait from the standard library. Its essential shape is:
`type Item; fn next(&mut self) -> Option<Self::Item>;`.

The associated `Item` type says what the iterator yields. The `next` method mutates the iterator's
internal position and returns `None` when iteration is finished.

## How it works
Implementing `next` unlocks many default methods: `map`, `filter`, `sum`, `collect`, `find`,
`any`, `all`, `fold`, and more. These methods are either [[Iterator Adapters]] that create a new
lazy iterator or [[Consuming Adapters]] that drive the iterator to produce a final result.

Because `next` takes `&mut self`, an explicit iterator variable must be mutable when calling
`next` directly. A `for` loop takes ownership of the iterator and handles that mutable state
behind the scenes.

`Iterator` uses an associated type rather than a generic parameter, so each iterator
implementation has one `Item` type. Many provided methods require `Self: Sized` because they take
or return concrete adapter values; trait-object use such as `&mut dyn Iterator<Item = i32>` is
still possible for object-safe methods like `next`.

## Example
```rust
struct Countdown {
    next: u8,
}

impl Iterator for Countdown {
    type Item = u8;

    fn next(&mut self) -> Option<Self::Item> {
        if self.next == 0 {
            None
        } else {
            let current = self.next;
            self.next -= 1;
            Some(current)
        }
    }
}

fn main() {
    let values: Vec<u8> = Countdown { next: 3 }.collect();
    assert_eq!(values, vec![3, 2, 1]);
}
```

This custom iterator only implements `next`; `collect` comes from the default methods on
`Iterator`.

## Worked example
```rust
struct EveryOther<I> {
    iter: I,
}

impl<I> Iterator for EveryOther<I>
where
    I: Iterator,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<Self::Item> {
        let item = self.iter.next();
        let _ = self.iter.next();
        item
    }
}

fn every_other<I>(iter: I) -> EveryOther<I::IntoIter>
where
    I: IntoIterator,
{
    EveryOther { iter: iter.into_iter() }
}

fn main() {
    let values: Vec<_> = every_other([10, 20, 30, 40, 50]).collect();
    assert_eq!(values, vec![10, 30, 50]);
}
```

The custom adapter stores another iterator and implements only `next`; all higher-level behavior
still comes from the standard `Iterator` default methods.

## Common errors
```rust
fn main() {
    let values = [1, 2, 3];
    let iter = values.iter();
    // let first = iter.next();
}
```

Uncommenting the last line gives `error[E0596]: cannot borrow iter as mutable`. `next` advances
internal state, so the binding must be `let mut iter = values.iter();`.

## Best practice
- ✅ Implement `Iterator` when your type naturally owns traversal state.
- ✅ Make `next` advance reliably and eventually return `None` for finite sequences.
- ✅ Use existing adapters instead of adding custom iterator types unless the state machine is clearer as a type.
- ✅ Consider implementing `size_hint` only when you can state useful bounds correctly; consumers may use it for allocation planning.
- ✅ Prefer `IntoIterator` parameters for APIs that accept either collections or already-built iterators.

## Pitfalls
- ⚠️ Forgetting that direct `next` calls require a mutable iterator binding.
- ⚠️ Returning references from a custom iterator without designing the lifetimes carefully. See [[Lifetimes]].
- ⚠️ Assuming every iterator is finite; consumers like `collect` can run forever on infinite iterators.
- ⚠️ Returning `Some` again after `None` unless the behavior is intentional; use `.fuse()` when callers require permanent exhaustion.
- ⚠️ Exposing a custom iterator type publicly when `impl Iterator<Item = T>` would keep the API simpler.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Lazy Evaluation]] · [[Option vs Result]] · [[Traits]] · [[Associated Types]] · [[Return Iterators Instead of Collecting]] · [[Lifetimes]]

## Sources
- The Rust Programming Language, ch. 13.2 "The Iterator Trait and the next Method" - [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Rust standard library, `Iterator` trait - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html
