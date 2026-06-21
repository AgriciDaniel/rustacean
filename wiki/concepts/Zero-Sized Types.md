---
type: concept
title: "Zero-Sized Types"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, zst, layout, marker-types, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Unit-Like Structs]]", "[[The Never Type]]", "[[PhantomData]]", "[[Type-State Pattern]]", "[[Arrays]]", "[[Type layout]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/type-layout.html", "https://doc.rust-lang.org/nomicon/exotic-sizes.html#zero-sized-types-zsts"]
rust_version: "edition 2024 / 1.85+"
---

# Zero-Sized Types

A zero-sized type has values that occupy no storage, but it can still carry strong type-level meaning.
Use ZSTs for markers, tokens, typestate, and compile-time distinctions, while being careful in unsafe layout and allocation code.

## What it is
Rust permits types whose size is zero.
Examples include `()`, unit-like structs, structs whose fields are all zero-sized, and arrays of length zero.
A ZST can have values even though storing the value takes no bytes.
This is different from an empty enum such as `enum Never {}`, which has no values at all.
ZSTs are common in generic code because they let a type carry behavior or identity without runtime storage.
`HashSet<T>` can be understood as a map from `T` to `()`.
Marker types in typestate APIs are often ZSTs.
`PhantomData<T>` is also a ZST, but it has special type-system meaning.

## How it works
`std::mem::size_of::<T>()` returns `0` for a ZST.
References to ZSTs must still be non-null and properly aligned.
Rust may give ZST fields the same address as other fields in a struct.
Pointer arithmetic over ZSTs is a classic unsafe-code trap because offsetting by elements of size zero does not move the address.
Allocators usually require non-zero allocation sizes, so unsafe containers must special-case ZST element types.
Safe Rust mostly hides these issues.
The compiler can optimize many operations involving ZST values into no-ops.
The type identity still matters: `MarkerA` and `MarkerB` can both be zero-sized but remain distinct types.

## Example
```rust
use std::mem::size_of;

struct ReadOnly;
struct Writable;

struct File<State> {
    name: String,
    state: State,
}

impl File<ReadOnly> {
    fn open_read(name: impl Into<String>) -> Self {
        Self { name: name.into(), state: ReadOnly }
    }
}

impl File<Writable> {
    fn open_write(name: impl Into<String>) -> Self {
        Self { name: name.into(), state: Writable }
    }
}

fn main() {
    assert_eq!(size_of::<ReadOnly>(), 0);
    assert_eq!(size_of::<Writable>(), 0);

    let read = File::<ReadOnly>::open_read("config.toml");
    let write = File::<Writable>::open_write("output.log");

    assert_eq!(read.name, "config.toml");
    assert_eq!(write.name, "output.log");
}
```

## Edge cases
```rust
use std::mem::size_of;

struct Nothing;
struct AlsoNothing {
    unit: (),
    empty: [u8; 0],
    marker: Nothing,
}

fn main() {
    assert_eq!(size_of::<()>(), 0);
    assert_eq!(size_of::<Nothing>(), 0);
    assert_eq!(size_of::<AlsoNothing>(), 0);
}
```

## Best practice
- ✅ Use ZSTs for marker states and capabilities when no runtime data is needed.
- ✅ Prefer explicit unit-like marker structs over boolean flags when the state should be part of the type.
- ✅ Keep ZSTs private when they are implementation details of a typestate API.
- ✅ Use `PhantomData` rather than an ordinary ZST when you need to mention a generic type or lifetime.
- ✅ Special-case ZSTs in unsafe allocation, pointer iteration, and raw collection code.
- ✅ Test `size_of::<T>() == 0` assumptions in examples only as documentation, not as a substitute for safety invariants.

## Pitfalls
- ⚠️ Assuming two fields of ZST type have distinct addresses.
- ⚠️ Passing null references to ZSTs; references still have validity requirements.
- ⚠️ Writing pointer iteration that relies on `ptr.add(1)` moving for all `T`.
- ⚠️ Confusing zero-sized types with uninhabited types such as [[The Never Type]].
- ⚠️ Adding public marker ZSTs without thinking through semver and construction privacy.

## See also
[[Advanced Type System]]
[[Unit-Like Structs]]
[[The Never Type]]
[[PhantomData]]
[[Phantom Type Parameters]]
[[Type-State Pattern]]
[[Type-State State Machines]]
[[Arrays]]
[[Memory-Mapped I/O]]
[[Unsafe Rust]]

## Sources
- The Rust Reference, "Type layout" — [[the-reference]],
  https://doc.rust-lang.org/reference/type-layout.html
- The Rustonomicon, "Zero Sized Types" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/exotic-sizes.html#zero-sized-types-zsts
