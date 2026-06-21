---
type: concept
title: "PhantomData"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, phantomdata, marker-types, variance, unsafe]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Variance]]", "[[Zero-Sized Types]]", "[[Drop Check]]", "[[Send and Sync]]", "[[Phantom Type Parameters]]", "[[Unsafe Rust]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/special-types-and-traits.html#phantomdatat", "https://doc.rust-lang.org/nomicon/phantom-data.html"]
rust_version: "edition 2024 / 1.85+"
---

# PhantomData

`PhantomData<T>` is a zero-sized marker field that tells Rust a type logically acts as though it contains, borrows, or mentions `T`.
It matters for variance, drop checking, auto traits, and rejecting unused generic parameters.

## What it is
`std::marker::PhantomData<T>` occupies no storage and has minimum alignment.
Its purpose is type-system communication, not runtime data.
You use it when a struct has a generic type or lifetime parameter that is not present in a real field but is still part of the abstraction.
Common examples include raw-pointer iterators, FFI handles, arena IDs, typestate markers, and ownership wrappers.
The Reference says `PhantomData<T>` is considered to own a `T` for variance, drop check, and auto traits.
The Nomicon shows that different phantom shapes communicate different relationships.
`PhantomData<&'a T>` says the type is tied to a borrow of `T` for `'a`.
`PhantomData<*const T>` affects variance without implying thread-safety the same way a reference would.

## How it works
Rust forbids unused lifetime parameters on structs because they would otherwise be unbounded.
A phantom field gives the compiler a real field position to analyze.
Field positions determine [[Variance]] for user-defined structs.
They also influence whether the type is automatically `Send`, `Sync`, `Unpin`, and subject to drop-check constraints.
Because `PhantomData` has no runtime payload, it is usually named `_marker` or `_phantom`.
The exact phantom type is a design choice:
`PhantomData<T>` models ownership of `T`.
`PhantomData<&'a T>` models a shared borrow and is covariant in `'a` and `T`.
`PhantomData<&'a mut T>` models an exclusive borrow and is invariant in `T`.
`PhantomData<fn(T)>` can model contravariance without ownership.
Do not choose the shape by habit; choose the relationship your abstraction actually has.

## Example
```rust
use std::marker::PhantomData;

#[derive(Copy, Clone)]
struct SliceCursor<'a, T> {
    ptr: *const T,
    len: usize,
    _marker: PhantomData<&'a T>,
}

impl<'a, T> SliceCursor<'a, T> {
    fn new(slice: &'a [T]) -> Self {
        Self {
            ptr: slice.as_ptr(),
            len: slice.len(),
            _marker: PhantomData,
        }
    }

    fn len(&self) -> usize {
        self.len
    }
}

fn main() {
    let values = [10, 20, 30];
    let cursor = SliceCursor::new(&values);
    assert_eq!(cursor.len(), 3);
    assert_eq!(cursor.ptr, values.as_ptr());
}
```

## Edge cases
```rust
use std::marker::PhantomData;

struct Id<T> {
    raw: u64,
    _kind: PhantomData<fn() -> T>,
}

struct User;
struct Order;

fn main() {
    let user_id = Id::<User> { raw: 7, _kind: PhantomData };
    let order_id = Id::<Order> { raw: 7, _kind: PhantomData };
    assert_eq!(user_id.raw, order_id.raw);
}
```

## Best practice
- ✅ Add `PhantomData` only when the generic parameter is logically part of the type but absent from stored fields.
- ✅ Pick the phantom shape that matches ownership, borrowing, variance, and auto-trait intent.
- ✅ Use `_marker: PhantomData<...>` so the field name communicates intentional non-use.
- ✅ Prefer safe references in phantom shapes when your abstraction logically borrows.
- ✅ Review `Send` and `Sync` effects whenever a phantom field appears in unsafe code.
- ✅ Pair raw-pointer fields with comments explaining what invariant the phantom field represents.

## Pitfalls
- ⚠️ Using `PhantomData<T>` by default; it models ownership and may overconstrain drop checking.
- ⚠️ Using `PhantomData<*const T>` and accidentally making a type `!Send` or `!Sync` in contexts where that was not intended.
- ⚠️ Treating `PhantomData` as a substitute for real lifetime validation; unsafe constructors must still uphold invariants.
- ⚠️ Forgetting that `PhantomData` affects [[Variance]], which can make unsafe APIs too permissive or too restrictive.
- ⚠️ Adding phantom fields to silence compiler errors without understanding what relationship they encode.

## See also
[[Advanced Type System]]
[[Variance]]
[[Zero-Sized Types]]
[[Phantom Type Parameters]]
[[Unsafe Rust]]
[[Send and Sync]]
[[The Drop Trait]]
[[Destructor Semantics with Drop]]
[[Raw Pointers]]
[[Type-State Pattern]]

## Sources
- The Rust Reference, "`PhantomData<T>`" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html#phantomdatat
- The Rustonomicon, "`PhantomData`" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/phantom-data.html
