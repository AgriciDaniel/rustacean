---
type: concept
title: "AsRef and AsMut Conversion Traits"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, conversions, asref, asmut]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[AsRef for Flexible Arguments]]", "[[Borrowed Parameter APIs]]", "[[Borrowing Strings and Slices]]", "[[Deref and DerefMut]]"]
sources: ["[[std]]", "[[api-guidelines]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/trait.AsRef.html", "https://doc.rust-lang.org/std/convert/trait.AsMut.html", "https://doc.rust-lang.org/std/borrow/trait.Borrow.html"]
rust_version: "edition 2024 / 1.85+"
---

# AsRef and AsMut Conversion Traits

`AsRef<T>` and `AsMut<T>` are cheap, explicit reference-to-reference conversion traits for APIs that accept several owned or borrowed representations of the same view.

## What it is
`AsRef<T>` converts `&self` into `&T`.
`AsMut<T>` converts `&mut self` into `&mut T`.
They do not consume the value.
They should be cheap and infallible.

These traits are common in parameter bounds.
`impl AsRef<Path>` accepts `Path`, `PathBuf`, `&Path`, `&PathBuf`, and related wrappers.
`impl AsRef<str>` can accept `String` and `&str`.

The pattern note [[AsRef for Flexible Arguments]] covers the API-design use case.
This note focuses on the trait meaning and its difference from nearby traits.

## How it works
The required method for `AsRef<T>` is `as_ref(&self) -> &T`.
The required method for `AsMut<T>` is `as_mut(&mut self) -> &mut T`.

Use these traits for a view conversion.
They are not ownership conversions like [[Infallible Conversion Traits (std)]].
They are not fallible validation like [[Fallible Conversion Traits (std)]].
They are not formatting like [[Display and Debug Formatting Traits]].

`Borrow` is related but stricter.
`Borrow` is for key-equivalent borrowed forms and requires equality/hash/order consistency between owned and borrowed values.
`AsRef` is more general and is usually the right choice for flexible function arguments.

`Deref` is also related.
Do not implement `Deref` just to make argument passing convenient.
Prefer `AsRef` for explicit view conversions.

## Example
```rust
use std::path::{Path, PathBuf};

fn file_stem_text(path: impl AsRef<Path>) -> Option<String> {
    path.as_ref()
        .file_stem()
        .and_then(|stem| stem.to_str())
        .map(str::to_owned)
}

#[derive(Debug)]
struct Buffer(Vec<u8>);

impl AsMut<[u8]> for Buffer {
    fn as_mut(&mut self) -> &mut [u8] {
        &mut self.0
    }
}

fn zero<T: AsMut<[u8]>>(bytes: &mut T) {
    bytes.as_mut().fill(0);
}

fn main() {
    assert_eq!(file_stem_text(PathBuf::from("src/main.rs")), Some("main".into()));

    let mut buffer = Buffer(vec![1, 2, 3]);
    zero(&mut buffer);
    assert_eq!(buffer.0, vec![0, 0, 0]);
}
```

## Best practice
- ✅ Use `impl AsRef<Path>` for path-like input parameters.
- ✅ Use `impl AsRef<str>` only when the function truly just needs a string slice view.
- ✅ Use `AsMut` for APIs that need a mutable view into caller-owned storage.
- ✅ Prefer `Borrow` for map key lookup equivalence, not general conversion.
- ✅ Keep implementations cheap, infallible, and unsurprising.

## Pitfalls
- ⚠️ Do not use `AsRef` when the function needs ownership; use [[Infallible Conversion Traits (std)]] or take the owned type.
- ⚠️ Do not use `AsRef` to perform validation or allocation.
- ⚠️ Do not implement [[Deref and DerefMut]] just to get implicit argument coercions.
- ⚠️ Avoid overgeneric signatures when a simple borrowed parameter is clearer.

## See also
[[std: Core Trait Catalog]] · [[AsRef for Flexible Arguments]] · [[Borrowed Parameter APIs]] · [[Borrowing Strings and Slices]] · [[Deref and DerefMut]] · [[Infallible Conversion Traits (std)]] · [[Fallible Conversion Traits (std)]] · [[Borrow for Equivalent Keys]] · [[Implementing Borrow for Partial Views]] · [[String and str]]

## Sources
- Rust standard library, `std::convert::AsRef` - [[std]], https://doc.rust-lang.org/std/convert/trait.AsRef.html
- Rust standard library, `std::convert::AsMut` - [[std]], https://doc.rust-lang.org/std/convert/trait.AsMut.html
- Rust standard library, `std::borrow::Borrow` - [[std]], https://doc.rust-lang.org/std/borrow/trait.Borrow.html
