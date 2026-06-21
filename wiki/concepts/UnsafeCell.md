---
type: concept
title: "UnsafeCell"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafecell, interior-mutability, unsafe]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Static Items]]", "[[Variables and Mutability]]", "[[Borrowing]]", "[[Ownership]]", "[[Concurrency]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/reference/interior-mutability.html", "https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html", "https://doc.rust-lang.org/std/cell/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# UnsafeCell

`UnsafeCell<T>` is the only sound primitive for interior mutability; all of `Cell`, `RefCell`, `Mutex` build on it.

## What it is
`UnsafeCell<T>` is the standard library primitive that permits mutation through a shared reference.
It is the explicit opt-out from Rust's usual rule that data reachable through `&T` is not mutated.

Most Rust code should use safe wrappers such as `Cell<T>`, `RefCell<T>`, `OnceCell<T>`, `Mutex<T>`,
`RwLock<T>`, atomics, `OnceLock<T>`, or `LazyLock<T>`. `UnsafeCell` is for implementing those kinds of
abstractions, not for ordinary application state.

The name is accurate: it gives you a raw pointer with `get()`, but it does not enforce aliasing,
thread-safety, or borrowing rules for you.

## How it works
The Reference says `UnsafeCell<T>` is the only allowed way to disable the immutability guarantee of
shared references. If a type has interior mutability, it does so by containing an `UnsafeCell`.

`UnsafeCell::get` returns `*mut T`. Dereferencing that pointer is unsafe because the caller must prove
that access does not violate Rust's aliasing model. Shared aliasing plus mutation must be controlled
by some other mechanism: runtime borrow flags, atomics, locks, single-threaded ownership, or a more
specialized invariant.

`UnsafeCell` does not make `&mut` aliasing permissive. Multiple live `&mut UnsafeCell<T>` aliases are
still undefined behavior, just like multiple live `&mut T` aliases.

## Example
Use safe wrappers first:

```rust
use std::cell::Cell;

struct Counter {
    value: Cell<u32>,
}

impl Counter {
    fn increment(&self) {
        self.value.set(self.value.get() + 1);
    }

    fn get(&self) -> u32 {
        self.value.get()
    }
}

fn main() {
    let counter = Counter { value: Cell::new(0) };
    counter.increment();
    assert_eq!(counter.get(), 1);
}
```

## Edge cases
A tiny `UnsafeCell` wrapper can be sound only if the API prevents invalid aliasing. This example is
single-threaded and exposes only copy-in/copy-out access:

```rust
use std::cell::UnsafeCell;

struct Slot<T> {
    value: UnsafeCell<T>,
}

impl<T: Copy> Slot<T> {
    fn new(value: T) -> Self {
        Self { value: UnsafeCell::new(value) }
    }

    fn get(&self) -> T {
        unsafe { *self.value.get() }
    }

    fn set(&self, value: T) {
        unsafe { *self.value.get() = value; }
    }
}

fn main() {
    let slot = Slot::new(1);
    slot.set(2);
    assert_eq!(slot.get(), 2);
}
```

This deliberately does not implement `Sync`; sharing it across threads would require additional
synchronization.

## Common errors
Putting `UnsafeCell` in a `static` fails because it is not `Sync`:

```rust
use std::cell::UnsafeCell;

// static VALUE: UnsafeCell<u32> = UnsafeCell::new(0);
```

Typical diagnostic:

```text
error[E0277]: `UnsafeCell<u32>` cannot be shared between threads safely
```

Fix it with a thread-safe primitive:

```rust
use std::sync::atomic::{AtomicU32, Ordering};

static VALUE: AtomicU32 = AtomicU32::new(0);

fn main() {
    VALUE.store(1, Ordering::Relaxed);
    assert_eq!(VALUE.load(Ordering::Relaxed), 1);
}
```

## Best practice
- ✅ Use safe interior-mutability wrappers before writing `UnsafeCell` yourself.
- ✅ Make the unsafe invariant local to a small type with a safe public API.
- ✅ Avoid implementing `Sync` unless you have real synchronization.
- ✅ Write comments on each unsafe block explaining the aliasing proof.
- ✅ Prefer inherited mutability (`&mut T`) when unique access is already available.

## Pitfalls
- ⚠️ `UnsafeCell` removes one compiler guarantee; it does not remove all aliasing rules.
- ⚠️ Raw pointers from `get()` are not automatically valid to dereference.
- ⚠️ Do not use `UnsafeCell` to sidestep borrow-checker errors in ordinary code.
- ⚠️ Interior mutability can make APIs harder to reason about, especially across callbacks.
- ⚠️ In globals, combine interior mutability with thread-safe synchronization; see [[Static Items]].

## See also
[[Interior Mutability]] · [[Static Items]] · [[Variables and Mutability]] · [[Borrowing]] · [[Ownership]] · [[Concurrency]] · [[Smart Pointers]] · [[The Drop Trait]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Reference, "Interior mutability" — [[the-reference]], https://doc.rust-lang.org/reference/interior-mutability.html
- Standard library, `std::cell::UnsafeCell` — https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html
- Standard library, `std::cell` module — https://doc.rust-lang.org/std/cell/index.html
