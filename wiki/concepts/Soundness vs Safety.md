---
type: concept
title: "Soundness vs Safety"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, soundness, api]
domain: "Unsafe Rust & FFI"
difficulty: advanced
related: ["[[Unsafe Rust]]", "[[Undefined Behavior]]", "[[unsafe fn]]", "[[SAFETY Comments]]", "[[Safe Abstractions over Unsafe Code]]", "[[Miri]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/behavior-considered-undefined.html", "https://doc.rust-lang.org/nomicon/safe-unsafe-meaning.html", "https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html"]
rust_version: "edition 2024 / 1.85+"
---

# Soundness vs Safety

Safety is mostly a syntactic/API property, while soundness is the semantic property that safe clients cannot trigger undefined behavior through an abstraction.

## What it is
In Rust discussion, "safe" usually means callable or usable without the `unsafe`
keyword. "Sound" means no safe use of the API can cause [[Undefined Behavior]].

Unsafe code is allowed inside Rust libraries because it can be hidden behind sound
safe APIs. The standard library uses this pattern widely. The entire arrangement
depends on the rule that unsafe internals must not let safe callers violate Rust's
memory model.

## How it works
If a safe function contains an unsafe block, the function author owns the whole
proof. Every possible safe input must either produce a correct result, return an
ordinary error, or panic/abort without UB.

If a function is `unsafe fn`, some proof obligations move to the caller. That can
be appropriate, but only when the preconditions cannot be checked or represented
inside a safe signature.

An API can be safe but logically wrong, such as a bad ordering implementation. Unsafe
code must not rely on safe trait implementations for memory safety unless the trait
itself is unsafe and documents the required invariant.

This distinction is why `unsafe trait` exists. If implementors must uphold a
memory-safety invariant that callers of safe methods rely on, the trait itself
must make implementation unsafe and document the invariant. A safe trait may still
have bugs, but unsafe code should not assume safe implementors promised more than
the trait contract says.

## Example
```rust
fn get_checked(values: &[u8], index: usize) -> Option<u8> {
    if index < values.len() {
        // SAFETY: index was checked against this slice's length.
        Some(unsafe { *values.as_ptr().add(index) })
    } else {
        None
    }
}

fn main() {
    assert_eq!(get_checked(&[10, 20], 0), Some(10));
    assert_eq!(get_checked(&[10, 20], 9), None);
}
```

## Worked example
```rust
pub struct NonEmpty<T> {
    values: Vec<T>,
}

impl<T> NonEmpty<T> {
    pub fn new(values: Vec<T>) -> Option<Self> {
        if values.is_empty() {
            None
        } else {
            Some(Self { values })
        }
    }

    pub fn first(&self) -> &T {
        // SAFETY: new is the only constructor and rejects empty vectors.
        unsafe { self.values.get_unchecked(0) }
    }
}

fn main() {
    let values = NonEmpty::new(vec![3, 4]).unwrap();
    assert_eq!(*values.first(), 3);
    assert!(NonEmpty::<i32>::new(vec![]).is_none());
}
```

The method is safe because the type invariant prevents safe callers from creating
an empty `NonEmpty`. If the field were public, or if there were an unchecked safe
constructor, the safe `first` method would become unsound.

## Common errors
Soundness bugs usually do not have a dedicated compiler error. The compiler accepts
a safe wrapper if its types line up; the reviewer must ask whether any safe sequence
of calls can violate an unsafe operation's preconditions.

When you see an E0133 fix that simply moves an unsafe operation into a safe helper,
review the helper as a new public contract. The syntax error may be gone while the
soundness problem remains.

## Best practice
- ✅ Ask "can a safe caller trigger UB?" when reviewing unsafe abstractions.
- ✅ Move preconditions into types and constructors where possible.
- ✅ Use `unsafe fn` only for obligations that genuinely belong to the caller.
- ✅ Test sound wrappers with [[Miri]] and adversarial safe inputs.
- ✅ Make fields private when they participate in an invariant used by unsafe code.
- ✅ Use `unsafe trait` for implementor obligations that safe methods rely on for memory safety.

## Pitfalls
- ⚠️ Believing a safe wrapper is sound because its tests pass for friendly inputs.
- ⚠️ Relying on a safe trait method to uphold memory-safety invariants it never promised.
- ⚠️ Exposing raw pointers in a safe API and then assuming users will follow undocumented rules.
- ⚠️ Treating [[SAFETY Comments]] as decoration instead of as the proof that connects checks to operations.
- ⚠️ Adding a new safe constructor or `pub` field later without re-auditing every unsafe block that relied on the old invariant.

## See also
[[Unsafe Rust]] · [[Undefined Behavior]] · [[unsafe fn]] · [[SAFETY Comments]] · [[Safe Abstractions over Unsafe Code]] · [[Miri]] · [[Aliasing and Provenance]] · [[FFI Wrapper Types]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Reference, "Behavior considered undefined" — [[the-reference]], https://doc.rust-lang.org/reference/behavior-considered-undefined.html
- The Rustonomicon, "How Safe and Unsafe Interact" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/safe-unsafe-meaning.html
- The Rust Programming Language, ch. 20.1 "Unsafe Rust" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
