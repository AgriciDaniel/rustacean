---
type: concept
title: "Destructor Semantics with Drop"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, drop, destructors, raii]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[The Drop Trait]]", "[[Ownership]]", "[[RAII and Drop Guards]]", "[[Panic Unwinding and Abort]]"]
sources: ["[[std]]", "[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/std/ops/trait.Drop.html", "https://doc.rust-lang.org/book/ch15-03-drop.html", "https://doc.rust-lang.org/reference/destructors.html"]
rust_version: "edition 2024 / 1.85+"
---

# Destructor Semantics with Drop

`Drop` lets a type run cleanup code when its owner goes out of scope, forming Rust's RAII foundation for files, locks, memory, and other resources.

## What it is
`Drop` has one method: `fn drop(&mut self)`.
The compiler calls it automatically when a value is dropped.
Users do not call `drop` directly.
To drop a value early, call the free function `std::mem::drop(value)`.

The existing note [[The Drop Trait]] covers the basic concept.
This note focuses on the std trait contract and how it affects API design.

`Drop` is not just about heap memory.
It closes file descriptors.
It releases locks.
It decrements reference counts.
It returns borrowed resources to pools.
It is the mechanism behind many guard types.

## How it works
When a value goes out of scope, Rust runs its destructor.
For a struct, fields are then dropped after the custom `drop` method runs.
For local variables, drop order is deterministic and generally reverse order of declaration.

The `drop` method receives `&mut self`, not `self`.
That means it cannot move fields out directly without replacement techniques.
This prevents partially moved values from being accidentally destroyed twice.

Types that implement `Drop` cannot implement `Copy`.
Implicit copying would make destructor ownership ambiguous.
If a type owns a resource, moving it transfers responsibility for later cleanup.

Destructors run during unwinding if the panic strategy unwinds.
They may not run on abort, process termination, reference cycles, or intentional leaks.
Do not rely on destructors for externally critical protocol completion unless the process boundary is handled too.

## Example
```rust
use std::cell::Cell;
use std::rc::Rc;

#[derive(Clone)]
struct Counter {
    drops: Rc<Cell<u32>>,
}

struct Guard {
    name: &'static str,
    counter: Counter,
}

impl Drop for Guard {
    fn drop(&mut self) {
        let next = self.counter.drops.get() + 1;
        self.counter.drops.set(next);
        println!("dropped {}", self.name);
    }
}

fn main() {
    let counter = Counter { drops: Rc::new(Cell::new(0)) };
    {
        let _a = Guard { name: "a", counter: counter.clone() };
        let _b = Guard { name: "b", counter: counter.clone() };
    }
    assert_eq!(counter.drops.get(), 2);
}
```

## Best practice
- ✅ Use `Drop` to release resources owned by the type.
- ✅ Keep destructors small, deterministic, and panic-free.
- ✅ Use guard types to tie acquisition and release to lexical scope.
- ✅ Call `std::mem::drop(value)` when a lock or resource must be released before the end of scope.
- ✅ Document cleanup behavior when it matters to callers.

## Pitfalls
- ⚠️ Do not call `value.drop()` directly; use `std::mem::drop(value)` for early drop.
- ⚠️ Do not panic from destructors, especially during unwinding.
- ⚠️ Do not assume destructors run on process abort or intentional leaks.
- ⚠️ Do not expect `Copy` on types that own resources or implement `Drop`.

## See also
[[std: Core Trait Catalog]] · [[The Drop Trait]] · [[Ownership]] · [[Move Semantics]] · [[RAII and Drop Guards]] · [[Panic Unwinding and Abort]] · [[Smart Pointers]] · [[Box]] · [[Rc]] · [[Arc]]

## Sources
- Rust standard library, `std::ops::Drop` - [[std]], https://doc.rust-lang.org/std/ops/trait.Drop.html
- The Rust Programming Language, `Drop` cleanup - [[the-book]], https://doc.rust-lang.org/book/ch15-03-drop.html
- The Rust Reference, destructors - [[the-reference]], https://doc.rust-lang.org/reference/destructors.html
