---
type: antipattern
title: "Index Panics vs get"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, indexing, option, panic, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: basic
related: ["[[Slices]]", "[[Vec]]", "[[Option vs Result]]", "[[panic!]]", "[[Integer Overflow Assumptions]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.slice.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html", "https://doc.rust-lang.org/std/ops/trait.Index.html", "https://doc.rust-lang.org/std/option/enum.Option.html"]
rust_version: "edition 2024 / 1.85+"
---

# Index Panics vs get

Index panics happen when code uses `collection[i]` for input-dependent positions; use `.get(i)` when absence is a normal possibility.

## The mistake
Index syntax is concise and useful when an index is already known to be valid. It panics when the index is out of bounds. That is appropriate for programmer mistakes, but poor error handling for user input, parsed data, protocol fields, and optional columns.

The footgun is letting indexing become hidden `unwrap`: a runtime assumption with no local explanation and no recovery path.

## Why it happens
Slices and vectors implement `Index`, so `items[i]` looks like ordinary access. Rust makes out-of-bounds access memory-safe by panicking instead of reading invalid memory.

When an index comes from outside the program's invariant, the type should show uncertainty. `.get(i)` returns `Option<&T>`, and `.get_mut(i)` returns `Option<&mut T>`.

Index syntax calls the `Index` or `IndexMut` trait and assumes success. For slices, ranges are checked too: a bad start, end, or ordering panics. The non-panicking APIs return `Option` for both single indices and ranges, so the failure path can stay in normal control flow.

The same rule applies to strings, with an extra constraint: string ranges must land on UTF-8 character boundaries. `s.get(range)` returns `None` when the range is out of bounds or not on boundaries; `s[range]` panics.

## Example
```rust
fn label_at(labels: &[&str], index: usize) -> Option<String> {
    labels.get(index).map(|label| format!("selected: {label}"))
}

fn main() {
    let labels = ["red", "green", "blue"];

    match label_at(&labels, 1) {
        Some(label) => println!("{label}"),
        None => println!("no such label"),
    }

    match label_at(&labels, 9) {
        Some(label) => println!("{label}"),
        None => println!("no such label"),
    }
}
```

## Second example: range access and UTF-8 boundaries
```rust
fn prefix(input: &str, bytes: usize) -> Option<&str> {
    input.get(..bytes)
}

fn middle<T>(items: &[T]) -> Option<&T> {
    items.get(items.len() / 2)
}

fn main() {
    let word = "rust";
    println!("{:?}", prefix(word, 2));
    println!("{:?}", prefix("éclair", 1)); // not a char boundary

    let values = [10, 20, 30];
    println!("{:?}", middle(&values));
}
```

For text, byte indexing is rarely what users mean. Prefer iterator methods such as `.chars()` or domain-specific parsing when human characters matter.

## Common errors
Runtime panic:

```text
thread 'main' panicked at 'index out of bounds: the len is 3 but the index is 9'
```

Fix it by using `.get(index)` when the index is input-dependent, or by proving the index locally with an iterator or range that is derived from the collection length.

String boundary panic:

```text
thread 'main' panicked at 'byte index 1 is not a char boundary'
```

Fix it with `.get(range)` if byte ranges are expected to fail, or use `.chars()`, `.char_indices()`, or a Unicode-aware crate for user-visible text processing.

## Best practice
- ✅ Use `[]` when the index is guaranteed by a nearby invariant, such as a loop over `0..slice.len()`.
- ✅ Use `.get()` and pattern matching for input-dependent indices.
- ✅ Prefer iterator adapters like `iter`, `enumerate`, `windows`, and `chunks` over manual indexing loops.
- ✅ Convert `Option` to `Result` with a domain error when callers need to know why lookup failed.
- ✅ Use `.first()`, `.last()`, and `.split_first()` for common boundary-safe access patterns.
- ✅ Use `.get(range)` for slices and strings when both arithmetic and bounds can fail.

## Pitfalls
- ⚠️ `.get(i).unwrap()` is just indexing with extra steps unless the invariant is documented and local.
- ⚠️ Off-by-one errors often appear in hand-written index loops; iterators encode bounds more directly.
- ⚠️ Integer overflow in index math can become a later panic; see [[Integer Overflow Assumptions]].
- ⚠️ Using `i32` for indices invites casts; Rust collection indices are `usize`.
- ⚠️ `for i in 0..=slice.len()` has an off-by-one panic; prefer iterators or `0..slice.len()`.
- ⚠️ String slicing is byte-based, not character-based.

## See also
[[Slices]] · [[Vec]] · [[Option vs Result]] · [[panic!]] · [[Integer Overflow Assumptions]] · [[Is Some Then Unwrap]] · [[Unwrap and Expect Overuse]] · [[Unnecessary Collect]] · [[Sentinel Values]] · [[Anti-patterns & Footguns]]

## Sources
- Standard library, slices and `get` — [[the-reference]], https://doc.rust-lang.org/std/primitive.slice.html
- Standard library, `Vec` — [[the-reference]], https://doc.rust-lang.org/std/vec/struct.Vec.html
- Standard library, `Index` — [[the-reference]], https://doc.rust-lang.org/std/ops/trait.Index.html
- Standard library, `Option` — [[the-reference]], https://doc.rust-lang.org/std/option/enum.Option.html
