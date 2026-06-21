---
type: concept
title: "The match Expression"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, match, pattern-matching, control-flow]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[Patterns]]", "[[Enums]]", "[[Option]]", "[[Exhaustiveness]]", "[[Match Guards]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-02-match.html", "https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html#match-arms"]
rust_version: "edition 2024 / 1.85+"
---

# The match Expression

`match` compares one value against ordered patterns, runs the first matching arm, and must account for every possible value.

## What it is
`match` is Rust's main pattern-based branching expression.
It is an expression, so it can produce a value.
Each arm has a pattern on the left of `=>` and an expression or block on the right.

Unlike `if`, which branches on booleans, `match` branches on the structure of data.
That makes it the natural tool for [[Enums]], [[Option]], [[Result]], tuples, structs, literals, and ranges.

## How it works
Rust tests arms from top to bottom and chooses the first pattern that matches.
Bindings introduced in a pattern are available only in that arm.
Every arm must produce a compatible type when the whole `match` is used as a value.

The compiler checks [[Exhaustiveness]].
For enums, this means every variant must be covered unless a catch-all arm covers the rest.
For integers or characters, a wildcard or range coverage may be needed.
Use [[Match Guards]] for conditions that cannot be expressed as patterns alone.

The matched expression is called the scrutinee. If the scrutinee is a place expression such as a local
variable, matching can borrow or move from that place according to the patterns used. If it is a value
expression such as a function call, the temporary is matched for the duration of the `match`.

Arm order is semantic, not decorative. Rust chooses the first matching arm, so a broad arm can make a
later one unreachable. When the `match` itself is used as an expression, all reachable arm bodies must
coerce to one result type; `return`, `break`, `continue`, and `panic!` can fit because they diverge.

## Example
```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(&'static str),
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => {
            println!("state quarter from {state}");
            25
        }
    }
}

fn main() {
    assert_eq!(value_in_cents(Coin::Quarter("Alaska")), 25);
}
```

## Worked example
```rust
enum Token {
    Word(String),
    Number(i64),
    Symbol(char),
}

fn render(token: &Token) -> String {
    match token {
        Token::Word(word) if word.len() > 8 => format!("long word: {word}"),
        Token::Word(word) => format!("word: {word}"),
        Token::Number(0) => String::from("zero"),
        Token::Number(n) => format!("number: {n}"),
        Token::Symbol(';' | ',') => String::from("separator"),
        Token::Symbol(ch) => format!("symbol: {ch}"),
    }
}

fn main() {
    assert_eq!(render(&Token::Number(0)), "zero");
    assert_eq!(render(&Token::Symbol(',')), "separator");
}
```

## Common errors
A missing arm produces an exhaustiveness error:

```text
error[E0004]: non-exhaustive patterns: `None` not covered
```

Fix it by adding the missing case or a deliberate catch-all. If you see an unreachable-pattern warning,
move the more specific pattern earlier or remove it because an earlier arm already covers it.

## Best practice
- ✅ Use `match` when multiple cases matter or when you want compiler-enforced [[Exhaustiveness]].
- ✅ Put more specific patterns before broader patterns because arms are tested in order.
- ✅ Let the match return a value when that makes control flow clearer than assigning in each arm.
- ✅ Match on references (`match &value`) for read-only classification of non-`Copy` data.
- ✅ Group equivalent literal or variant cases with `|` instead of duplicating identical arm bodies.

## Pitfalls
- ⚠️ A variable pattern like `Some(y)` creates a new binding; it does not compare with an outer `y`. See [[Pattern Variable Shadowing]].
- ⚠️ A catch-all `_` arm can make future enum changes invisible; see [[Overbroad Catch-All Match Arms]].
- ⚠️ Match guards add expressiveness, but guarded arms do not by themselves prove all values are covered; see [[Match Guards]].
- ⚠️ Avoid side effects in guards and arm ordering that make the match hard to reason about.
- ⚠️ Do not use `match` as a verbose replacement for a direct combinator when handling one simple `Option` transformation.

## See also
[[Patterns]] · [[Enums]] · [[Option]] · [[Exhaustiveness]] · [[Match Guards]] · [[Binding with @]] · [[Catch-All and Wildcard Patterns]] · [[Refutable and Irrefutable Patterns]] · [[Pattern Variable Shadowing]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.2 "The match Control Flow Construct" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html
- The Rust Programming Language, ch. 19.1 "All the Places Patterns Can Be Used" - [[the-book]], https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html#match-arms
