---
type: concept
title: "Format Specifiers"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, fmt, formatting, specifiers]
domain: "std: I/O & Formatting"
difficulty: intermediate
related: ["[[Format Strings and format!]]", "[[Implementing Display by Hand]]", "[[Writing Standard Output]]", "[[Display and Debug Formatting Traits]]", "[[The Display Trait]]", "[[The Debug Trait]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/fmt/index.html#formatting-parameters", "https://doc.rust-lang.org/std/fmt/index.html#syntax", "https://doc.rust-lang.org/std/fmt/struct.Formatter.html"]
rust_version: "edition 2024 / 1.85+"
---

# Format Specifiers

Format specifiers are the `:...` options inside `{...}` that choose width, alignment, fill, sign, precision, alternate output, numeric base, and formatting trait.

## What it is
A format placeholder has an optional argument and optional format specifier.
The colon introduces formatting options.
`{}` uses the default `Display` formatting.
`{:?}` uses `Debug`.
`{:04}` pads an integer with zeros to a minimum width.
`{:<10}`, `{:^10}`, and `{:>10}` align within a minimum width.
`{:.2}` controls precision.
`{:#x}` requests an alternate hexadecimal form.
The final type marker maps to a formatting trait.
For example, `x` maps to `LowerHex`, and `b` maps to `Binary`.
The behavior is compiler-checked against the argument type.

## How it works
Width is a minimum display width.
If the rendered value is shorter, fill and alignment decide where padding goes.
For non-numeric values, the default is space fill and left alignment.
For numeric values, the default is space fill and right alignment.
The `0` flag performs sign-aware zero padding for numeric output.
Precision means different things for different types.
For strings, precision is a maximum number of characters.
For floating-point values, precision is digits after the decimal point.
For integers, precision is ignored.
Dynamic width and precision can come from other `usize` arguments with `$`.
Alternate `#` has type-specific meanings, such as pretty `Debug` with `{:#?}` or prefixes for bases.
Formatting is locale-independent.

## Example
```rust
fn main() {
    assert_eq!(format!("{:>6}", "rs"), "    rs");
    assert_eq!(format!("{:-<6}", "rs"), "rs----");
    assert_eq!(format!("{:^6}", "rs"), "  rs  ");
    assert_eq!(format!("{:04}", 42), "0042");
    assert_eq!(format!("{:#x}", 27), "0x1b");
    assert_eq!(format!("{:.3}", "abcdef"), "abc");
    assert_eq!(format!("{:.2}", 3.14159), "3.14");
}
```

## Example: dynamic width and precision
```rust
fn main() {
    let width = 8;
    let precision = 3;
    let value = 12.34567;

    assert_eq!(format!("{value:>width$.precision$}"), "  12.346");
}
```

## Best practice
- ✅ Use simple specifiers for stable, human-readable layout.
- ✅ Use named dynamic width and precision for clarity.
- ✅ Use `#?` for temporary pretty debug output.
- ✅ Use `write!` with specifiers to avoid intermediate `String` allocation.
- ✅ Choose the specifier that matches the semantic trait you want.
- ✅ Test exact formatting when output is consumed by scripts or snapshots.
- ✅ Keep formatting logic near presentation boundaries.

## Pitfalls
- ⚠️ Width is a minimum, not a maximum.
- ⚠️ String precision truncates by characters, not bytes.
- ⚠️ Some custom `Debug` implementations may not honor all alignment expectations.
- ⚠️ `Debug` format is not stable API for machine parsing.
- ⚠️ Dynamic width and precision arguments must be `usize`.
- ⚠️ Locale-independent numbers always use standard Rust formatting, not the user's locale.
- ⚠️ `{:p}` prints pointer formatting and should not be used as a persistent identity.

## See also
[[std IO & Formatting]] · [[Format Strings and format!]] · [[Implementing Display by Hand]] ·
[[Writing Standard Output]] · [[The Read and Write Traits]] · [[Display and Debug Formatting Traits]] ·
[[The Display Trait]] · [[The Debug Trait]] · [[String and str]] · [[Snapshot Testing]]

## Sources
- Rust Standard Library, formatting parameters — [[std]],
  https://doc.rust-lang.org/std/fmt/index.html#formatting-parameters
- Rust Standard Library, formatting syntax — [[std]],
  https://doc.rust-lang.org/std/fmt/index.html#syntax
- Rust Standard Library, `Formatter` — [[std]],
  https://doc.rust-lang.org/std/fmt/struct.Formatter.html
