---
type: concept
title: "Enum Variants with Data"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, enums, variants, data-modeling]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Enums]]", "[[Destructuring]]", "[[The match Expression]]", "[[Patterns]]", "[[Option]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html", "https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#destructuring-to-break-apart-values"]
rust_version: "edition 2024 / 1.85+"
---

# Enum Variants with Data

Enum variants can carry their own data, so one enum can represent several shapes of related values without losing type safety.

## What it is
A variant may be unit-like, tuple-like, or struct-like.
That means an enum can represent cases with no payload, positional payloads, or named fields.
This is one of the main reasons [[Enums]] are more expressive than a separate `kind` field plus optional data fields.

The payload belongs only to that variant.
For example, a `Move` message can have coordinates while a `Quit` message has no data.
The compiler will not let you read coordinates unless you have matched the `Move` variant.

## How it works
Each variant constructor is namespaced under the enum name.
Tuple-like variants are called like functions: `Message::Write(String::from("hi"))`.
Struct-like variants use field syntax: `Message::Move { x: 1, y: 2 }`.

To use the payload, match the variant and destructure it with the same shape used to define it.
Borrowing in the match expression lets you inspect a message without consuming it.
Moving in the match expression transfers ownership of any non-`Copy` payloads you bind.

The discriminant says which variant is active; only that variant's fields are initialized and valid.
Pattern matching is the safe way to prove to the compiler which payload can be read. This is different
from a struct with `kind: Kind` plus several optional fields, where the compiler cannot know that
`kind == Move` implies `x` and `y` are present.

Variant constructors are values too. `Message::Write` can be passed to iterator adapters as a function
from `String` to `Message`, while struct-like variants are constructed with named-field syntax. Payload
ownership follows normal [[Ownership]] rules: matching by value consumes non-`Copy` fields, matching
`&message` borrows them, and `ref`/`ref mut` can request references in a by-value pattern.

## Example
```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

fn summarize(message: &Message) -> String {
    match message {
        Message::Quit => String::from("quit"),
        Message::Move { x, y } => format!("move to ({x}, {y})"),
        Message::Write(text) => format!("write {text}"),
        Message::ChangeColor(r, g, b) => format!("rgb({r}, {g}, {b})"),
    }
}

fn main() {
    let message = Message::Move { x: 3, y: 4 };
    assert_eq!(summarize(&message), "move to (3, 4)");
}
```

## Worked example
```rust
enum Job {
    Sleep,
    Fetch { url: String, retries: u8 },
    Compute(Vec<i64>),
}

fn cost(job: &Job) -> usize {
    match job {
        Job::Sleep => 0,
        Job::Fetch { url, retries } => url.len() + usize::from(*retries),
        Job::Compute(values) => values.len() * 10,
    }
}

fn main() {
    let job = Job::Fetch {
        url: String::from("https://example.invalid"),
        retries: 2,
    };

    assert_eq!(cost(&job), 25);
}
```

## Common errors
Moving a payload out while still using the original enum produces a moved-value error:

```text
error[E0382]: borrow of partially moved value
```

Fix it by matching a reference (`match &message`) or by borrowing a field in the pattern
(`Message::Write(ref text)`) when the original enum must remain usable.

## Best practice
- ✅ Put data directly on the variant that owns it instead of storing many unrelated optional fields.
- ✅ Use struct-like variants when field names clarify meaning or when variants may gain more fields.
- ✅ Match by reference when you only need to inspect payloads; match by value when consuming them is intended.
- ✅ Keep variant payloads minimal and invariant-preserving; if a payload has its own rules, introduce a named struct.
- ✅ Box rare, very large payloads if enum size affects hot collections or stack usage.

## Pitfalls
- ⚠️ Do not create a `kind` enum plus separate nullable payload fields when a data-carrying enum models the invariant directly.
- ⚠️ Do not bind a non-`Copy` payload by value if you still need the original enum afterward; borrow it or match on `&value`.
- ⚠️ Avoid a final `_` arm while designing a public enum inside your own crate; see [[Overbroad Catch-All Match Arms]].
- ⚠️ Do not use positional tuple-like variants for several same-typed fields when names would prevent swaps.
- ⚠️ Avoid exposing payload types you may need to change unless the enum is internal or intentionally stable.

## See also
[[Enums]] · [[Destructuring]] · [[The match Expression]] · [[Patterns]] · [[Option]] · [[Ownership]] · [[Refutable and Irrefutable Patterns]] · [[Catch-All and Wildcard Patterns]] · [[Overbroad Catch-All Match Arms]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.1 "Defining an Enum" - [[the-book]], https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html
- The Rust Programming Language, ch. 19.3 "Pattern Syntax" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#destructuring-to-break-apart-values
