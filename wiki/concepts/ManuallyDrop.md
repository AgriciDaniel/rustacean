---
type: concept
title: "ManuallyDrop"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, unsafe, memory]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[The Drop Trait]]", "[[MaybeUninit]]", "[[Pin projection]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/mem/struct.ManuallyDrop.html"]
rust_version: "edition 2024 / 1.85+"
---

# ManuallyDrop

`ManuallyDrop<T>` wraps a value so its destructor is **not** run automatically; you call
`ManuallyDrop::drop` (unsafe) yourself, or leak it deliberately. It gives precise control of drop
order and ownership in `unsafe` code, at zero runtime cost.

## What it is
A transparent wrapper that suppresses automatic `Drop`. Reading the inner value is safe; running its
destructor exactly once is your responsibility.

## Example
```rust
use std::mem::ManuallyDrop;

struct Noisy;
impl Drop for Noisy {
    fn drop(&mut self) { println!("dropped"); }
}

fn main() {
    let mut m = ManuallyDrop::new(Noisy);
    // ... use &*m ...
    // SAFETY: dropped exactly once and not used afterwards.
    unsafe { ManuallyDrop::drop(&mut m); }
}
```

## Best practice
- ✅ Use it only in `unsafe`/FFI code needing manual drop ordering; document the SAFETY invariant.

## Pitfalls
- ⚠️ Forgetting to drop leaks resources; double-dropping is [[Undefined Behavior]].

> [!todo] Seed note — expand (see [[Coverage Backlog]]).

## See also
[[The Drop Trait]] · [[MaybeUninit]] · [[Pin projection]] · [[Undefined Behavior]] · [[unsafe fn]] · [[Raw Pointers]] · [[Unsafe Rust & FFI]]

## Sources
- Rust std, `std::mem::ManuallyDrop` — [[std]], https://doc.rust-lang.org/std/mem/struct.ManuallyDrop.html
