---
type: concept
title: "Enums"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, enums, pattern-matching, types]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Enum Variants with Data]]", "[[The match Expression]]", "[[Patterns]]", "[[Exhaustiveness]]", "[[Option]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html", "https://doc.rust-lang.org/book/ch06-00-enums.html"]
rust_version: "edition 2024 / 1.85+"
---

# Enums

Enums define a type whose value is exactly one of a fixed set of variants, making illegal states harder to represent.

## What it is
An `enum` is Rust's algebraic "one of these cases" type.
Each variant is namespaced under the enum name, such as `Direction::North`.
All variants have the same outer type, so a function can accept one enum and handle every case.

Enums are best when a domain concept has a closed set of possibilities:
directions, states, commands, protocol messages, or outcomes.
Unlike a loose integer or string code, an enum lets the compiler check that callers pass only known cases.

## How it works
Define an enum with the `enum` keyword and list its variants inside braces.
A value can be only one variant at a time.
Use `match`, `if let`, or other [[Patterns]] to inspect which variant you have.

Enums can also have methods in `impl` blocks, just like structs.
When a variant carries no data, it behaves like a named constant of the enum type.
When variants carry data, use [[Enum Variants with Data]] and [[Destructuring]] to extract that data.

At runtime, a Rust enum is represented as a tagged union: enough storage for the largest variant plus
information that says which variant is currently active. The compiler owns those layout details, and
it can optimize some enums heavily. For example, `Option<&T>` can often use the invalid null pointer
value as the `None` tag, so it does not need to be larger than `&T`; write code against the type
semantics, not against guessed layout.

The variant namespace matters. `North` by itself is only available if imported or matched in a context
where name resolution finds it; `Direction::North` is always explicit. Methods usually take `&self`
when they only classify the current variant and `self` when they intentionally consume variant data.

## Example
```rust
#[derive(Debug, PartialEq)]
enum Direction {
    North,
    South,
    East,
    West,
}

impl Direction {
    fn is_vertical(&self) -> bool {
        matches!(self, Direction::North | Direction::South)
    }
}

fn main() {
    let direction = Direction::North;

    assert!(direction.is_vertical());
    assert_eq!(format!("{direction:?}"), "North");
}
```

## Worked example
```rust
#[derive(Debug, PartialEq)]
enum Connection {
    Disconnected,
    Connecting { attempts: u8 },
    Connected { peer: String },
}

impl Connection {
    fn label(&self) -> String {
        match self {
            Connection::Disconnected => String::from("offline"),
            Connection::Connecting { attempts } => format!("connecting, attempt {attempts}"),
            Connection::Connected { peer } => format!("connected to {peer}"),
        }
    }
}

fn main() {
    let state = Connection::Connected {
        peer: String::from("db-primary"),
    };

    assert_eq!(state.label(), "connected to db-primary");
}
```

## Common errors
The common enum error is forgetting to handle a newly added variant:

```text
error[E0004]: non-exhaustive patterns: `Connection::Connecting { .. }` not covered
```

Fix it by adding an explicit arm when the variant has domain meaning. Use `_` only when all remaining
variants really share one behavior; otherwise you lose the compiler prompt that makes enum refactors
safe.

## Best practice
- ✅ Use enums for closed sets of states instead of string or integer constants; see [[Stringly-Typed Code]].
- ✅ Put behavior that naturally belongs to the enum in an `impl` block.
- ✅ Prefer meaningful variants that model the domain, then let [[Exhaustiveness]] force every user to handle them.
- ✅ Keep enum variants at one abstraction level; avoid mixing transport details, UI labels, and business states in one enum.
- ✅ Derive `Debug`, `Copy`, `Clone`, `Eq`, or `Hash` only when the semantics are right for every variant payload.

## Pitfalls
- ⚠️ Do not encode enum-like state with sentinel values such as `0`, `-1`, or `""`; see [[Sentinel Values]].
- ⚠️ Do not add a broad `_` arm too early when matching your own enum; it can hide future variants. See [[Overbroad Catch-All Match Arms]].
- ⚠️ Do not use an enum when callers must add new cases outside your crate; a trait object or generic trait bound may fit better.
- ⚠️ Avoid relying on enum memory layout across FFI boundaries unless you use an explicit representation and understand its limits.
- ⚠️ A large payload in one variant can make every enum value large; box rare, bulky payloads if size matters.

## See also
[[Enum Variants with Data]] · [[Option]] · [[The match Expression]] · [[Patterns]] · [[Exhaustiveness]] · [[Destructuring]] · [[Match Guards]] · [[Binding with @]] · [[Catch-All and Wildcard Patterns]] · [[Overbroad Catch-All Match Arms]] · [[Stringly-Typed Code]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.1 "Defining an Enum" - [[the-book]], https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html
- The Rust Programming Language, ch. 6 "Enums and Pattern Matching" - [[the-book]], https://doc.rust-lang.org/book/ch06-00-enums.html
