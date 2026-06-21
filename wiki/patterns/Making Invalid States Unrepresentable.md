---
type: pattern
title: "Making Invalid States Unrepresentable"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, invariants, types, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[Newtype Pattern]]", "[[Type-State Pattern]]", "[[TryFrom and TryInto]]", "[[Sentinel Values]]", "[[Stringly-Typed Code]]"]
sources: ["[[the-book]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html", "https://doc.rust-lang.org/book/ch06-02-match.html", "https://doc.rust-lang.org/std/option/enum.Option.html", "https://doc.rust-lang.org/std/result/enum.Result.html"]
rust_version: "edition 2024 / 1.85+"
---

# Making Invalid States Unrepresentable

Making invalid states unrepresentable means designing types so impossible domain states cannot be constructed, not merely detected later.

## What it is
Many bugs come from broad representations: `String` for an email, `i32` with `-1` meaning missing, or several booleans whose combinations include nonsense.
Rust's enums, structs, privacy, `Option`, `Result`, and conversion traits let you narrow those representations.

The goal is to parse or validate at the boundary, then move precise types through the rest of the program.
Once the type exists, the compiler helps preserve the invariant.

## How it works
Use enums for alternatives, `Option<T>` for absence, [[Newtype Pattern]] for domain-specific scalars, and [[Type-State Pattern]] for protocol phases.
Keep fields private when construction must go through validation.
Expose constructors or [[TryFrom and TryInto]] implementations that reject invalid input.

This shifts correctness from repeated runtime checks into type checking.
You still need tests for constructors and transitions, but you need fewer tests for impossible downstream states.

The mechanism is ordinary Rust visibility and exhaustiveness.
Private fields prevent external code from manufacturing unchecked values.
Enums force callers to handle every state, and `match` becomes the place where the compiler verifies coverage.
`Option<T>` and `Result<T, E>` are not just containers; they are standard vocabulary for absence and failure, so APIs become easier to compose with `?`, `map`, and pattern matching.

This design often reduces the number of booleans in a type.
Two booleans have four combinations, even if the domain has only three valid states.
An enum with three variants has exactly three states.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct Email(String);

impl Email {
    fn new(value: String) -> Option<Self> {
        value.contains('@').then_some(Self(value))
    }
}

#[derive(Debug, PartialEq, Eq)]
enum Account {
    Guest,
    Registered { email: Email },
}

fn can_receive_mail(account: &Account) -> bool {
    matches!(account, Account::Registered { .. })
}

fn main() {
    let guest = Account::Guest;
    let registered = Account::Registered {
        email: Email::new(String::from("ferris@example.com")).unwrap(),
    };

    assert!(!can_receive_mail(&guest));
    assert!(can_receive_mail(&registered));
}
```

## Boolean-combination example
Replace flags with the state they meant to encode.

```rust
#[derive(Debug, PartialEq, Eq)]
enum Subscription {
    Trial { days_left: u8 },
    Active,
    Cancelled { reason: String },
}

fn can_access(subscription: &Subscription) -> bool {
    match subscription {
        Subscription::Trial { days_left } => *days_left > 0,
        Subscription::Active => true,
        Subscription::Cancelled { .. } => false,
    }
}

fn main() {
    let trial = Subscription::Trial { days_left: 7 };
    let cancelled = Subscription::Cancelled { reason: String::from("expired card") };

    assert!(can_access(&trial));
    assert!(!can_access(&cancelled));
}
```

## Common errors
Private invariant-bearing fields intentionally block external construction:

```text
error[E0451]: field `0` of struct `Email` is private
```

That error is the point of the design.
Call the checked constructor or `TryFrom` implementation instead of making the field public.
If tests need unchecked construction, consider a crate-private helper rather than weakening the public API.

## Best practice
- ✅ Replace related booleans with enums that name the real states.
- ✅ Replace sentinel values with `Option` or `Result`; see [[Sentinel Values]].
- ✅ Validate raw input once into a precise type, then pass that type around.
- ✅ Keep invariant-bearing fields private and expose checked construction.
- ✅ Use exhaustive `match` as documentation for the legal states and their behavior.
- ✅ Choose `Result<T, E>` over `Option<T>` when callers need to know why construction failed.

## Pitfalls
- ⚠️ Avoid catch-all enum variants such as `Unknown` unless the domain truly has that state.
- ⚠️ Do not expose public fields that let callers bypass validation.
- ⚠️ Do not keep a loose `String` or integer and revalidate it in every function; see [[Stringly-Typed Code]].
- ⚠️ Do not overfit the type model to today's UI flow if the domain state machine is still uncertain; small constructors can evolve more easily than public typestate generics.
- ⚠️ Avoid `Default` for invariant-bearing types unless there is a real, valid default state.

## See also
[[Newtype Pattern]] · [[Type-State Pattern]] · [[TryFrom and TryInto]] · [[Sentinel Values]] · [[Stringly-Typed Code]] · [[Option vs Result]] · [[Builder Pattern]] · [[Constructor Naming]] · [[Idioms & API Design]]

## Sources
- The Rust Programming Language, "Defining an Enum" - [[the-book]], https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html
- The Rust Programming Language, "`match` Control Flow Construct" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html
- `Option` - https://doc.rust-lang.org/std/option/enum.Option.html
- `Result` - https://doc.rust-lang.org/std/result/enum.Result.html
