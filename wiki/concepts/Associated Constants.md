---
type: concept
title: "Associated Constants"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, traits, constants, associated-items]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[Fully Qualified Syntax]]", "[[Operator Overloading]]", "[[Traits]]", "[[Type Aliases]]", "[[The Never Type]]", "[[Advanced Types & Features]]"]
sources: ["[[the-reference]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/associated-items.html#associated-constants", "https://doc.rust-lang.org/book/ch20-02-advanced-traits.html"]
rust_version: "edition 2024 / 1.85+"
---

# Associated Constants

Associated constants are compile-time constants attached to a type or required by a trait implementation.

## What it is
An associated constant is a `const` item inside an `impl` block or a trait.
In inherent impls, it is accessed through the type path, such as `Color::WHITE`.
In traits, it becomes part of the trait contract; implementors must define required constants and may override defaults.

Associated constants are useful when a value is logically tied to a type rather than to a module.
Examples include protocol limits, numeric identities, format tags, dimensions, and capability flags.

Associated constants are associated items, like associated functions and associated types.
They live in the value namespace and are named with paths.

## How it works
In a trait, `const NAME: Type;` declares a required associated constant.
`const NAME: Type = expression;` provides a default.
An implementation of that trait must provide all non-default associated items, including required associated constants.

Use `Type::CONST` for inherent constants.
Use `<Type as Trait>::CONST` when a trait-associated constant needs disambiguation or when generic code must be precise.
Associated constant definitions are evaluated when referenced, and generic associated constants are evaluated after monomorphization.

Associated constants are not fields.
They are accessed through paths, do not occupy per-instance storage, and cannot depend on runtime values.
Because they are associated items, a trait can use `Self::CONST` in default methods, and generic code can refer to `T::CONST` once `T` is bounded by the trait.

Evaluation timing matters for constants that can fail const evaluation.
An associated constant body is checked for type correctness when compiled, but const evaluation of the value happens when the constant is referenced.
For generic associated constants, that evaluation happens after the generic parameters have been substituted.

## Example
```rust
trait Packet {
    const HEADER_LEN: usize;
    const VERSION: u8 = 1;

    fn payload_len(bytes: &[u8]) -> usize {
        bytes.len().saturating_sub(Self::HEADER_LEN)
    }
}

struct Telemetry;

impl Packet for Telemetry {
    const HEADER_LEN: usize = 8;
}

fn main() {
    let bytes = [0_u8; 20];

    assert_eq!(Telemetry::HEADER_LEN, 8);
    assert_eq!(<Telemetry as Packet>::VERSION, 1);
    assert_eq!(Telemetry::payload_len(&bytes), 12);
}
```

## More realistic example
```rust
trait FixedRecord {
    const NAME: &'static str;
    const WIDTH: usize;

    fn parse_line(line: &str) -> Option<&str> {
        (line.len() == Self::WIDTH).then_some(line)
    }
}

struct AccountRecord;
struct AuditRecord;

impl FixedRecord for AccountRecord {
    const NAME: &'static str = "account";
    const WIDTH: usize = 12;
}

impl FixedRecord for AuditRecord {
    const NAME: &'static str = "audit";
    const WIDTH: usize = 8;
}

fn describe<T: FixedRecord>() -> String {
    format!("{} records are {} bytes", T::NAME, T::WIDTH)
}

fn main() {
    assert_eq!(describe::<AccountRecord>(), "account records are 12 bytes");
    assert_eq!(AuditRecord::parse_line("20240621"), Some("20240621"));
    assert_eq!(AuditRecord::parse_line("too long"), None);
}
```

The constants are part of the trait contract, so generic code can use them without constructing a value.

## Common errors
```rust
trait Packet {
    const HEADER_LEN: usize;
}

struct Telemetry;

// impl Packet for Telemetry {}
// error[E0046]: not all trait items implemented, missing: `HEADER_LEN`

impl Packet for Telemetry {
    const HEADER_LEN: usize = 8;
}
```

The fix is to provide every required associated constant or give the trait a semantically valid default.

```rust
trait Id {
    const VALUE: u32;
}

struct User;

impl User {
    const VALUE: u32 = 1;
}

impl Id for User {
    const VALUE: u32 = 2;
}

fn main() {
    assert_eq!(User::VALUE, 1);
    assert_eq!(<User as Id>::VALUE, 2);
}
```

If the wrong constant is selected, this is usually not a type error.
Use [[Fully Qualified Syntax]] to make the trait source explicit.

## Best practice
- ✅ Use associated constants for values that are part of a type or trait contract.
- ✅ Give required trait constants clear documentation because implementors must choose semantically valid values.
- ✅ Use [[Fully Qualified Syntax]] when an associated constant comes from a trait and ambiguity is possible.
- ✅ Prefer associated constants over magic numbers repeated inside methods.
- ✅ Keep public associated constants small, cheap to evaluate, and stable enough to be relied on by downstream generic code.
- ✅ Use `const` generics when the value should be a type parameter chosen by the caller, and associated constants when the value belongs to the implementor.

## Pitfalls
- ⚠️ Do not use associated constants for runtime configuration; they are compile-time constants.
- ⚠️ Avoid putting large computed data in associated constants when construction cost or binary size matters.
- ⚠️ Be explicit when both inherent and trait-associated constants have the same name.
- ⚠️ Do not encode values as associated constants if implementations need to read files, environment variables, clocks, or feature flags at runtime.
- ⚠️ Remember that changing a public trait constant's meaning can break generic code even if the type remains the same.

## See also
[[Fully Qualified Syntax]] · [[Traits]] · [[Operator Overloading]] · [[Type Aliases]] · [[The Never Type]] · [[Dynamically Sized Types]] · [[Associated Types]] · [[Const Generics]] · [[Advanced Types & Features]]

## Sources
- The Rust Reference, "Associated constants" — [[the-reference]], https://doc.rust-lang.org/reference/items/associated-items.html#associated-constants
- The Rust Programming Language, ch. 20.2 "Advanced Traits" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html
