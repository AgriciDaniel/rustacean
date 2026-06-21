---
type: concept
title: "Practice: Conversions"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, conversions]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Conversion Traits]]", "[[From and Into]]", "[[TryFrom and TryInto]]", "[[Fallible Conversion Traits (std)]]", "[[Infallible Conversion Traits (std)]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Conversions

The conversions group teaches choosing explicit, trait-based conversion APIs. The key idea is that infallible conversions use `From` and `Into`, while conversions that can fail use `TryFrom`, `TryInto`, or parsing.

## What it is
These exercises cover `From`, `Into`, `TryFrom`, `TryInto`, `FromStr`, `parse`, and converting external data into domain types.

## How it works
Implementing `From<A> for B` gives callers `B::from(a)` and usually `a.into()`. Implementing `TryFrom<A> for B` returns `Result<B, E>` so invalid input stays explicit.

## Example
```rust
use std::convert::TryFrom;

#[derive(Debug)]
struct Percent(u8);

impl TryFrom<u8> for Percent {
    type Error = String;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        if value <= 100 {
            Ok(Percent(value))
        } else {
            Err(format!("{value} is greater than 100"))
        }
    }
}

fn main() -> Result<(), String> {
    let p = Percent::try_from(85)?;
    println!("{p:?}");
    Ok(())
}
```

## Best practice
- ✅ Use `From` only when conversion cannot fail and is unsurprising.
- ✅ Use `TryFrom` when validation is required.
- ✅ Prefer domain types that validate once at the boundary.

## Pitfalls
- ⚠️ Do not implement lossy or surprising conversions as `From`.
- ⚠️ Avoid relying on `as` casts for semantic conversions that need validation.
- ⚠️ Type inference with `.into()` can be unclear; use `Type::from(value)` when needed.

## See also
[[Practice (Rustlings)]] · [[Conversion Traits]] · [[From and Into]] · [[TryFrom and TryInto]] · [[Fallible Conversion Traits (std)]] · [[Infallible Conversion Traits (std)]] · [[AsRef and AsMut Conversion Traits]]

## Sources
- Rustlings `23_conversions` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

