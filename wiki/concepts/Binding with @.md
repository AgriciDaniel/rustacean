---
type: concept
title: "Binding with @"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, patterns, bindings, at-patterns]
domain: "Enums & Pattern Matching"
difficulty: intermediate
related: ["[[Patterns]]", "[[The match Expression]]", "[[Match Guards]]", "[[Destructuring]]", "[[Catch-All and Wildcard Patterns]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#using--bindings", "https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#matching-ranges-of-values-with-"]
rust_version: "edition 2024 / 1.85+"
---

# Binding with @

The `@` operator binds a matched value to a name while also testing it against a subpattern.

## What it is
An at-pattern has the form `name @ pattern`.
It is useful when you need both facts: the value matched a narrower pattern, and the arm body needs the actual value.

Without `@`, a range or literal pattern can test the value but does not bind it.
With a plain variable binding, you get the value but do not constrain it.
`@` combines those two jobs in one pattern.

## How it works
Rust checks the subpattern after `@`.
If the subpattern matches, Rust binds the whole matched value to the name before `@`.
The binding is available in the arm body just like any other pattern binding.

At-patterns compose with struct and enum destructuring.
They are especially handy with ranges, nested enum variants, and any place where a predicate can be written structurally.
If the condition is not structural, prefer [[Match Guards]].

`@` binds the value matched by the subpattern, not the textual pattern. In `id @ 3..=7`, `id` is the
actual integer that matched the range. In `whole @ [first, ..]`, `whole` is the entire slice pattern
matched at that position while `first` is the first element.

The binding mode still follows normal pattern rules. If the matched value is owned and not `Copy`, an
at-pattern can move it. If you need a borrowed binding, match a reference (`match &value`) or use `ref`
where edition-2024 binding-mode rules allow it. The subpattern must be a real pattern; use a guard for
conditions such as `value.is_valid()`.

## Example
```rust
enum Message {
    Hello { id: u32 },
}

fn route(message: Message) -> String {
    match message {
        Message::Hello { id: id @ 3..=7 } => format!("priority {id}"),
        Message::Hello { id: 10..=12 } => String::from("reserved"),
        Message::Hello { id } => format!("normal {id}"),
    }
}

fn main() {
    assert_eq!(route(Message::Hello { id: 5 }), "priority 5");
    assert_eq!(route(Message::Hello { id: 11 }), "reserved");
}
```

## Worked example
```rust
fn classify_path(parts: &[&str]) -> String {
    match parts {
        [] => String::from("root"),
        whole @ ["api", version @ ("v1" | "v2"), tail @ ..] => {
            format!("{version} api path with {} extra parts in {whole:?}", tail.len())
        }
        [first @ ("static" | "assets"), file] => format!("{first} file {file}"),
        [first, ..] => format!("other path starting with {first}"),
    }
}

fn main() {
    assert_eq!(
        classify_path(&["api", "v2", "users"]),
        r#"v2 api path with 1 extra parts in ["api", "v2", "users"]"#
    );
    assert_eq!(classify_path(&["static", "app.css"]), "static file app.css");
}
```

## Common errors
Using `@` where the right side is an expression, not a pattern, does not work:

```text
error: expected a pattern, found an expression
```

Fix it by moving runtime logic into a match guard, for example `value if is_valid(value) => ...`.
If an at-pattern moves a value you need later, match by reference or bind `ref name @ ...` where valid.

## Best practice
- ✅ Use `@` when a range, literal, or nested pattern must also provide the matched value to the arm body.
- ✅ Prefer `@` over repeating the same test in the arm body after a broader match.
- ✅ Keep the bound name close to the concept it represents, such as `id @ 3..=7`.
- ✅ Use `@ ..` in slice patterns when you need a named rest slice rather than just ignoring it.
- ✅ Combine `@` with `|` only when the binding has the same type and meaning for every alternative.

## Pitfalls
- ⚠️ Do not reach for `@` when a normal binding is enough; `Message::Hello { id }` is clearer for any value.
- ⚠️ Do not use `@` for arbitrary runtime predicates; use [[Match Guards]].
- ⚠️ Remember that binding can move non-`Copy` values unless you match a reference.
- ⚠️ Do not make at-patterns so dense that the tested shape and the bound value become hard to distinguish.
- ⚠️ Be aware that range at-patterns are limited to the pattern types Rust supports, such as numeric and `char` ranges.

## See also
[[Patterns]] · [[The match Expression]] · [[Match Guards]] · [[Destructuring]] · [[Catch-All and Wildcard Patterns]] · [[Ownership]] · [[Enum Variants with Data]] · [[Refutable and Irrefutable Patterns]] · [[Exhaustiveness]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 19.3 "Using @ Bindings" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#using--bindings
- The Rust Programming Language, ch. 19.3 "Matching Ranges of Values with ..=" - [[the-book]], https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#matching-ranges-of-values-with-
