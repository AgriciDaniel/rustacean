---
type: concept
title: "Unit-Like Structs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, unit-like, zero-sized-types]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Tuple Structs]]", "[[Traits]]", "[[Marker Traits]]", "[[Deriving Traits on Structs]]", "[[Zero-Cost Abstractions]]", "[[Visibility and Privacy]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/items/structs.html", "https://doc.rust-lang.org/reference/expressions/struct-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Unit-Like Structs

Unit-like structs are fieldless struct types used when a named type needs behavior, identity, or trait implementations but no stored data.

## What it is
A unit-like struct is declared with only a name and a semicolon: `struct AlwaysEqual;`.
It is called unit-like because its value has no fields, similar to the unit value `()`, but it is still a distinct named type.

Use a unit-like struct when the type itself carries the meaning.
Common examples include marker values, stateless services, test doubles, and types whose behavior is entirely in trait implementations.

## How it works
Declare and instantiate a unit-like struct with the same bare name.
There are no braces, parentheses, or field values.
Because there is no instance data to inspect, useful behavior usually comes from `impl` blocks or trait implementations.

Unit-like structs are also a simple way to name a zero-sized type.
They can be passed around like ordinary values, but their meaning is in the type, not in stored state.

A unit-like struct introduces both a type and a value-like constructor in the value namespace.
The bare path `AlwaysApprove` denotes the only value of that type.
The Reference also allows `AlwaysApprove {}` as a struct expression, but the bare name is the idiomatic construction form.
Because there are no fields, moving or copying the value has no payload to move; the type can still have meaningful trait implementations and method calls.

## Example
```rust
struct AlwaysApprove;

impl AlwaysApprove {
    fn allows(&self, _action: &str) -> bool {
        true
    }
}

fn main() {
    let policy = AlwaysApprove;

    if policy.allows("publish") {
        println!("allowed");
    }
}
```

## Worked example
```rust
trait Clock {
    fn now_millis(&self) -> u64;
}

struct FixedClock;

impl Clock for FixedClock {
    fn now_millis(&self) -> u64 {
        1_700_000_000_000
    }
}

fn cache_key(clock: &impl Clock, user_id: u64) -> String {
    format!("user:{user_id}:{}", clock.now_millis())
}

fn main() {
    let clock = FixedClock;
    println!("{}", cache_key(&clock, 42));
}
```

This shape is common in tests and generic code: the type supplies behavior through a trait, but each value carries no runtime configuration.

## Common errors
Unit-like structs are constructed with a bare path, not tuple-call syntax:

```rust
struct Marker;

fn main() {
    let _marker = Marker();
}
```

```console
error[E0618]: expected function, found `Marker`
```

Fix it by writing `let marker = Marker;`, or change the definition to a tuple struct such as `struct Marker();` if call syntax is intentionally part of the API.

## Best practice
- ✅ Use unit-like structs for stateless behavior that still deserves a named type.
- ✅ Implement traits on a unit-like struct when you need a concrete type but no fields.
- ✅ Keep construction obvious: `let value = TypeName;`.
- ✅ Use [[Named Field Structs]] instead when each instance must carry configuration or runtime state.
- ✅ Derive `Debug`, `Copy`, `Clone`, `Default`, `PartialEq`, or `Eq` when those semantics make the marker easier to use.
- ✅ Prefer a unit-like type over a global function when the behavior needs to satisfy a trait bound.

## Pitfalls
- ⚠️ Do not use a unit-like struct when future state is already known; changing it into a fielded struct can break construction syntax.
- ⚠️ Avoid global mutable state hidden behind a stateless type; make state explicit in [[Structs]].
- ⚠️ Deriving traits is easy, but derived equality on a fieldless type means all instances compare the same by construction.
- ⚠️ A unit-like struct is not a singleton with runtime identity; it is just a zero-sized value of a named type.
- ⚠️ If callers need to configure behavior, adding fields later changes construction and may require a migration path through [[Associated Functions]].

## See also
[[Structs]] · [[Named Field Structs]] · [[Tuple Structs]] · [[Methods]] · [[Associated Functions]] · [[Traits]] · [[Marker Traits]] · [[Zero-Cost Abstractions]] · [[Deriving Traits on Structs]] · [[Visibility and Privacy]]

## Sources
- The Rust Programming Language, ch. 5.1 "Defining Unit-Like Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Structs" — [[the-reference]], https://doc.rust-lang.org/reference/items/structs.html
- The Rust Reference, "Struct expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/struct-expr.html
