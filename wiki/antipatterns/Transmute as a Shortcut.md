---
type: antipattern
title: "Transmute as a Shortcut"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, transmute, antipattern]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Undefined Behavior]]", "[[MaybeUninit]]", "[[Aliasing and Provenance]]", "[[Raw Pointers]]", "[[FFI with C]]"]
sources: ["[[rustonomicon]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/nomicon/transmutes.html", "https://doc.rust-lang.org/std/mem/fn.transmute.html", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html#invalid-values"]
rust_version: "edition 2024 / 1.85+"
---

# Transmute as a Shortcut

Using `transmute` as a shortcut is a footgun because it bypasses type meaning, validity, layout, provenance, and lifetime checks all at once; use narrower conversions instead.

## The mistake
`mem::transmute<T, U>` reinterprets a value of one type as another same-sized type.
That sounds convenient, which is exactly why it is dangerous. It can create invalid
values, invent lifetimes, break aliasing, rely on unspecified layout, or lose pointer
provenance.

The Rustonomicon calls transmute one of the most unsafe operations available. The
problem is not that it is never correct; the problem is that it is almost always a
larger hammer than the conversion needs.

## Why it happens
Developers reach for `transmute` to convert bytes to structs, integers to enums,
shared references to mutable references, arrays of `MaybeUninit<T>` to arrays of
`T`, or C representations to Rust types.

Most of these have a narrower API: `from_ne_bytes`, `try_from`, `NonNull::new`,
`ptr::cast`, `MaybeUninit`, `repr(C)` plus field-by-field validation, or an explicit
safe enum conversion. Narrow APIs document the exact invariant instead of silently
assuming all invariants at once.

`transmute` also moves its input and forgets the source type's meaning. That can
accidentally skip a destructor, duplicate ownership, or create a destination value
whose destructor later runs on invalid data. If the goal is "reinterpret a pointer
type" or "parse bytes," use an API that says only that.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
enum Mode {
    Read,
    Write,
}

impl TryFrom<u8> for Mode {
    type Error = ();

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            0 => Ok(Self::Read),
            1 => Ok(Self::Write),
            _ => Err(()),
        }
    }
}

fn main() {
    assert_eq!(Mode::try_from(1), Ok(Mode::Write));
    assert!(Mode::try_from(9).is_err());
}
```

## Worked example
```rust
#[repr(transparent)]
#[derive(Debug, PartialEq, Eq)]
struct Milliseconds(u32);

impl Milliseconds {
    fn from_le_bytes(bytes: [u8; 4]) -> Self {
        Self(u32::from_le_bytes(bytes))
    }

    fn get(self) -> u32 {
        self.0
    }
}

fn main() {
    let timeout = Milliseconds::from_le_bytes([0x10, 0, 0, 0]);
    assert_eq!(timeout.get(), 16);
}
```

This handles a byte-level representation without relying on Rust struct layout or
host endianness. Even with `repr(transparent)`, value validation belongs in the
constructor rather than in a blanket transmute.

## Common errors
`transmute` itself checks only that source and destination sizes match. If they do
not, rustc reports E0512:

```text
error[E0512]: cannot transmute between types of different sizes
```

Passing the size check does not prove validity, alignment, lifetime, aliasing, or
provenance. Treat any transmute that compiles as still requiring a full unsafe-code
proof, then look for a narrower API that removes most of that proof.

## Best practice
- ✅ Prefer typed constructors and `TryFrom` for values that need validation.
- ✅ Use byte conversion methods for numeric serialization, not layout reinterpretation.
- ✅ Use [[MaybeUninit]] for uninitialized memory rather than transmuting invalid values into existence.
- ✅ Use `repr(C)` or `repr(transparent)` only when you also validate all value-level invariants.
- ✅ Use pointer casts such as `ptr.cast::<U>()` when only the pointer type changes and no value is being reinterpreted yet.
- ✅ Keep lifetime changes out of transmutes; use APIs whose signatures tie borrowed data to a real input lifetime.

## Pitfalls
- ⚠️ Transmuting an integer into `bool`, `char`, or an enum without validating the valid range.
- ⚠️ Transmuting `&T` to `&mut T`; this is UB because shared references imply immutability.
- ⚠️ Extending lifetimes by transmuting references.
- ⚠️ Assuming two `repr(Rust)` types with the same fields have the same layout.
- ⚠️ Treating `repr(C)` as a promise that every byte pattern valid in C is valid for the corresponding Rust type.

## See also
[[Unsafe Rust]] · [[Undefined Behavior]] · [[MaybeUninit]] · [[Aliasing and Provenance]] · [[Raw Pointers]] · [[FFI with C]] · [[Safe Abstractions over Unsafe Code]] · [[SAFETY Comments]] · [[Unsafe Rust & FFI]]

## Sources
- The Rustonomicon, "Transmutes" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/transmutes.html
- The standard library, `std::mem::transmute` — https://doc.rust-lang.org/std/mem/fn.transmute.html
- The Rust Reference, "Invalid values" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html#invalid-values
