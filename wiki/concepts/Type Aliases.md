---
type: concept
title: "Type Aliases"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, types, aliases, abstraction]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[Newtype Pattern]]", "[[Result Type Aliases]]", "[[Using Type Aliases as Newtypes]]", "[[Dynamically Sized Types]]", "[[Returning Closures]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-03-advanced-types.html#type-synonyms-and-type-aliases", "https://doc.rust-lang.org/reference/items/type-aliases.html"]
rust_version: "edition 2024 / 1.85+"
---

# Type Aliases

A type alias gives an existing type another name; it reduces repetition and communicates intent, but it does not create a distinct type.

## What it is
`type Name = ExistingType;` introduces a synonym for an existing type.
The alias can be used in signatures, variable annotations, associated type definitions, and public APIs.
After type checking expands the alias, the aliased type and the original type are the same type.

That makes aliases excellent for long signatures, repeated error types, and semantic names for callback shapes.
It also means aliases are not a unit-safety or domain-boundary tool.
For distinctness, use [[Newtype Pattern]] instead.

Common examples include `std::io::Result<T>`, which is an alias for `std::result::Result<T, std::io::Error>`, and local aliases such as `type Handler = Box<dyn Fn(&str) + Send + Sync + 'static>;`.

## How it works
An alias does not introduce a new constructor, layout, trait implementation set, or conversion boundary.
If `type Kilometers = i32;`, a `Kilometers` value can be passed to any function expecting `i32`, and an `i32` can be passed where `Kilometers` is expected.

Aliases can be generic:
`type AppResult<T> = Result<T, AppError>;`.
They can also name trait-object types:
`type Thunk = Box<dyn Fn() + Send + 'static>;`.

Because an alias is transparent, methods and trait implementations available on the underlying type remain available on the alias.
This is useful for ergonomics, but it is exactly why aliases should not be used when you need compiler-enforced separation between values.
Name lookup still matters: an alias lives in the type namespace, so it can be imported, re-exported, documented, and used in public signatures.
Once the compiler resolves that name, however, trait selection and method lookup operate on the underlying type.
You cannot implement a trait "for the alias" separately from the underlying type, because there is no separate nominal type to target.

For recursive or self-referential shapes, remember that an alias does not add indirection.
`type Node = Option<(i32, Node)>;` is not a valid way to define a recursive list; use a nominal type plus `Box`, `Rc`, or another pointer.

## Example
```rust
type UserId = u64;
type Job = Box<dyn Fn() + Send + 'static>;

fn fetch_user(id: UserId) -> String {
    format!("user-{id}")
}

fn run(job: Job) {
    job();
}

fn main() {
    let raw: u64 = 42;
    let id: UserId = raw;

    assert_eq!(fetch_user(id), "user-42");

    run(Box::new(|| println!("work scheduled")));
}
```

## More realistic example
```rust
use std::sync::Arc;

type Validator = Arc<dyn Fn(&str) -> bool + Send + Sync + 'static>;

struct Field {
    name: String,
    validate: Validator,
}

impl Field {
    fn accepts(&self, value: &str) -> bool {
        (self.validate)(value)
    }
}

fn non_empty() -> Validator {
    Arc::new(|value| !value.trim().is_empty())
}

fn main() {
    let username = Field {
        name: String::from("username"),
        validate: non_empty(),
    };

    assert_eq!(username.name, "username");
    assert!(username.accepts("ferris"));
    assert!(!username.accepts("   "));
}
```

The alias keeps the callback shape readable, but callers can still see that this is shared ownership of a dynamically dispatched callable.

## Common errors
```rust
type UserId = u64;
type OrderId = u64;

fn load_user(id: UserId) -> String {
    format!("user-{id}")
}

fn main() {
    let order: OrderId = 10;
    let text = load_user(order); // compiles, but it is a domain bug
    assert_eq!(text, "user-10");
}
```

There is no compiler error here, which is the point: aliases cannot enforce domain separation.
Fix it with [[Newtype Pattern]] when the compiler should reject a mix-up.

```rust
type Kilometers = i32;

// impl std::fmt::Display for Kilometers { ... }
// error[E0117]: only traits defined in the current crate can be implemented for primitive types
```

The alias does not make `i32` local to your crate.
Wrap it in `struct Kilometers(i32);` if you need a local type for trait implementations or invariants.

## Best practice
- ✅ Use aliases to shorten repeated, noisy types such as callback, iterator, or `Result` signatures.
- ✅ Choose names that explain the role of the type in this API, not just the implementation detail.
- ✅ Keep public aliases stable only when you are comfortable exposing the aliased shape as part of the API contract.
- ✅ Prefer [[Result Type Aliases]] for crate-local error signatures that repeatedly use the same error type.
- ✅ Leave important ownership markers visible in the aliased type name or docs: `BoxedHandler`, `SharedValidator`, and `IoResult` communicate more than `Thing`.
- ✅ Re-export aliases deliberately; downstream code may name them in its own public API.

## Pitfalls
- ⚠️ Do not expect aliases to prevent mixing units, IDs, currencies, or capability tokens; use [[Newtype Pattern]] and see [[Using Type Aliases as Newtypes]].
- ⚠️ Avoid hiding important ownership or dynamic-dispatch costs behind vague aliases such as `Thing` or `Callback`; make `Box`, `dyn`, `Send`, and lifetimes visible when they matter.
- ⚠️ Remember that changing a public alias can be a breaking API change if users name it or rely on trait bounds that follow from the aliased type.
- ⚠️ Do not use aliases to dodge a long type that should really be an explicit struct with named fields and invariants.
- ⚠️ Be careful with a local alias named `Result`; inside the alias definition, write `std::result::Result` to avoid resolving to the alias itself.

## See also
[[Newtype Pattern]] · [[Result Type Aliases]] · [[Using Type Aliases as Newtypes]] · [[Returning Closures]] · [[Function Pointers]] · [[Dynamically Sized Types]] · [[Boxed Closure Returns]] · [[Trait Objects]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.3 "Type Synonyms and Type Aliases" — [[the-book]], https://doc.rust-lang.org/book/ch20-03-advanced-types.html#type-synonyms-and-type-aliases
- The Rust Reference, "Type aliases" — [[the-reference]], https://doc.rust-lang.org/reference/items/type-aliases.html
