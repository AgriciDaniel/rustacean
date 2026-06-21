---
type: concept
title: "String vs str Methods"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, string, str, utf8, methods]
domain: "std: Vec, String & Slices"
difficulty: basic
related: ["[[String and str]]", "[[Borrowing Strings and Slices]]", "[[Building Strings Efficiently]]", "[[Bytes Chars and Unicode]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/string/struct.String.html", "https://doc.rust-lang.org/std/primitive.str.html"]
rust_version: "edition 2024 / 1.85+"
---

# String vs str Methods

`String` is the owned, growable UTF-8 buffer; `str` is the borrowed UTF-8 text slice, and `String` gets most `str` methods through deref coercion.

## What it is
`String` owns heap allocation and can change length.
`str` is dynamically sized and is usually seen as `&str`.
Both represent valid UTF-8.
Methods that allocate, reserve, push, insert, remove, or clear belong to `String`.
Methods that inspect, search, trim, split, parse, or iterate text generally belong to `str`.
Because `String` dereferences to `str`, you can call `text.trim()` or `text.split(',')` on a `String`.
Because `&String` coerces to `&str`, APIs should usually accept `&str` for read-only text.
Because `String` is a byte buffer with a UTF-8 invariant, length is measured in bytes.

## How it works
`String::new` and `String::with_capacity` construct owned buffers.
`push_str` appends a string slice.
`push` appends one `char`.
`reserve`, `try_reserve`, `capacity`, `shrink_to`, and `shrink_to_fit` mirror vector capacity operations in bytes.
`as_str` borrows text as `&str`.
`as_bytes` borrows the UTF-8 bytes.
`into_bytes` consumes the string and returns `Vec<u8>`.
`String::from_utf8` validates bytes and returns `Result<String, FromUtf8Error>`.
`str::from_utf8` validates a byte slice and returns `Result<&str, Utf8Error>`.
`split`, `split_once`, `lines`, `contains`, `find`, `trim`, `parse`, `chars`, and `char_indices` are `str` methods.
Use `String` when ownership or mutation is required; use `&str` when reading.

## Example
```rust
fn shout(input: &str) -> String {
    let mut out = String::with_capacity(input.len() + 1);
    out.push_str(input.trim());
    out.push('!');
    out.make_ascii_uppercase();
    out
}

fn main() {
    let owned = String::from(" hello ");
    let result = shout(&owned);

    assert_eq!(result, "HELLO!");
    assert_eq!(owned.trim(), "hello");
    assert_eq!(String::from_utf8(vec![82, 117, 115, 116]).unwrap(), "Rust");
}
```

## Best practice
- ✅ Accept `&str` when a function only reads text.
- ✅ Return `String` when a function builds or transforms owned text.
- ✅ Use `String::with_capacity` for predictable builders.
- ✅ Use `push_str` for string slices and `push` for one Unicode scalar value.
- ✅ Use `str` methods directly on `String` through deref coercion.
- ✅ Use `from_utf8` instead of unchecked conversion unless an invariant is already proven.
- ✅ Treat `len()` as bytes and use `chars().count()` only when scalar count is truly needed.
- ✅ Use `char_indices` when you need safe byte offsets into a string.

## Pitfalls
- ⚠️ Accepting `String` by value forces callers to give up ownership; see [[Borrowing Strings and Slices]].
- ⚠️ `String::len` is not a user-visible character count.
- ⚠️ `remove`, `insert`, `truncate`, `split_off`, and `drain` require character-boundary byte indexes.
- ⚠️ `make_ascii_uppercase` only changes ASCII bytes, not full Unicode case mapping.
- ⚠️ `chars` iterates Unicode scalar values, not grapheme clusters.
- ⚠️ `as_bytes_mut` and unchecked UTF-8 constructors are unsafe because they can break the UTF-8 invariant.
- ⚠️ Repeated `+` concatenation in loops can allocate excessively; see [[Building Strings Efficiently]].
- ⚠️ Pattern-based search returns byte indexes, so treat them as byte offsets.

## See also
[[std: Vec, String & Slices]] · [[String and str]] · [[Borrowing Strings and Slices]] · [[Building Strings Efficiently]] · [[Splitting Strings Without Collecting]] · [[Bytes Chars and Unicode]] · [[String Byte Indexing]] · [[Assuming String Indexes Are Characters]] · [[Vec Capacity and Growth]]

## Sources
- Rust standard library, `std::string::String` — [[std]], https://doc.rust-lang.org/std/string/struct.String.html
- Rust standard library, primitive `str` — [[std]], https://doc.rust-lang.org/std/primitive.str.html
