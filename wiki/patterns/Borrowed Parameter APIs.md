---
type: pattern
title: "Borrowed Parameter APIs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, api-design, borrowing]
domain: "Ownership & Memory"
difficulty: intermediate
related: ["[[Borrowing]]", "[[References]]", "[[The Slice Type]]", "[[String and str]]", "[[Vec]]", "[[AsRef for Flexible Arguments]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/book/ch04-03-slices.html"]
rust_version: "edition 2024 / 1.85+"
---

# Borrowed Parameter APIs

Borrowed parameter APIs accept the least-owning reference type that supports the operation, such as `&str`, `&[T]`, `&T`, or `&mut T`. This keeps ownership with the caller and makes functions usable with more input shapes.

## What it is
This pattern designs function signatures around temporary access rather than unnecessary ownership transfer.
If a function only reads text, take `&str`.
If it reads a sequence, take `&[T]`.
If it mutates a caller-owned value in place, take `&mut T`.
If it consumes, stores, or returns ownership, then take `T`.

The pattern is especially important for public APIs.
`&str` accepts string literals, `String`, and string slices.
`&[T]` accepts arrays, vectors, and slices.
Concrete references such as `&String` and `&Vec<T>` reject useful callers without adding capability in most read-only code.

## How it works
Borrowed parameters rely on [[Borrowing]] and deref coercions.
A `&String` can coerce to `&str`, and a `&Vec<T>` can coerce to `&[T]`.
That means a function can ask for the abstract borrowed view it needs rather than the caller's exact owner type.

This signature style also documents behavior.
`fn parse(s: &str)` says parsing will not take or keep the string.
`fn normalize(s: &mut String)` says the function edits the caller's string.
`fn into_bytes(s: String)` says ownership is consumed.

Use generic conversions such as `AsRef<str>` deliberately, not automatically.
For many functions, plain borrowed references are simpler, clearer, and easier for type inference.

The receiver form follows the same idea.
Use `&self` for inspection, `&mut self` for in-place mutation, and `self` for consuming
transformations.
This makes method chains and ownership transitions predictable: `as_*` and `get_*` usually borrow,
while `into_*` usually consumes.

Borrowed parameters also reduce allocation pressure.
If callers already own a `String` or `Vec<T>`, passing a borrowed view avoids a clone.
If callers have literals, arrays, or slices, the same function still works without forcing them to
allocate an owned container just to call it.

## Example
```rust
fn main() {
    let owned = String::from("rust brain");
    let literal = "ownership";
    let values = vec![1, 2, 3];

    println!("{}", first_word(&owned));
    println!("{}", first_word(literal));
    println!("{}", sum(&values));
}

fn first_word(s: &str) -> &str {
    s.split_once(' ').map_or(s, |(first, _)| first)
}

fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}
```

## Worked example
```rust
#[derive(Debug, Default)]
struct Report {
    title: String,
    rows: Vec<String>,
}

impl Report {
    fn rename(&mut self, title: &str) {
        self.title.clear();
        self.title.push_str(title);
    }

    fn add_rows(&mut self, rows: &[&str]) {
        self.rows.extend(rows.iter().map(|row| row.to_string()));
    }

    fn into_rows(self) -> Vec<String> {
        self.rows
    }
}

fn main() {
    let mut report = Report::default();
    report.rename("ownership");
    report.add_rows(&["moves", "borrows"]);
    println!("{:?}", report.into_rows());
}
```

## Common errors
Taking ownership in a read-only helper causes moved-value diagnostics for callers:

```text
error[E0382]: borrow of moved value: `name`
```

Change `fn display(name: String)` to `fn display(name: &str)` when the helper only reads:

```rust
fn main() {
    let name = String::from("Ferris");
    display(&name);
    println!("{name}");
}

fn display(name: &str) {
    println!("{name}");
}
```

## Best practice
- ✅ Start with `&str` for text and `&[T]` for read-only sequences.
- ✅ Take `&mut T` for in-place mutation when the caller should keep ownership.
- ✅ Take owned `T` when you need to store it, transform it into another owner, or guarantee no caller aliases remain.
- ✅ Consider `AsRef`, `Borrow`, or generics only when the extra flexibility pays for its complexity.
- ✅ Use naming conventions that match ownership: `as_`/`get_` borrow, `to_` clones or converts, and
  `into_` consumes.
- ✅ Return borrowed views only when they are tied to an input or `self`; otherwise return owned data.

## Pitfalls
- ⚠️ Do not take `String` or `Vec<T>` just to read; that forces a move or clone from callers. See [[Needless Clone]].
- ⚠️ Do not take `&String` when `&str` expresses the need; it unnecessarily excludes literals and slices.
- ⚠️ Do not return borrowed data from an owned parameter that will be dropped at function end. See [[Returning References to Locals]].
- ⚠️ Do not over-genericize simple APIs; concrete borrowed types are often the most readable contract.
- ⚠️ Do not choose `impl AsRef<str>` for every text parameter; it can complicate inference and error
  messages when a plain `&str` would be clearer.

## See also
[[Borrowing]] · [[References]] · [[Mutable References]] · [[The Slice Type]] · [[String and str]] · [[Vec]] · [[AsRef for Flexible Arguments]] · [[Borrow for Equivalent Keys]] · [[Needless Clone]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.2 "References and Borrowing" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- The Rust Programming Language, ch. 4.3 "String Slices as Parameters" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-03-slices.html
