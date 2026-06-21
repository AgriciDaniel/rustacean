---
type: concept
title: "Practice: Strings"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, strings]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[String and str]]", "[[String vs str Methods]]", "[[Bytes Chars and Unicode]]", "[[The Slice Type]]", "[[Borrowing Strings and Slices]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Strings

The strings group teaches the difference between owned UTF-8 text and borrowed string slices. The key idea is to design text APIs around borrowing first, then allocate only when producing new text.

## What it is
These exercises cover `String`, `&str`, converting between them, appending text, slicing safely, and avoiding byte-index assumptions.

## How it works
`String` owns a growable UTF-8 buffer. `str` is a dynamically sized string slice, almost always used as `&str`. Indexing by byte is restricted because not every byte boundary is a valid character boundary.

## Example
```rust
fn greet(name: &str) -> String {
    let mut message = String::from("Hello, ");
    message.push_str(name);
    message.push('!');
    message
}

fn main() {
    let owned = String::from("Rust");
    println!("{}", greet(&owned));
}
```

## Best practice
- ✅ Accept `&str` when reading text.
- ✅ Use `String` when you need ownership or mutation.
- ✅ Use `.chars()` or `.bytes()` only after choosing the correct unit deliberately.

## Pitfalls
- ⚠️ Do not index strings as if they were arrays of characters.
- ⚠️ Avoid allocating with `to_string()` when a borrow is enough.
- ⚠️ Slicing strings with byte ranges can panic if the bounds split a UTF-8 code point.

## See also
[[Practice (Rustlings)]] · [[String and str]] · [[String vs str Methods]] · [[Bytes Chars and Unicode]] · [[The Slice Type]] · [[Borrowing Strings and Slices]] · [[Building Strings Efficiently]]

## Sources
- Rustlings `09_strings` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

