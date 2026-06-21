---
type: concept
title: "Practice: Enums"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, enums]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice (Rustlings)]]", "[[Enums]]", "[[Enum Variants with Data]]", "[[The match Expression]]", "[[Exhaustiveness]]", "[[Patterns]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Enums

The enums group teaches modeling a value that is exactly one of several variants. The key idea is to put the data for each case inside the variant that needs it, then handle all cases explicitly.

## What it is
These exercises cover defining enums, variants with and without payloads, matching variants, and calling methods that branch by variant.

## How it works
An enum value carries a discriminant plus any variant data. A `match` over an enum is checked for exhaustiveness, so adding or missing a case is visible at compile time.

## Example
```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}

fn handle(message: Message) -> String {
    match message {
        Message::Quit => String::from("quit"),
        Message::Move { x, y } => format!("move to {x},{y}"),
        Message::Write(text) => text,
    }
}

fn main() {
    println!("{}", handle(Message::Move { x: 2, y: 3 }));
}
```

## Best practice
- ✅ Use enums for closed sets of alternatives.
- ✅ Put variant-specific data in the variant rather than in parallel optional fields.
- ✅ Let exhaustive `match` document how every case is handled.

## Pitfalls
- ⚠️ Do not add wildcard arms too early; they can hide new variants that deserve explicit handling.
- ⚠️ Remember that matching by value may move payloads like `String`.
- ⚠️ Use `if let` only when ignoring other variants is intentional.

## See also
[[Practice (Rustlings)]] · [[Enums]] · [[Enum Variants with Data]] · [[The match Expression]] · [[Exhaustiveness]] · [[Patterns]] · [[Refutable and Irrefutable Patterns]]

## Sources
- Rustlings `08_enums` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

