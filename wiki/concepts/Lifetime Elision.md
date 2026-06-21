---
type: concept
title: "Lifetime Elision"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, lifetimes, elision, references]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Lifetimes]]", "[[The 'static Lifetime]]", "[[Borrowing]]", "[[References]]", "[[Generic Associated Types]]", "[[Overconstraining Lifetimes]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-elision", "https://doc.rust-lang.org/reference/lifetime-elision.html"]
rust_version: "edition 2024 / 1.85+"
---

# Lifetime Elision

Lifetime elision is the compiler's limited set of deterministic rules for filling in obvious reference lifetimes in function and method signatures.

## What it is
Elision means you can write `fn first(s: &str) -> &str` instead of spelling out `fn first<'a>(s: &'a str) -> &'a str`.
It is not full lifetime inference for all signatures.
The compiler applies a small fixed set of rules and errors if a borrowed output remains ambiguous.
Elision keeps ordinary Rust readable while preserving precise lifetime contracts.
You still need explicit lifetimes when an output could borrow from more than one input.

## How it works
Rule 1: each elided lifetime in input position becomes a distinct lifetime parameter.
Rule 2: if there is exactly one input lifetime, elided output lifetimes get that same lifetime.
Rule 3: in methods, if one input is `&self` or `&mut self`, elided output lifetimes get the receiver's lifetime.
The placeholder lifetime `'_` can make elision visible in paths and some impl headers without naming a lifetime.
Trait object lifetime defaults are a related but separate set of default object-bound rules.
Elision happens in item signatures before the borrow checker validates the body.
It never guesses between multiple possible input lifetimes for an output, because that choice would be part of the public API contract.
The receiver rule is why `fn get(&self, key: &str) -> &Value` means the returned value borrows from `self`, not from `key`.
The same rules apply to `extern "Rust"` function signatures, but closure lifetime inference has additional context-sensitive behavior.

## Example
```rust
struct Document {
    title: String,
}

impl Document {
    // Rule 3: output borrows from &self.
    fn title(&self) -> &str {
        &self.title
    }
}

// Rule 2: output borrows from the single input.
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap_or("")
}

fn main() {
    let doc = Document { title: "Rust notes".into() };
    assert_eq!(doc.title(), "Rust notes");
    assert_eq!(first_word("borrow checker"), "borrow");
}
```

## Common errors
An ambiguous borrowed return produces:

```text
error[E0106]: missing lifetime specifier
```

For `fn longest(a: &str, b: &str) -> &str`, write `fn longest<'a>(a: &'a str, b: &'a str) -> &'a str` only if the result may come from either input.
If the result always comes from one input, name only that relationship and leave the other input elided.
A common method mistake is writing an explicit lifetime that ties `&mut self` to an output longer than needed, keeping the mutable borrow active for too much of the caller's code.
Prefer elision first, then expand it only to communicate a real relationship.

## Best practice
- ✅ Omit lifetimes when elision expresses the contract exactly.
- ✅ Add explicit names when a function returns one of several input references.
- ✅ Use `'_` when you want to show that a type has a lifetime without inventing a meaningful name.
- ✅ Keep method return references tied to `self` when that is the natural ownership model.
- ✅ Read elided signatures by mentally expanding the three rules when debugging borrow errors.

## Pitfalls
- ⚠️ `fn longest(a: &str, b: &str) -> &str` is ambiguous because two distinct inputs leave no output lifetime.
- ⚠️ Adding `<'a>` everywhere can make independent borrows appear dependent; see [[Overconstraining Lifetimes]].
- ⚠️ Elision in closures has different limitations than named `fn` items.
- ⚠️ Hidden trait object bounds can default to `'static` in owned trait objects; see [[The 'static Lifetime]].

## See also
[[Lifetimes]] · [[The 'static Lifetime]] · [[Borrowing]] · [[References]] · [[Generic Associated Types]] · [[Trait Bounds]] · [[Overconstraining Lifetimes]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.3 "Lifetime Elision" — [[the-book]], https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-elision
- The Rust Reference, "Lifetime elision" — [[the-reference]], https://doc.rust-lang.org/reference/lifetime-elision.html
