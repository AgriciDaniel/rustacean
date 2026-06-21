---
type: antipattern
title: "Unnecessary Collect"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, collect, allocation, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Iterators]]", "[[Vec]]", "[[Borrowing]]", "[[Needless Clone]]", "[[Index Panics vs get]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html"]
rust_version: "edition 2024 / 1.85+"
---

# Unnecessary Collect

Unnecessary collect is materializing an iterator into a collection when the next operation could consume the iterator directly.

## The mistake
`collect()` is the right tool when you need an owned collection, need to cross an API boundary requiring one, or need to reuse the results multiple times. It is wasteful when used only as a stepping stone to `len`, `any`, `sum`, `find`, `for`, or another iterator pass.

The footgun is turning lazy, streaming transformations into allocation-heavy code by habit.

## Why it happens
Many APIs in other languages return arrays at every step. Rust iterators are lazy: adapters such as `map`, `filter`, and `take` describe work, and consumers such as `sum`, `collect`, `find`, and `for_each` drive it.

Collecting too early can allocate memory, copy or move values into a `Vec`, and make lifetime problems worse. Keeping the iterator chain alive often removes both the allocation and the temptation to clone.

An iterator chain is usually a small state machine. Adapters store the previous iterator and a closure; they do not process elements until a consumer asks for `next()`. `collect()` switches from streaming to materialized storage by repeatedly extending a collection from those items.

That switch is sometimes exactly right: sorting, deduplication, random access, reuse, and API boundaries may require a `Vec` or map. The antipattern is collecting only because the next step could have been another iterator consumer.

## Example
```rust
fn count_long_words(text: &str) -> usize {
    text.split_whitespace()
        .filter(|word| word.len() > 4)
        .count()
}

fn first_long_word(text: &str) -> Option<&str> {
    text.split_whitespace().find(|word| word.len() > 4)
}

fn main() {
    let text = "small precise Rust examples";

    println!("{}", count_long_words(text));
    println!("{:?}", first_long_word(text));

    // Mistake:
    // let words: Vec<_> = text.split_whitespace().filter(|w| w.len() > 4).collect();
    // println!("{}", words.len());
}
```

## Second example: use `try_fold` instead of collect-then-validate
```rust
#[derive(Debug, PartialEq, Eq)]
enum ParseTotalError {
    BadNumber,
    Overflow,
}

fn total(input: &str) -> Result<u32, ParseTotalError> {
    input.split(',')
        .map(str::trim)
        .filter(|part| !part.is_empty())
        .try_fold(0_u32, |sum, part| {
            let value = part.parse::<u32>().map_err(|_| ParseTotalError::BadNumber)?;
            sum.checked_add(value).ok_or(ParseTotalError::Overflow)
        })
}

fn main() {
    println!("{:?}", total("1, 2, 3"));
    println!("{:?}", total("1, nope, 3"));
}
```

This avoids allocating `Vec<&str>` or `Vec<u32>` just to immediately reduce it to one number. It also stops at the first parse or overflow error.

## Common errors
Type inference around `collect`:

```text
error[E0283]: type annotations needed
```

Fix it by either avoiding `collect` when a direct consumer works, or specifying the target collection with `collect::<Vec<_>>()`, `collect::<Result<Vec<_>, _>>()`, or an annotated binding.

Borrow checker pressure after collecting references:

```text
error[E0502]: cannot borrow `items` as mutable because it is also borrowed as immutable
```

If the collected vector only stores references into `items`, those borrows remain live. Consume the iterator directly, narrow the scope of the collected references, or collect owned values only when the ownership cost is intentional.

## Best practice
- ✅ Let iterator consumers such as `count`, `any`, `all`, `find`, `sum`, and `try_fold` finish the chain directly.
- ✅ Collect when ownership, random access, sorting, reuse, or an API boundary requires a collection.
- ✅ Prefer slices (`&[T]`) in function parameters so callers are not forced to allocate a `Vec<T>`.
- ✅ Use `collect::<Result<Vec<_>, _>>()` when collecting is also the error-propagating operation you need.
- ✅ Use `try_fold` or `try_for_each` for fallible single-pass processing.
- ✅ Collect once when you need to sort, deduplicate, index repeatedly, or pass data to an API that genuinely requires ownership.

## Pitfalls
- ⚠️ Collecting before indexing can introduce both an allocation and an index panic; see [[Index Panics vs get]].
- ⚠️ Collecting borrowed data into owned `String`s often pairs with [[Needless Clone]].
- ⚠️ A collected intermediate can hide an easy single-pass algorithm.
- ⚠️ Do not contort clear code to avoid every allocation; collect when the collection is the actual result.
- ⚠️ Collecting an infinite iterator never terminates; use `take`, `find`, or another bounded consumer.
- ⚠️ Collecting references can keep borrows alive longer than the reader expects.

## See also
[[Iterators]] · [[Vec]] · [[Borrowing]] · [[Needless Clone]] · [[Index Panics vs get]] · [[Result]] · [[Option vs Result]] · [[Integer Overflow Assumptions]] · [[Stringly-Typed Code]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" — [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Standard library, `Iterator` and `collect` — [[the-reference]], https://doc.rust-lang.org/std/iter/trait.Iterator.html
- Standard library, `Vec` — [[the-reference]], https://doc.rust-lang.org/std/vec/struct.Vec.html
