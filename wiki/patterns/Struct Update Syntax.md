---
type: pattern
title: "Struct Update Syntax"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, initialization, update-syntax]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Field Init Shorthand]]", "[[Ownership]]", "[[Move Semantics]]", "[[Partially Moved Structs with Update Syntax]]", "[[Copy and Clone]]", "[[The Default Trait]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/expressions/struct-expr.html", "https://doc.rust-lang.org/std/default/trait.Default.html"]
rust_version: "edition 2024 / 1.85+"
---

# Struct Update Syntax

Struct update syntax builds a new instance by overriding selected fields and taking the remaining fields from another instance of the same type.

## What it is
The syntax `Struct { changed: value, ..base }` means "use this explicit field value, and fill every unspecified field from `base`."
It is useful when a new value should mostly match an existing value.

The update expression must come last in the struct literal.
The base value must have the same struct type as the new instance.

## How it works
Struct update syntax behaves like assignment for the fields it pulls from the base value.
Fields with non-`Copy` types are moved into the new value.
Fields with `Copy` types are copied.
Fields that you explicitly provide are not moved from the base.

Because moving a field can partially move the base value, the original struct instance may no longer be usable as a whole after the update.
You can still use fields that were not moved when Rust can prove they remain valid, but relying on that often makes code harder to read.

The base expression is evaluated as the source of the remaining fields and must have the exact same struct type.
The syntax is functional update, not mutation: it produces a separate value.
All fields, including fields filled by `..base`, must be visible at the construction site.
For configuration structs whose default values are valid, `Struct { changed, ..Default::default() }` is the same mechanism with a freshly constructed base value.

## Example
```rust
#[derive(Debug)]
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
        ..user1
    };

    println!("{user2:?}");
}
```

## Worked example
```rust
#[derive(Debug, Clone)]
struct RetryPolicy {
    attempts: u8,
    backoff_millis: u64,
    jitter: bool,
}

impl Default for RetryPolicy {
    fn default() -> Self {
        Self {
            attempts: 3,
            backoff_millis: 250,
            jitter: true,
        }
    }
}

fn main() {
    let fast = RetryPolicy {
        backoff_millis: 25,
        ..RetryPolicy::default()
    };

    let no_jitter = RetryPolicy {
        jitter: false,
        ..fast.clone()
    };

    println!("{fast:?}");
    println!("{no_jitter:?}");
}
```

This is a good fit because every default is valid and the clone is explicit where both configurations must stay usable.

## Common errors
Using an updated value after a non-`Copy` field was moved produces `E0382`:

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

Fix it by cloning the base or selected fields deliberately, or by constructing the new value from borrowed data rather than moving fields out of the old one.

## Best practice
- ✅ Use update syntax when it makes the unchanged fields obvious.
- ✅ Put the `..base` expression last; Rust requires it there.
- ✅ Be deliberate about moves from the base value, especially for fields like `String`, `Vec<T>`, and owned structs.
- ✅ Prefer `Clone` or explicit construction when both old and new values must remain fully usable.
- ✅ Use `..Default::default()` for option structs only when default values are meaningful and documented.
- ✅ Prefer explicit fields when moving from the base would be surprising or when invariants need a named constructor.

## Pitfalls
- ⚠️ Updating from a value with non-`Copy` fields can partially move the original; see [[Partially Moved Structs with Update Syntax]].
- ⚠️ Struct update syntax is not a mutation; it creates a new instance.
- ⚠️ The base expression must be the same struct type, not merely another struct with identical fields.
- ⚠️ Struct update syntax can bypass validation if callers can access all fields directly.
- ⚠️ It can interact with borrows at the field level: only fields actually copied or moved from the base are accessed.

## See also
[[Structs]] · [[Named Field Structs]] · [[Field Init Shorthand]] · [[Ownership]] · [[Move Semantics]] · [[Copy and Clone]] · [[Partially Moved Structs with Update Syntax]] · [[Deriving Traits on Structs]] · [[The Default Trait]] · [[Making Invalid States Unrepresentable]]

## Sources
- The Rust Programming Language, ch. 5.1 "Creating Instances with Struct Update Syntax" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Functional update syntax" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/struct-expr.html#functional-update-syntax
- The Rust standard library, `Default` — [[std]], https://doc.rust-lang.org/std/default/trait.Default.html
