---
type: antipattern
title: "Pattern Variable Shadowing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, patterns, shadowing, footgun]
domain: "Enums & Pattern Matching"
difficulty: intermediate
related: ["[[Patterns]]", "[[Match Guards]]", "[[The match Expression]]", "[[Shadowing]]", "[[if let]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#matching-named-variables", "https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#adding-conditionals-with-match-guards"]
rust_version: "edition 2024 / 1.85+"
---

# Pattern Variable Shadowing

Pattern variable shadowing happens when a name in a pattern creates a new binding instead of comparing with an existing variable of the same name.

## The mistake
The mistake is writing a pattern such as `Some(y)` and expecting it to mean "match `Some` containing the outer variable `y`."
In Rust, `y` in that pattern is a new binding.
It matches any inner value and shadows the outer `y` only inside that arm.

This is easy to miss because literal patterns do compare directly.
`Some(10)` tests for the value `10`, but `Some(y)` binds a fresh name.

## Why it happens
Patterns use bare identifiers as bindings by default.
That rule makes destructuring concise, but it means equality with an outer variable needs a different tool.
The usual fix is to bind a new name and add a [[Match Guards]] condition.

Use `Some(n) if n == y` to compare with an outer `y`.
The guard expression is not a pattern, so `y` there refers to the outer binding.

This behavior is not limited to `match`. It appears in [[if let]], `while let`, `let else`, closure
parameters, and any other pattern position. A bare lowercase identifier usually binds. A path pattern
can compare against a constant or enum variant, but relying on lowercase constants is hard to read;
prefer named constants such as `TARGET` or use a guard.

The compiler is doing normal lexical shadowing: the inner pattern binding exists only in the arm or
block where it was introduced, and the outer variable is visible again afterward. The bug is semantic,
not memory unsafe, so it often compiles cleanly while doing the wrong thing.

## Example
```rust
fn compare_to_target(value: Option<i32>, target: i32) -> &'static str {
    match value {
        Some(50) => "exactly fifty",
        Some(n) if n == target => "matched target",
        Some(_) => "some other number",
        None => "missing",
    }
}

fn main() {
    assert_eq!(compare_to_target(Some(5), 10), "some other number");
    assert_eq!(compare_to_target(Some(10), 10), "matched target");
}
```

## Worked example
```rust
const ADMIN_ID: u32 = 1;

fn role_for(user_id: Option<u32>, selected: u32) -> &'static str {
    match user_id {
        Some(ADMIN_ID) => "admin",
        Some(id) if id == selected => "selected",
        Some(_) => "user",
        None => "anonymous",
    }
}

fn main() {
    assert_eq!(role_for(Some(1), 99), "admin");
    assert_eq!(role_for(Some(42), 42), "selected");
    assert_eq!(role_for(Some(7), 42), "user");
}
```

## Common errors
This antipattern often has no compiler error. The suspicious code compiles:

```rust
fn main() {
    let y = 10;

    match Some(5) {
        Some(y) => println!("matched inner {y}"),
        None => {}
    }

    assert_eq!(y, 10);
}
```

If you expected `y` to refer to an outer variable, the fix is:

```rust
fn main() {
    let y = 10;

    match Some(5) {
        Some(n) if n == y => println!("matched outer y"),
        _ => {}
    }
}
```

## Best practice
- ✅ Use a different binding name in the pattern, then compare to the outer value in a match guard.
- ✅ Prefer literals or ranges directly in the pattern when the comparison value is fixed.
- ✅ Keep outer names and pattern binding names distinct in complex matches.
- ✅ Use ALL_CAPS constants for constant patterns so they are visually different from bindings.
- ✅ Add tests for equality-sensitive matches, especially when one arm is meant to compare against runtime state.

## Pitfalls
- ⚠️ Do not assume `Some(y)` compares to an existing `y`; it binds a new `y`.
- ⚠️ Do not hide this issue with a broad `_` fallback; make the intended equality explicit.
- ⚠️ Watch for the same shadowing behavior in [[if let]] and `while let`.
- ⚠️ Do not use a lowercase constant name in a pattern if readers may mistake it for a binding.
- ⚠️ Be careful with or-patterns: every alternative must bind the same names with compatible types.

## See also
[[Patterns]] · [[Match Guards]] · [[The match Expression]] · [[Shadowing]] · [[if let]] · [[Binding with @]] · [[Exhaustiveness]] · [[Catch-All and Wildcard Patterns]] · [[Refutable and Irrefutable Patterns]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 19.3 "Matching Named Variables" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#matching-named-variables
- The Rust Programming Language, ch. 19.3 "Adding Conditionals with Match Guards" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#adding-conditionals-with-match-guards
