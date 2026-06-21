---
type: antipattern
title: "Returning References to Locals"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, lifetimes, borrowing]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Borrowing]]", "[[References]]", "[[Lifetimes]]", "[[Move Semantics]]", "[[The Drop Trait]]", "[[Borrowed Parameter APIs]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[ownership-borrowing-lifetimes]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/reference/destructors.html"]
rust_version: "edition 2024 / 1.85+"
---

# Returning References to Locals

Returning a reference to a local variable is invalid because the local is dropped when the function returns. Return an owned value, or return a reference borrowed from an input that outlives the call.

## The mistake
The mistake is trying to create data inside a function and return `&T` or `&str` pointing into that local data.
The returned reference would outlive the value it points to.
In unsafe languages this is a dangling pointer bug; in safe Rust it is a compile error.

This often appears when writing helpers that build a `String`, pick part of it, and try to return `&str`.
It also appears when adding lifetime annotations in the hope that annotations can extend a value's lifetime.
They cannot.
Lifetimes describe relationships the data already satisfies; they do not make local stack data live longer.

## Why it happens
Local variables belong to the function's stack frame or to owners stored in that frame.
When the function returns, initialized locals are dropped.
If a local owns heap data, its destructor releases that heap data.

A reference returned from the function must point to data that remains valid after the function returns.
That usually means returning a reference to one of the function's inputs, to `self`, or to a true static item.
For newly created data, the correct answer is usually to move the owned value out.

Heap allocation does not change this rule.
If a local `String` owns heap bytes, returning `&str` into those bytes still dangles because dropping
the `String` frees the allocation.
The stack frame is not the only problem; the owner and all resources it controls are gone.

The compiler's lifetime errors are therefore reporting a real memory safety issue.
Adding a named lifetime such as `<'a>` to `fn make<'a>() -> &'a str` would promise that the caller
chooses how long the returned borrow lives, but the function has no input or static storage capable
of satisfying that promise.

## Example
```rust
fn main() {
    let greeting = build_greeting("Ferris");
    println!("{greeting}");
}

fn build_greeting(name: &str) -> String {
    let mut s = String::from("hello, ");
    s.push_str(name);
    s
}
```

## Bad example
```rust
// This does not compile:
//
// fn first_word_owned() -> &str {
//     let text = String::from("hello world");
//     text.split_once(' ').map_or(text.as_str(), |(first, _)| first)
// }
```

The function creates both the owner (`text`) and the borrowed view.
When the function returns, `text` is dropped, so the view would point at freed memory.

## Borrow-from-input example
```rust
fn main() {
    let text = String::from("hello world");
    let first = first_word(&text);
    println!("{first}");
}

fn first_word(text: &str) -> &str {
    text.split_once(' ').map_or(text, |(first, _)| first)
}
```

## Common errors
Typical diagnostics include:

```text
error[E0106]: missing lifetime specifier
error[E0515]: cannot return value referencing local variable `text`
```

`E0106` often appears when the signature has no input lifetime for the return value to borrow from.
`E0515` appears when the body returns a reference tied to a local temporary or local owner.
The fix is not "add `'static`"; it is to return an owned value or borrow from an input.

## Best practice
- ✅ Return owned data such as `String`, `Vec<T>`, or a domain type when the function creates the data.
- ✅ Return `&T` only when it borrows from an input, `self`, or valid static data.
- ✅ Let [[Move Semantics]] move constructed values to the caller instead of trying to lend dead locals.
- ✅ Use lifetime annotations to express real input-output relationships, not to force longer storage.
- ✅ Use `Cow<'a, str>` or `Cow<'a, [T]>` when an API sometimes returns a borrowed input and sometimes
  must allocate an owned fallback.
- ✅ Accept a caller-provided buffer (`&mut String`, `&mut Vec<T>`) when reuse of allocation matters.

## Pitfalls
- ⚠️ Do not write `fn f() -> &String` for a value created inside `f`; there is no owner left after return.
- ⚠️ Do not add `'static` to silence the compiler unless the returned data truly is static.
- ⚠️ Do not return `&str` into a temporary `String`; return `String` or accept a caller-provided buffer.
- ⚠️ Do not fight the diagnostic with unsafe raw pointers; the compiler is pointing at a real use-after-free.
- ⚠️ Do not confuse string literals with constructed strings; literals can be `&'static str`, but a
  `String` built at runtime is owned data that must be returned or stored somewhere.

## See also
[[Borrowing]] · [[References]] · [[Lifetimes]] · [[Move Semantics]] · [[The Drop Trait]] · [[Borrowed Parameter APIs]] · [[The Slice Type]] · [[Copy and Clone]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.2 "Dangling References" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- The Rust Reference, "Destructors" — [[the-reference]],
  https://doc.rust-lang.org/reference/destructors.html
