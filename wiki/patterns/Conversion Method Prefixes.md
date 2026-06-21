---
type: pattern
title: "Conversion Method Prefixes"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, naming, conversions, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[Naming Conventions (Rust API Guidelines)]]", "[[From and Into]]", "[[TryFrom and TryInto]]", "[[AsRef for Flexible Arguments]]", "[[Conversion Traits]]"]
sources: ["[[rust-by-example]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/convert/index.html", "https://doc.rust-lang.org/std/convert/trait.AsRef.html", "https://doc.rust-lang.org/std/convert/trait.From.html", "https://doc.rust-lang.org/std/string/struct.String.html"]
rust_version: "edition 2024 / 1.85+"
---

# Conversion Method Prefixes

Rust conversion prefixes are semantic promises: `as_` is a cheap borrowed view, `to_` may do work, and `into_` consumes `self`.

## What it is
Inherent conversion methods should use names that reveal cost and ownership.
This mirrors the Rust API Guidelines and standard-library style.

The common meanings are:

1. `as_` - cheap borrowed view at a lower level of abstraction, such as `as_bytes`.
2. `to_` - creates or computes another value without consuming `self`; it may allocate or otherwise be nontrivial.
3. `into_` - consumes `self` and returns another owned value, often reusing allocation.

## How it works
These prefixes complement [[Conversion Traits]].
Use traits for generic conversion relationships.
Use inherent methods when the operation is more specific, has a conventional name, needs extra arguments, or exposes a representation intentionally.

A bad prefix misleads callers.
An `as_` method that allocates violates a performance expectation.
A `to_` method that consumes `self` hides an ownership transfer.

The receiver is the key signal.
`as_` normally takes `&self` and returns a borrowed view or cheap proxy.
`to_` normally takes `&self` and returns an owned value, often by cloning, allocating, formatting, or otherwise computing.
`into_` takes `self` and may reuse allocation because the original value is no longer available.

These are conventions, not keywords, but they are strong conventions across the standard library.
Following them makes performance and ownership visible in code review without opening the implementation.

## Example
```rust
use std::fmt::Write;

struct Bytes(Vec<u8>);

impl Bytes {
    fn as_slice(&self) -> &[u8] {
        &self.0
    }

    fn to_hex(&self) -> String {
        let mut out = String::with_capacity(self.0.len() * 2);
        for byte in &self.0 {
            write!(&mut out, "{byte:02x}").unwrap();
        }
        out
    }

    fn into_vec(self) -> Vec<u8> {
        self.0
    }
}

fn main() {
    let bytes = Bytes(vec![0, 15, 255]);
    assert_eq!(bytes.as_slice(), &[0, 15, 255]);
    assert_eq!(bytes.to_hex(), "000fff");
    assert_eq!(bytes.into_vec(), vec![0, 15, 255]);
}
```

## Borrowed versus owned example
The same conceptual data can expose all three forms when each form has a distinct ownership story.

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct HeaderName(String);

impl HeaderName {
    fn as_str(&self) -> &str {
        &self.0
    }

    fn to_lowercase(&self) -> String {
        self.0.to_ascii_lowercase()
    }

    fn into_string(self) -> String {
        self.0
    }
}

fn main() {
    let header = HeaderName(String::from("Content-Type"));
    assert_eq!(header.as_str(), "Content-Type");
    assert_eq!(header.to_lowercase(), "content-type");
    assert_eq!(header.into_string(), "Content-Type");
}
```

## Common errors
Calling an `into_` method consumes the value, so using it afterward triggers a move error:

```text
error[E0382]: borrow of moved value
```

Use an `as_` or `to_` method when the original value must remain usable.
If only an `into_` method exists, bind the returned value and stop using the original binding.

## Best practice
- ✅ Use `as_` only for cheap borrowed conversions.
- ✅ Use `to_` for conversions that keep `self` available and may allocate or compute.
- ✅ Use `into_` for conversions that consume `self`.
- ✅ Prefer [[From and Into]] or [[TryFrom and TryInto]] when the conversion is a general trait relationship.
- ✅ Include the target representation in the name when ambiguity exists, such as `to_le_bytes` or `from_utf8_lossy`.
- ✅ Match receiver type to the prefix; reviewers should be able to infer ownership from the name.

## Pitfalls
- ⚠️ Do not hide allocation behind `as_`.
- ⚠️ Do not consume `self` from a `to_` method.
- ⚠️ Avoid `from_` inherent constructors when a standard `From` or `TryFrom` impl fits.
- ⚠️ Do not use `into_` for a method that merely mutates in place; use a verb like `make_ascii_lowercase`.
- ⚠️ Avoid a generic name like `convert` when a standard prefix would describe the operation precisely.

## See also
[[Naming Conventions (Rust API Guidelines)]] · [[Conversion Traits]] · [[From and Into]] · [[TryFrom and TryInto]] · [[AsRef for Flexible Arguments]] · [[Constructor Naming]] · [[Move Semantics]] · [[String and str]] · [[Idioms & API Design]]

## Sources
- Standard library conversion traits - https://doc.rust-lang.org/std/convert/index.html
- `AsRef` - https://doc.rust-lang.org/std/convert/trait.AsRef.html
- `From` - https://doc.rust-lang.org/std/convert/trait.From.html
- `String` methods - https://doc.rust-lang.org/std/string/struct.String.html
- Rust API Guidelines, "Naming" - https://rust-lang.github.io/api-guidelines/naming.html
