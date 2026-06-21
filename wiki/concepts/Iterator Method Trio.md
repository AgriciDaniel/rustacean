---
type: concept
title: "Iterator Method Trio"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, map, filter, collect]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[While and For Loops]]", "[[Type Inference]]", "[[Readable Generic APIs]]", "[[Ownership]]", "[[Arrays]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-02-iterators.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator Method Trio

`map`, `filter`, and `collect` (often with `fold`) form the core composable iterator workflow.

## What it is
The iterator method trio is the common Rust workflow of transforming a sequence with `map`, narrowing
it with `filter`, and materializing or summarizing it with `collect`, `sum`, `count`, `fold`, or
another consuming method.

Iterators are lazy. Adapter methods describe work; consuming methods perform it by repeatedly calling
`next`.

This trio is not a replacement for every loop. It is a compact way to express linear data processing
when each step has a clear sequence meaning.

## How it works
Every iterator has an `Item` type and a `next(&mut self) -> Option<Self::Item>` method. Adapter methods
such as `map` and `filter` return new iterator values that wrap earlier iterators.

`map` transforms each item. `filter` receives a reference to each item for the predicate and keeps only
items whose predicate returns `true`. `collect` consumes the iterator and builds a collection chosen
by type context.

Ownership depends on how the iterator is created: `.iter()` yields references, `.iter_mut()` yields
mutable references, and `.into_iter()` yields owned items when the source can be consumed.

## Example
```rust
fn main() {
    let raw = ["  ferris ", "", " rust "];

    let names: Vec<String> = raw
        .iter()
        .map(|name| name.trim())
        .filter(|name| !name.is_empty())
        .map(str::to_owned)
        .collect();

    assert_eq!(names, vec!["ferris", "rust"]);
}
```

## Edge cases
Use `filter_map` when filtering and mapping are naturally one operation:

```rust
fn main() {
    let values = ["10", "nope", "30"];

    let parsed: Vec<u32> = values
        .into_iter()
        .filter_map(|value| value.parse::<u32>().ok())
        .collect();

    assert_eq!(parsed, vec![10, 30]);
}
```

For fallible pipelines where an error should stop the whole operation, collect into `Result<Vec<_>, _>`
instead of dropping errors.

## Common errors
Calling an adapter without consuming it triggers an `unused_must_use` warning:

```rust
fn main() {
    let values = vec![1, 2, 3];
    // values.iter().map(|value| value + 1);
}
```

Typical diagnostic:

```text
warning: unused `Map` that must be used
note: iterators are lazy and do nothing unless consumed
```

Fix it by consuming the iterator:

```rust
fn main() {
    let values = vec![1, 2, 3];
    let incremented: Vec<_> = values.iter().map(|value| value + 1).collect();
    assert_eq!(incremented, vec![2, 3, 4]);
}
```

## Best practice
- ✅ End adapter chains with an intentional consumer: `collect`, `sum`, `count`, `any`, `all`, `find`, or `for_each`.
- ✅ Use `filter_map` for "parse if valid" and `flat_map` for one-to-many expansion.
- ✅ Let `for` loops handle complex branching, mutation, or early exits that would make a chain opaque.
- ✅ Add a collection type annotation near `collect` when [[Type Inference]] cannot choose one.
- ✅ Choose `.iter()`, `.iter_mut()`, or `.into_iter()` based on ownership, not habit.

## Pitfalls
- ⚠️ Long chains with dense closures can be harder to debug than a named loop.
- ⚠️ `filter` predicate arguments are references to items; destructuring may require `|&&x|` or `.copied()`.
- ⚠️ Collecting too early can allocate unnecessarily; keep data lazy until a real boundary.
- ⚠️ Ignoring `Result` inside `filter_map` may silently discard important errors.
- ⚠️ `for_each` is not automatically clearer than `for`; prefer the loop for side effects.

## See also
[[While and For Loops]] · [[Type Inference]] · [[Readable Generic APIs]] · [[Ownership]] · [[Borrowing]] · [[Arrays]] · [[Vectors]] · [[Result]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 13.2 "Processing a Series of Items with Iterators" — [[the-book]], https://doc.rust-lang.org/book/ch13-02-iterators.html
- Standard library, `Iterator` — https://doc.rust-lang.org/std/iter/trait.Iterator.html
