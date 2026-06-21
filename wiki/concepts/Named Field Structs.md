---
type: concept
title: "Named Field Structs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, data-modeling]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Tuple Structs]]", "[[Unit-Like Structs]]", "[[Methods]]", "[[Field Init Shorthand]]", "[[Struct Update Syntax]]", "[[Ownership]]", "[[Pattern Matching]]", "[[Visibility and Privacy]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/book/ch05-02-example-structs.html", "https://doc.rust-lang.org/reference/items/structs.html", "https://doc.rust-lang.org/reference/expressions/struct-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Named Field Structs

Named field structs define custom product types: one named value made from multiple related fields whose field names document the meaning of the data.

## What it is
A named field struct packages related values into a new type owned by your program's domain.
Unlike a plain tuple, it gives each field a name, so call sites can say `width` and `height` instead of relying on tuple positions like `.0` and `.1`.

Use named field structs when several values belong together and should move, borrow, validate, or gain behavior as a unit.
The struct definition is the type template; each struct expression creates an instance with concrete field values.

## How it works
A named field struct is declared with `struct Name { field: Type, ... }`.
Construct an instance with `Name { field: value, ... }`; field order at construction does not have to match declaration order.
Read fields with dot notation, as in `rect.width`.
If a binding is mutable, fields can be reassigned through that binding, but Rust makes the whole instance mutable rather than allowing individual fields to be declared mutable.

Struct fields participate in [[Ownership]].
A struct that stores `String` owns those strings; a struct that stores references needs explicit [[Lifetimes]].
Behavior is usually attached in an `impl` block through [[Methods]] and [[Associated Functions]].

Struct types are nominal, not structural: two structs with the same field names and field types are still different types.
The compiler checks construction by field name, so missing, duplicate, or unknown fields are compile-time errors rather than runtime shape checks.
Field access is a place expression; if the container place is mutable, the selected field is mutable too.
Pattern matching can destructure by field name, and `..` in a pattern ignores the rest without constructing a new value.

## Example
```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}

fn main() {
    let mut rect = Rectangle {
        width: 30,
        height: 50,
    };

    rect.width = 40;
    println!("{rect:?}");
    println!("area = {}", area(&rect));
}
```

## Worked example
```rust
#[derive(Debug)]
struct Account {
    id: u64,
    email: String,
    verified: bool,
}

impl Account {
    fn new(id: u64, email: impl Into<String>) -> Self {
        Self {
            id,
            email: email.into(),
            verified: false,
        }
    }

    fn verify(&mut self) {
        self.verified = true;
    }
}

fn domain(account: &Account) -> Option<&str> {
    account.email.split_once('@').map(|(_, domain)| domain)
}

fn main() {
    let mut account = Account::new(7, "lee@example.com");
    account.verify();

    let Account { id, verified, .. } = account;
    println!("account {id} verified = {verified}");
}
```

This example keeps construction and mutation behind methods while still using field patterns for local destructuring.
The `String` field is ignored by `..`, so it is dropped when `account` is no longer needed.

## Common errors
Trying to omit a field produces `E0063` because every field needs a value unless you use [[Struct Update Syntax]]:

```rust
struct User {
    email: String,
    active: bool,
}

fn main() {
    let user = User {
        email: String::from("a@example.com"),
    };
}
```

```console
error[E0063]: missing field `active` in initializer of `User`
```

Fix it by supplying the missing field, using `..base` with a valid base value, or moving construction into an [[Associated Functions|associated constructor]] that chooses defaults deliberately.

## Best practice
- ✅ Prefer named-field structs when the meaning of each value matters at call sites.
- ✅ Store owned data such as `String` when each instance should be self-contained; use references only when the lifetime relationship is part of the design.
- ✅ Attach domain behavior with [[Methods]] so data and operations stay discoverable together.
- ✅ Use [[Deriving Traits on Structs]] for standard behavior such as `Debug`, `Clone`, `Copy`, `Eq`, or ordering when every field supports it.
- ✅ Keep fields private in libraries when invariants matter, then expose narrow methods or constructors.
- ✅ Use field patterns in local code when destructuring improves clarity, especially with `Struct { wanted, .. }`.

## Pitfalls
- ⚠️ Replacing meaningful field names with positional tuple access makes code harder to audit; use [[Tuple Structs]] only when positions are obvious or field names would be redundant.
- ⚠️ Expecting per-field mutability does not work; see [[Expecting Per-Field Mutability in Structs]].
- ⚠️ Storing borrowed data without modeling lifetimes fails quickly; see [[Storing References in Structs Without Lifetimes]] and [[Lifetimes]].
- ⚠️ Public fields let downstream code construct and update values directly, bypassing validation in `new` or setter methods.
- ⚠️ Reordering fields usually does not affect named construction, but it can affect derived ordering and debug output.

## See also
[[Structs]] · [[Tuple Structs]] · [[Unit-Like Structs]] · [[Methods]] · [[Associated Functions]] · [[Field Init Shorthand]] · [[Struct Update Syntax]] · [[Deriving Traits on Structs]] · [[Ownership]] · [[Pattern Matching]] · [[Visibility and Privacy]]

## Sources
- The Rust Programming Language, ch. 5.1 "Defining and Instantiating Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Programming Language, ch. 5.2 "An Example Program Using Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-02-example-structs.html
- The Rust Reference, "Structs" — [[the-reference]], https://doc.rust-lang.org/reference/items/structs.html
- The Rust Reference, "Struct expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/struct-expr.html
