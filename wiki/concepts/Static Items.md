---
type: concept
title: "Static Items"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, static, globals, interior-mutability]
domain: "Basic Concepts & Syntax"
difficulty: intermediate
related: ["[[Constants]]", "[[UnsafeCell]]", "[[Variables and Mutability]]", "[[Ownership]]", "[[Borrowing]]", "[[Build-Time Code Execution]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-reference]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/static-items.html", "https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html"]
rust_version: "edition 2024 / 1.85+"
---

# Static Items

A `static` binds a value to a fixed memory address that lives for the whole program (`'static`). Immutable statics are safe; `static mut` is discouraged in favor of `&raw` and interior mutability.

## What it is
A static item is a named allocation owned by the program rather than by a stack frame or heap owner.
Every reference or raw pointer to that static refers to the same allocation for the duration of the
program.

Use immutable `static` for address-stable global data, such as process-wide tables or atomic counters.
Use [[Constants]] when you only need a named compile-time value and not one shared storage location.

The type of a static must be `Sync` because shared access to a global can happen from multiple
threads. Mutation through safe APIs usually means using an interior-mutability type such as atomics,
`Mutex`, `OnceLock`, or a custom abstraction based on [[UnsafeCell]].

## How it works
A static initializer is a constant expression evaluated at compile time. Unlike a `const`, a non-zero
sized static represents one allocation; raw pointers and references to it have a stable identity.

Static items have the `'static` lifetime, but they do not run destructors at program shutdown. This is
intentional: code should not rely on global drop order for correctness. If a resource must be released
deterministically, own it in an ordinary value and let [[Ownership]] and [[The Drop Trait]] manage it.

In edition 2024, the `static_mut_refs` lint is `deny` by default. Creating `&T` or `&mut T` directly
to a `static mut` is rejected because forming such a reference can already violate aliasing rules.
If unavoidable FFI code needs a pointer, use `&raw const` or `&raw mut` and keep the unsafe region
small.

## Example
```rust
use std::sync::atomic::{AtomicUsize, Ordering};

static REQUESTS: AtomicUsize = AtomicUsize::new(0);
static GREETING: &str = "hello";

fn next_request_id() -> usize {
    REQUESTS.fetch_add(1, Ordering::Relaxed) + 1
}

fn main() {
    assert_eq!(GREETING, "hello");
    assert_eq!(next_request_id(), 1);
    assert_eq!(next_request_id(), 2);
}
```

## Edge cases
Statics inside generic scopes are not instantiated once per type parameter. A static declared inside
a generic function or trait default still denotes one item for that code location, not a separate
global per monomorphization.

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

fn count_for<T>() -> usize {
    static CALLS: AtomicUsize = AtomicUsize::new(0);
    let _ = std::any::type_name::<T>();
    CALLS.fetch_add(1, Ordering::Relaxed) + 1
}

fn main() {
    assert_eq!(count_for::<u8>(), 1);
    assert_eq!(count_for::<String>(), 2);
}
```

## Common errors
Creating a reference to `static mut` in edition 2024 fails before the unsafe block can make it sound:

```rust
static mut COUNT: u32 = 0;

fn main() {
    // let r = unsafe { &mut COUNT };
}
```

Typical diagnostic:

```text
error: creating a mutable reference to mutable static is discouraged
note: `#[deny(static_mut_refs)]` on by default
```

Fix it by replacing the global with an atomic, lock, or one-time cell when possible. For FFI pointer
handoff, use a raw borrow and document the global safety invariant:

```rust
static mut COUNT: u32 = 0;

fn pointer_for_ffi() -> *mut u32 {
    &raw mut COUNT
}
```

## Best practice
- ✅ Prefer `const` for named values and `static` only when one address-stable allocation matters.
- ✅ Use `Atomic*`, `Mutex`, `RwLock`, `OnceLock`, or `LazyLock` instead of `static mut`.
- ✅ Keep statics private and expose functions that preserve invariants.
- ✅ Use explicit memory orderings on atomics and document why the weakest chosen ordering is enough.
- ✅ Treat every global as API surface: it affects tests, reentrancy, and concurrency.

## Pitfalls
- ⚠️ Do not rely on static destructors; statics are not dropped at program end.
- ⚠️ Do not use `static mut` as a shortcut around [[Borrowing]]; it shifts proof obligations to humans.
- ⚠️ Do not put non-`Sync` interior mutability types such as `RefCell<T>` in shared statics.
- ⚠️ Do not confuse `&'static T` with "allocated in a static item"; leaked, promoted, and string data can also have `'static` lifetimes.
- ⚠️ Avoid global mutable state in tests unless it can be reset or isolated.

## See also
[[Constants]] · [[Variables and Mutability]] · [[UnsafeCell]] · [[Interior Mutability]] · [[Ownership]] · [[Borrowing]] · [[The Drop Trait]] · [[Concurrency]] · [[Build-Time Code Execution]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Reference, "Static items" — [[the-reference]], https://doc.rust-lang.org/reference/items/static-items.html
- The Edition Guide, "Disallow references to static mut" — [[edition-guide]], https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html
