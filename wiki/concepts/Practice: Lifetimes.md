---
type: concept
title: "Practice: Lifetimes"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, lifetimes]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Lifetimes]]", "[[Lifetime Elision]]", "[[References]]", "[[Borrowing]]", "[[The 'static Lifetime]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Lifetimes

The lifetimes group teaches describing how borrowed outputs relate to borrowed inputs. The key idea is that lifetime annotations do not extend data; they tell the compiler which borrows must remain valid together.

## What it is
These exercises cover explicit lifetime parameters, references in structs, returning one of multiple borrowed inputs, and recognizing impossible returned references.

## How it works
When a function returns a reference, Rust must know which input reference it came from. A signature like `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str` says the returned reference is valid only as long as both inputs are valid.

## Example
```rust
fn longest<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() {
        left
    } else {
        right
    }
}

fn main() {
    let a = String::from("rust");
    let b = String::from("borrow checker");
    println!("{}", longest(&a, &b));
}
```

## Best practice
- ✅ Add explicit lifetimes when returned borrows need a named relationship.
- ✅ Prefer owned return values when the data is created inside the function.
- ✅ Rely on lifetime elision for simple single-input borrowing APIs.

## Pitfalls
- ⚠️ Lifetime annotations cannot make a local variable live after the function returns.
- ⚠️ Do not use `'static` as a general escape hatch for borrow errors.
- ⚠️ Avoid storing references in structs unless the borrowed relationship is truly part of the design.

## See also
[[Practice (Rustlings)]] · [[Lifetimes]] · [[Lifetime Elision]] · [[References]] · [[Borrowing]] · [[The 'static Lifetime]] · [[Returning References to Locals]]

## Sources
- Rustlings `16_lifetimes` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

