---
type: concept
title: "Drop Check"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, drop-check, dropck, lifetimes, unsafe]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[The Drop Trait]]", "[[Destructor Semantics with Drop]]", "[[Lifetimes]]", "[[PhantomData]]", "[[Variance]]", "[[Ownership]]", "[[Unsafe Rust]]", "[[Advanced Type System]]"]
sources: ["[[rustonomicon]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/nomicon/dropck.html", "https://doc.rust-lang.org/nomicon/phantom-data.html", "https://doc.rust-lang.org/reference/destructors.html"]
rust_version: "edition 2024 / 1.85+"
---

# Drop Check

Drop check is Rust's conservative lifetime analysis for values that may run destructors: generic data reachable from a value must remain valid for the value's destructor to run safely.
It is why adding `Drop` to a generic type can make otherwise plausible self-borrowing or field-borrowing code fail to compile.

## What it is
Drop check, often called dropck, protects [[The Drop Trait]] from observing expired data.
A destructor is arbitrary Rust code.
If a type stores `&'a T`, or stores a generic `T` that might itself contain references, the destructor might read through those references.
The compiler therefore rejects values whose borrowed data could be destroyed before the value that may run the destructor.
The Rustonomicon summarizes the central rule for sound generic drop as: generic arguments of a type with a destructor must strictly outlive the value being dropped.
This rule is conservative.
Some destructors do not inspect their generic data at all, but ordinary stable Rust does not let downstream code prove that fact to the borrow checker.

Drop check matters most in advanced code:
unsafe containers,
raw-pointer iterators,
FFI handle wrappers,
self-referential designs,
and marker-field designs using [[PhantomData]].
Safe application code usually notices it only as a lifetime error that appears after adding a `Drop` implementation.

## How it works
When a value goes out of scope, Rust runs drop glue for its fields and any explicit `Drop::drop` implementation.
For a generic `Drop` implementation, the compiler assumes the destructor may access generic fields or call trait methods that access them.
That includes indirect access through formatting, callbacks, or helper methods.
Because such access would be undefined behavior if the referenced data were already gone, dropck requires the referenced data to outlive the dropped value.

This is stricter than "the destructor I wrote today does not read that field."
The type signature gives the destructor the capability to access `self`, and stable Rust checks that capability conservatively.
Changing field order rarely fixes the issue because dropck is not just simulating one textual drop order.
It is checking whether destructor code could observe a value whose borrow no longer lives long enough.

For unsafe abstractions, marker fields affect this analysis.
`PhantomData<T>` says the type logically owns or may drop a `T`.
`PhantomData<&'a T>` says the type is tied to a shared borrow for `'a`.
Raw pointers alone do not express ownership or borrowing to the same degree.
Since RFC 1238, an explicit `impl<T> Drop for MyType<T>` already makes Rust consider that `T` may be used during drop; adding `PhantomData<T>` only for dropck is normally redundant when the type has its own `Drop` impl, though it can still affect [[Variance]] and auto traits.

The unstable `#[may_dangle]` attribute exists for the standard library's most specialized unsafe code.
It is not stable user-facing Rust, and it requires an unsafe promise that a destructor will not access particular dangling generic parameters except where owned drop glue demands it.
For edition 2024 / stable 1.85+ code, design around ordinary dropck instead of relying on that escape hatch.

## Example
```rust
use std::marker::PhantomData;

struct LogOnDrop<'a> {
    label: &'a str,
}

impl<'a> Drop for LogOnDrop<'a> {
    fn drop(&mut self) {
        println!("dropping {}", self.label);
    }
}

struct BorrowedHandle<'a> {
    id: u32,
    _borrow: PhantomData<&'a str>,
}

impl<'a> BorrowedHandle<'a> {
    fn new(id: u32, _owner: &'a str) -> Self {
        Self {
            id,
            _borrow: PhantomData,
        }
    }

    fn id(&self) -> u32 {
        self.id
    }
}

fn main() {
    let name = String::from("session");
    let _log = LogOnDrop { label: &name };
    let handle = BorrowedHandle::new(7, &name);

    assert_eq!(handle.id(), 7);
}
```

This example is intentionally ordinary.
Both values borrow `name`, and `name` outlives the values that mention it.
If you try to store a borrow into a value that is dropped after the borrowed owner, the compiler rejects the program before any destructor can observe freed data.

## Practical design
Prefer arranging ownership so that borrowed data naturally outlives the destructor that could inspect it.
If a destructor only needs to release a raw resource, keep borrowed views out of the dropped object or make the resource wrapper own what it needs.
If a type contains raw pointers into external data, use lifetime parameters and [[PhantomData]] to communicate the real relationship.
If a type owns initialized elements behind raw pointers, ensure the destructor drops those elements exactly once before deallocating.

Do not use `Drop` for logging or bookkeeping that unnecessarily touches borrowed generic data.
A destructor with fewer capabilities is easier for callers to satisfy.
If cleanup order matters, design explicit methods such as `close`, `finish`, or `into_inner`, and let `Drop` be the final fallback.

## Best practice
- ✅ Treat `Drop::drop(&mut self)` as arbitrary code that may observe any data reachable from `self`.
- ✅ Keep generic destructors simple and avoid reading borrowed generic data unless the type contract requires it.
- ✅ Use [[PhantomData]] to model real logical borrowing or ownership when fields are raw pointers.
- ✅ Prefer safe ownership arrangements over self-referential structures that depend on field drop order.
- ✅ Test unsafe containers with borrowed element types such as `&str` and custom types that implement `Drop`.
- ✅ Remember that adding a `Drop` impl can change which lifetime relationships the compiler accepts.
- ✅ Use `ManuallyDrop` only when you have a precise unsafe drop-order proof.

## Pitfalls
- ⚠️ Assuming a destructor that "does not currently inspect the reference" relaxes dropck; the compiler checks conservatively.
- ⚠️ Adding `#[may_dangle]` in ordinary code; it is unstable and unsafe, and it is primarily a standard-library tool.
- ⚠️ Using raw pointers to hide lifetimes from the compiler without restoring the invariant through [[PhantomData]].
- ⚠️ Relying on struct field order to justify a generic destructor that can observe borrowed fields.
- ⚠️ Adding `PhantomData<T>` by habit; when a type already has `Drop`, it may be redundant for dropck and still changes variance or auto traits.
- ⚠️ Forgetting that trait calls, callbacks, and formatting inside `drop` may indirectly access borrowed generic data.

## See also
[[Advanced Type System]]
[[The Drop Trait]]
[[Destructor Semantics with Drop]]
[[Ownership]]
[[Borrowing]]
[[Lifetimes]]
[[PhantomData]]
[[Variance]]
[[Raw Pointers]]
[[Unsafe Rust]]
[[ManuallyDrop]]
[[Type layout]]

## Sources
- The Rustonomicon, "Drop Check" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/dropck.html
- The Rustonomicon, "`PhantomData`" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/phantom-data.html
- The Rust Reference, "Destructors" — [[the-reference]],
  https://doc.rust-lang.org/reference/destructors.html
