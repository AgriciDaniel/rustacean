---
type: concept
title: "The Guessing Game Tutorial"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, tutorial, cargo, beginner]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[crates.io and Dependencies Intro]]", "[[Result]]", "[[The match Expression]]", "[[Loop Expressions]]", "[[Variables and Mutability]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html", "https://doc.rust-lang.org/book/ch01-03-hello-cargo.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Guessing Game Tutorial

The Guessing Game is the Book's first complete Cargo project: it combines input, mutable strings, `Result`, parsing, matching, looping, and a crates.io dependency into one small executable.

## What it is
The game chooses a secret number from 1 through 100, repeatedly asks the user for
a guess, parses input into a number, compares the guess with the secret, and
exits when the user wins. It is intentionally small, but it touches many core
Rust habits in context.

For tooling, its most important lesson is iteration. The Book starts with
`cargo new guessing_game`, runs `cargo run` often, adds `rand` as a dependency,
observes Cargo downloading transitive crates, and lets compiler errors guide the
next fix.

## How it works
The tutorial starts with `String::new()` and `io::stdin().read_line(&mut guess)`
to read user input. `read_line` appends into a mutable string and returns a
`Result`, so beginner code calls `expect` at first and later handles parse errors
with `match`.

Adding `rand = "0.8.5"` under `[dependencies]` teaches the first dependency
workflow. Cargo downloads `rand` and its transitive dependencies from the
registry, compiles them, writes exact versions to [[Cargo.lock]], and reuses
unchanged work on later builds.

The tutorial also introduces inference boundaries. `"40".trim().parse()` needs
a target type, so the example annotates `let guess: u32`. `guess.cmp(&secret)`
uses a reference because `cmp` compares against another value without taking
ownership. The `loop` expression keeps the program alive until `break` exits on
the winning guess.

The code intentionally improves over time. Early `expect` calls are acceptable
while learning what `Result` is; the loop version should handle invalid user
input with `match` and `continue`, because bad input is expected user behavior,
not a programmer bug.

## Example
```rust
use std::cmp::Ordering;

fn main() {
    let secret = 42;
    let guess: u32 = "40".trim().parse().expect("number expected");

    match guess.cmp(&secret) {
        Ordering::Less => println!("Too small!"),
        Ordering::Greater => println!("Too big!"),
        Ordering::Equal => println!("You win!"),
    }
}
```

## Worked example
This helper captures the final tutorial's parse-and-compare core without
interactive input:

```rust
use std::cmp::Ordering;

fn compare_guess(input: &str, secret: u32) -> Option<Ordering> {
    let guess: u32 = match input.trim().parse() {
        Ok(number) => number,
        Err(_) => return None,
    };

    Some(guess.cmp(&secret))
}

fn main() {
    match compare_guess(" 42\n", 42) {
        Some(Ordering::Less) => println!("Too small!"),
        Some(Ordering::Greater) => println!("Too big!"),
        Some(Ordering::Equal) => println!("You win!"),
        None => println!("Please type a number."),
    }
}
```

This is not the full game, but it isolates two beginner lessons: trim input
before parsing, and model invalid input as a recoverable branch.

## Common errors
Ignoring `read_line`'s result triggers a must-use warning:

```text
warning: unused `Result` that must be used
```

Call `expect` for the tutorial's first draft, or handle the `Result` with
`match`, `?`, or another explicit error path.

Parsing without a target type leaves inference ambiguous:

```text
error[E0284]: type annotations needed
```

Annotate the binding (`let guess: u32 = ...`) or use turbofish syntax
(`parse::<u32>()`) so `parse` knows which `FromStr` implementation to use.

Forgetting to add `rand` produces an unresolved crate error:

```text
error[E0432]: unresolved import `rand`
```

Add the dependency to [[Cargo.toml Manifest]] or run `cargo add rand@0.8.5`
when following the Book's versioned tutorial.

## Best practice
- ✅ Use the tutorial as a survey, not as the final design for production input
  handling; later notes deepen [[Result]], [[The match Expression]], and
  [[Borrowing]].
- ✅ Run `cargo run` after each small change so compiler messages stay local to
  the change you just made.
- ✅ Replace "crash on bad input" code with explicit `match` handling as soon as
  the tutorial reaches the loop.
- ✅ Remove temporary debug output, such as printing the secret number, before
  treating the program as finished.
- ✅ Keep the Book's dependency version while learning, then update intentionally
  after understanding the API you are calling.
- ✅ Recognize tutorial staging: code that is acceptable in Listing 2-1 may be
  deliberately improved a few pages later.
- ✅ Extract small helpers when you want to test parsing or comparison without
  driving stdin manually.

## Pitfalls
- ⚠️ Leaving `expect("Please type a number!")` as the input policy after the game
  has a loop; the tutorial's correct alternative is `match guess.trim().parse()`
  and `continue` on invalid guesses.
- ⚠️ Comparing a `String` directly with a number; parse text into a concrete
  integer type before numeric comparison.
- ⚠️ Copying the `rand` example without the matching dependency entry in
  [[Cargo.toml Manifest]].
- ⚠️ Forgetting that `read_line` appends into the existing `String`; create a new
  string or clear it each loop iteration if you reuse the buffer.
- ⚠️ Comparing text and numbers directly; parse text first, then compare numbers
  with `cmp`.

## See also
[[Cargo Basics]] · [[crates.io and Dependencies Intro]] · [[Result]] · [[The match Expression]] · [[Loop Expressions]] · [[Variables and Mutability]] · [[String and str]] · [[Borrowing]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, ch. 2 "Programming a Guessing Game" — [[the-book]],
  https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html
