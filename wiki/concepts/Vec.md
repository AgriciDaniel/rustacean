---
type: concept
title: "Vec"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, vec, sequence]
domain: "Collections & Strings"
difficulty: basic
related: ["[[Capacity and Reallocation]]", "[[Iterating Collections]]", "[[Index Panics vs get]]", "[[Ownership]]", "[[Borrowing Strings and Slices]]", "[[VecDeque]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-01-vectors.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html", "https://doc.rust-lang.org/reference/expressions/array-expr.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Vectors"]
---

# Vec

`Vec<T>` is Rust's standard growable, heap-allocated, contiguous sequence type for holding zero or more values of one element type.

## What it is
Use `Vec<T>` when you need an owned list whose length can change at runtime.
It stores elements contiguously, so indexing, slicing, iteration, and appending at the back are fast in the common case.

A vector is homogeneous: every element has type `T`.
If a logical list contains a fixed set of different shapes, use an enum as the element type rather than trying to make one vector hold unrelated concrete types.

`Vec<T>` owns its elements.
Dropping the vector drops every element it still contains, and moving the vector moves ownership of the whole list, not a copy of the allocation.

## How it works
The stable mental model is pointer, length, and capacity.
Length is the number of initialized elements.
Capacity is how many elements can fit in the current allocation before growth is required.

`push` appends one element.
`pop` removes from the end and returns `Option<T>`.
Indexing with `v[i]` returns a reference but panics if `i` is out of bounds; `v.get(i)` returns `Option<&T>`.

Many slice methods are available on `Vec<T>` because `Vec<T>` dereferences to `[T]`.
That is why APIs should usually accept `&[T]` when they only need to read a sequence.

Internally, initialized elements occupy the first `len` slots of the allocation.
The spare capacity after `len` is not initialized `T` values and safe Rust never lets you read it as elements.
This is why `capacity()` is useful for allocation planning but never changes what iteration, slicing, or indexing can see.

Moving a `Vec<T>` value copies only the vector handle, not every element.
The heap allocation remains in place and ownership of all elements transfers to the new binding.
Cloning a vector is different: it clones each element and allocates storage for the clone.

## Example
```rust
fn main() {
    let mut scores = Vec::with_capacity(3);
    scores.push(10);
    scores.push(25);
    scores.push(40);

    if let Some(second) = scores.get(1) {
        println!("second score: {second}");
    }

    for score in &mut scores {
        *score += 1;
    }

    assert_eq!(scores.pop(), Some(41));
    assert_eq!(scores, [11, 26]);
}
```

## More realistic example
```rust
fn top_three(mut values: Vec<i32>) -> Vec<i32> {
    values.sort_unstable_by(|a, b| b.cmp(a));
    values.truncate(3);
    values
}

fn normalize_in_place(values: &mut [i32]) {
    if let Some(max) = values.iter().copied().max() {
        if max != 0 {
            for value in values {
                *value = (*value * 100) / max;
            }
        }
    }
}

fn main() {
    let mut readings = vec![4, 10, 2, 8, 6];
    normalize_in_place(&mut readings);
    assert_eq!(readings, [40, 100, 20, 80, 60]);
    assert_eq!(top_three(readings), [100, 80, 60]);
}
```

This example shows the API boundary: `normalize_in_place` only needs a mutable slice,
while `top_three` takes ownership because it is free to reorder and truncate the vector.

## Common errors
```text
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
```

This usually appears when code keeps `let first = &v[0];`, calls `v.push(...)`, and then uses `first`.
Limit the reference to a smaller scope, copy the element if `T: Copy`, or store an index and look up again after mutation.

```text
thread 'main' panicked at 'index out of bounds'
```

Indexing with `v[i]` is for cases where out-of-bounds is a bug.
For data from users, files, network packets, or search results, use `v.get(i)` and handle `None`.

## Best practice
- ✅ Use `Vec::with_capacity(n)` when you have a good estimate for final length; it avoids avoidable reallocations.
- ✅ Accept `&[T]` or `&mut [T]` in functions that do not need ownership or growth.
- ✅ Prefer iterator methods or `for item in &vec` over manual index loops unless the index is part of the domain.
- ✅ Use `get` or `get_mut` when an index may come from outside trusted code paths.
- ✅ Use `Vec<T>` as a stack with `push` and `pop`; those operations match its storage layout.
- ✅ Use `extend` or `collect::<Vec<_>>()` when building from an iterator instead of pushing through a hand-written loop with extra state.
- ✅ Use `retain` for simple in-place filtering instead of hand-mutating indices while removing elements.

## Pitfalls
- ⚠️ `v[i]` panics when `i >= v.len()`; use `get` for fallible access. See [[Index Panics vs get]].
- ⚠️ Holding `&v[0]` and then calling `v.push(...)` is rejected because growth may reallocate and invalidate references. See [[Holding Collection Element References Across Mutation]].
- ⚠️ Removing from the front with `remove(0)` shifts every later element; use [[VecDeque]] for queue behavior.
- ⚠️ Do not rely on any specific growth factor or drop order for vector elements.
- ⚠️ Do not use `Vec<char>` as the default string representation; it changes the unit from UTF-8 bytes to Unicode scalar values and still is not grapheme-aware. See [[String Byte Indexing]].
- ⚠️ Do not confuse `clear()` with freeing memory; it drops elements and sets length to zero but usually keeps capacity for reuse.

## See also
[[Capacity and Reallocation]] · [[Iterating Collections]] · [[Index Panics vs get]] · [[Holding Collection Element References Across Mutation]] · [[VecDeque]] · [[Ownership]] · [[Borrowing Strings and Slices]] · [[Choosing Collection Types]] · [[The Slice Type]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.1 "Storing Lists of Values with Vectors" — [[the-book]], https://doc.rust-lang.org/book/ch08-01-vectors.html
- Standard library `Vec<T>` docs — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html
- The Rust Reference, array and index expressions — [[the-reference]], https://doc.rust-lang.org/reference/expressions/array-expr.html
