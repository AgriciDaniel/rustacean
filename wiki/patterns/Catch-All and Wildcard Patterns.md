---
type: pattern
title: "Catch-All and Wildcard Patterns"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, patterns, wildcard, match]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Patterns]]", "[[The match Expression]]", "[[Exhaustiveness]]", "[[Destructuring]]", "[[Overbroad Catch-All Match Arms]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-02-match.html#catch-all-patterns-and-the-_-placeholder", "https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#ignoring-values-in-a-pattern"]
rust_version: "edition 2024 / 1.85+"
---

# Catch-All and Wildcard Patterns

Catch-all patterns cover remaining values in a match, and `_` is the wildcard form that matches without binding.

## What it is
A catch-all pattern is any pattern that matches all values not matched by earlier arms.
The common forms are a named binding such as `other` and the wildcard `_`.
Use a named binding when the fallback arm still needs the value.
Use `_` when the value is intentionally ignored.

Inside larger patterns, `_` ignores one piece and `..` ignores the remaining pieces.
An underscore-prefixed name such as `_value` still binds the value; it only suppresses the unused-variable warning.

## How it works
Match arms are ordered.
A catch-all arm should almost always be last because it prevents later arms from being reached.
The wildcard satisfies [[Exhaustiveness]] without introducing a binding.

`..` expands to the number of fields or tuple positions needed to ignore the rest.
It must be unambiguous.
For example, `(first, .., last)` is clear, but `(.., middle, ..)` is not.

`_` and a named catch-all are both irrefutable, but they have different ownership behavior. `_` does
not bind, copy, move, or borrow the ignored value. A name such as `other` binds the value, and an
underscore-prefixed name such as `_other` also binds even though it suppresses an unused-variable
warning. This matters for non-`Copy` payloads.

Catch-all patterns are a tool for open value spaces and genuinely equivalent remainders. They are less
appropriate for small domain enums you own, because explicit variants let [[Exhaustiveness]] tell you
when a future variant needs a decision.

## Example
```rust
enum Command {
    Save,
    Load,
    Quit,
    Unknown(String),
}

fn handle(command: Command) -> String {
    match command {
        Command::Save => String::from("saved"),
        Command::Load => String::from("loaded"),
        Command::Quit => String::from("quit"),
        Command::Unknown(text) => format!("unknown command: {text}"),
    }
}

fn main() {
    assert_eq!(handle(Command::Unknown(String::from("sync"))), "unknown command: sync");
}
```

## Worked example
```rust
struct WindowEvent {
    window_id: u32,
    kind: EventKind,
}

enum EventKind {
    Close,
    Key(char),
    Resize { width: u32, height: u32 },
}

fn route(event: WindowEvent) -> String {
    match event {
        WindowEvent { window_id: 0, kind: EventKind::Close } => String::from("main close"),
        WindowEvent { window_id, kind: EventKind::Key('q') } => format!("quit from {window_id}"),
        WindowEvent { kind: EventKind::Resize { width, height }, .. } => {
            format!("resize to {width}x{height}")
        }
        WindowEvent { window_id, .. } => format!("ignored event from {window_id}"),
    }
}

fn main() {
    let event = WindowEvent { window_id: 2, kind: EventKind::Key('x') };
    assert_eq!(route(event), "ignored event from 2");
}
```

## Common errors
A catch-all placed too early makes later arms unreachable:

```text
warning: unreachable pattern
```

Fix it by ordering arms from most specific to broadest. If an underscore-prefixed binding moves a
value, replace it with `_` when you truly do not need the value.

## Best practice
- ✅ Use `_` when ignoring a value is part of the design, not a shortcut around thinking through cases.
- ✅ Use a named catch-all such as `other` when you need to log, return, or process the unmatched value.
- ✅ Prefer `..` for large structs when only a few fields are relevant.
- ✅ Place catch-all arms last and keep a comment or arm name clear when the fallback is policy.
- ✅ Use explicit variants for closed domain enums until the repeated behavior is unquestionably identical.

## Pitfalls
- ⚠️ Do not put `_` before more specific arms; later arms become unreachable.
- ⚠️ Do not hide future domain decisions behind `_`; see [[Overbroad Catch-All Match Arms]].
- ⚠️ Do not confuse `_value` with `_`: `_value` still binds and can move ownership.
- ⚠️ Do not use `..` in two places in one tuple or slice pattern; Rust cannot infer how to split the ignored elements.
- ⚠️ Do not log a named catch-all by value if logging can borrow; moving may prevent later use.

## See also
[[Patterns]] · [[The match Expression]] · [[Exhaustiveness]] · [[Destructuring]] · [[Overbroad Catch-All Match Arms]] · [[Ownership]] · [[Enum Variants with Data]] · [[Pattern Variable Shadowing]] · [[Refutable and Irrefutable Patterns]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.2 "Catch-All Patterns and the _ Placeholder" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html#catch-all-patterns-and-the-_-placeholder
- The Rust Programming Language, ch. 19.3 "Ignoring Values in a Pattern" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#ignoring-values-in-a-pattern
