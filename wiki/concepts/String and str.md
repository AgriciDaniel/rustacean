---
type: concept
title: "String and str"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, strings, utf8, str]
domain: "Collections & Strings"
difficulty: basic
related: ["[[Borrowing Strings and Slices]]", "[[String Byte Indexing]]", "[[Capacity and Reallocation]]", "[[Ownership]]", "[[Dynamically Sized Types]]", "[[Iterating Collections]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-02-strings.html", "https://doc.rust-lang.org/std/string/struct.String.html", "https://doc.rust-lang.org/std/primitive.str.html", "https://doc.rust-lang.org/reference/tokens.html#string-literals"]
rust_version: "edition 2024 / 1.85+"
---

# String and str

`String` is an owned, growable UTF-8 buffer; `str` is a borrowed UTF-8 string slice, usually written as `&str`.

## What it is
Rust has a primitive string slice type, `str`, but it is dynamically sized and normally appears behind a reference.
String literals have type `&'static str`.

`String` is a standard library type for owned text that can grow and change.
It stores UTF-8 bytes and enforces the invariant that safe `String` and `&str` values contain valid UTF-8.

Rust programmers often say "string" to mean either `String` or `&str`.
The ownership distinction matters: `String` owns allocation, while `&str` borrows bytes stored elsewhere.

## How it works
`String` behaves like a specialized `Vec<u8>` with UTF-8 validity guarantees and text-oriented methods.
Its `len()` is a byte count, not a count of user-visible letters.
Like `Vec`, a `String` handle stores a pointer, length, and capacity; the allocation contains bytes, not `char` values.

Appending text uses `push_str(&str)` for a string slice and `push(char)` for one Unicode scalar value.
Concatenation with `+` consumes the left-hand `String` and borrows the right-hand side as `&str`.
For several pieces, `format!` is usually clearer and does not move its interpolated arguments.

Because UTF-8 characters can occupy multiple bytes, Rust does not support `s[0]` to get a character from a string.
Use `.chars()` for Unicode scalar values, `.bytes()` for raw bytes, or a Unicode segmentation crate when the domain needs grapheme clusters.

Safe constructors and mutation methods preserve UTF-8 validity.
If you need to parse bytes from outside the program, use `String::from_utf8` or `str::from_utf8` so invalid input is reported instead of smuggled into a string.
Unsafe unchecked constructors exist for specialized code that has already proven UTF-8 validity; ordinary application code should not need them.

## Example
```rust
fn shout(name: &str) -> String {
    let mut out = String::from("hello, ");
    out.push_str(name);
    out.push('!');
    out.to_uppercase()
}

fn main() {
    let owned = String::from("Rust");
    let literal: &str = "Ferris";

    assert_eq!(shout(&owned), "HELLO, RUST!");
    assert_eq!(shout(literal), "HELLO, FERRIS!");
    assert_eq!("Здравствуйте".len(), 24);
    assert_eq!("Здравствуйте".chars().count(), 12);
}
```

## More realistic example
```rust
fn display_name(first: &str, last: &str, nickname: Option<&str>) -> String {
    match nickname {
        Some(nick) if !nick.trim().is_empty() => format!("{first} \"{nick}\" {last}"),
        _ => format!("{first} {last}"),
    }
}

fn first_char(s: &str) -> Option<char> {
    s.chars().next()
}

fn main() {
    let owned_first = String::from("Grace");
    let name = display_name(&owned_first, "Hopper", Some("Amazing Grace"));

    assert_eq!(name, "Grace \"Amazing Grace\" Hopper");
    assert_eq!(first_char("éclair"), Some('é'));
    assert_eq!("éclair".len(), 7);
}
```

The function accepts `&str` so callers can pass literals, `String`, substrings, or borrowed data from a parser.
It returns `String` because the display name is newly constructed owned text.

## Common errors
```text
error[E0277]: the type `str` cannot be indexed by `{integer}`
```

The fix is to choose the intended unit: `s.as_bytes()[0]` for a byte, `s.chars().next()` for a scalar value,
or a Unicode segmentation crate for user-visible grapheme clusters.

```text
error[E0382]: borrow of moved value
```

This often appears after `let combined = left + right;` followed by another use of `left`.
The `+` operator takes ownership of the left `String`; use `format!("{left}{right}")`, `push_str`, or clone only when a second owner is actually needed.

## Best practice
- ✅ Accept `&str` in read-only APIs and return `String` when producing owned text.
- ✅ Treat `len()` as bytes; use `.chars()` or domain-specific Unicode handling for text units.
- ✅ Use `push_str` and `push` for incremental appends to an existing `String`.
- ✅ Use `format!` when combining multiple values into a new string for readability.
- ✅ Prefer `String::from("text")` or `"text".to_owned()` when you need ownership of a literal.
- ✅ Validate external bytes with `String::from_utf8` or `str::from_utf8` before treating them as text.
- ✅ Use `with_capacity` when constructing a large string from pieces and a good byte-size estimate is available.

## Pitfalls
- ⚠️ Do not index strings by integer; `s[0]` is intentionally invalid. See [[String Byte Indexing]].
- ⚠️ Slicing with byte ranges, such as `&s[0..4]`, panics if the range is not on UTF-8 character boundaries.
- ⚠️ Do not expose `String` in parameters when a borrowed `&str` would accept more callers. See [[Borrowing Strings and Slices]].
- ⚠️ Remember that `+` moves the left-hand `String`; use `format!` or clone only when ownership semantics require it.
- ⚠️ Do not assume `char` means "what the user sees as one character"; combining marks and emoji sequences can contain multiple scalar values.
- ⚠️ Do not store byte offsets across string mutation unless the validity contract is explicit. See [[Stale Slice Indices]].

## See also
[[Borrowing Strings and Slices]] · [[String Byte Indexing]] · [[Capacity and Reallocation]] · [[Ownership]] · [[Dynamically Sized Types]] · [[Iterating Collections]] · [[Vec]] · [[The Slice Type]] · [[Stale Slice Indices]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.2 "Storing UTF-8 Encoded Text with Strings" — [[the-book]], https://doc.rust-lang.org/book/ch08-02-strings.html
- Standard library `String` docs — [[std]], https://doc.rust-lang.org/std/string/struct.String.html
- Standard library `str` docs — [[std]], https://doc.rust-lang.org/std/primitive.str.html
- The Rust Reference, string literals — [[the-reference]], https://doc.rust-lang.org/reference/tokens.html#string-literals
