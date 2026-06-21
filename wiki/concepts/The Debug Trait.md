---
type: concept
title: "The Debug Trait"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, debug, formatting, traits]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[The Display Trait]]", "[[PartialEq]]", "[[Documentation Comments]]", "[[Readable Generic APIs]]", "[[Testing]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-02-example-structs.html#adding-useful-functionality-with-derived-traits", "https://doc.rust-lang.org/std/fmt/trait.Debug.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Debug"]
---

# The Debug Trait

`std::fmt::Debug` gives a programmer-facing representation via `{:?}`; usually obtained with `#[derive(Debug)]`.

## What it is
`Debug` is the standard formatting trait for developer-oriented output. It powers `{:?}`,
`{:#?}`, `dbg!`, many assertion failure messages, and common diagnostic logs.

Unlike [[The Display Trait]], `Debug` is not required to be pretty, stable, or suitable for end users.
Its job is to expose enough structure for programmers to inspect a value while developing or
debugging.

Most structs and enums should derive it unless doing so would expose secrets or produce misleading
output.

## How it works
The formatting macros use the format string to choose a trait. `{:?}` requires `T: Debug`, while `{}`
requires `T: Display`. Pretty debug formatting with `{:#?}` uses the same trait but asks the
formatter for alternate layout.

`#[derive(Debug)]` generates an implementation that prints the type name, field names for structs,
variant names for enums, and nested fields using their own `Debug` implementations. Every field must
also implement `Debug`.

Manual implementations use `std::fmt::Formatter` helpers such as `debug_struct`, `debug_tuple`, and
`debug_list`, which handle alternate formatting consistently.

## Example
```rust
#[derive(Debug, PartialEq)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let rect = Rectangle { width: 30, height: 50 };

    assert_eq!(
        format!("{rect:?}"),
        "Rectangle { width: 30, height: 50 }"
    );
}
```

## Edge cases
Use a manual implementation when a derived one would leak sensitive data or drown diagnostics in
irrelevant fields:

```rust
use std::fmt;

struct ApiKey {
    label: String,
    secret: String,
}

impl fmt::Debug for ApiKey {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("ApiKey")
            .field("label", &self.label)
            .field("secret", &"<redacted>")
            .finish()
    }
}

fn main() {
    let key = ApiKey { label: "prod".into(), secret: "s3cr3t".into() };
    assert!(format!("{key:?}").contains("<redacted>"));
}
```

## Common errors
Using `{:?}` for a type without `Debug` produces E0277:

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // println!("{:?}", Point { x: 1, y: 2 });
}
```

Typical diagnostic:

```text
error[E0277]: `Point` doesn't implement `Debug`
help: consider annotating `Point` with `#[derive(Debug)]`
```

Fix it with a derive or a manual implementation:

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}
```

## Best practice
- ✅ Derive `Debug` on most public data types unless output would reveal secrets.
- ✅ Pair `Debug` with [[PartialEq]] in tests so assertion failures show useful values.
- ✅ Use `{value:#?}` for nested structures that are hard to read on one line.
- ✅ Use manual `Debug` to redact tokens, passwords, and personal data.
- ✅ Do not promise exact `Debug` text as a stable public format.

## Pitfalls
- ⚠️ Do not use `Debug` output for machine-readable serialization.
- ⚠️ Do not show secrets just because a derive is convenient.
- ⚠️ Remember that all fields must implement `Debug` for a derived implementation to compile.
- ⚠️ `dbg!(expr)` moves or borrows according to the expression; do not leave it in polished APIs.
- ⚠️ `Debug` is for developers; implement [[The Display Trait]] for user-facing text.

## See also
[[The Display Trait]] · [[PartialEq]] · [[Testing]] · [[Documentation Comments]] · [[Readable Generic APIs]] · [[Functions]] · [[Type Inference]] · [[Scalar Types]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 5.2 "Adding Useful Functionality with Derived Traits" — [[the-book]], https://doc.rust-lang.org/book/ch05-02-example-structs.html#adding-useful-functionality-with-derived-traits
- Standard library, `std::fmt::Debug` — https://doc.rust-lang.org/std/fmt/trait.Debug.html
