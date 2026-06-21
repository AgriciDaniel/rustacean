---
type: concept
title: "Const Generics and Const Parameters"
aliases: ["Const Generics"]
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, generics, const-generics, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Generics]]", "[[Arrays]]", "[[Associated Constants]]", "[[Trait Bounds]]", "[[Type-State Pattern]]", "[[Zero-Sized Types]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/generics.html#const-generics", "https://doc.rust-lang.org/reference/items/generics.html#standalone"]
rust_version: "edition 2024 / 1.85+"
---

# Const Generics and Const Parameters

Const generics let a generic item vary over compile-time values, not only over types and lifetimes.
Use them when the value is part of the type contract, such as an array length, protocol width, or type-level mode.

## What it is
Const generic parameters are declared with `const NAME: Type` in an item's generic parameter list.
They are in the value namespace and every monomorphized instance gets a concrete constant value.
The most common stable form is `const N: usize`, because array lengths are `usize`.
Const parameters can appear on structs, enums, functions, traits, trait impls, and type aliases.
They complement [[Generics]] by moving small compile-time values into the type identity.
`Buffer<u8, 16>` and `Buffer<u8, 32>` are different types, just as `Vec<u8>` and `Vec<u16>` are different types.
This is useful when a size or mode must be checked before runtime.
It is also useful when array lengths should stay visible in function signatures.

## How it works
Stable const parameters are restricted to primitive scalar const-parameter types:
integer types, `usize`/`isize`, `char`, and `bool`.
The parameter can be used where a const item can be used, but type-level expressions have an important limitation.
Inside a type or array repeat expression, the const parameter generally must appear as a standalone argument such as `N` or `{ N }`.
For example, `[u8; N]` is stable, but `[u8; N + 1]` is not accepted by stable Rust's generic const expression rules.
At runtime inside a generic function body, `N` is just a compile-time constant value and can be used in ordinary expressions.
Const arguments in paths may be literals, single-segment const paths, inferred consts, or braced const expressions.
The type checker treats each distinct const argument as part of the instantiated type.
This means const generics can encode invariants without carrying a runtime field.
It also means public const parameters become part of your semver surface.

## Example
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct Packet<const N: usize> {
    bytes: [u8; N],
}

impl<const N: usize> Packet<N> {
    const LEN: usize = N;

    fn new(bytes: [u8; N]) -> Self {
        Self { bytes }
    }

    fn checksum(&self) -> u8 {
        self.bytes.iter().fold(0, |acc, byte| acc.wrapping_add(*byte))
    }
}

fn accepts_four(packet: Packet<4>) -> u8 {
    packet.checksum()
}

fn main() {
    let packet = Packet::<4>::new([1, 2, 3, 4]);
    assert_eq!(Packet::<4>::LEN, 4);
    assert_eq!(accepts_four(packet), 10);
}
```

## Edge cases
```rust
struct Flag<const ENABLED: bool>;

impl<const ENABLED: bool> Flag<ENABLED> {
    fn is_enabled(&self) -> bool {
        ENABLED
    }
}

fn main() {
    let on = Flag::<true>;
    let off = Flag::<false>;
    assert!(on.is_enabled());
    assert!(!off.is_enabled());
}
```

## Best practice
- ✅ Use const generics when the constant is part of the API's type-level contract.
- ✅ Prefer `const N: usize` for lengths and capacities that index arrays or slices.
- ✅ Keep arithmetic on const parameters in runtime code unless you have verified a stable type-level form.
- ✅ Treat changes to public const parameters as breaking API changes.
- ✅ Name const parameters like constants: `N`, `LEN`, `ROWS`, `COLS`, or `ENABLED`.
- ✅ Link const generic APIs to [[Arrays]], [[Associated Constants]], and [[Type-State Pattern]] when the invariant is visible to callers.

## Pitfalls
- ⚠️ Assuming stable Rust accepts arbitrary type-level arithmetic such as `[T; N + 1]`; see [[Unnecessary Bounds on Data Types]] for related overconstraint habits.
- ⚠️ Encoding ordinary configuration as const generics when a field or enum would be simpler.
- ⚠️ Forgetting that `Thing<3>` and `Thing<4>` are different types and may require separate impl resolution.
- ⚠️ Making every capacity const-generic in a public API; this can multiply monomorphization and complicate users' type signatures.
- ⚠️ Using const generics to simulate dependent types; Rust's stable type system is intentionally more limited.

## See also
[[Advanced Type System]]
[[Generics]]
[[Arrays]]
[[Associated Constants]]
[[Trait Bounds]]
[[Type-State Pattern]]
[[Zero-Sized Types]]
[[Static Dispatch with Generics]]
[[Readable Generic APIs]]
[[Overgeneric Public APIs]]

## Sources
- The Rust Reference, "Generic parameters" and "Const generics" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/generics.html#const-generics
- The Rust Reference, "Standalone const parameters in types" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/generics.html#standalone
