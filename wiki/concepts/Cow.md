---
type: concept
title: "Cow"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cow, clone-on-write, borrowing, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Borrowing]]", "[[Ownership]]", "[[String and str]]", "[[Borrowing Strings and Slices]]", "[[Copy and Clone]]", "[[Needless Clone]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/borrow/enum.Cow.html", "https://doc.rust-lang.org/std/borrow/trait.ToOwned.html", "https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cow

`Cow<'a, B>` is clone-on-write storage that can hold either a borrowed `&'a B` or an owned `<B as ToOwned>::Owned`, cloning only when mutation or ownership is needed.

## What it is
`Cow` means "clone on write."
It is an enum with borrowed and owned variants.
For common cases, `Cow<'_, str>` can hold either `&str` or `String`, and `Cow<'_, [T]>` can hold either `&[T]` or `Vec<T>`.

`Cow` is useful when most inputs can be returned or passed through borrowed, but a minority need normalization, escaping, filtering, or other allocation-producing changes.

## How it works
Read-only access works through `Deref`, so a `Cow<'_, str>` can be passed to many APIs expecting `&str`.
When mutable access is required, `to_mut()` ensures the value is owned.
If it was borrowed, `to_mut()` clones into the owned representation first.

`into_owned()` consumes the `Cow` and returns the owned value.
It reuses the existing owned value when possible and clones when the value is currently borrowed.

The borrowed type parameter `B` is usually unsized, such as `str` or `[T]`, and must implement `ToOwned`.
For `str`, the owned type is `String`; for `[T]`, the owned type is `Vec<T>` where `T: Clone`.
The lifetime `'a` applies only to the borrowed variant; once converted with `into_owned`, the result no longer borrows from the input.

## Example
```rust
use std::borrow::Cow;

fn normalize_label(input: &str) -> Cow<'_, str> {
    let trimmed = input.trim();
    if trimmed == input {
        Cow::Borrowed(input)
    } else {
        Cow::Owned(trimmed.to_owned())
    }
}

fn main() {
    let clean = normalize_label("rust");
    let padded = normalize_label("  rust  ");

    assert_eq!(&*padded, "rust");
    assert!(matches!(clean, Cow::Borrowed(_)));
    assert!(matches!(padded, Cow::Owned(_)));
}
```

## Worked example: mutate only when needed
```rust
use std::borrow::Cow;

fn ensure_trailing_slash(mut path: Cow<'_, str>) -> Cow<'_, str> {
    if !path.ends_with('/') {
        path.to_mut().push('/');
    }
    path
}

fn main() {
    let unchanged = ensure_trailing_slash(Cow::Borrowed("/api/"));
    let changed = ensure_trailing_slash(Cow::Borrowed("/api"));
    let owned = ensure_trailing_slash(Cow::Owned(String::from("/tmp")));

    assert!(matches!(unchanged, Cow::Borrowed(_)));
    assert!(matches!(changed, Cow::Owned(_)));
    assert_eq!(&*owned, "/tmp/");
}
```

`to_mut()` is the write barrier: it keeps borrowed data borrowed until mutation actually requires owned storage.

## Common errors
Returning `Cow::Borrowed` from data created inside the function fails with a lifetime error, commonly `E0515`:

```text
error[E0515]: cannot return value referencing local variable
```

Return `Cow::Owned(local_string)` for newly created data, or borrow from an input whose lifetime is tied to the returned `Cow<'a, B>`.

Type inference can also need help with `Cow::Owned(String::from("x"))` when no expected `Cow<'_, str>` type is available.
Add an annotation such as `let label: Cow<'_, str> = Cow::Owned(String::from("x"));`.

## Best practice
- ✅ Use `Cow<'a, str>` or `Cow<'a, [T]>` for APIs that often borrow but sometimes allocate.
- ✅ Return `Cow` from normalization functions when preserving borrowed data avoids common allocations.
- ✅ Call `into_owned()` at boundaries that require owned storage.
- ✅ Prefer simple `&str`, `&[T]`, `String`, or `Vec<T>` when clone-on-write does not simplify the API.
- ✅ Accept `impl Into<Cow<'a, str>>` only when the API genuinely benefits from both borrowed and owned callers; otherwise keep signatures direct.
- ✅ Make allocation points visible in reviews: `to_mut`, `into_owned`, and conversions from borrowed `Cow` are the operations to inspect.

## Pitfalls
- ⚠️ `Cow` can make signatures harder to read if every call site always owns or always borrows.
- ⚠️ `to_mut()` may allocate and clone; do not hide that cost in hot paths without measuring.
- ⚠️ `Cow<'a, T>` still carries lifetime constraints when it is borrowed.
- ⚠️ Using `Cow` to avoid thinking about ownership can become a subtler form of [[Needless Clone]].
- ⚠️ `Cow` is not shared ownership; if multiple owners must keep the same allocation alive, use [[Rc]] or [[Arc]] instead.

## See also
[[Borrowing]] · [[Ownership]] · [[String and str]] · [[Borrowing Strings and Slices]] · [[Copy and Clone]] · [[Needless Clone]] · [[Deref and DerefMut]] · [[Smart Pointers & Interior Mutability]]

## Sources
- Standard library, `std::borrow::Cow` - [[std]],
  https://doc.rust-lang.org/std/borrow/enum.Cow.html
- Standard library, `std::borrow::ToOwned` - [[std]],
  https://doc.rust-lang.org/std/borrow/trait.ToOwned.html
