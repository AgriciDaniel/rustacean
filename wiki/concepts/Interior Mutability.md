---
type: concept
title: "Interior Mutability"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, interior-mutability, borrowing, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[RefCell]]", "[[Cell]]", "[[Rc]]", "[[Ownership]]", "[[Borrowing]]", "[[Shared State with Mutex]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-05-interior-mutability.html", "https://doc.rust-lang.org/std/cell/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Interior Mutability

Interior mutability is the Rust pattern where a type safely permits mutation through a shared reference by moving borrow checking into a specialized abstraction.

## What it is
Ordinary Rust mutation requires unique access through `&mut T`.
Interior mutability types make selected mutation possible through `&T`, while preserving safety through runtime checks, copy-in/copy-out APIs, atomics, locks, or other controlled mechanisms.

The Book introduces the pattern through [[RefCell]].
The standard library also provides [[Cell]], atomics, `Mutex<T>`, and `RwLock<T>` as different interior-mutability tools with different guarantees.

## How it works
Interior mutability is implemented with `UnsafeCell<T>` inside safe abstractions.
The public type is responsible for enforcing the rules that the compiler cannot enforce directly.
`UnsafeCell<T>` is the core marker that tells the compiler "this memory may be mutated through a shared reference."
Using it directly is low-level; most code should use the standard abstractions whose APIs preserve Rust's aliasing rules.

That means each abstraction has a specific contract.
`Cell<T>` avoids references to the inner value and works by copying, replacing, or moving values.
`RefCell<T>` hands out borrow guards and panics on invalid borrow overlap.
`Mutex<T>` blocks or fails when another thread holds the lock.
Atomics provide hardware-supported operations for specific scalar types.
The choice is not just about "can I mutate through `&self`?"
It is also about whether conflicts are impossible by construction, checked dynamically, synchronized between threads, or expressed as atomic operations.

Use the narrowest abstraction that matches the access pattern.
Interior mutability should make an invariant expressible, not make every part of the program able to mutate everything.

## Example
```rust
use std::cell::Cell;

struct HitCounter {
    hits: Cell<u64>,
}

impl HitCounter {
    fn hit(&self) {
        self.hits.set(self.hits.get() + 1);
    }

    fn hits(&self) -> u64 {
        self.hits.get()
    }
}

fn main() {
    let counter = HitCounter { hits: Cell::new(0) };
    counter.hit();
    counter.hit();
    assert_eq!(counter.hits(), 2);
}
```

## Worked example: a test double behind `&self`
```rust
use std::cell::RefCell;

trait Sink {
    fn send(&self, line: &str);
}

struct RecordingSink {
    lines: RefCell<Vec<String>>,
}

impl RecordingSink {
    fn new() -> Self {
        Self {
            lines: RefCell::new(Vec::new()),
        }
    }

    fn lines(&self) -> Vec<String> {
        self.lines.borrow().clone()
    }
}

impl Sink for RecordingSink {
    fn send(&self, line: &str) {
        self.lines.borrow_mut().push(line.to_owned());
    }
}

fn main() {
    let sink = RecordingSink::new();
    sink.send("warn");
    assert_eq!(sink.lines(), vec![String::from("warn")]);
}
```

## Common errors
Without interior mutability, mutating through `&self` usually triggers `E0596`:

```text
error[E0596]: cannot borrow `self.items` as mutable, as it is behind a `&` reference
```

The fix is either to change the API to `&mut self` when unique access is semantically required, or to wrap only the interior field in [[Cell]], [[RefCell]], [[Shared State with Mutex]], or an atomic type when mutation through `&self` is the intended contract.

## Best practice
- ✅ Use interior mutability for hidden bookkeeping, caches, test doubles, graph links, and synchronization boundaries.
- ✅ Choose [[Cell]] for small `Copy` values and simple replacement.
- ✅ Choose [[RefCell]] for single-threaded dynamic borrowing of non-`Copy` values.
- ✅ Choose [[Shared State with Mutex]], [[RwLock]], or [[Atomics]] for cross-thread access.
- ✅ Document what is allowed to change through `&self`; callers should know whether mutation is logical bookkeeping, caching, or externally visible state.
- ✅ Prefer putting the cell around the field that needs it, not around the whole struct, so ordinary fields still benefit from compile-time borrowing.

## Pitfalls
- ⚠️ Interior mutability is not permission to ignore ownership design.
- ⚠️ `RefCell<T>` can panic if guards overlap incorrectly; see [[Long-Lived RefCell Borrows]].
- ⚠️ `Cell<T>` cannot hand out ordinary references to its inner value.
- ⚠️ Shared ownership plus interior mutability can produce leaks if strong references cycle; see [[Reference Cycles and Weak]].
- ⚠️ Choosing `RefCell` where `&mut self` would work moves bugs from compile time to runtime for no benefit.

## See also
[[RefCell]] · [[Cell]] · [[Rc]] · [[Weak Back References]] · [[Borrowing]] · [[Ownership]] · [[Shared State with Mutex]] · [[Atomics]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.5 "`RefCell<T>` and the Interior Mutability Pattern" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-05-interior-mutability.html
- Standard library, `std::cell` module - [[std]],
  https://doc.rust-lang.org/std/cell/index.html
