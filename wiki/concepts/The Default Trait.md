---
type: concept
title: "The Default Trait"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, default, derive]
domain: "std: Core Trait Catalog"
difficulty: basic
related: ["[[Default Implementations]]", "[[Struct Update Syntax]]", "[[Builder Pattern]]", "[[Deriving Traits on Structs]]"]
sources: ["[[std]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/default/trait.Default.html", "https://doc.rust-lang.org/reference/attributes/derive.html", "https://doc.rust-lang.org/std/keyword.struct.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Default Trait

`Default` provides a conventional no-argument value for a type, most often used for configuration structs, empty collections, zero-like primitives, and struct update syntax.

## What it is
`Default` has one required method: `fn default() -> Self`.
It is deliberately small.
It does not promise that the value is useful in every context.
It promises that the type has a reasonable baseline value.

The trait is implemented for many primitive and standard-library types.
Numeric values default to zero.
`bool` defaults to `false`.
`Option<T>` defaults to `None`.
Collections usually default to empty collections.

For structs, `#[derive(Default)]` works when every field implements `Default`.
For enums, `#[derive(Default)]` requires one unit variant marked with `#[default]`.
The `#[default]` attribute cannot be placed on variants with fields.

## How it works
`Default::default()` is often used when the target type is known from context.
`Type::default()` is clearer when the type would otherwise be hard to infer.

The trait pairs naturally with [[Struct Update Syntax]].
You can override one or two fields and fill the rest from defaults.
This is common for option structs and test fixtures.

`Default` is not a constructor replacement.
If a value must satisfy nontrivial validation, a named constructor can communicate failure or intent better.
If a type has required fields, forcing a fake default can make invalid states easier to create.

In public APIs, adding or changing a default value can be observable behavior.
Treat it as part of the type's contract.

## Example
```rust
#[derive(Debug, PartialEq)]
struct RetryPolicy {
    attempts: u8,
    backoff_ms: u64,
    jitter: bool,
}

impl Default for RetryPolicy {
    fn default() -> Self {
        Self {
            attempts: 3,
            backoff_ms: 250,
            jitter: true,
        }
    }
}

#[derive(Debug, Default, PartialEq, Eq)]
enum Mode {
    #[default]
    Conservative,
    Fast,
}

fn main() {
    let policy = RetryPolicy {
        attempts: 5,
        ..RetryPolicy::default()
    };

    assert_eq!(policy.backoff_ms, 250);
    assert_eq!(Mode::default(), Mode::Conservative);
}
```

## Best practice
- ✅ Derive `Default` for plain data structs when each field's default is meaningful together.
- ✅ Implement `Default` manually when a domain-specific baseline is clearer than field defaults.
- ✅ Use `..Default::default()` for sparse option construction.
- ✅ Prefer `Type::default()` when inference would make `Default::default()` cryptic.
- ✅ Consider [[Builder Pattern]] when callers need required fields plus many optional settings.

## Pitfalls
- ⚠️ Do not invent a misleading default for a type that has no natural baseline.
- ⚠️ Do not use `Default` to bypass validation; use [[Fallible Conversion Traits (std)]] or named constructors.
- ⚠️ Be careful when `Default` creates a valid but expensive value.
- ⚠️ Do not assume default means "empty" for every custom type.

## See also
[[std: Core Trait Catalog]] · [[Default Implementations]] · [[Struct Update Syntax]] · [[Builder Pattern]] · [[Deriving Traits on Structs]] · [[Making Invalid States Unrepresentable]] · [[Private Fields with Public Constructors]] · [[Option]] · [[Vec]] · [[HashMap]]

## Sources
- Rust standard library, `std::default::Default` - [[std]], https://doc.rust-lang.org/std/default/trait.Default.html
- The Rust Reference, derive attributes - [[the-reference]], https://doc.rust-lang.org/reference/attributes/derive.html
- Rust standard library, struct syntax - [[std]], https://doc.rust-lang.org/std/keyword.struct.html
