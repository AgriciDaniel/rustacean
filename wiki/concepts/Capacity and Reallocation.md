---
type: concept
title: "Capacity and Reallocation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, allocation, capacity]
domain: "Collections & Strings"
difficulty: intermediate
related: ["[[Vec]]", "[[String and str]]", "[[VecDeque]]", "[[Holding Collection Element References Across Mutation]]", "[[Borrowing Strings and Slices]]", "[[Ownership]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-01-vectors.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation", "https://doc.rust-lang.org/std/string/struct.String.html", "https://doc.rust-lang.org/std/collections/struct.VecDeque.html"]
rust_version: "edition 2024 / 1.85+"
---

# Capacity and Reallocation

Capacity is reserved allocation beyond current length; reallocation is the move to a new allocation when a growable collection outgrows its current storage.

## What it is
Growable collections such as `Vec<T>`, `String`, and `VecDeque<T>` track both length and capacity.
Length is how much initialized data is present.
Capacity is how much can fit before another allocation is needed.

Preallocating capacity is a performance tool, not a semantic requirement.
It is most useful when the program already knows a good upper bound or typical final size.

Reallocation matters for performance and for reference validity.
When a vector or string grows beyond capacity, elements or bytes may be moved to a different heap allocation.

## How it works
`Vec::with_capacity(n)` requests room for at least `n` elements.
`String::with_capacity(n)` requests room for at least `n` bytes.
`reserve(additional)` ensures room for at least `len + additional`, possibly reserving more.
`reserve_exact(additional)` requests the minimum, but the allocator may still provide more.

`Vec` guarantees `push` and `insert` will not reallocate when reported capacity is sufficient, and will reallocate when `len == capacity`.
It does not guarantee a specific growth strategy.

Collections generally do not shrink automatically after removals.
Use `shrink_to` or `shrink_to_fit` only when retaining excess memory is a real problem.

For `Vec<T>`, capacity is counted in elements.
For `String`, capacity is counted in UTF-8 bytes.
For `HashMap`, capacity is an implementation-level number of entries the table can hold before growing; it is not an ordering or indexing concept.

Zero capacity does not necessarily mean a null pointer internally, and zero-sized element types are special.
For ordinary safe code, the actionable rule is simple: only elements in `0..len` are initialized and visible.

## Example
```rust
fn main() {
    let mut bytes = Vec::with_capacity(4);
    let starting_capacity = bytes.capacity();

    for b in [1_u8, 2, 3, 4] {
        bytes.push(b);
    }

    assert_eq!(bytes.len(), 4);
    assert!(bytes.capacity() >= 4);
    assert_eq!(bytes.capacity(), starting_capacity);

    let mut text = String::with_capacity("hello".len() + 2);
    text.push_str("hello");
    text.push('!');
    assert!(text.capacity() >= text.len());
}
```

## More realistic example
```rust
fn csv_line(fields: &[&str]) -> String {
    let byte_estimate = fields.iter().map(|field| field.len()).sum::<usize>() + fields.len().saturating_sub(1);
    let mut out = String::with_capacity(byte_estimate);

    for (index, field) in fields.iter().enumerate() {
        if index > 0 {
            out.push(',');
        }
        out.push_str(field);
    }

    out
}

fn main() {
    let line = csv_line(&["id", "name", "city"]);
    assert_eq!(line, "id,name,city");

    let mut reusable = Vec::with_capacity(128);
    reusable.extend([1, 2, 3]);
    reusable.clear();
    assert!(reusable.capacity() >= 128);
}
```

The string estimate is in bytes, and `clear` demonstrates reuse: length changes, capacity usually remains.

## Common errors
```text
error[E0502]: cannot borrow `items` as mutable because it is also borrowed as immutable
```

This often means a reference into a collection is live across an operation that might reallocate.
Use a smaller scope, copy or clone the specific value, reserve before building, or look up again after mutation.

```text
memory allocation failed
```

Most allocation APIs panic or abort on allocation failure depending on context.
Use `try_reserve` when an allocation failure should be represented as a recoverable error.

## Best practice
- ✅ Use `with_capacity` when building a collection from known-size input.
- ✅ Reserve bytes for `String`, not characters; UTF-8 characters may require more than one byte.
- ✅ Let collections keep capacity when they will be reused soon.
- ✅ Use `try_reserve` in fallible or memory-sensitive code paths where allocation failure should be handled.
- ✅ Scope element references tightly before operations that can grow or reorganize a collection.
- ✅ Use `reserve` for amortized growth and `reserve_exact` only when minimizing requested excess allocation matters.
- ✅ Measure before adding capacity tuning to code that is not on a hot path.

## Pitfalls
- ⚠️ Do not assume a particular doubling or growth factor for `Vec` or `String`.
- ⚠️ Do not hold references into a collection across a possible reallocation. See [[Holding Collection Element References Across Mutation]].
- ⚠️ Do not call `shrink_to_fit` in hot loops; freeing and reallocating can be slower than reuse.
- ⚠️ Do not confuse `len()` with `capacity()`; reading beyond `len()` is never reading valid initialized elements.
- ⚠️ Do not reserve string capacity by character count unless all text is known ASCII; reserve by byte count or an upper bound.
- ⚠️ Do not assume `reserve_exact` means the allocator returned exactly that many bytes or elements of backing storage.

## See also
[[Vec]] · [[String and str]] · [[VecDeque]] · [[HashMap]] · [[Holding Collection Element References Across Mutation]] · [[Ownership]] · [[Borrowing Strings and Slices]] · [[Choosing Collection Types]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.1 vector reallocation discussion — [[the-book]], https://doc.rust-lang.org/book/ch08-01-vectors.html
- Standard library `Vec<T>` capacity and reallocation docs — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation
- Standard library `String` docs — [[std]], https://doc.rust-lang.org/std/string/struct.String.html
- Standard library `VecDeque` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.VecDeque.html
