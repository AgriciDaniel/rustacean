---
type: pattern
title: "Pin projection"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, pin, projection, async]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Pinning]]", "[[Unsafe Rust]]", "[[Safe Abstractions over Unsafe Code]]", "[[SAFETY Comments]]", "[[Futures]]", "[[Unions]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]", "[[04-async-rust]]", "pin-project docs (verify latest version)"]
source_urls: ["https://doc.rust-lang.org/std/pin/", "https://doc.rust-lang.org/std/pin/struct.Pin.html", "https://doc.rust-lang.org/book/ch17-05-traits-for-async.html", "https://doc.rust-lang.org/reference/special-types-and-traits.html#pinp", "https://docs.rs/pin-project/latest/pin_project/"]
rust_version: "edition 2024 / 1.85+"
---

# Pin projection

Pin projection is the pattern of turning `Pin<&mut Struct>` into access to its fields while preserving the promise that structurally pinned fields will not be moved.

## What it is
`Pin<Ptr>` constrains what safe code can do through a pointer once the pointee is pinned.
That matters for `!Unpin` values whose correctness depends on address stability, such as self-referential futures and hand-written low-level async state.

Projection is what happens when a method has pinned access to the whole value but needs field access:

- `Pin<&mut Outer>` to `Pin<&mut outer.pinned_field>`;
- `Pin<&mut Outer>` to `&mut outer.unpinned_field`;
- `Pin<&Outer>` to `Pin<&pinned_field>` or `&field`.

The operation is easy to write with unsafe standard-library APIs, but the proof is subtle.
Moving a field out of a pinned struct can break invariants even when the struct itself remains at the same address.
That is why production code usually uses a projection helper crate or keeps the projected unsafe block tiny and heavily documented.

Crates such as `pin-project` can generate projection code and prevent common mistakes.
If you add a projection crate, cite its docs at https://docs.rs/pin-project/latest/pin_project/ and verify the latest version before changing `Cargo.toml`.
This note describes the underlying pattern so reviews can recognize the invariant.

## How it works
Pinning is not recursive by default in a way the compiler can infer for arbitrary fields.
An API designer must decide which fields are structurally pinned.
If a field is structurally pinned, then once the outer value is pinned, that field must never be moved until it is dropped in place.
Projecting to `Pin<&mut Field>` is sound only for fields covered by that promise.

For unpinned fields, a projection method may return `&mut Field`.
That means the field can be replaced or moved out with safe operations such as `mem::replace`.
Returning `&mut Field` for a field that participates in a self-reference or other address-sensitive invariant is unsound.

The standard library exposes unsafe helpers for manual projection:

- `Pin::map_unchecked_mut` maps `Pin<&mut T>` to `Pin<&mut U>`;
- `Pin::map_unchecked` maps shared pinned references;
- `Pin::get_unchecked_mut` exposes `&mut T` when the caller upholds the pin invariants.

Those APIs are unsafe because the compiler cannot know whether the returned reference points to a structurally pinned field, whether the closure moves from the source, or whether later safe methods can move the field.

The type's `Drop` implementation is part of the contract.
Dropping a pinned value may observe pinned fields, but it must not move them out.
If cleanup needs ownership, store `Option<T>` only for fields that are not structurally pinned, or design the pinned field's own `Drop` to do the work in place.

## Example
```rust
use std::marker::PhantomPinned;
use std::pin::Pin;

struct Inner {
    polls: u32,
    _pin: PhantomPinned,
}

impl Inner {
    fn bump(self: Pin<&mut Self>) {
        // SAFETY: this method only mutates an ordinary integer field in place.
        let this = unsafe { self.get_unchecked_mut() };
        this.polls += 1;
    }
}

struct Task {
    state: Inner,
    label: String,
    _pin: PhantomPinned,
}

impl Task {
    fn new(label: String) -> Pin<Box<Self>> {
        Box::pin(Self {
            state: Inner {
                polls: 0,
                _pin: PhantomPinned,
            },
            label,
            _pin: PhantomPinned,
        })
    }

    fn project_state(self: Pin<&mut Self>) -> Pin<&mut Inner> {
        // SAFETY: `state` is structurally pinned. This method does not move from
        // `self`, and no safe method on `Task` moves `state` after pinning.
        unsafe { self.map_unchecked_mut(|task| &mut task.state) }
    }
}

fn main() {
    let mut task = Task::new(String::from("flush"));

    task.as_mut().project_state().bump();

    let task_ref = task.as_ref().get_ref();
    assert_eq!(task_ref.state.polls, 1);
    assert_eq!(task_ref.label, "flush");
}
```

This example keeps projection inside one method and states the structural pinning invariant at the unsafe block.
It does not expose a general `&mut Task`, because that would let callers move the `!Unpin` fields.

## Best practice
- ✅ Avoid manual pin projection unless you are writing low-level async, intrusive data structures, or another library that genuinely needs pin invariants.
- ✅ Prefer generated projection from a maintained crate such as `pin-project`; verify the latest version on docs.rs before adding the dependency.
- ✅ Decide and document which fields are structurally pinned.
- ✅ Keep `map_unchecked_mut` and `get_unchecked_mut` in tiny methods with precise [[SAFETY Comments]].
- ✅ Return `Pin<&mut Field>` for structurally pinned fields and `&mut Field` only for fields that may be moved after the outer value is pinned.
- ✅ Audit `Drop`, setters, `mem::replace`, `Option::take`, and public `&mut self` methods for accidental moves of pinned fields.
- ✅ Use `PhantomPinned` to opt a type out of `Unpin` when its own invariants require pinning.
- ✅ Add tests that exercise projection paths, and use [[Miri]] for unsafe pinning code where possible.

## Pitfalls
- ⚠️ Treating `Pin<&mut Outer>` as permission to call `&mut outer.field` freely can move a `!Unpin` field.
- ⚠️ Returning `&mut` to a structurally pinned field makes safe code capable of replacing it.
- ⚠️ Implementing `Unpin` manually to silence a compiler error can invalidate the whole pinning design.
- ⚠️ Moving a pinned field in `Drop` is still a move; cleanup must happen in place.
- ⚠️ Projecting through enums or conditional fields requires extra care because the active variant can change.
- ⚠️ `Pin<Box<T>>` pins the `T`, not the `Box` handle; moving the handle is fine, moving out of the box is not.
- ⚠️ Projection helpers remove boilerplate, not the need to understand the generated safety contract.

## See also
[[Pinning]] · [[Futures]] · [[Unsafe Rust]] · [[Safe Abstractions over Unsafe Code]] ·
[[SAFETY Comments]] · [[Undefined Behavior]] · [[Aliasing and Provenance]] · [[Miri]] ·
[[Box]] · [[The Drop Trait]] · [[Unsafe Rust & FFI]]

## Sources
- Rust standard library, `std::pin` module — https://doc.rust-lang.org/std/pin/
- Rust standard library, `Pin` — https://doc.rust-lang.org/std/pin/struct.Pin.html
- The Rust Programming Language, ch. 17.5 "The Pin Type and the Unpin Trait" — [[the-book]],
  https://doc.rust-lang.org/book/ch17-05-traits-for-async.html
- The Rust Reference, "`Pin<P>`" — [[the-reference]],
  https://doc.rust-lang.org/reference/special-types-and-traits.html#pinp
- The Rustonomicon, unsafe-code background — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/
- `pin-project` crate docs (verify latest version before depending on it) —
  https://docs.rs/pin-project/latest/pin_project/
