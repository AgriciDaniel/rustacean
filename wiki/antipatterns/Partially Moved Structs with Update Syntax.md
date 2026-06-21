---
type: antipattern
title: "Partially Moved Structs with Update Syntax"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, move-semantics, footgun]
domain: "Structs"
difficulty: intermediate
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Struct Update Syntax]]", "[[Ownership]]", "[[Move Semantics]]", "[[Needless Clone]]", "[[Copy and Clone]]", "[[Making Invalid States Unrepresentable]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/expressions/struct-expr.html#functional-update-syntax"]
rust_version: "edition 2024 / 1.85+"
---

# Partially Moved Structs with Update Syntax

Using `..base` with non-`Copy` fields can move fields out of `base`, making the original struct unusable as a whole after the new struct is built.

## The mistake
The mistake is treating struct update syntax like a borrowing copy or a mutation.
`User { email: new_email, ..user1 }` creates a new `User`.
Any unspecified non-`Copy` fields are moved from `user1` into the new value.

After that move, `user1` may be partially moved.
Rust prevents using `user1` as a whole because one or more of its owned fields no longer belong to it.

## Why it happens
Struct update syntax uses assignment-like move semantics for fields that come from the base expression.
In the Book's `User` example, `active: bool` and `sign_in_count: u64` are `Copy`, but `username: String` is moved.
The explicitly provided `email` field is not moved from `user1`, but the old `user1` still cannot be used as a complete `User` after `username` has moved.

This is ordinary [[Ownership]], not special behavior.
The concise syntax can make the move less visible than spelling out every field.

The key detail is "unspecified fields."
Fields written explicitly in the new literal are not read from the base.
Fields omitted from the new literal are copied or moved exactly as if you had written `field: base.field`.
After a partial move, Rust may still allow access to fields that were not moved, but it will reject using the original struct as a complete value.

## Example
```rust
#[derive(Debug, Clone)]
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}

fn main() {
    let user1 = User {
        active: true,
        username: String::from("someusername123"),
        email: String::from("someone@example.com"),
        sign_in_count: 1,
    };

    let user2 = User {
        email: String::from("another@example.com"),
        ..user1.clone()
    };

    println!("original still usable: {user1:?}");
    println!("new user: {user2:?}");
}
```

## Edge case
```rust
#[derive(Debug)]
struct User {
    active: bool,
    username: String,
    email: String,
}

fn main() {
    let user1 = User {
        active: true,
        username: String::from("lee"),
        email: String::from("lee@example.com"),
    };

    let user2 = User {
        username: String::from("new-name"),
        email: String::from("new@example.com"),
        ..user1
    };

    println!("old active flag still copied: {}", user1.active);
    println!("{user2:?}");
}
```

Here only `active: bool` is taken from `user1`, and `bool` is `Copy`, so `user1.active` remains usable.
The complete `user1` value would still be unavailable if any non-`Copy` field had been moved.

## Common errors
The classic failure is using the whole base after an update moved an owned field:

```rust
#[derive(Debug)]
struct User {
    username: String,
    email: String,
}

fn main() {
    let user1 = User {
        username: String::from("lee"),
        email: String::from("lee@example.com"),
    };

    let user2 = User {
        email: String::from("new@example.com"),
        ..user1
    };

    println!("{user1:?}");
    println!("{user2:?}");
}
```

```console
error[E0382]: borrow of partially moved value: `user1`
```

Fix by constructing `user2` from `..user1.clone()` when both full values are needed, by cloning only the fields that must be shared, or by redesigning the update as a method that borrows `self`.

## Best practice
- ✅ Assume `..base` moves unspecified non-`Copy` fields unless you explicitly clone or borrow data elsewhere.
- ✅ Use `..base.clone()` only when keeping both values is genuinely necessary and cloning cost is acceptable.
- ✅ Prefer explicit construction when move behavior would otherwise surprise readers.
- ✅ Design constructors or update methods when your type has invariants that raw update syntax can bypass.
- ✅ For reusable configurations, consider small `with_*` methods that take `self` and return an updated value.
- ✅ In reviews, check which fields are omitted from the literal; those are the fields affected by move/copy behavior.

## Pitfalls
- ⚠️ Cloning just to silence a move error can hide design problems; see [[Needless Clone]].
- ⚠️ Struct update syntax does not call validation code unless the field expressions do so themselves.
- ⚠️ Public fields make update syntax available to downstream callers, which can matter for API invariants.
- ⚠️ Access to one surviving field after a partial move can be legal, but it often makes code harder to maintain.
- ⚠️ Adding a new non-`Copy` field to a public struct can change whether existing update-syntax call sites leave the base usable.

## See also
[[Structs]] · [[Named Field Structs]] · [[Struct Update Syntax]] · [[Ownership]] · [[Move Semantics]] · [[Copy and Clone]] · [[Needless Clone]] · [[Associated Functions]] · [[Making Invalid States Unrepresentable]] · [[Deriving Traits on Structs]]

## Sources
- The Rust Programming Language, ch. 5.1 "Creating Instances with Struct Update Syntax" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Functional update syntax" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/struct-expr.html#functional-update-syntax
