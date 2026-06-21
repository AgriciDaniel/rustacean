---
type: pattern
title: "Implementing Display by Hand"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, fmt, display, traits]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[Format Strings and format!]]", "[[Format Specifiers]]", "[[Display and Debug Formatting Traits]]", "[[The Display Trait]]", "[[The Debug Trait]]", "[[Traits]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/fmt/trait.Display.html", "https://doc.rust-lang.org/std/fmt/struct.Formatter.html", "https://doc.rust-lang.org/std/fmt/index.html#formatting-traits"]
rust_version: "edition 2024 / 1.85+"
---

# Implementing Display by Hand

Implement `fmt::Display` when a type has a clear user-facing textual representation, and write only through the provided `Formatter`.

## What it is
`Display` controls `{}` formatting.
It is the trait used by `to_string()` for types that implement it.
Unlike `Debug`, `Display` is not meant for every type.
It should represent a value in a way users or domain experts expect.
`Display` cannot be derived by the standard library.
You implement it by writing `fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result`.
Inside `fmt`, use `write!(f, ...)`.
The formatter is the destination supplied by the formatting machinery.
The implementation should not allocate unless allocation is genuinely needed.
The implementation should not fail for its own reasons.

## How it works
`fmt::Result` is an alias for `Result<(), fmt::Error>`.
The error is for propagating an error from the formatter.
String formatting itself is normally infallible.
The standard docs state that formatting implementations should not return errors spuriously.
This means you return the result of `write!`, `f.write_str`, `f.pad`, or another formatter call.
You do not validate business rules inside `fmt`.
Validation belongs in constructors or parsing.
The `Formatter` exposes flags such as width, precision, alternate, sign, and alignment.
Simple `Display` implementations often ignore these flags.
More polished implementations can use helpers such as `pad` or `pad_integral`.
If the type is mainly for diagnostics, derive or implement `Debug` instead.

## Example
```rust
use std::fmt;

struct Point {
    x: i32,
    y: i32,
}

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

fn main() {
    let point = Point { x: 3, y: 4 };
    assert_eq!(point.to_string(), "(3, 4)");
    assert_eq!(format!("point={point}"), "point=(3, 4)");
}
```

## Example: honoring width through pad
```rust
use std::fmt;

struct UserId(u64);

impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let text = format!("user-{}", self.0);
        f.pad(&text)
    }
}

fn main() {
    assert_eq!(format!("{:>10}", UserId(7)), "    user-7");
}
```

## Best practice
- ✅ Implement `Display` only when there is one obvious textual representation.
- ✅ Derive `Debug` for diagnostics even when `Display` exists.
- ✅ Use `write!(f, ...)` and propagate its result directly.
- ✅ Keep `fmt` side-effect free.
- ✅ Keep validation out of `fmt`.
- ✅ Consider honoring width and precision for reusable public types.
- ✅ Use newtypes when you need a different display for an existing foreign type.

## Pitfalls
- ⚠️ Returning `Err(fmt::Error)` manually for domain errors is wrong; see [[Panicking From Implementations]].
- ⚠️ `Display` output is not automatically parseable; document parse/display round trips if promised.
- ⚠️ Allocating with `format!` inside `fmt` can be unnecessary.
- ⚠️ Recursively formatting `self` with `{self}` inside its own `Display` overflows.
- ⚠️ Implementing a foreign trait for a foreign type violates coherence; use [[Newtype Pattern]].
- ⚠️ `to_string()` only exists via `Display`, not `Debug`.
- ⚠️ Hiding important state in `Display` can make logs misleading.

## See also
[[std IO & Formatting]] · [[Format Strings and format!]] · [[Format Specifiers]] ·
[[Display and Debug Formatting Traits]] · [[The Display Trait]] · [[The Debug Trait]] ·
[[Newtype Pattern]] · [[Use a Newtype to Implement Foreign Traits]] · [[Panicking From Implementations]] · [[Traits]]

## Sources
- Rust Standard Library, `Display` — [[std]],
  https://doc.rust-lang.org/std/fmt/trait.Display.html
- Rust Standard Library, formatting traits — [[std]],
  https://doc.rust-lang.org/std/fmt/index.html#formatting-traits
- Rust Standard Library, `Formatter` — [[std]],
  https://doc.rust-lang.org/std/fmt/struct.Formatter.html
