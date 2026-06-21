---
type: antipattern
title: "Storing References in Structs Without Lifetimes"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, lifetimes, references, footgun]
domain: "Structs"
difficulty: intermediate
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Lifetimes]]", "[[References]]", "[[Borrowing]]", "[[Ownership]]", "[[String and str]]", "[[Lifetime Elision]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html"]
rust_version: "edition 2024 / 1.85+"
---

# Storing References in Structs Without Lifetimes

A struct can store references, but those references must have lifetime parameters that prove the borrowed data outlives the struct value.

## The mistake
The mistake is defining a struct field as `name: &str` or `data: &T` without a lifetime parameter.
Rust rejects this because the struct type does not say how long the referenced data must remain valid.

For beginner data models, the better default is often owned data such as `String`.
Owned fields make each struct instance self-contained and avoid tying its validity to another owner.

## Why it happens
References never own their referents.
If a struct stores a reference, Rust must know that the referent will remain valid for at least as long as the struct instance.
Lifetime parameters express that relationship in the type.

The Book introduces structs with owned `String` fields for exactly this reason.
References in structs are powerful, but they are a lifetime design decision rather than a way to avoid allocation by default.

Lifetime annotations on structs are part of the type definition.
`User<'a>` means "a `User` value whose borrowed fields are valid for at least lifetime `'a`."
The annotation does not extend the lifetime of the borrowed data; it only lets the borrow checker reject code where the owner would be dropped too early.
Unlike function lifetime elision, struct fields cannot omit the named relationship because the type must carry the relationship wherever it is used.

## Example
```rust
#[derive(Debug)]
struct User<'a> {
    username: &'a str,
    email: &'a str,
    active: bool,
}

fn main() {
    let username = String::from("someusername123");
    let email = String::from("someone@example.com");

    let user = User {
        username: &username,
        email: &email,
        active: true,
    };

    println!("{user:?}");
}
```

## Worked example
```rust
#[derive(Debug)]
struct Header<'a> {
    name: &'a str,
    value: &'a str,
}

fn parse_header(line: &str) -> Option<Header<'_>> {
    let (name, value) = line.split_once(':')?;
    Some(Header {
        name: name.trim(),
        value: value.trim(),
    })
}

fn main() {
    let line = String::from("content-type: text/plain");
    let header = parse_header(&line).expect("header");

    println!("{header:?}");
}
```

This is a good borrowed-view design: the `Header` does not own text, and its lifetime is tied to the input line.

## Common errors
Omitting the lifetime on reference fields produces `E0106`:

```rust
struct User {
    username: &str,
    email: &str,
}

fn main() {}
```

```console
error[E0106]: missing lifetime specifier
  |
  |     username: &str,
  |               ^ expected named lifetime parameter
```

Fix it by storing owned `String` values, or by declaring the relationship explicitly: `struct User<'a> { username: &'a str, email: &'a str }`.

Returning a borrowed struct that points at locals fails for the same reason dangling references are rejected:

```rust
struct User<'a> {
    username: &'a str,
}

fn make_user<'a>() -> User<'a> {
    let username = String::from("lee");
    User { username: &username }
}
```

```console
error[E0515]: cannot return value referencing local variable `username`
```

Return an owned `User { username: String }` instead, or borrow from data supplied by the caller.

## Best practice
- ✅ Use owned fields like `String` when each struct should own its data.
- ✅ Add lifetime parameters when a struct is intentionally a borrowed view over data owned elsewhere.
- ✅ Keep the lifetime relationship simple; if the type becomes hard to use, reconsider ownership.
- ✅ Accept `&str` in constructors and convert to `String` when the struct should own the text.
- ✅ Use `Cow<'a, str>` only when you truly need one type to support both borrowed and owned text.
- ✅ Prefer short-lived borrowed view structs for parsing and inspection, not for long-lived application state.

## Pitfalls
- ⚠️ Adding `&str` fields does not automatically make a struct cheaper or better; it shifts lifetime constraints to every user.
- ⚠️ Do not use `'static` to silence lifetime errors unless the data truly lives for the whole program.
- ⚠️ Returning a struct that borrows local variables is invalid because the locals are dropped at function exit.
- ⚠️ A struct with one lifetime parameter ties all referenced fields to a compatible lifetime; use separate parameters only when the independence matters.
- ⚠️ Borrowed fields can make collections, caches, and async tasks harder to design because owners must outlive all stored views.

## See also
[[Structs]] · [[Named Field Structs]] · [[Lifetimes]] · [[References]] · [[Borrowing]] · [[Ownership]] · [[String and str]] · [[Lifetime Elision]] · [[Cow]] · [[Making Invalid States Unrepresentable]]

## Sources
- The Rust Programming Language, ch. 5.1 "Ownership of Struct Data" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Programming Language, ch. 10.3 "Validating References with Lifetimes" — [[the-book]], https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
