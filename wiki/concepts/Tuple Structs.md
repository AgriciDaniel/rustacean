---
type: concept
title: "Tuple Structs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, tuple-structs, newtypes]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Tuples]]", "[[Newtype Pattern]]", "[[Unit-Like Structs]]", "[[Using Type Aliases as Newtypes]]", "[[Pattern Matching]]", "[[Visibility and Privacy]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-01-defining-structs.html", "https://doc.rust-lang.org/reference/items/structs.html", "https://doc.rust-lang.org/reference/expressions/struct-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Tuple Structs

Tuple structs are named tuple-shaped structs that create distinct types while keeping positional fields.

## What it is
A tuple struct is declared as `struct Name(T1, T2, ...);`.
It has a real type name like any other struct, but its fields are accessed by numeric position rather than by field name.

This is useful when a tuple's positions are already conventional or obvious, but the tuple still needs a domain-specific type.
Two tuple structs with identical field types are still different types, so `Color(u8, u8, u8)` and `Point(u8, u8, u8)` cannot be passed to each other's APIs by accident.

## How it works
Construct tuple structs with function-call-like syntax: `Meters(3.0)`.
Access fields with `.0`, `.1`, and so on.
Destructure them by writing the type name in the pattern: `let Point(x, y) = point;`.

A one-field tuple struct is the core shape used by the [[Newtype Pattern]].
Unlike a type alias, it creates a distinct type that can enforce units, hide representation, or support trait implementations.

Tuple struct constructors live in the value namespace, so `Meters` can be used like a function that takes the field values and returns `Meters`.
This is why `let make = Meters; let distance = make(3.0);` works for public tuple fields.
Field visibility still matters: a public tuple struct with private fields can be named by downstream crates but not constructed or destructured directly.
The Reference also permits curly-brace construction with numeric field names, such as `Color { 0: 255, 1: 0, 2: 0 }`, but the call form is the idiomatic form.

## Example
```rust
#[derive(Debug, Copy, Clone, PartialEq)]
struct Meters(f64);

#[derive(Debug, Copy, Clone, PartialEq)]
struct Seconds(f64);

fn speed(distance: Meters, time: Seconds) -> f64 {
    distance.0 / time.0
}

fn main() {
    let distance = Meters(120.0);
    let time = Seconds(10.0);
    let Meters(raw_distance) = distance;

    println!("{distance:?} over {time:?}");
    println!("raw distance = {raw_distance}");
    println!("speed = {}", speed(distance, time));
}
```

## Worked example
```rust
#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
struct UserId(u64);

#[derive(Debug)]
struct User {
    id: UserId,
    name: String,
}

fn load_user(id: UserId) -> User {
    User {
        id,
        name: format!("user-{}", id.0),
    }
}

fn main() {
    let id = UserId(42);
    let user = load_user(id);
    let UserId(raw_id) = user.id;

    println!("{user:?}");
    println!("raw id = {raw_id}");
}
```

This is a typical newtype-style tuple struct: the representation is a `u64`, but APIs must opt in to accepting a `UserId`.
That prevents accidentally passing an unrelated `u64` where a domain identity is required.

## Common errors
Two tuple structs with identical fields are still different types:

```rust
struct Color(u8, u8, u8);
struct Point(u8, u8, u8);

fn draw_at(point: Point) {
    println!("{}, {}, {}", point.0, point.1, point.2);
}

fn main() {
    let red = Color(255, 0, 0);
    draw_at(red);
}
```

```console
error[E0308]: mismatched types
  = note: expected struct `Point`
             found struct `Color`
```

Fix it by constructing the expected type explicitly, converting through a named function, or using a shared domain type only when the values truly mean the same thing.

## Best practice
- ✅ Use tuple structs when the type name carries most of the meaning and field names would add little.
- ✅ Prefer a one-field tuple struct over a type alias when you need type safety; see [[Newtype Pattern]].
- ✅ Derive obvious traits such as `Debug`, `Copy`, `Clone`, and `PartialEq` when the fields support them.
- ✅ Keep tuple structs small; many positional fields become hard to read.
- ✅ Make tuple fields private in public APIs when you want constructors to enforce validation.
- ✅ Add small accessor methods when direct `.0` access would leak too much representation detail.

## Pitfalls
- ⚠️ Positional fields can hide meaning in wider data shapes; choose [[Named Field Structs]] when readers need labels.
- ⚠️ A type alias does not create a new type; see [[Using Type Aliases as Newtypes]].
- ⚠️ Reordering tuple struct fields is a breaking API change if the type is public.
- ⚠️ Public tuple fields make `.0` part of your API; changing representation later can break callers.
- ⚠️ Deriving `Ord` on a multi-field tuple struct orders lexicographically by field position, which may not match the domain.

## See also
[[Structs]] · [[Named Field Structs]] · [[Tuples]] · [[Newtype Pattern]] · [[Unit-Like Structs]] · [[Deriving Traits on Structs]] · [[Pattern Matching]] · [[Using Type Aliases as Newtypes]] · [[Visibility and Privacy]] · [[Copy and Clone]]

## Sources
- The Rust Programming Language, ch. 5.1 "Creating Different Types with Tuple Structs" — [[the-book]], https://doc.rust-lang.org/book/ch05-01-defining-structs.html
- The Rust Reference, "Structs" — [[the-reference]], https://doc.rust-lang.org/reference/items/structs.html
- The Rust Reference, "Struct expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/struct-expr.html
