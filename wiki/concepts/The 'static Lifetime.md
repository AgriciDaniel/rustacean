---
type: concept
title: "The 'static Lifetime"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, lifetimes, static, references]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Lifetimes]]", "[[Lifetime Elision]]", "[[Trait Bounds]]", "[[String and str]]", "[[Threads]]", "[[Overconstraining Lifetimes]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#the-static-lifetime", "https://doc.rust-lang.org/reference/trait-bounds.html#lifetime-bounds"]
rust_version: "edition 2024 / 1.85+"
---

# The 'static Lifetime

`'static` is the lifetime for references that can be valid for the whole program, and as a bound it means a type contains no non-static borrowed data.

## What it is
String literals have type `&'static str` because their bytes are stored in the program binary.
A `static` item also has storage that lasts for the program duration.
The bound `T: 'static` is different: it says values of type `T` do not contain references shorter than `'static`.
Owned values such as `String`, `Vec<u8>`, or `Box<Foo>` usually satisfy `T: 'static` even though each value can be dropped earlier.
This distinction is essential for thread spawning, task spawning, and owned trait objects.

## How it works
For a reference type, `&'static T` means the referenced data can be borrowed for the whole program.
For a generic type, `T: 'static` permits `T` to be safely stored wherever no shorter borrow is tracked.
`Box<dyn Trait>` often means `Box<dyn Trait + 'static>` unless a shorter object lifetime is written.
Compiler suggestions to add `'static` are sometimes symptoms, not solutions: a dangling reference should usually be fixed by changing ownership.
Use `'static` when the API truly needs independence from the caller's stack frame.
For `thread::spawn`, the closure may outlive the stack frame that created it, so captured values must be owned or otherwise valid for `'static`.
This does not mean the thread runs forever; it means the type of captured data contains no shorter borrowed references.
Leaking with `Box::leak` can create a `&'static mut T`, but that intentionally gives up normal deallocation and is rarely the right library API.
Trait object default object bounds are a separate source of surprise: `Box<dyn Display>` means an owned object with a `'static` object lifetime unless a shorter bound is written.

## Example
```rust
use std::thread;

fn run_owned<T>(value: T) -> thread::JoinHandle<T>
where
    T: Send + 'static,
{
    thread::spawn(move || value)
}

fn main() {
    let literal: &'static str = "stored in the binary";
    assert_eq!(literal.len(), 20);

    let handle = run_owned(String::from("owned data"));
    assert_eq!(handle.join().unwrap(), "owned data");
}
```

## Common errors
Spawning work that captures a stack borrow often reports:

```text
error[E0373]: closure may outlive the current function, but it borrows `value`
```

Use `move` to capture owned data, clone an `Arc`, or keep the work scoped so the borrow cannot outlive the owner.
For boxed trait objects, a borrowed implementor can produce a message that the value "does not live long enough" with an implied `'static` requirement.
Write `Box<dyn Trait + 'a>` or avoid boxing if the object is intentionally borrowed.
If the compiler suggests `'static` while you are returning a reference to a local, the real fix is to return an owned value, not to claim the local is static.

## Best practice
- ✅ Use `&'static str` for string literals, static messages, and names that truly never borrow from caller-owned data.
- ✅ Use `T: 'static` when spawned work or stored callbacks must not capture stack borrows.
- ✅ Prefer owned data when an API must cross thread or task boundaries.
- ✅ Write explicit shorter trait object lifetimes, such as `Box<dyn Trait + 'a>`, when borrowed data is intended.
- ✅ Investigate why the compiler asks for `'static` before accepting the suggestion.

## Pitfalls
- ⚠️ Reading `T: 'static` as "the value is never dropped" is wrong; owned values can be dropped normally.
- ⚠️ Adding `'static` to silence a borrow error can reject valid borrowed callers or mask a bad ownership design.
- ⚠️ `Box<dyn Trait>` defaulting to a static object bound surprises APIs that meant to store borrowed implementors.
- ⚠️ Leaking memory to manufacture `&'static` references is almost never an acceptable API fix.

## See also
[[Lifetimes]] · [[Lifetime Elision]] · [[Trait Bounds]] · [[String and str]] · [[Threads]] · [[Tasks and spawn]] · [[Overconstraining Lifetimes]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.3 "The Static Lifetime" — [[the-book]], https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#the-static-lifetime
- The Rust Reference, "Lifetime bounds" — [[the-reference]], https://doc.rust-lang.org/reference/trait-bounds.html#lifetime-bounds
