---
type: concept
title: "Match Guards"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, match, guards, patterns]
domain: "Enums & Pattern Matching"
difficulty: intermediate
related: ["[[The match Expression]]", "[[Patterns]]", "[[Pattern Variable Shadowing]]", "[[Exhaustiveness]]", "[[Binding with @]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#adding-conditionals-with-match-guards", "https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#matching-named-variables"]
rust_version: "edition 2024 / 1.85+"
---

# Match Guards

A match guard is an `if` condition attached to a `match` arm after the pattern, and the arm is chosen only when both the pattern and condition match.

## What it is
Match guards handle conditions that pattern syntax cannot express by itself.
They are written as `PATTERN if condition => expression`.
The condition can use variables bound by the pattern and variables from the outer scope.

Guards are available on `match` arms.
They are not the same thing as `if let` conditions, and the Book notes them as a `match` feature.
Use guards when the structural shape is easy to match but a semantic predicate decides the exact case.

## How it works
Rust first checks whether the pattern matches.
If it does, Rust evaluates the guard.
If the guard is true, that arm runs.
If the guard is false, matching continues with later arms.

A guard applies to an entire `|` pattern group.
`4 | 5 | 6 if enabled` means `(4 | 5 | 6) if enabled`, not `4 | 5 | (6 if enabled)`.
Because arbitrary conditions can be involved, guarded arms often need an unguarded fallback for the same shape.

Guards are evaluated only after the pattern has matched and its bindings are available. If the guard
is false, matching resumes at the next arm as though that arm had not matched. The guard expression
does not introduce pattern bindings; names inside it follow normal expression name lookup, which is why
guards are the right tool for comparing a bound value with an outer variable.

Because guards are arbitrary boolean expressions, the exhaustiveness checker cannot treat a guarded arm
as covering every value of that pattern. `Some(n) if n > 0` narrows `Some`, but it does not cover
`Some(0)` or negative values; add `Some(_)` when all remaining present values should be handled.

## Example
```rust
fn classify(value: Option<i32>, forbidden: i32) -> &'static str {
    match value {
        Some(n) if n == forbidden => "forbidden",
        Some(n) if n % 2 == 0 => "even",
        Some(_) => "odd",
        None => "missing",
    }
}

fn main() {
    assert_eq!(classify(Some(10), 10), "forbidden");
    assert_eq!(classify(Some(8), 10), "even");
    assert_eq!(classify(None, 10), "missing");
}
```

## Worked example
```rust
enum Command {
    Resize { width: u16, height: u16 },
    Write(String),
    Quit,
}

fn validate(command: &Command, max_area: u32) -> &'static str {
    match command {
        Command::Resize { width, height } if u32::from(*width) * u32::from(*height) > max_area => {
            "too large"
        }
        Command::Resize { width: 0, .. } | Command::Resize { height: 0, .. } => "empty",
        Command::Resize { .. } => "resize",
        Command::Write(text) if text.trim().is_empty() => "blank write",
        Command::Write(_) => "write",
        Command::Quit => "quit",
    }
}

fn main() {
    assert_eq!(validate(&Command::Resize { width: 80, height: 24 }, 10_000), "resize");
    assert_eq!(validate(&Command::Write(String::from("   ")), 10_000), "blank write");
}
```

## Common errors
Relying on only guarded arms can still be non-exhaustive:

```text
error[E0004]: non-exhaustive patterns: `Some(_)` not covered
```

Fix it by adding an unguarded fallback for the same shape, such as `Some(_) => ...`, or by replacing
the guard with a literal/range/or-pattern when the condition is structural.

## Best practice
- ✅ Use a guard to compare a pattern binding with an outer variable without shadowing it.
- ✅ Keep guards side-effect-free and cheap so the match remains readable.
- ✅ Add an unguarded arm for the same broad pattern when the guard is only a refinement.
- ✅ Prefer literal, range, and `|` patterns when they can express the condition without a guard.
- ✅ Put guarded refinements before their unguarded fallback because arm order decides behavior.

## Pitfalls
- ⚠️ Do not write `Some(y)` expecting to compare with an outer `y`; use `Some(n) if n == y`. See [[Pattern Variable Shadowing]].
- ⚠️ Do not assume a guarded arm covers all values of its pattern; the guard can be false.
- ⚠️ Do not use guards when a literal, range, or `|` pattern communicates the case more directly.
- ⚠️ Avoid guards with side effects; later refactors that change arm order can change when they run.
- ⚠️ Do not let a complex guard hide business rules that deserve a named predicate.

## See also
[[The match Expression]] · [[Patterns]] · [[Pattern Variable Shadowing]] · [[Exhaustiveness]] · [[Binding with @]] · [[if let]] · [[Refutable and Irrefutable Patterns]] · [[Catch-All and Wildcard Patterns]] · [[Enums]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 19.3 "Adding Conditionals with Match Guards" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#adding-conditionals-with-match-guards
- The Rust Programming Language, ch. 19.3 "Matching Named Variables" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#matching-named-variables
