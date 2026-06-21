---
type: concept
title: "Lifetimes"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, lifetimes, borrowing, references]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Ownership]]", "[[Borrowing]]", "[[References]]", "[[Lifetime Elision]]", "[[The 'static Lifetime]]", "[[Overconstraining Lifetimes]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html", "https://doc.rust-lang.org/reference/trait-bounds.html#lifetime-bounds"]
rust_version: "edition 2024 / 1.85+"
---

# Lifetimes

Lifetimes are compile-time regions describing how long references are valid and how borrowed inputs and outputs relate.

## What it is
Every Rust reference has a lifetime, whether written explicitly or inferred.
Most lifetimes are invisible because [[Lifetime Elision]] and local borrow analysis infer them.
Explicit lifetime parameters do not make values live longer; they describe relationships the borrow checker must enforce.
Lifetimes are a kind of generic parameter, written with an apostrophe such as `'a`.
You write them when a signature has multiple possible borrow relationships and the compiler cannot infer the intended one.

## How it works
A signature like `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str` says the returned reference is valid only for the overlap of the two input borrows.
The concrete `'a` at a call site becomes the smaller region that satisfies all annotated references.
If a function returns a reference, that return reference usually must be tied to an input reference or to data with a valid longer lifetime.
Returning a reference to a local owned value is impossible because the local value is dropped at function exit.
Structs that store references include lifetime parameters so instances cannot outlive the borrowed data.
The borrow checker reasons over regions in the program, not just lexical braces; non-lexical lifetimes can end a borrow after its last use.
Lifetime subtyping lets a longer borrow be shortened to fit a smaller required region.
When one named lifetime appears on multiple inputs, the actual lifetime chosen at a call site is the intersection that satisfies all of them.
That is why annotations constrain callers even though they do not change runtime behavior.

## Example
```rust
fn longest<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() { left } else { right }
}

struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn text(&self) -> &str {
        self.text
    }
}

fn main() {
    let book = String::from("Call me Ferris. Safe systems ahead.");
    let first = book.split('.').next().unwrap();
    let excerpt = Excerpt { text: first };
    assert_eq!(longest(excerpt.text(), "Rust"), "Call me Ferris");
}
```

## Common errors
Returning a reference to a local value typically reports:

```text
error[E0515]: cannot return reference to local variable
```

Return the owned value instead, or borrow from an input that outlives the return.
Borrowing a value for longer than it lives reports `error[E0597]: borrowed value does not live long enough`.
Move the owner outward, shorten the use of the reference, or return owned data.
When the compiler reports `error[E0106]: missing lifetime specifier`, decide which input the output can borrow from; do not add the same `'a` to every reference unless that is the true relationship.

## Best practice
- ✅ Treat lifetime annotations as API contracts about borrowed data, not as commands to extend storage.
- ✅ Let elision handle ordinary cases; add names only when a relationship must be expressed.
- ✅ Tie output references only to inputs they can actually come from.
- ✅ Return owned data (`String`, `Vec<T>`, `Arc<T>`) when the result is newly created inside the function.
- ✅ Use distinct lifetime names when inputs are independent; tying them together can reject valid callers.

## Pitfalls
- ⚠️ Adding the same `'a` everywhere often overconstrains unrelated borrows; see [[Overconstraining Lifetimes]].
- ⚠️ Returning references to locals is always invalid; return the owned value instead.
- ⚠️ Reading `'static` as "this value lives forever" is wrong for generic bounds; see [[The 'static Lifetime]].
- ⚠️ Assuming closure lifetime behavior exactly matches `fn` elision can produce surprising errors.

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[Lifetime Elision]] · [[The 'static Lifetime]] · [[Generic Associated Types]] · [[Overconstraining Lifetimes]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.3 "Validating References with Lifetimes" — [[the-book]], https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
- The Rust Reference, "Lifetime bounds" — [[the-reference]], https://doc.rust-lang.org/reference/trait-bounds.html#lifetime-bounds
