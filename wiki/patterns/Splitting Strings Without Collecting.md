---
type: pattern
title: "Splitting Strings Without Collecting"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, string, str, iterators, parsing]
domain: "std: Vec, String & Slices"
difficulty: basic
related: ["[[String vs str Methods]]", "[[Bytes Chars and Unicode]]", "[[Unnecessary Collect]]", "[[Return Iterators Instead of Collecting]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/primitive.str.html#method.split", "https://doc.rust-lang.org/std/primitive.str.html#method.split_once"]
rust_version: "edition 2024 / 1.85+"
---

# Splitting Strings Without Collecting

Use `str` split iterators directly when processing delimited text, and collect only when the caller truly needs owned storage or random access.

## What it is
String splitting in the standard library is iterator-based.
Methods such as `split`, `rsplit`, `splitn`, `split_once`, `lines`, and `split_whitespace` borrow from the original string.
They do not allocate substrings.
Each yielded item is an `&str` slice into the input.
That makes them ideal for parsers, validators, command handlers, and log processing.
Collecting into `Vec<&str>` is fine when you need to store fields briefly, inspect length, or index repeatedly.
It is unnecessary when each field is consumed once.
Use `split_once` for key-value pairs because it communicates "at most one delimiter matters."

## How it works
`split(pat)` yields all substrings separated by a pattern.
The pattern can be a `char`, `&str`, closure, or other supported pattern.
`split_terminator` omits a trailing empty field caused by a final terminator.
`split_whitespace` treats Unicode whitespace as separators.
`split_ascii_whitespace` is narrower and useful for ASCII protocols.
`lines` splits on line endings and omits the line terminator.
`splitn(n, pat)` limits the number of yielded pieces.
`rsplitn(n, pat)` does the same from the right.
`split_once(pat)` returns `Option<(&str, &str)>`.
All offsets and slices remain tied to the input lifetime.

## Example
```rust
fn parse_assignment(line: &str) -> Option<(&str, u16)> {
    let (key, value) = line.split_once('=')?;
    let key = key.trim();
    let value = value.trim().parse().ok()?;
    Some((key, value))
}

fn main() {
    assert_eq!(parse_assignment("port = 8080"), Some(("port", 8080)));
    assert_eq!(parse_assignment("missing"), None);

    let words: Vec<&str> = "red green  blue".split_whitespace().collect();
    assert_eq!(words, vec!["red", "green", "blue"]);
}
```

## Best practice
- ✅ Use `split_once` for one delimiter and two fields.
- ✅ Use `split_whitespace` for human-ish whitespace-delimited text.
- ✅ Use `split_ascii_whitespace` for ASCII protocols where Unicode whitespace is not wanted.
- ✅ Use `splitn` or `rsplitn` when only the first or last separators matter.
- ✅ Keep the iterator lazy when you can process each field once.
- ✅ Collect only when you need indexing, length checks, reuse, or ownership of the list.
- ✅ Convert fields to owned `String` only when they must outlive the source string.
- ✅ Combine splitting with `trim`, `parse`, and `filter` in small pipelines.

## Pitfalls
- ⚠️ Empty fields are significant: `"a,,b".split(',')` yields an empty middle field.
- ⚠️ `split_whitespace` and `split(' ')` are not equivalent.
- ⚠️ Returned slices cannot outlive the input string.
- ⚠️ Collecting into `Vec<String>` clones every field and is often unnecessary.
- ⚠️ Pattern search returns byte positions internally; do not treat them as character indexes.
- ⚠️ `lines` does not include line terminators in yielded strings.
- ⚠️ User-facing CSV is more complex than `split(',')`; use a CSV crate and verify the latest version on docs.rs.
- ⚠️ Repeated `nth` calls on split iterators can hide linear scans.

## See also
[[std: Vec, String & Slices]] · [[String vs str Methods]] · [[Bytes Chars and Unicode]] · [[Building Strings Efficiently]] · [[Unnecessary Collect]] · [[Return Iterators Instead of Collecting]] · [[Iterator Adapters]] · [[The Iterator Trait]] · [[Borrowing Strings and Slices]]

## Sources
- Rust standard library, `str::split` family — [[std]], https://doc.rust-lang.org/std/primitive.str.html#method.split
- Rust standard library, `str::split_once` — [[std]], https://doc.rust-lang.org/std/primitive.str.html#method.split_once
