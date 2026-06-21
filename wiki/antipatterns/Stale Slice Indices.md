---
type: antipattern
title: "Stale Slice Indices"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, slices, footgun]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[The Slice Type]]", "[[Borrowing]]", "[[References]]", "[[String Byte Indexing]]", "[[Index Panics vs get]]", "[[Holding Collection Element References Across Mutation]]"]
sources: ["[[the-book]]", "[[ownership-borrowing-lifetimes]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-03-slices.html", "https://doc.rust-lang.org/book/ch08-02-strings.html"]
rust_version: "edition 2024 / 1.85+"
---

# Stale Slice Indices

Stale slice indices happen when code stores numeric positions into a string or collection, then mutates the data so the numbers no longer describe the same valid region. Prefer slices, ranges with clear ownership, or recomputing positions after mutation.

## The mistake
The mistake is treating `usize` indexes as if they were checked references into a particular version of data.
An index by itself has no lifetime and no relationship to the collection it came from.
After mutation, the same number can point to different data, point past the end, or split a UTF-8 code point in a string.

The Book's `first_word` example shows this directly.
Returning `5` for `"hello world"` is fine until the string is cleared or changed.
The number remains `5`, but its meaning has vanished.

## Why it happens
Rust's borrow checker can reason about references and slices because they are tied to borrowed data.
It cannot infer that a plain integer should become invalid when a collection changes.
The integer is just data.

A slice such as `&str` or `&[T]` carries the borrow relationship in its type.
If a string slice is still going to be used, Rust prevents a mutable borrow such as `clear` from running at the same time.
That turns a delayed logic bug into an immediate compile-time error.

Indices are still useful for algorithms, storage formats, and arena-style data structures.
The key is to keep their validity contract explicit and local, or recompute them after mutations.

For `String`, stale indices have an extra UTF-8 hazard.
Even if a byte offset is still within bounds after editing, it may no longer be a character boundary.
Slicing with that index can panic, and using it as a semantic "character position" can quietly point
at the wrong user-visible text.

For `Vec<T>`, the most common logical bugs come from insertion, removal, sorting, deduplication, and
clearing.
These operations can shift elements, invalidate ordering assumptions, or make an index out of
bounds even when no reference was held.

## Example
```rust
fn main() {
    let mut text = String::from("hello world");

    {
        let word = first_word(&text);
        println!("{word}");
    }

    text.clear();
    text.push_str("rust");
    println!("{text}");
}

fn first_word(s: &str) -> &str {
    s.split_once(' ').map_or(s, |(first, _)| first)
}
```

## Bad example
```rust
fn main() {
    let mut names = vec!["ada", "grace", "linus"];
    let grace = 1;

    names.remove(0);

    // The index is still in bounds, but it now points to "linus".
    println!("{}", names[grace]);
}
```

## Safer example
```rust
fn main() {
    let mut names = vec!["ada", "grace", "linus"];
    let target = "grace";

    names.remove(0);

    if let Some(name) = names.iter().find(|name| **name == target) {
        println!("{name}");
    }
}
```

## Common errors
When stale string indexes are reused as slice bounds, runtime failure often looks like:

```text
thread 'main' panicked at ... byte index ... is not a char boundary
```

When vector indexes go stale past the end, indexing panics:

```text
index out of bounds: the len is ... but the index is ...
```

Use `get`, recompute after mutation, or keep a borrowed slice active so the compiler prevents
conflicting mutation while the view is still needed.

## Best practice
- ✅ Return `&str` or `&[T]` when a result is a view into input data.
- ✅ Keep numeric indices local to the operation that computed them.
- ✅ Use `get` and checked range APIs when indexing may fail.
- ✅ Recompute indexes after mutating a collection or make mutation impossible while a view is active.
- ✅ Store stable identifiers instead of positions when elements have identity independent of order.
- ✅ For parser-like code, keep ranges paired with the exact source version they came from.

## Pitfalls
- ⚠️ Do not store a byte index into a `String` and later slice with it after edits. See [[String Byte Indexing]].
- ⚠️ Do not use stale vector indexes after insertion, removal, sort, or clear unless your algorithm updates them deliberately.
- ⚠️ Do not use indexing syntax when absence is expected; prefer `get`. See [[Index Panics vs get]].
- ⚠️ Do not hold element references across collection mutation. See [[Holding Collection Element References Across Mutation]].
- ⚠️ Do not treat a UTF-8 byte offset as a character count; those are different coordinate systems.

## See also
[[The Slice Type]] · [[Borrowing]] · [[References]] · [[String Byte Indexing]] · [[Index Panics vs get]] · [[Holding Collection Element References Across Mutation]] · [[Vec]] · [[Borrowed Parameter APIs]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.3 "The Slice Type" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-03-slices.html
- The Rust Programming Language, ch. 8.2 "Storing UTF-8 Encoded Text with Strings" — [[the-book]],
  https://doc.rust-lang.org/book/ch08-02-strings.html
