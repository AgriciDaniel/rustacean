---
type: antipattern
title: "Overconstraining Lifetimes"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, lifetimes, borrowing, antipattern]
domain: "Generics, Traits & Lifetimes"
difficulty: intermediate
related: ["[[Lifetimes]]", "[[Lifetime Elision]]", "[[The 'static Lifetime]]", "[[Borrowing]]", "[[Trait Bounds]]", "[[References]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html", "https://doc.rust-lang.org/reference/lifetime-elision.html"]
rust_version: "edition 2024 / 1.85+"
---

# Overconstraining Lifetimes

Overconstraining lifetimes means tying borrows together with the same named lifetime, or with `'static`, when the API only needed shorter independent borrows.

## The mistake
Beginners often add `<'a>` everywhere after seeing a lifetime error.
That can make unrelated inputs appear to have the same lifetime.
The code may compile but reject valid callers because the signature promises a stricter relationship than the body needs.
Another version is adding `T: 'static` because the compiler suggested it, even though the API could accept borrowed data.
Lifetime annotations should describe real data flow, not serve as decorative type-system padding.

## Why it happens
Lifetime names are constraints, not labels for variables.
Using the same name twice says those references must be valid for a common region chosen by the caller and accepted by the function.
If the output only borrows from one input, the other input should usually have an independent elided lifetime.
If no output borrow exists, most explicit lifetime names are unnecessary.
The compiler proves safety, but it cannot tell whether your overly strict signature is the ergonomic API you wanted.
The same problem appears in impl blocks: `impl<'a> Parser<'a>` is fine for a type that stores a borrow, but method-level `'a` should not be reused for every temporary borrow.
Overusing `T: 'static` is the trait-bound version of the mistake; it excludes values containing ordinary borrows even when the function consumes them immediately.
Because lifetime constraints are invisible at runtime, the cost shows up as rejected callers and confusing diagnostics rather than slower code.
Good lifetime design keeps the returned borrow tied to the smallest real source.

## Example
```rust
// Good: `fallback` is independent; the return can only borrow from `primary`.
fn choose_primary<'a>(primary: &'a str, fallback: &str) -> &'a str {
    if primary.is_empty() { fallback.len(); }
    primary
}

fn main() {
    let owned = String::from("kept");
    let result;
    {
        let short = String::from("temporary");
        result = choose_primary(owned.as_str(), short.as_str());
    }
    assert_eq!(result, "kept");
}
```

## Common errors
The overconstrained version of the example would be:

```rust
fn choose_primary_bad<'a>(primary: &'a str, fallback: &'a str) -> &'a str {
    if primary.is_empty() { fallback.len(); }
    primary
}
```

At a call site where `fallback` is short-lived, this can lead to `error[E0597]: borrowed value does not live long enough` even though the returned reference never points to `fallback`.
The fix is to remove the false relationship: `fn choose_primary<'a>(primary: &'a str, fallback: &str) -> &'a str`.
If the compiler suggests adding `'static`, check whether an owned return, `move` closure, or shorter trait object lifetime is the real fix.
Explicit lifetimes should explain data flow, not make all borrows equally long.

## Best practice
- ✅ Start with elided lifetimes and add names only when the compiler needs a relationship.
- ✅ Name only the references that are related to the returned borrow.
- ✅ Give independent inputs independent lifetimes by eliding them or naming them separately.
- ✅ Use owned returns when the function creates new data.
- ✅ Treat `T: 'static` as an ownership boundary requirement, not a universal borrow fix.

## Pitfalls
- ⚠️ `fn f<'a>(x: &'a str, y: &'a str) -> &'a str` says the result may borrow from either input, even if the body only returns `x`.
- ⚠️ Adding `'static` often shifts the burden to callers instead of fixing ownership.
- ⚠️ Explicit lifetimes in methods can fight [[Lifetime Elision]] rule 3 and make `self` borrows look longer than needed.
- ⚠️ A compiling lifetime signature can still be needlessly restrictive.

## See also
[[Lifetimes]] · [[Lifetime Elision]] · [[The 'static Lifetime]] · [[Borrowing]] · [[References]] · [[Trait Bounds]] · [[Ownership]] · [[Generics, Traits & Lifetimes]]

## Sources
- The Rust Programming Language, ch. 10.3 "Validating References with Lifetimes" — [[the-book]], https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
- The Rust Reference, "Lifetime elision" — [[the-reference]], https://doc.rust-lang.org/reference/lifetime-elision.html
