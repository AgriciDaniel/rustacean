---
type: concept
title: "Closures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, functions, functional]
domain: "Closures & Iterators"
difficulty: basic
related: ["[[Capturing the Environment]]", "[[Fn, FnMut, FnOnce]]", "[[move Closures]]", "[[Closure Type Inference]]", "[[Function Pointers]]", "[[Iterator Adapters]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-01-closures.html", "https://doc.rust-lang.org/std/ops/trait.Fn.html"]
rust_version: "edition 2024 / 1.85+"
---

# Closures

Closures are anonymous function values that can be stored, passed, called later, and optionally capture variables from the scope where they are defined.

## What it is
A closure is written with pipes around its parameters, such as `|x| x + 1` or `|| fallback()`.
It behaves like a function call value, but unlike a plain `fn` item it can carry captured state
from the surrounding lexical environment.

Closures are usually local implementation details: a fallback passed to `Option::unwrap_or_else`,
a predicate passed to `Iterator::filter`, a key extractor passed to `slice::sort_by_key`, or a
small callback kept in a variable.

## How it works
Every closure expression has its own anonymous compiler-generated type. That type stores any
captured values as fields and implements one or more call traits: [[Fn, FnMut, FnOnce]].

The compiler infers closure parameter and return types from use. Once inferred, a particular
closure value has one concrete signature; it is not a generic function that can be called with
unrelated argument types.

At code generation time, a closure call is usually a statically dispatched call on that generated
type. Captures become ordinary fields, so an immutable capture is like storing `&T`, a mutable
capture is like storing `&mut T`, and an owning capture is like storing `T`. That is why closure
errors often look exactly like [[Borrowing]] or [[Move Semantics]] errors: the closure is not
special at runtime, it is a value whose fields are borrowed, mutated, moved, and dropped normally.

Use a closure when you need inline behavior customization, especially when the behavior uses
nearby variables. Use a named function or function pointer when no capture is needed and a stable
named operation communicates the intent better.

## Example
```rust
fn pick_name(explicit: Option<&str>, default_prefix: &str) -> String {
    explicit
        .map(str::to_owned)
        .unwrap_or_else(|| format!("{default_prefix}-guest"))
}

fn main() {
    assert_eq!(pick_name(Some("ferris"), "rust"), "ferris");
    assert_eq!(pick_name(None, "rust"), "rust-guest");
}
```

The closure `|| format!("{default_prefix}-guest")` captures `default_prefix` by immutable
reference and runs only when the option is `None`.

## Worked example
```rust
#[derive(Debug, PartialEq)]
struct User {
    name: String,
    active: bool,
}

fn active_names<'a>(users: &'a [User], prefix: &'a str) -> impl Iterator<Item = &'a str> {
    users
        .iter()
        .filter(move |user| user.active && user.name.starts_with(prefix))
        .map(|user| user.name.as_str())
}

fn main() {
    let users = [
        User { name: String::from("rustacean"), active: true },
        User { name: String::from("borrower"), active: true },
        User { name: String::from("rustling"), active: false },
    ];

    let names: Vec<&str> = active_names(&users, "rust").collect();
    assert_eq!(names, vec!["rustacean"]);
}
```

The `filter` closure captures `prefix`, and `move` moves the reference into the returned iterator
so the closure owns its small capture while the referenced string still lives for `'a`.

## Common errors
```rust
fn main() {
    let identity = |x| x;
    let word = identity(String::from("rust"));
    // let number = identity(42);
}
```

Uncommenting the last line gives `error[E0308]: mismatched types` because the first call fixes
the closure as `String -> String`. Use a generic function (`fn identity<T>(x: T) -> T`) when the
same operation must accept unrelated types.

## Best practice
- ✅ Keep closures short and local; extract a named function when the body needs a name, tests, or documentation.
- ✅ Prefer `unwrap_or_else`, `or_else`, and iterator closures when fallback or per-item work should be lazy.
- ✅ Let the compiler infer closure types unless an annotation clarifies a public boundary or a difficult error.
- ✅ Name the variable captured by the closure close to the closure definition; distant captures make ownership errors harder to read.
- ✅ Use function items such as `Vec::new` or `str::to_owned` when no environment capture is needed and the name is clearer.

## Pitfalls
- ⚠️ Treating one closure value as if it were generic; after first use, its parameter and return types are fixed. See [[Closure Type Inference]].
- ⚠️ Moving captured values out of a closure passed where repeated calls are required. See [[Moving Out of FnMut Closures]].
- ⚠️ Building an iterator chain with closures and never consuming it. See [[Unconsumed Iterator Adapters]].
- ⚠️ Hiding expensive work inside a closure passed to a repeated callback such as `sort_by_key`; it may run many times.
- ⚠️ Returning a closure that borrows locals without using an appropriate `move` capture or owned state. See [[Returning Closures]].

## See also
[[Closures & Iterators]] · [[Closure Type Inference]] · [[Capturing the Environment]] · [[Fn, FnMut, FnOnce]] · [[move Closures]] · [[Iterator Adapters]] · [[Function Pointers]] · [[Returning Closures]] · [[Boxed Closure Returns]] · [[Lazy Evaluation]]

## Sources
- The Rust Programming Language, ch. 13.1 "Closures" - [[the-book]], https://doc.rust-lang.org/book/ch13-01-closures.html
- Rust standard library, `Fn` trait - [[std]], https://doc.rust-lang.org/std/ops/trait.Fn.html
