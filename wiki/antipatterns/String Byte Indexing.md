---
type: antipattern
title: "String Byte Indexing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, strings, utf8, footgun]
domain: "Collections & Strings"
difficulty: basic
related: ["[[String and str]]", "[[Iterating Collections]]", "[[Index Panics vs get]]", "[[Borrowing Strings and Slices]]", "[[Dynamically Sized Types]]", "[[Unnecessary Collect]]"]
sources: ["[[the-book]]", "[[std]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-02-strings.html#indexing-into-strings", "https://doc.rust-lang.org/book/ch08-02-strings.html#slicing-strings", "https://doc.rust-lang.org/std/primitive.str.html", "https://doc.rust-lang.org/reference/tokens.html#string-literals"]
rust_version: "edition 2024 / 1.85+"
---

# String Byte Indexing

String byte indexing is the mistake of treating UTF-8 byte offsets as characters or user-visible letters; Rust prevents `s[0]` and makes range slicing panic on invalid boundaries.

## The mistake
The tempting model is "a string is an array of characters, so index 0 is the first character."
That model is false for UTF-8.
Many characters use multiple bytes, and many user-visible letters are made from multiple Unicode scalar values.

Rust rejects integer indexing into `String` and `str` because there is no single correct return type.
Should it return a byte, a `char`, a grapheme cluster, or a slice?
Each answer is right for some domains and wrong for others.

## Why it happens
In Rust, `String::len()` and `str::len()` return bytes.
The string `"Зд"` contains two `char` values but four bytes.
The string `"नमस्ते"` contains more scalar values than user-visible letters.

Range slicing such as `&s[0..4]` is allowed because the programmer explicitly asks for byte offsets, but it panics if a boundary lands inside a UTF-8 code point.
Integer indexing is not allowed because returning the byte at that offset would surprise most text code, and returning the nth character would not be constant time.

Choose the unit first: bytes for protocols and encodings, `char` for Unicode scalar values, or grapheme clusters through a Unicode segmentation crate for user-facing text editing.

The compiler can reject `s[0]`, but it cannot know whether an arbitrary `usize` range came from valid text boundaries.
That is why byte-range string slicing remains a runtime-checked operation.
Use `is_char_boundary`, `char_indices`, or `get` when boundary validity is uncertain.

## Example
```rust
fn main() {
    let text = "Зд";

    let bytes: Vec<u8> = text.bytes().collect();
    assert_eq!(bytes, [208, 151, 208, 180]);

    let chars: Vec<char> = text.chars().collect();
    assert_eq!(chars, ['З', 'д']);

    let first_two_bytes = &text[0..2];
    assert_eq!(first_two_bytes, "З");
}
```

## Edge cases
```rust
fn safe_prefix(s: &str, max_bytes: usize) -> &str {
    if max_bytes >= s.len() {
        return s;
    }

    let end = s
        .char_indices()
        .map(|(index, _)| index)
        .take_while(|index| *index <= max_bytes)
        .last()
        .unwrap_or(0);
    &s[..end]
}

fn main() {
    assert_eq!("é".len(), 2);
    assert_eq!("e\u{301}".chars().count(), 2);
    assert_eq!(safe_prefix("Здравствуйте", 5), "Зд");
    assert_eq!("Здравствуйте".get(0..1), None);
}
```

The composed-looking strings `"é"` and `"e\u{301}"` are different scalar-value sequences.
For cursor movement and visual text editing, scalar values are still not enough; use grapheme segmentation.

## Common errors
```text
error[E0277]: the type `str` cannot be indexed by `{integer}`
```

Replace integer indexing with the unit-specific operation: `.bytes().nth(i)`, `.chars().nth(i)`, `char_indices`, or a parser that works on validated byte positions.

```text
thread 'main' panicked at 'byte index ... is not a char boundary'
```

Use `s.get(range)` to receive `None` for invalid boundaries, or derive ranges from `char_indices` so boundaries are valid by construction.

## Best practice
- ✅ Use `.chars()` when you need Unicode scalar values.
- ✅ Use `.bytes()` when the domain is bytes, such as wire formats or ASCII-only parsing with validation.
- ✅ Use `str::get(range)` if a byte range may be invalid; it returns `Option<&str>`.
- ✅ Use a Unicode segmentation crate for grapheme clusters in user-facing editing or cursor movement.
- ✅ Keep byte offsets tied to APIs that explicitly document byte offsets.
- ✅ Use `char_indices` when you need both byte offsets and scalar values.
- ✅ Treat ASCII-only fast paths as an optimization guarded by validation, not as the default model of text.

## Pitfalls
- ⚠️ Do not write code that assumes `s.len()` is the number of characters.
- ⚠️ Do not slice strings with arbitrary byte offsets from user input.
- ⚠️ Do not repeatedly call `.chars().nth(i)` in a loop expecting random access performance.
- ⚠️ Do not "fix" this by collecting chars into a `Vec<char>` unless random scalar-value indexing is genuinely required. See [[Unnecessary Collect]].
- ⚠️ Do not use `len()` for display width; terminal cells, grapheme clusters, and bytes are different units.
- ⚠️ Do not store string byte offsets across mutation without revalidating them. See [[Stale Slice Indices]].

## See also
[[String and str]] · [[Iterating Collections]] · [[Index Panics vs get]] · [[Borrowing Strings and Slices]] · [[Dynamically Sized Types]] · [[Unnecessary Collect]] · [[Stale Slice Indices]] · [[Vec]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.2 "Indexing into Strings" — [[the-book]], https://doc.rust-lang.org/book/ch08-02-strings.html#indexing-into-strings
- The Rust Programming Language, ch. 8.2 "Slicing Strings" — [[the-book]], https://doc.rust-lang.org/book/ch08-02-strings.html#slicing-strings
- Standard library `str` docs — [[std]], https://doc.rust-lang.org/std/primitive.str.html
- The Rust Reference, string literals — [[the-reference]], https://doc.rust-lang.org/reference/tokens.html#string-literals
