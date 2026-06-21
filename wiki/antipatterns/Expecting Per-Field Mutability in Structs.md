---
type: antipattern
title: "Expecting Per-Field Mutability in Structs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, mutability, footgun]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Variables and Mutability]]", "[[Methods]]", "[[Borrowing]]", "[[Ownership]]", "[[Visibility and Privacy]]", "[[Interior Mutability]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/expressions/field-expr.html", "https://doc.rust-lang.org/reference/items/structs.html"]
rust_version: "edition 2024 / 1.85+"
---

# Expecting Per-Field Mutability in Structs

Rust does not let you mark individual struct fields as mutable; mutability belongs to the binding or reference used to access the struct.

## The mistake
The mistake is looking for syntax like `mut email: String` inside a struct definition.
Rust's struct fields declare names and types, not field-level mutability.
Whether a field can be reassigned depends on how the instance is bound or borrowed.

If the instance is bound with `let mut user`, field assignment through that binding is allowed.
If it is bound with `let user`, field assignment is rejected.

## Why it happens
Rust models mutability as a property of places: bindings, references, and access paths.
This keeps the ownership and borrowing rules uniform.
A `&mut User` permits mutation through the reference; a `&User` does not.

For public API design, this means field mutability is controlled by visibility and methods, not by annotating selected fields.
Expose mutation intentionally with [[Methods]], or use interior mutability primitives only when shared mutation is truly required.

A field access expression is mutable only when its container place is mutable.
`let mut user` makes the local binding mutable.
`fn rename(&mut self, ...)` makes the method require an exclusive mutable borrow for the duration of the call.
Neither choice changes the struct definition; another binding to the same type can still be immutable.

## Example
```rust
#[derive(Debug)]
struct User {
    active: bool,
    email: String,
}

impl User {
    fn deactivate(&mut self) {
        self.active = false;
    }
}

fn main() {
    let mut user = User {
        active: true,
        email: String::from("someone@example.com"),
    };

    user.email = String::from("another@example.com");
    user.deactivate();
    println!("{user:?}");
}
```

## Worked example
```rust
#[derive(Debug)]
struct Session {
    id: u64,
    active: bool,
}

impl Session {
    fn new(id: u64) -> Self {
        Self { id, active: true }
    }

    fn close(&mut self) {
        self.active = false;
    }

    fn is_active(&self) -> bool {
        self.active
    }
}

fn main() {
    let mut session = Session::new(99);
    session.close();

    println!("{} active = {}", session.id, session.is_active());
}
```

This gives callers controlled mutation without exposing every field for arbitrary assignment.

## Common errors
Assigning through an immutable binding fails even when only one field changes:

```rust
struct User {
    email: String,
}

fn main() {
    let user = User {
        email: String::from("old@example.com"),
    };

    user.email = String::from("new@example.com");
}
```

```console
error[E0594]: cannot assign to `user.email`, as `user` is not declared as mutable
```

Fix it with `let mut user = ...`, or provide an `&mut self` method when the mutation is part of the type's public behavior.

## Best practice
- ✅ Put `mut` on the binding when local code needs to reassign fields.
- ✅ Use `&mut self` methods to make mutation part of the type's API.
- ✅ Keep fields private when callers should not freely mutate them.
- ✅ Reach for interior mutability or locks only for shared-mutation designs, not ordinary struct updates.
- ✅ Prefer small methods such as `deactivate`, `rename`, or `set_limit` when mutation carries domain meaning.
- ✅ Use immutable bindings by default and introduce `mut` at the smallest scope where reassignment is needed.

## Pitfalls
- ⚠️ `mut` in `let mut user` does not make the value globally mutable; it only affects that binding.
- ⚠️ `&User` prevents field reassignment even if the original owner used `let mut`.
- ⚠️ Making every field public to "solve" mutability usually weakens invariants.
- ⚠️ Interior mutability types such as `Cell`, `RefCell`, or `Mutex` change the borrowing model; they are not replacements for ordinary `mut`.
- ⚠️ A setter for every field can recreate public-field problems while adding ceremony.

## See also
[[Structs]] · [[Named Field Structs]] · [[Methods]] · [[Variables and Mutability]] · [[Borrowing]] · [[Ownership]] · [[Visibility and Privacy]] · [[Shared State with Mutex]] · [[Interior Mutability]] · [[References]]

## Sources
- The Rust Programming Language, ch. 5.1 "Defining and Instantiating Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Field access expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/field-expr.html
- The Rust Reference, "Structs" — [[the-reference]], https://doc.rust-lang.org/reference/items/structs.html
