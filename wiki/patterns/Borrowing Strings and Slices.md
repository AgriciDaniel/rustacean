---
type: pattern
title: "Borrowing Strings and Slices"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, borrowing, strings, slices]
domain: "Collections & Strings"
difficulty: basic
related: ["[[String and str]]", "[[Vec]]", "[[Ownership]]", "[[Borrowing]]", "[[Dynamically Sized Types]]", "[[Needless Clone]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-03-slices.html", "https://doc.rust-lang.org/book/ch08-02-strings.html", "https://doc.rust-lang.org/std/primitive.str.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html#slicing"]
rust_version: "edition 2024 / 1.85+"
---

# Borrowing Strings and Slices

Accept `&str` and `&[T]` for read-only inputs so callers can pass owned values, literals, arrays, vectors, or subslices without transferring ownership.

## What it is
This pattern is the collection version of "borrow when you do not need ownership."
An API that reads text should usually take `&str`, not `String`.
An API that reads a sequence should usually take `&[T]`, not `Vec<T>`.

The result is more flexible and often cheaper.
Callers keep ownership, and the function does not force allocation or cloning.

Use owned `String` or `Vec<T>` parameters only when the function must store, mutate capacity, consume, or return the owned allocation.

## How it works
`String` dereferences to `str`, so `&String` can coerce to `&str`.
`Vec<T>` dereferences to `[T]`, so `&Vec<T>` can coerce to `&[T]`.
Arrays can also be borrowed as slices.

The callee receives a borrowed view with a lifetime no longer than the caller's data.
That view can be indexed, iterated, searched, and sliced, but it cannot grow the original collection.

For mutable element access without changing length or capacity, accept `&mut [T]`.
For appending or removing elements, accept `&mut Vec<T>` or own the vector.

This pattern also improves type inference at call sites.
A `&str` parameter accepts string literals, `String`, `Cow<'_, str>` after deref, and substrings.
A `&[T]` parameter accepts arrays, vectors, boxed slices, and ranges of existing slices.
The function commits to a view of data, not to the caller's storage strategy.

## Example
```rust
fn contains_word(haystack: &str, needle: &str) -> bool {
    haystack.split_whitespace().any(|word| word == needle)
}

fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}

fn main() {
    let owned = String::from("rust makes ownership visible");
    assert!(contains_word(&owned, "ownership"));
    assert!(contains_word("borrow string literals too", "borrow"));

    let vec = vec![1, 2, 3];
    let array = [4, 5, 6];
    assert_eq!(sum(&vec), 6);
    assert_eq!(sum(&array), 15);
}
```

## More realistic example
```rust
fn parse_header(line: &str) -> Option<(&str, &str)> {
    let (name, value) = line.split_once(':')?;
    Some((name.trim(), value.trim()))
}

fn middle_value(values: &[i32]) -> Option<i32> {
    let middle = values.len() / 2;
    values.get(middle).copied()
}

fn zero_negatives(values: &mut [i32]) {
    for value in values {
        if *value < 0 {
            *value = 0;
        }
    }
}

fn main() {
    assert_eq!(parse_header("Content-Type: text/plain"), Some(("Content-Type", "text/plain")));

    let mut readings = vec![3, -1, 8, -5, 13];
    zero_negatives(&mut readings);
    assert_eq!(readings, [3, 0, 8, 0, 13]);
    assert_eq!(middle_value(&readings), Some(8));
}
```

The parser returns slices borrowed from the input line, so it does not allocate.
The numeric functions show the split between read-only slices and mutable slices that preserve length.

## Common errors
```text
error[E0515]: cannot return value referencing local variable
```

This happens when a function builds a local `String` or `Vec` and returns `&str` or `&[T]` into it.
Return the owned `String` or `Vec<T>` instead, or borrow from an input parameter whose lifetime can outlive the return value.

```text
error[E0308]: mismatched types
```

Public APIs that take `&String` or `&Vec<T>` often force callers into unnecessary conversions.
Change the parameter to `&str` or `&[T]` when the function only reads the data.

## Best practice
- ✅ Prefer `fn f(s: &str)` over `fn f(s: &String)` for text readers.
- ✅ Prefer `fn f(xs: &[T])` over `fn f(xs: &Vec<T>)` for sequence readers.
- ✅ Use `&mut [T]` for in-place element changes that do not alter length.
- ✅ Return owned `String` or `Vec<T>` when the result is newly constructed data.
- ✅ Let callers decide whether to allocate; do not force `.to_string()` or `.to_vec()` at API boundaries.
- ✅ Use `AsRef<str>` or `AsRef<[T]>` only when a generic API truly benefits; plain borrowed parameters are simpler for most functions.
- ✅ Keep returned slices tied to input slices, not to temporary buffers created inside the function.

## Pitfalls
- ⚠️ Do not clone a collection just to pass it into a reader. See [[Needless Clone]].
- ⚠️ Do not return a slice into a local `String` or `Vec`; the owner will be dropped at function exit.
- ⚠️ Do not accept `&String` as a public API habit; it needlessly excludes string literals and other `&str` sources.
- ⚠️ Do not accept `&Vec<T>` when slice methods are enough; it leaks the caller's storage choice into the signature.
- ⚠️ Do not use `&mut Vec<T>` for element-only mutation; it advertises that the function may change length or capacity.
- ⚠️ Do not store borrowed slices in long-lived structs unless the lifetime relationship is intentional and documented.

## See also
[[String and str]] · [[Vec]] · [[The Slice Type]] · [[Ownership]] · [[Borrowing]] · [[Dynamically Sized Types]] · [[Needless Clone]] · [[The Entry API]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 4.3 "The Slice Type" — [[the-book]], https://doc.rust-lang.org/book/ch04-03-slices.html
- The Rust Programming Language, ch. 8.2 strings — [[the-book]], https://doc.rust-lang.org/book/ch08-02-strings.html
- Standard library `str` docs — [[std]], https://doc.rust-lang.org/std/primitive.str.html
- Standard library `Vec<T>` slicing docs — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#slicing
