---
type: concept
title: "Destructuring"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, patterns, destructuring, enums]
domain: "Enums & Pattern Matching"
difficulty: intermediate
related: ["[[Patterns]]", "[[Enum Variants with Data]]", "[[The match Expression]]", "[[Catch-All and Wildcard Patterns]]", "[[Ownership]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#destructuring-to-break-apart-values", "https://doc.rust-lang.org/book/ch06-02-match.html#patterns-that-bind-to-values"]
rust_version: "edition 2024 / 1.85+"
---

# Destructuring

Destructuring is using a pattern to break a compound value into named pieces at the point where it is matched.

## What it is
Rust patterns can destructure tuples, structs, enum variants, nested enums, references, and combinations of these.
Destructuring binds only the pieces you name.
Other pieces can be ignored with `_` or `..`.

Destructuring keeps control flow close to the shape of the data.
Instead of matching a variant and then indexing or calling accessors, the pattern states exactly what must be present.

## How it works
For structs, match field names with `Point { x, y }` or rename them with `Point { x: horizontal, y: vertical }`.
For tuple-like variants, the number of pattern positions must match the payload shape.
For struct-like variants, use field syntax after the variant name.

Bindings may move fields out of a value.
When the matched expression is borrowed, match ergonomics usually binds references instead.
This is why `match &message` is often the right choice for read-only inspection.

A destructuring pattern is checked against the exact type shape. Tuple-like enum variants require the
right number of positions; struct-like variants require existing field names; tuple patterns require
the tuple arity to match. `..` can ignore the rest of a struct, tuple, tuple struct, array, or slice
where the language allows it, but it cannot appear twice in an ambiguous tuple or slice pattern.

Destructuring can cause partial moves. If one field of a non-`Copy` struct is moved and another is
borrowed, the moved field and the whole struct are no longer usable, though untouched fields may still
be usable in limited cases. Matching a reference avoids this when you only need to inspect.

## Example
```rust
enum Event {
    Resize { width: u32, height: u32 },
    Key(char),
    Quit,
}

fn describe(event: Event) -> String {
    match event {
        Event::Resize { width, height } => format!("{width}x{height}"),
        Event::Key('q') | Event::Quit => String::from("exit"),
        Event::Key(key) => format!("key {key}"),
    }
}

fn main() {
    assert_eq!(describe(Event::Resize { width: 80, height: 24 }), "80x24");
    assert_eq!(describe(Event::Key('q')), "exit");
}
```

## Worked example
```rust
struct Packet {
    id: u32,
    route: (&'static str, &'static str),
    payload: Option<String>,
}

fn summarize(packet: &Packet) -> String {
    match packet {
        Packet {
            id,
            route: ("client", destination),
            payload: Some(body),
        } => format!("#{id} to {destination}: {} bytes", body.len()),
        Packet { id, route: (_, destination), payload: None } => {
            format!("#{id} to {destination}: empty")
        }
        Packet { id, .. } => format!("#{id}: unsupported route"),
    }
}

fn main() {
    let packet = Packet { id: 7, route: ("client", "api"), payload: Some(String::from("ping")) };
    assert_eq!(summarize(&packet), "#7 to api: 4 bytes");
}
```

## Common errors
Shape mismatches are reported as type errors:

```text
error[E0027]: pattern does not mention field
```

Fix struct patterns by naming all required fields or adding `..` when ignoring the rest is intentional.
For moved-field errors such as `E0382`, match `&value` or bind fields with `ref`/`ref mut`.

## Best practice
- ✅ Destructure where it clarifies which fields or payloads are relevant.
- ✅ Use `..` for ignored struct fields when naming every field would add noise.
- ✅ Match by reference when destructuring non-`Copy` data only for inspection.
- ✅ Rename fields in the pattern (`x: horizontal`) when the local meaning differs from the field name.
- ✅ Use nested destructuring for simple invariants, but stop before the pattern becomes harder than code.

## Pitfalls
- ⚠️ Do not destructure by value accidentally when you still need the whole value later; see [[Ownership]].
- ⚠️ Do not use `..` ambiguously in tuple patterns; Rust allows it only where the ignored positions are clear.
- ⚠️ Avoid huge nested patterns when named helper functions or intermediate matches would be easier to read.
- ⚠️ Do not ignore public fields with `..` if adding a field should force you to revisit behavior.
- ⚠️ Be careful when destructuring references in edition 2024; rely on match ergonomics or explicit `as_ref()` first.

## See also
[[Patterns]] · [[Enum Variants with Data]] · [[The match Expression]] · [[Catch-All and Wildcard Patterns]] · [[Ownership]] · [[Tuples]] · [[Arrays]] · [[Refutable and Irrefutable Patterns]] · [[Binding with @]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 19.3 "Destructuring to Break Apart Values" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#destructuring-to-break-apart-values
- The Rust Programming Language, ch. 6.2 "Patterns That Bind to Values" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html#patterns-that-bind-to-values
