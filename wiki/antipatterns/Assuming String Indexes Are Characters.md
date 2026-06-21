---
type: antipattern
title: "Assuming String Indexes Are Characters"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, string, unicode, indexing, antipattern]
domain: "std: Vec, String & Slices"
difficulty: basic
related: ["[[String Byte Indexing]]", "[[Bytes Chars and Unicode]]", "[[Slicing and Range Indexing]]", "[[String vs str Methods]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.str.html#method.is_char_boundary", "https://doc.rust-lang.org/std/string/struct.String.html#method.truncate"]
rust_version: "edition 2024 / 1.85+"
---

# Assuming String Indexes Are Characters

The mistake is treating Rust string indexes as character positions; Rust string ranges use byte offsets, and invalid UTF-8 boundaries panic.

## The mistake
Code receives "character position 3" from a UI, protocol, or mental model.
It then uses that number as `text[..3]`, `remove(3)`, `insert(3, ch)`, `truncate(3)`, or `split_off(3)`.
This appears to work for ASCII.
It fails or panics for non-ASCII text.
It can also silently cut at the wrong human-visible place when scalar values and grapheme clusters differ.
The standard library intentionally does not implement `Index<usize>` for `str` because a byte at an arbitrary position is not a `char`.

## Why it happens
UTF-8 is variable-width.
ASCII characters take one byte.
Many other Unicode scalar values take two, three, or four bytes.
Rust keeps strings valid UTF-8 at all times.
Therefore string operations that split or mutate at byte offsets require character boundaries.
`String::len` returns bytes because that is O(1) and matches storage.
`chars().count()` returns scalar count but requires scanning.
`char_indices()` is the bridge: it gives valid byte offsets for scalar boundaries.
For displayed characters, even scalar boundaries may not match user expectations because grapheme clusters can contain multiple scalar values.

## Example
```rust
fn prefix_chars(text: &str, count: usize) -> &str {
    if count == 0 {
        return "";
    }

    match text.char_indices().nth(count) {
        Some((byte_index, _)) => &text[..byte_index],
        None => text,
    }
}

fn main() {
    let text = "aé日";

    assert_eq!(text.len(), 6);
    assert_eq!(prefix_chars(text, 2), "aé");
    assert_eq!(text.get(0..2), None);
    assert_eq!(text.get(0..3), Some("aé"));
}
```

## Best practice
- ✅ Keep string offsets as byte offsets when they come from `find`, `match_indices`, or `char_indices`.
- ✅ Use `get(range)` to handle invalid string ranges without panicking.
- ✅ Use `char_indices` to convert scalar positions into byte ranges.
- ✅ Use `chars` for scalar-value iteration rather than indexing.
- ✅ Use a Unicode segmentation crate for grapheme clusters; verify the latest version on docs.rs.
- ✅ Define public text APIs in terms of bytes, scalar values, or graphemes explicitly.
- ✅ Prefer delimiter and pattern methods over manual string slicing.
- ✅ Test text logic with non-ASCII cases.

## Pitfalls
- ⚠️ `s[..n]` can panic if `n` is not a character boundary.
- ⚠️ `String::truncate`, `insert`, `remove`, `split_off`, and `drain` also require character-boundary byte indexes.
- ⚠️ `chars().nth(i)` in a loop repeatedly scans from the start.
- ⚠️ `char` is a Unicode scalar value, not necessarily a displayed character.
- ⚠️ Byte offsets become stale when the string is modified before that offset.
- ⚠️ `make_ascii_uppercase` is not full Unicode uppercase conversion.
- ⚠️ A byte index from one string is meaningless for another string.
- ⚠️ ASCII-only tests hide this bug.

## See also
[[std: Vec, String & Slices]] · [[String Byte Indexing]] · [[Bytes Chars and Unicode]] · [[Slicing and Range Indexing]] · [[String vs str Methods]] · [[Splitting Strings Without Collecting]] · [[Index Panics vs get]] · [[Stale Slice Indices]] · [[Borrowing Strings and Slices]]

## Sources
- Rust standard library, `str::is_char_boundary` and string slicing behavior — [[std]], https://doc.rust-lang.org/std/primitive.str.html#method.is_char_boundary
- Rust standard library, `String::truncate` boundary requirements — [[std]], https://doc.rust-lang.org/std/string/struct.String.html#method.truncate
