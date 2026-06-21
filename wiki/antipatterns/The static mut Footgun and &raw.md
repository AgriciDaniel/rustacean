---
type: antipattern
title: "The static mut Footgun and &raw"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, static-mut, antipattern]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Raw Pointers]]", "[[Undefined Behavior]]", "[[Aliasing and Provenance]]", "[[unsafe extern Blocks]]", "[[Unsynchronized static mut in Interrupts]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#accessing-or-modifying-a-mutable-static-variable", "https://doc.rust-lang.org/reference/items/static-items.html#mutable-statics", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#raw-borrow-operators"]
rust_version: "edition 2024 / 1.85+"
---

# The static mut Footgun and &raw

The `static mut` footgun is treating global mutable memory like an ordinary variable; the correct alternative is usually atomics, locks, or at least raw-pointer access with `&raw` and a documented synchronization contract.

## The mistake
`static mut` creates globally reachable mutable state. Reading or writing it is
unsafe because concurrent access can produce data races, and references to it can
create aliasing promises the program cannot globally uphold.

In edition 2024 practice, the `static_mut_refs` lint denies creating references to
mutable statics by default. Even implicit references, such as formatting a `static
mut` directly in `println!`, can be a problem. Use `&raw const` or `&raw mut` when
you truly need a pointer to a mutable static.

## Why it happens
Global mutable state feels convenient for counters, caches, callbacks, and embedded
registers. But a `static mut` can be accessed from anywhere, by any thread or
interrupt context, and Rust cannot prove exclusive access.

Creating `&T` or `&mut T` to a mutable static is stronger than many authors intend:
the reference asserts validity, alignment, and aliasing guarantees for its lifetime.
Raw pointers make the unsafety visible without creating those reference guarantees.

Most application code should use `Atomic*`, `Mutex`, `OnceLock`, or another safe
concurrency primitive instead.

`&raw` is not a synchronization primitive. It is a way to avoid creating a reference
when a reference would make invalid aliasing claims. The program still needs a
separate proof that reads and writes are serialized, atomic, interrupt-free, or
otherwise protected according to the execution environment.

## Example
```rust
use std::sync::atomic::{AtomicU32, Ordering};

static COUNTER: AtomicU32 = AtomicU32::new(0);

fn bump() -> u32 {
    COUNTER.fetch_add(1, Ordering::Relaxed)
}

fn main() {
    assert_eq!(bump(), 0);
    assert_eq!(bump(), 1);
}
```

## Worked example
```rust
use std::sync::Mutex;

static LOG: Mutex<Vec<&'static str>> = Mutex::new(Vec::new());

fn record(message: &'static str) {
    LOG.lock().unwrap().push(message);
}

fn snapshot() -> Vec<&'static str> {
    LOG.lock().unwrap().clone()
}

fn main() {
    record("boot");
    record("ready");
    assert_eq!(snapshot(), vec!["boot", "ready"]);
}
```

Since `Mutex::new` is const, ordinary global state rarely needs `static mut`.
The lock carries the synchronization contract in the type system and makes access
safe for callers.

## Common errors
Edition-2024 code rejects references to mutable statics by default:

```text
error: creating a shared reference to mutable static is discouraged
```

This can be triggered implicitly by formatting or method calls. The fix is usually
to replace the global with `Atomic*`, `Mutex`, `RwLock`, or `OnceLock`. If a raw
pointer is truly required, use `&raw const` or `&raw mut` and document the separate
synchronization proof.

## Best practice
- ✅ Prefer atomics for numeric global counters and `Mutex`/`RwLock`/`OnceLock` for structured global state.
- ✅ If `static mut` is unavoidable, hide it behind a tiny API with a precise synchronization contract.
- ✅ Use `&raw const STATIC` or `&raw mut STATIC` instead of creating references to mutable statics.
- ✅ Treat extern mutable statics as FFI hazards and wrap access in [[FFI Wrapper Types]].
- ✅ In embedded or interrupt code, name the critical section or interrupt-masking rule that protects every access.
- ✅ Keep mutable global state typed around its synchronization primitive instead of storing a primitive beside a separate lock by convention.

## Pitfalls
- ⚠️ Using `static mut` in multi-threaded code without synchronization; data races are UB.
- ⚠️ Formatting or borrowing a `static mut` directly, creating an implicit reference.
- ⚠️ Marking a `static mut` helper safe when callers must guarantee single-threaded or interrupt-free access.
- ⚠️ Assuming raw pointers solve synchronization; they only avoid creating references.
- ⚠️ Splitting the lock and the mutable static into separate globals, which lets future code access the data without taking the lock.

## See also
[[Unsafe Rust]] · [[Raw Pointers]] · [[Undefined Behavior]] · [[Aliasing and Provenance]] · [[unsafe extern Blocks]] · [[Unsynchronized static mut in Interrupts]] · [[Atomics]] · [[FFI Wrapper Types]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Accessing or Modifying a Mutable Static Variable" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#accessing-or-modifying-a-mutable-static-variable
- The Rust Reference, "Mutable statics" — [[the-reference]], https://doc.rust-lang.org/reference/items/static-items.html#mutable-statics
- The Rust Reference, "Raw borrow operators" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/operator-expr.html#raw-borrow-operators
