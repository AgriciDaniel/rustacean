---
type: concept
title: "References"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, references, borrowing]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Borrowing]]", "[[Mutable References]]", "[[Lifetimes]]", "[[The Slice Type]]", "[[The Stack and the Heap]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/reference/types/pointer.html#references"]
rust_version: "edition 2024 / 1.85+"
---

# References

A reference is a non-owning pointer-like value, written `&T` or `&mut T`, that Rust guarantees points to valid data for the reference's lifetime. References are the concrete values produced by [[Borrowing]].

## What it is
References let code access data owned somewhere else.
They are like pointers in that they contain an address, but safe references carry stronger rules: they must be valid, aligned, and obey Rust's aliasing discipline.

Shared references, `&T`, allow read access.
Mutable references, `&mut T`, allow exclusive write access.
Both are non-owning: when the reference goes out of scope, the referent is not dropped.

References are also how [[The Slice Type]] is represented at the surface of the language.
A string slice `&str` and a slice `&[T]` are references to a contiguous region plus metadata.

## How it works
The expression `&value` borrows a place and produces a shared reference.
The expression `&mut value` borrows a mutable place and produces a mutable reference.
The dereference operator `*` follows a reference to the value it refers to, though method calls and field access often insert dereferences automatically.

The compiler tracks the lifetime of each reference.
A reference cannot outlive the value it points to, which prevents dangling references in safe Rust.
When a reference is passed to a function, ownership of the referent stays with the caller.

References are values, so they can be copied freely as long as copying the reference does not violate the borrow rules.
Copying a `&T` copies access to the same data; it does not copy the data itself.

References are always tied to a lifetime, even when that lifetime is elided from the source code.
In `fn first(values: &[i32]) -> &i32`, lifetime elision ties the returned reference to the input
slice because there is exactly one input lifetime.
When there are multiple possible inputs, the signature may need an explicit lifetime or a different
return type so the relationship is unambiguous.

Shared references implement `Copy`, so passing `&T` by value is cheap.
Mutable references are also movable values, but safe Rust prevents duplicating active exclusive
access to the same referent.
That distinction is why `&mut T` parameters should be treated as a temporary capability, not as a
long-lived handle to stash casually.

## Example
```rust
fn main() {
    let numbers = vec![10, 20, 30];
    let first = first_item(&numbers);

    println!("first = {first}");
    println!("len = {}", numbers.len());
}

fn first_item(values: &[i32]) -> &i32 {
    &values[0]
}
```

## Worked example
```rust
#[derive(Debug)]
struct Config {
    host: String,
    port: u16,
}

fn main() {
    let config = Config {
        host: String::from("localhost"),
        port: 8080,
    };

    let endpoint = endpoint_parts(&config);
    println!("{}:{}", endpoint.0, endpoint.1);
    println!("{config:?}");
}

fn endpoint_parts(config: &Config) -> (&str, u16) {
    (&config.host, config.port)
}
```

## Common errors
A reference cannot outlive the value it points at:

```text
error[E0515]: cannot return reference to local variable `value`
```

Return owned data when the function creates it, or return a reference that is borrowed from an input:

```rust
fn first(values: &[String]) -> Option<&str> {
    values.first().map(String::as_str)
}
```

## Best practice
- ✅ Use references when the caller should retain [[Ownership]] of the value.
- ✅ Prefer `&str` over `&String` and `&[T]` over `&Vec<T>` in parameters unless the concrete container matters.
- ✅ Keep references short-lived in mutation-heavy code so later mutable operations are not blocked.
- ✅ Return references only when they clearly borrow from an input or from `self`.
- ✅ Use `Option<&T>` instead of sentinel indices or panicking access when a borrowed result may be absent.
- ✅ Let lifetime elision do routine work; add explicit lifetime names only when they clarify multiple
  input-output relationships.

## Pitfalls
- ⚠️ A reference is not an owning handle; returning `&local` would create a dangling reference, so Rust rejects it. See [[Returning References to Locals]].
- ⚠️ `&mut T` does not mean "a mutable variable"; it means exclusive access to the referent while the borrow is active. See [[Mutable References]].
- ⚠️ Do not use indices as if they were checked references after mutation; prefer slices or recompute the index. See [[Stale Slice Indices]].
- ⚠️ References do not make heap allocation free or shared ownership automatic; use [[Arc]] or [[Rc RefCell Overuse]] guidance when ownership is truly shared.
- ⚠️ Do not store references in structs until you have considered owning the data instead; reference
  fields make the struct's lifetime part of its public API.

## See also
[[Ownership]] · [[Borrowing]] · [[Mutable References]] · [[Lifetimes]] · [[The Slice Type]] · [[The Stack and the Heap]] · [[Borrowed Parameter APIs]] · [[Returning References to Locals]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.2 "References and Borrowing" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- The Rust Reference, "Reference types" — [[the-reference]],
  https://doc.rust-lang.org/reference/types/pointer.html#references
