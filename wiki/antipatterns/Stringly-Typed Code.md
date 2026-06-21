---
type: antipattern
title: "Stringly-Typed Code"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, types, newtype, enum, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Newtype Pattern]]", "[[Enums]]", "[[Type Aliases]]", "[[Custom Error Types]]", "[[Stringly-Typed Errors]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-00-enums.html", "https://doc.rust-lang.org/book/ch20-03-advanced-types.html", "https://doc.rust-lang.org/std/string/struct.String.html"]
rust_version: "edition 2024 / 1.85+"
---

# Stringly-Typed Code

Stringly-typed code represents structured domain facts as loose `String` or `&str` values when enums, newtypes, or dedicated structs would let the compiler enforce the rules.

## The mistake
Strings are excellent for text. They are poor substitutes for domain types. If a user ID, order ID, state, unit, permission, or protocol command is passed as a string, every caller can accidentally pass the wrong string and every callee must validate again.

The same smell appears with bare integers and booleans: `fn configure(true, false, true)` and `fn transfer(12, 34, 50)` carry too little meaning at the type level.

## Why it happens
Strings are easy at boundaries: command-line args, environment variables, JSON, HTTP, and databases all provide text. The mistake is letting boundary representation leak into the core model.

Rust gives you cheap ways to make invalid states harder to represent. Enums model closed sets. Newtype structs distinguish values with the same representation. Type aliases improve readability but do not create a distinct type.

The compiler can only protect distinctions that appear in types. `String` and `&str` say "valid UTF-8 text"; they do not say "known user ID", "state accepted by this protocol", or "meters rather than feet". A newtype has the same runtime representation after optimization, but it gives the type checker a separate name and a place to put validation and methods.

Enums also centralize change. Adding a new variant forces relevant `match` expressions to be reconsidered, while adding a new magic string relies on search, tests, and memory.

## Example
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct UserId(u64);

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct OrderId(u64);

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum OrderState {
    Draft,
    Submitted,
    Shipped,
}

fn can_edit(_user: UserId, state: OrderState) -> bool {
    matches!(state, OrderState::Draft | OrderState::Submitted)
}

fn main() {
    let user = UserId(7);
    let _order = OrderId(7);

    println!("{}", can_edit(user, OrderState::Draft));
    println!("{:?}", OrderState::Shipped);
}
```

## Second example: parse at the boundary
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Command {
    Start,
    Stop,
    Status,
}

impl TryFrom<&str> for Command {
    type Error = String;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        match value {
            "start" => Ok(Self::Start),
            "stop" => Ok(Self::Stop),
            "status" => Ok(Self::Status),
            other => Err(format!("unknown command: {other}")),
        }
    }
}

fn run(command: Command) {
    match command {
        Command::Start => println!("starting"),
        Command::Stop => println!("stopping"),
        Command::Status => println!("status"),
    }
}

fn main() -> Result<(), String> {
    let raw = "status";
    let command = Command::try_from(raw)?;
    run(command);
    Ok(())
}
```

After parsing, the core program cannot accidentally call `run("statsu")`; misspellings are boundary errors, not latent branches.

## Common errors
Newtype mismatch:

```text
error[E0308]: mismatched types
```

This is the desired failure when `OrderId` is passed where `UserId` is required. Fix the caller's data flow, or convert explicitly in the rare case where conversion is meaningful.

Type alias non-error:

```text
type UserIdAlias = u64;
type OrderIdAlias = u64;
```

Aliases improve names in signatures, but the compiler still treats both as `u64`. Use `struct UserId(u64);` and `struct OrderId(u64);` when mixups must be rejected.

## Best practice
- ✅ Parse strings at the boundary and convert them into domain types quickly.
- ✅ Use enums for known finite states instead of matching on magic strings.
- ✅ Use newtypes for IDs, units, tokens, and other values with the same primitive representation.
- ✅ Keep display text separate from programmatic identity; `Display` output is for humans.
- ✅ Implement `FromStr` or `TryFrom<&str>` for boundary parsing when a string must become a domain value.
- ✅ Keep newtype fields private when construction must validate invariants.

## Pitfalls
- ⚠️ A type alias such as `type UserId = u64` does not prevent passing an `OrderId` alias where a user ID is expected.
- ⚠️ Stringly errors force callers to inspect messages; prefer structured errors. See [[Stringly-Typed Errors]].
- ⚠️ Overusing `String` can force avoidable allocations; many read-only APIs should accept `&str`.
- ⚠️ Boolean parameter lists create call sites that are correct only by memory.
- ⚠️ Matching on localized or formatted text makes program behavior depend on human-facing output.
- ⚠️ Replacing every primitive with a type can add noise; focus on values whose mixups would be bugs.

## See also
[[Newtype Pattern]] · [[Enums]] · [[Type Aliases]] · [[Custom Error Types]] · [[Stringly-Typed Errors]] · [[Result]] · [[Option vs Result]] · [[Sentinel Values]] · [[Deref Polymorphism Antipattern]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 6 "Enums and Pattern Matching" — [[the-book]], https://doc.rust-lang.org/book/ch06-00-enums.html
- The Rust Programming Language, ch. 20.3 "Advanced Types" — [[the-book]], https://doc.rust-lang.org/book/ch20-03-advanced-types.html
- Standard library, `String` — [[the-reference]], https://doc.rust-lang.org/std/string/struct.String.html
