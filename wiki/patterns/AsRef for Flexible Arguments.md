---
type: pattern
title: "AsRef for Flexible Arguments"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, asref, borrowing, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[Conversion Traits]]", "[[Borrow for Equivalent Keys]]", "[[Accepting impl Trait vs Generics]]", "[[Borrowing Strings and Slices]]", "[[Implementing Borrow for Partial Views]]"]
sources: ["[[rust-by-example]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/trait.AsRef.html", "https://doc.rust-lang.org/std/path/struct.Path.html", "https://doc.rust-lang.org/std/primitive.str.html"]
rust_version: "edition 2024 / 1.85+"
---

# AsRef for Flexible Arguments

`AsRef<T>` is the idiom for accepting cheap borrowed views from multiple input types without taking ownership.

## What it is
`AsRef<T>` converts `&Self` to `&T`.
It is useful when an API needs to read a `str`, `Path`, byte slice, or similar borrowed target, and callers may have owned or borrowed wrappers.

The most familiar shape is `fn open(path: impl AsRef<Path>)`.
That lets callers pass `&Path`, `PathBuf`, `&str`, `String`, and other path-like values while the function only borrows a `Path`.

## How it works
The function receives a generic value, calls `.as_ref()`, and works with the borrowed target.
No ownership transfer is implied.
No equality or hashing promise is implied.

That last point separates `AsRef` from [[Borrow for Equivalent Keys]].
Use `AsRef` for argument flexibility.
Use `Borrow` when a collection key must be looked up through an equivalent borrowed form.

`AsRef` is intentionally shallow: it says only that a cheap reference conversion exists.
It does not promise allocation-free ownership conversion, it does not promise a stable identity, and it does not promise that the returned reference is the only meaningful view of the value.
That makes it excellent for parameters and poor for key semantics.

Because argument-position `impl Trait` creates a generic function, each distinct input type is monomorphized.
This is usually fine for boundary helpers such as path or string readers, but internal hot code can often take a plain `&str`, `&Path`, or `&[u8]` after the boundary has normalized the input.

## Example
```rust
fn nonempty_lines(text: impl AsRef<str>) -> usize {
    text.as_ref()
        .lines()
        .filter(|line| !line.trim().is_empty())
        .count()
}

fn main() {
    let owned = String::from("a\n\nb\n");
    let borrowed = "x\ny\n";

    assert_eq!(nonempty_lines(owned), 2);
    assert_eq!(nonempty_lines(borrowed), 2);
}
```

## Path-like example
`AsRef<Path>` is useful when the function only needs to inspect or pass along a borrowed path.

```rust
use std::path::{Path, PathBuf};

fn extension_lowercase(path: impl AsRef<Path>) -> Option<String> {
    path.as_ref()
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.to_ascii_lowercase())
}

fn main() {
    let path_buf = PathBuf::from("README.MD");
    let path_ref = Path::new("src/lib.rs");

    assert_eq!(extension_lowercase(&path_buf), Some(String::from("md")));
    assert_eq!(extension_lowercase(path_ref), Some(String::from("rs")));
    assert_eq!(extension_lowercase("LICENSE"), None);
}
```

## Common errors
Passing a wrapper that has no `AsRef` implementation produces a trait-bound error:

```text
error[E0277]: the trait bound `Config: AsRef<str>` is not satisfied
```

Fix it by passing the field (`config.name.as_str()`), adding a deliberate `AsRef<str>` implementation, or changing the function to accept the real domain type.
Do not add `AsRef` just because it is convenient if exposing that view would be misleading.

## Best practice
- ✅ Use `impl AsRef<Path>`, `impl AsRef<str>`, or `impl AsRef<[u8]>` at boundaries where caller ergonomics matter.
- ✅ Call `as_ref()` once near the top of the function and use the borrowed target afterward.
- ✅ Prefer plain `&str` or `&[u8]` in small internal functions where every caller already has that exact type.
- ✅ Use [[Accepting impl Trait vs Generics]] to choose between anonymous `impl Trait` and named generic parameters.
- ✅ Prefer `AsRef<Path>` over `AsRef<str>` for filesystem APIs; paths are not always valid UTF-8.
- ✅ Treat `AsRef` setters on builders as boundary ergonomics, then store the owned type the target needs.

## Pitfalls
- ⚠️ Do not use `AsRef` when the function must store the value beyond the call; take ownership instead.
- ⚠️ Do not use `AsRef` as a substitute for [[Borrow for Equivalent Keys]] in map lookup semantics.
- ⚠️ Do not make every parameter generic just for style; excessive monomorphization can hurt compile times.
- ⚠️ Do not return a reference derived from a temporary created inside `as_ref()` logic; `AsRef` should return a view into `self`.
- ⚠️ Avoid `impl AsRef<str>` when `impl Display` or `ToString` is the real requirement; those communicate formatting, not borrowing.

## See also
[[Conversion Traits]] · [[Borrow for Equivalent Keys]] · [[Accepting impl Trait vs Generics]] · [[Borrowing Strings and Slices]] · [[String and str]] · [[Vec]] · [[Constructor Naming]] · [[Builder Pattern]] · [[Idioms & API Design]]

## Sources
- `AsRef` - https://doc.rust-lang.org/std/convert/trait.AsRef.html
- `Path` - https://doc.rust-lang.org/std/path/struct.Path.html
- Primitive `str` - https://doc.rust-lang.org/std/primitive.str.html
