---
type: pattern
title: "Newtype Pattern"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, pattern, newtype, traits]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[Type Aliases]]", "[[Using Type Aliases as Newtypes]]", "[[Operator Overloading]]", "[[Fully Qualified Syntax]]", "[[Dynamically Sized Types]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern", "https://doc.rust-lang.org/book/ch20-03-advanced-types.html#type-safety-and-abstraction-with-the-newtype-pattern"]
rust_version: "edition 2024 / 1.85+"
---

# Newtype Pattern

The newtype pattern wraps an existing type in a single-field tuple struct to create a distinct local type with its own trait impls and API.

## What it is
A newtype is usually written as `struct UserId(u64);` or `pub struct Millimeters(pub u32);`.
It has the same simple runtime representation as its field in ordinary optimized code, but it is a different Rust type.

Use newtypes to enforce units, distinguish identifiers, hide implementation details, and implement traits that the orphan rules would otherwise prevent.
Unlike [[Type Aliases]], newtypes create a compiler-enforced boundary.
`UserId` is not a `u64` unless you explicitly expose conversion or access.

The Book shows this pattern for implementing `Display` on a wrapper around `Vec<String>` and for keeping units such as meters and millimeters distinct.

## How it works
Because the wrapper type is local to your crate, you can implement foreign traits for it.
For example, you cannot implement `Display` for `Vec<String>` directly because both the trait and the type are foreign.
You can implement `Display` for `Wrapper(Vec<String>)` because `Wrapper` is local.

The tradeoff is that the wrapper does not automatically expose all methods of the inner type.
Expose only the operations you want, or deliberately implement `Deref` only when behaving like the inner type is really the goal.

A tuple newtype with one field is nominal: Rust treats it as a separate type even if the field has the same layout as a primitive or standard-library type.
That nominal boundary is what lets the type checker reject mixed IDs and what gives your crate an orphan-rule "anchor" for trait impls.
In optimized code, a simple wrapper is usually elided, but layout is only a formal FFI guarantee if you specify an appropriate representation such as `#[repr(transparent)]`.

Privacy is part of the pattern.
`pub struct Email(String);` with a private field forces callers through constructors, while `pub struct Email(pub String);` is mostly a documented wrapper.
Choose the visibility based on whether the type protects invariants.

## Example
```rust
use std::fmt;

struct UserId(u64);

impl UserId {
    fn new(raw: u64) -> Self {
        Self(raw)
    }
}

impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "user-{}", self.0)
    }
}

fn load_user(id: UserId) -> String {
    format!("loaded {id}")
}

fn main() {
    let id = UserId::new(7);
    assert_eq!(load_user(id), "loaded user-7");
}
```

## More realistic example
```rust
use std::convert::TryFrom;

#[derive(Debug, Clone, PartialEq, Eq)]
struct NonEmptyName(String);

impl TryFrom<String> for NonEmptyName {
    type Error = &'static str;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        let trimmed = value.trim();
        if trimmed.is_empty() {
            Err("name cannot be empty")
        } else {
            Ok(Self(trimmed.to_owned()))
        }
    }
}

impl NonEmptyName {
    fn as_str(&self) -> &str {
        &self.0
    }
}

fn greet(name: &NonEmptyName) -> String {
    format!("hello, {}", name.as_str())
}

fn main() {
    let name = NonEmptyName::try_from(String::from(" Ferris ")).unwrap();
    assert_eq!(name.as_str(), "Ferris");
    assert_eq!(greet(&name), "hello, Ferris");

    assert!(NonEmptyName::try_from(String::from("   ")).is_err());
}
```

The type stores a plain `String`, but the constructor turns "non-empty after trimming" into a maintained invariant.

## Common errors
```rust
use std::fmt;

// impl fmt::Display for Vec<String> {
//     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
//         write!(f, "{}", self.join(", "))
//     }
// }
// error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate

struct Lines(Vec<String>);

impl fmt::Display for Lines {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0.join(", "))
    }
}
```

The newtype makes the target type local, satisfying the orphan rules.

```rust
struct UserId(u64);

fn load_user(id: UserId) -> String {
    format!("user {}", id.0)
}

fn main() {
    let raw = 7_u64;
    // load_user(raw);
    // error[E0308]: mismatched types, expected `UserId`, found `u64`
    assert_eq!(load_user(UserId(raw)), "user 7");
}
```

This error is the value of the pattern: the conversion must be explicit.

## Best practice
- ✅ Use newtypes for domain values that must not be mixed accidentally: IDs, units, validated strings, and capabilities.
- ✅ Keep the inner field private when the wrapper enforces invariants.
- ✅ Implement `From`, `TryFrom`, `Display`, and operator traits intentionally to define the boundary.
- ✅ Prefer small explicit methods over blindly forwarding the entire inner API.
- ✅ Add `#[repr(transparent)]` only when layout compatibility is part of an FFI or unsafe-code contract; otherwise do not over-specify layout.
- ✅ Derive common traits only when their semantics match the domain, especially `Copy`, `Ord`, `Hash`, and `Default`.

## Pitfalls
- ⚠️ Do not substitute [[Type Aliases]] when you need a distinct type; see [[Using Type Aliases as Newtypes]].
- ⚠️ Avoid implementing `Deref` just to reduce boilerplate if it leaks invariants or makes the newtype indistinguishable from the inner type.
- ⚠️ Remember that deriving traits delegates behavior mechanically; check whether `Copy`, `Ord`, or `Default` make semantic sense.
- ⚠️ A public tuple field lets callers bypass validation; keep construction private when invalid values are possible.
- ⚠️ Do not hide expensive parsing or allocation behind `From` if it can fail or surprise callers; use `TryFrom` or a named constructor.

## See also
[[Type Aliases]] · [[Using Type Aliases as Newtypes]] · [[Operator Overloading]] · [[Fully Qualified Syntax]] · [[Dynamically Sized Types]] · [[Traits]] · [[Custom Error Types]] · [[Copy and Clone]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.2 "Implementing External Traits with the Newtype Pattern" — [[the-book]], https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern
- The Rust Programming Language, ch. 20.3 "Type Safety and Abstraction with the Newtype Pattern" — [[the-book]], https://doc.rust-lang.org/book/ch20-03-advanced-types.html#type-safety-and-abstraction-with-the-newtype-pattern
