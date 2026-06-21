---
type: pattern
title: "Field Init Shorthand"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, initialization, idiom]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Associated Functions]]", "[[Struct Update Syntax]]", "[[Constructor Naming]]", "[[Ownership]]", "[[Shadowing]]", "[[Move Semantics]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/expressions/struct-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Field Init Shorthand

Field init shorthand lets `field` stand for `field: field` when a local variable or parameter has the same name as a struct field.

## What it is
When constructing a named-field struct, Rust normally uses `field_name: expression`.
If the expression is a variable with the same name as the field, you can write only the field name.

This is an idiom for constructors and builder-like functions whose parameters intentionally mirror field names.
It reduces noise without changing ownership, evaluation order, or field visibility rules.

## How it works
In `User { email, username, active: true }`, `email` expands conceptually to `email: email`.
The variable is moved or copied into the field exactly as it would be in the long form.
Shorthand only works for identifiers in scope; it does not work for arbitrary expressions or differently named variables.

Use explicit `field: expression` when the source name differs, the expression is computed, or clarity benefits from spelling out the mapping.

The shorthand is part of struct expression syntax.
It is checked after name resolution: the identifier must be a visible field of the struct and a local binding in scope.
For non-`Copy` values, shorthand is still a move into the field.
For `Copy` values, it copies exactly as the longer `field: field` form would.

## Example
```rust
#[derive(Debug)]
struct User {
    email: String,
    username: String,
    active: bool,
    sign_in_count: u64,
}

fn build_user(email: String, username: String) -> User {
    User {
        email,
        username,
        active: true,
        sign_in_count: 1,
    }
}

fn main() {
    let user = build_user(
        String::from("someone@example.com"),
        String::from("someusername123"),
    );

    println!("{user:?}");
}
```

## Worked example
```rust
#[derive(Debug)]
struct Signup {
    email: String,
    username: String,
    newsletter: bool,
}

fn normalize_signup(email: &str, username: &str) -> Signup {
    let email = email.trim().to_ascii_lowercase();
    let username = username.trim().to_owned();

    Signup {
        email,
        username,
        newsletter: false,
    }
}

fn main() {
    let signup = normalize_signup("  LEE@EXAMPLE.COM ", " lee ");
    println!("{signup:?}");
}
```

Here shadowing is intentional: the borrowed parameters are converted into owned, normalized locals with the same names as the fields.
That makes the final struct literal read as a direct handoff of ownership.

## Common errors
Shorthand uses the identifier as the field name, so a differently named local is not enough:

```rust
struct User {
    email: String,
}

fn main() {
    let email_address = String::from("a@example.com");
    let user = User { email_address };
    println!("{}", user.email);
}
```

```console
error[E0560]: struct `User` has no field named `email_address`
```

Fix it by spelling out the mapping: `User { email: email_address }`.

## Best practice
- ✅ Name constructor parameters after the fields they initialize when that improves readability.
- ✅ Combine shorthand with explicit fields for defaults or computed values.
- ✅ Use shorthand in small, direct constructors; it is a strong signal that the parameter maps one-to-one into the struct.
- ✅ Keep parameter names domain-specific rather than shortening them just to save characters.
- ✅ Use local normalization plus shadowing when it makes ownership transfer clearer than introducing throwaway names.
- ✅ Prefer explicit `field: expression` for conversions, validation, or values assembled from several inputs.

## Pitfalls
- ⚠️ Shorthand still moves non-`Copy` values; see [[Ownership]] and [[Struct Update Syntax]] for related move behavior.
- ⚠️ Overusing shadowed names can make it unclear which binding is in scope; see [[Shadowing]].
- ⚠️ Do not force shorthand when the source value has a clearer distinct name; explicit `field: value` is often better.
- ⚠️ Shorthand does not bypass field visibility; private fields still cannot be initialized outside their module.
- ⚠️ A shorthand-heavy constructor can hide defaults if the explicit fields are buried in a long literal.

## See also
[[Structs]] · [[Named Field Structs]] · [[Associated Functions]] · [[Struct Update Syntax]] · [[Constructor Naming]] · [[Shadowing]] · [[Ownership]] · [[Deriving Traits on Structs]] · [[Move Semantics]] · [[Visibility and Privacy]]

## Sources
- The Rust Programming Language, ch. 5.1 "Using the Field Init Shorthand" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Struct expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/struct-expr.html
