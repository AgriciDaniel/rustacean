---
type: concept
title: "The Slice Type"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, slices, borrowing]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Borrowing]]", "[[References]]", "[[String and str]]", "[[Vec]]", "[[Stale Slice Indices]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-03-slices.html", "https://doc.rust-lang.org/reference/types/slice.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Slices", "String Slices"]
---

# The Slice Type

A slice is a non-owning view of a contiguous sequence, written most often as `&str` or `&[T]`. It ties a range to the borrowed data so the compiler can keep the view valid.

## What it is
Slices let you refer to part or all of a collection without copying it and without taking [[Ownership]].
`&str` is a string slice.
`&[T]` is a slice of elements of type `T`.

A slice contains a pointer to the first element and length metadata.
For `str`, the range must be on valid UTF-8 boundaries.
For `[T]`, the range is counted in elements.

Slices are usually the right abstraction for read-only sequence parameters.
They let callers pass arrays, vectors, string literals, `String` values, and already-sliced values through one API shape.

## How it works
The range syntax `&value[start..end]` borrows a contiguous region.
`start` is inclusive and `end` is exclusive.
Omitting either side means the beginning or end of the collection.

Returning a slice is safer than returning a plain index when the returned value describes a part of the input.
The borrow checker knows that the slice depends on the original data.
If code tries to mutate the original `String` while the slice will still be used, Rust rejects the program.

For string data, prefer taking `&str` in parameters.
For generic element sequences, prefer `&[T]`.
Use owned `String` or `Vec<T>` only when the function needs ownership, allocation, capacity management, or mutation of the container itself.

Slices are dynamically sized types, so they are almost always used behind a pointer such as `&[T]`,
`&mut [T]`, `Box<[T]>`, or `Rc<[T]>`.
The pointer part identifies the first element, and the metadata records the element count.
For `&str`, the metadata is a byte length, and Rust requires the bytes to remain valid UTF-8.

Mutable slices, `&mut [T]`, let an API mutate elements without changing the allocation or capacity of
the original collection.
That distinction is useful: sorting a `&mut [T]` is fine, but pushing a new element requires a
`Vec<T>` because only the vector owner manages capacity.

## Example
```rust
fn main() {
    let text = String::from("hello world");
    let first = first_word(&text);

    println!("{first}");
}

fn first_word(s: &str) -> &str {
    match s.find(' ') {
        Some(index) => &s[..index],
        None => s,
    }
}
```

## Worked example
```rust
fn main() {
    let mut scores = vec![30, 10, 20];
    normalize(&mut scores);
    println!("{scores:?}");

    let top_two = prefix(&scores, 2);
    println!("{top_two:?}");
}

fn normalize(values: &mut [i32]) {
    values.sort_unstable();
    for value in values {
        *value *= 10;
    }
}

fn prefix<T>(values: &[T], len: usize) -> &[T] {
    let end = len.min(values.len());
    &values[..end]
}
```

## Common errors
String slices must use UTF-8 boundary byte offsets:

```text
thread 'main' panicked at ... byte index ... is not a char boundary
```

Prefer character-aware methods, pattern searches, or checked slicing:

```rust
fn first_char(s: &str) -> Option<&str> {
    let ch = s.chars().next()?;
    Some(&s[..ch.len_utf8()])
}
```

## Best practice
- ✅ Accept `&str` for text input and `&[T]` for sequence input when ownership is unnecessary.
- ✅ Return slices when the result is a view into input data.
- ✅ Use safe methods such as `find`, `split`, `get`, and iterator adapters before manual byte indexing.
- ✅ Remember that string slicing uses byte offsets, and those offsets must be UTF-8 boundaries.
- ✅ Use `&mut [T]` for in-place element algorithms that do not need to grow or shrink a `Vec<T>`.
- ✅ Use `get(range)` when a range may be invalid and absence should be handled instead of panicking.

## Pitfalls
- ⚠️ Do not return standalone indices as long-lived handles into changing text or vectors. See [[Stale Slice Indices]].
- ⚠️ Do not byte-index strings as if every character were one byte. See [[String Byte Indexing]].
- ⚠️ Do not accept `&String` or `&Vec<T>` when `&str` or `&[T]` is enough. See [[Borrowed Parameter APIs]].
- ⚠️ Do not mutate a collection while a slice into it must still be used; the borrow checker is preventing a real invalidation bug.
- ⚠️ Do not confuse a slice's length with a container's capacity; slices have no capacity and cannot
  push or reserve.

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[Mutable References]] · [[String and str]] · [[Vec]] · [[Borrowed Parameter APIs]] · [[Stale Slice Indices]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.3 "The Slice Type" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-03-slices.html
- The Rust Reference, "Slice types" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/slice.html
