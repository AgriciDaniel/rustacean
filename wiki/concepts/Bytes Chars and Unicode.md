---
type: concept
title: "Bytes Chars and Unicode"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unicode, utf8, string, chars]
domain: "std: Vec, String & Slices"
difficulty: intermediate
related: ["[[String vs str Methods]]", "[[String Byte Indexing]]", "[[Assuming String Indexes Are Characters]]", "[[Slicing and Range Indexing]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.str.html#method.bytes", "https://doc.rust-lang.org/std/primitive.str.html#method.chars", "https://doc.rust-lang.org/std/primitive.str.html#method.char_indices"]
rust_version: "edition 2024 / 1.85+"
---

# Bytes Chars and Unicode

Rust strings are valid UTF-8 bytes; `bytes()` iterates raw bytes, `chars()` iterates Unicode scalar values, and neither directly means "visible character."

## What it is
`String` and `&str` store UTF-8.
`len()` returns the number of bytes.
`bytes()` yields each encoded byte as `u8`.
`chars()` decodes Unicode scalar values as `char`.
`char_indices()` yields byte offsets paired with decoded `char` values.
A Unicode scalar value can require one to four bytes in UTF-8.
A user-perceived character can be multiple scalar values, such as a base character plus combining marks.
The standard library does not provide full grapheme cluster segmentation.
For grapheme clusters, use a Unicode-aware crate such as `unicode-segmentation`; verify the latest version on docs.rs before adding it.

## How it works
ASCII text has one byte per scalar value.
Non-ASCII text does not.
For example, `é` is one scalar value but two UTF-8 bytes.
`日` is one scalar value but three UTF-8 bytes.
String slicing requires byte offsets that are also character boundaries.
`is_char_boundary(i)` checks whether a byte offset can be used as a boundary.
`find`, `rfind`, `match_indices`, and `char_indices` return byte offsets.
That is good: byte offsets can be used directly with slicing if they came from the same string and remain valid.
Case conversion and normalization are separate Unicode topics; `to_lowercase` on `char` can produce multiple `char` values.
Use byte APIs for protocols and file formats, scalar APIs for Rust-level Unicode values, and specialized crates for human text segmentation.

## Example
```rust
fn main() {
    let text = "aé日";

    assert_eq!(text.len(), 6);
    assert_eq!(text.bytes().count(), 6);
    assert_eq!(text.chars().count(), 3);

    let offsets: Vec<(usize, char)> = text.char_indices().collect();
    assert_eq!(offsets, vec![(0, 'a'), (1, 'é'), (3, '日')]);

    assert!(text.is_char_boundary(3));
    assert!(!text.is_char_boundary(2));
    assert_eq!(text.get(1..3), Some("é"));
}
```

## Best practice
- ✅ Use `as_bytes` or `bytes` for wire formats, ASCII checks, and binary protocols.
- ✅ Use `chars` for Unicode scalar transformations where scalar values are the correct unit.
- ✅ Use `char_indices` when you need safe offsets for later slicing.
- ✅ Store byte offsets only if they are derived from the same string version.
- ✅ Use pattern APIs such as `split`, `find`, and `strip_prefix` before writing manual scanners.
- ✅ Reach for a Unicode crate when product behavior depends on grapheme clusters or normalization.
- ✅ Document text units in public APIs: bytes, scalar values, lines, words, or graphemes.
- ✅ Prefer checked slicing with `get` when offsets may be wrong.

## Pitfalls
- ⚠️ `chars().count()` is O(n), not a cached length.
- ⚠️ `chars().nth(n)` repeatedly in a loop is usually quadratic.
- ⚠️ `char` is not "a displayed character" in all languages.
- ⚠️ Byte indexes from one string are not valid for another string just because text looks similar.
- ⚠️ Unicode normalization can make visually similar strings compare unequal.
- ⚠️ `make_ascii_lowercase` and `eq_ignore_ascii_case` are intentionally ASCII-only.
- ⚠️ Slicing at an arbitrary byte offset can panic; see [[String Byte Indexing]].
- ⚠️ `split_whitespace` uses Unicode whitespace, while `split_ascii_whitespace` is ASCII-only.

## See also
[[std: Vec, String & Slices]] · [[String vs str Methods]] · [[Slicing and Range Indexing]] · [[String Byte Indexing]] · [[Assuming String Indexes Are Characters]] · [[Splitting Strings Without Collecting]] · [[Borrowing Strings and Slices]] · [[The Slice Type]] · [[Iterator Performance]]

## Sources
- Rust standard library, `str::bytes` — [[std]], https://doc.rust-lang.org/std/primitive.str.html#method.bytes
- Rust standard library, `str::chars` and `str::char_indices` — [[std]], https://doc.rust-lang.org/std/primitive.str.html#method.chars
- `unicode-segmentation` crate documentation, if used in real code verify latest version — https://docs.rs/unicode-segmentation/latest/unicode_segmentation/
