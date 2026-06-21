---
type: antipattern
title: "Is Some Then Unwrap"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, option, pattern-matching, unwrap, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: basic
related: ["[[Option vs Result]]", "[[Unwrap and Expect Overuse]]", "[[Pattern Matching]]", "[[Result]]", "[[Index Panics vs get]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-02-match.html", "https://doc.rust-lang.org/book/ch06-03-if-let.html", "https://doc.rust-lang.org/std/option/enum.Option.html"]
rust_version: "edition 2024 / 1.85+"
---

# Is Some Then Unwrap

`is_some()` followed by `unwrap()` splits one `Option` decision into two operations; pattern matching keeps the check and extraction together.

## The mistake
`Option<T>` already says a value may be absent. Writing `if value.is_some() { value.unwrap() }` duplicates the decision and leaves a panic nearby if the code changes incorrectly.

The same pattern appears with `Result::is_ok()` followed by `unwrap()`. It is usually clearer to use `if let`, `match`, `let else`, or combinators such as `map`, `and_then`, and `ok_or`.

## Why it happens
Predicate methods are convenient when the program only needs a yes/no answer. Once the code also needs the inner value, the predicate is no longer enough.

Pattern matching binds the inner value only in the branch where it exists. That makes the compiler enforce the relationship between the check and the use.

`unwrap()` consumes the `Option` or `Result` and panics on the absent/error variant. `if let`, `match`, and `let else` destructure the enum in one operation, so the compiler knows that the bound variable exists only in the valid branch.

Modern `Option` also has predicate helpers for the cases where you truly only need a boolean: `is_some_and` checks a present value, and `is_none_or` accepts absence or a predicate match. Those avoid extracting the value just to put it back into control flow.

## Example
```rust
fn extension(path: &str) -> Option<&str> {
    path.rsplit_once('.').map(|(_, ext)| ext)
}

fn describe(path: &str) -> String {
    let Some(ext) = extension(path) else {
        return String::from("no extension");
    };

    format!("extension: {ext}")
}

fn main() {
    println!("{}", describe("notes.md"));
    println!("{}", describe("LICENSE"));

    // Mistake:
    // if extension("notes.md").is_some() {
    //     println!("{}", extension("notes.md").unwrap());
    // }
}
```

## Second example: mutate through `Option` without moving it
```rust
#[derive(Debug)]
struct Session {
    token: Option<String>,
}

impl Session {
    fn refresh_suffix(&mut self) {
        if let Some(token) = self.token.as_mut() {
            token.push_str("-fresh");
        }
    }
}

fn main() {
    let mut session = Session {
        token: Some(String::from("abc")),
    };

    session.refresh_suffix();
    println!("{session:?}");
}
```

`as_mut()` converts `&mut Option<String>` into `Option<&mut String>`, so the code can edit the inner string without moving it out of the struct.

## Common errors
Moved value after unwrap:

```text
error[E0382]: use of moved value
```

`unwrap()` takes ownership of the option. If you only need to inspect the inner value, use `as_ref()`, `as_mut()`, `if let`, or `match` on a reference.

Panic from a stale check:

```text
thread 'main' panicked at 'called `Option::unwrap()` on a `None` value'
```

Fix it by binding the value in the same expression that checks it. Avoid recomputing the option between `is_some()` and `unwrap()`.

## Best practice
- ✅ Use `if let Some(value) = option` for a single success branch.
- ✅ Use `match` when both `Some` and `None` need meaningful handling.
- ✅ Use `let Some(value) = option else { ... };` for early returns.
- ✅ Convert to `Result` with `ok_or` or `ok_or_else` when absence is an error.
- ✅ Use `as_ref()` or `as_mut()` when matching a field without moving it out of its owner.
- ✅ Use `is_some_and` or `is_none_or` only when the result should remain a boolean.

## Pitfalls
- ⚠️ Calling the producing function twice can change behavior or duplicate work.
- ⚠️ `.is_ok()` plus `.unwrap()` has the same smell for `Result`.
- ⚠️ `.unwrap()` is acceptable for a local invariant, but the reason should be obvious or documented; see [[Unwrap and Expect Overuse]].
- ⚠️ `.get(i).is_some()` plus indexing repeats a bounds check and can drift; see [[Index Panics vs get]].
- ⚠️ `if option.is_none() { return } option.unwrap()` is less clear than `let Some(value) = option else { return };`.
- ⚠️ Matching by value moves non-`Copy` contents; borrow with `.as_ref()` when the owner must remain usable.

## See also
[[Option vs Result]] · [[Unwrap and Expect Overuse]] · [[Pattern Matching]] · [[Result]] · [[Index Panics vs get]] · [[panic!]] · [[Recoverable vs Unrecoverable Errors]] · [[Sentinel Values]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 6.2 "The `match` Control Flow Construct" — [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html
- The Rust Programming Language, ch. 6.3 "Concise Control Flow with `if let` and `let else`" — [[the-book]], https://doc.rust-lang.org/book/ch06-03-if-let.html
- Standard library, `Option` — [[the-reference]], https://doc.rust-lang.org/std/option/enum.Option.html
