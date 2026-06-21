---
type: concept
title: "Cell"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cell, interior-mutability, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Interior Mutability]]", "[[RefCell]]", "[[Copy and Clone]]", "[[Ownership]]", "[[Borrowing]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/cell/struct.Cell.html", "https://doc.rust-lang.org/std/cell/index.html", "https://doc.rust-lang.org/book/ch15-05-interior-mutability.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cell

`Cell<T>` is an interior-mutability container for value replacement: it lets shared references get, set, take, or replace the inner value without handing out references to it.

## What it is
`Cell<T>` is the simplest standard-library interior-mutability type.
It is best for small values, flags, counters, and options where mutation can be expressed as copying, taking, or replacing the whole value.

Unlike [[RefCell]], `Cell<T>` does not track borrows at runtime and does not return `Ref` guards.
Its safety comes from not exposing normal references to the inner `T`.

## How it works
For `T: Copy`, `get()` copies the value out.
For any `T`, `set(value)` replaces the inner value and drops the old one, `replace(value)` returns the old value, and `take()` replaces the value with `Default::default()`.
`into_inner()` consumes the `Cell<T>` and returns the inner value without replacement.
These APIs are value-oriented: the caller never receives a long-lived borrow into the cell.

Because no `&T` or `&mut T` to the inner value is exposed by the core API, there can be no aliasing violation through those references.
This makes `Cell<T>` cheap and predictable for local, single-threaded interior state.
It has no borrow counter and no panic path for overlapping borrows, unlike [[RefCell]].

`Cell<T>` is not a synchronization primitive.
For cross-thread shared mutation, use [[Atomics]] for supported scalar operations or [[Shared State with Mutex]] for general data.

## Example
```rust
use std::cell::Cell;

struct ParserState {
    line: Cell<usize>,
    had_error: Cell<bool>,
}

impl ParserState {
    fn advance(&self) {
        self.line.set(self.line.get() + 1);
    }

    fn mark_error(&self) {
        self.had_error.set(true);
    }
}

fn main() {
    let state = ParserState {
        line: Cell::new(1),
        had_error: Cell::new(false),
    };

    state.advance();
    state.mark_error();
    assert_eq!(state.line.get(), 2);
    assert!(state.had_error.get());
}
```

## Worked example: taking a non-`Copy` value
```rust
use std::cell::Cell;

struct OneShot {
    message: Cell<Option<String>>,
}

impl OneShot {
    fn take(&self) -> Option<String> {
        self.message.take()
    }
}

fn main() {
    let slot = OneShot {
        message: Cell::new(Some(String::from("ready"))),
    };

    assert_eq!(slot.take().as_deref(), Some("ready"));
    assert_eq!(slot.take(), None);
}
```

`Cell<Option<T>>` is a common way to move a value out through `&self` exactly once without exposing an interior reference.

## Common errors
Calling `get()` on a non-`Copy` cell produces a trait-bound error because `get` must copy the value out:

```text
error[E0599]: the method `get` exists for struct `Cell<String>`, but its trait bounds were not satisfied
```

Use `replace`, `take`, or `into_inner` for non-`Copy` values, or use [[RefCell]] if callers need borrowed access to the value in place.

## Best practice
- ✅ Use `Cell<T>` for `Copy` counters, booleans, enum states, and small handles mutated through `&self`.
- ✅ Use `replace` or `take` when `T` is not `Copy` and whole-value movement is the right operation.
- ✅ Prefer [[RefCell]] when callers need temporary borrowed access to a non-`Copy` inner value.
- ✅ Keep `Cell` fields private so methods preserve the type's invariants.
- ✅ Use `Cell<Option<T>>` for one-shot initialization handoff, delayed extraction, or "take once" fields in single-threaded code.
- ✅ Prefer atomics over `Cell` for counters that may be touched from multiple threads.

## Pitfalls
- ⚠️ `Cell<T>` cannot give you `&T` or `&mut T` to arbitrary inner data.
- ⚠️ Replacing a large value repeatedly can be more expensive than borrowing it mutably through [[RefCell]].
- ⚠️ `Cell<T>` is for single-threaded interior mutability; do not use it as a thread-safe counter.
- ⚠️ Widespread public `Cell` fields can make mutation paths hard to audit.
- ⚠️ `Cell` makes every write a whole-value operation; for collections, that often means moving or replacing the whole collection instead of editing one element.

## See also
[[Interior Mutability]] · [[RefCell]] · [[Copy and Clone]] · [[Ownership]] · [[Borrowing]] · [[Atomics]] · [[Shared State with Mutex]] · [[Smart Pointers & Interior Mutability]]

## Sources
- Standard library, `std::cell::Cell` - [[std]],
  https://doc.rust-lang.org/std/cell/struct.Cell.html
- Standard library, `std::cell` module - [[std]],
  https://doc.rust-lang.org/std/cell/index.html
