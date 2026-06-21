---
type: concept
title: "Functions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, functions, fn, parameters]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Statements vs Expressions]]", "[[Ownership]]", "[[Borrowing]]", "[[Tuples]]", "[[Documentation Comments]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-03-how-functions-work.html", "https://doc.rust-lang.org/reference/items/functions.html"]
rust_version: "edition 2024 / 1.85+"
---

# Functions

Rust functions are named `fn` items with typed parameters and an optional return type, returning the body block's tail expression unless an explicit `return` exits earlier.

## What it is
A function packages reusable behavior behind a name, parameter list, and return type. The `main` function is the entry point of binary crates; ordinary functions are declared with `fn`.

Rust convention uses `snake_case` for function names and variable names. Function definitions may appear before or after callers as long as they are in a scope visible to the caller.

Every function parameter needs a type annotation. If no return type is written, the function returns unit `()`.

## How it works
The Reference describes a function as a block body plus a name, parameters, and output type. Parameters are irrefutable patterns, so simple names are common but destructuring patterns are also possible.

The body of a function is a block expression. Its tail expression becomes the return value. A semicolon after the intended tail expression turns it into a statement, making the body return `()` instead.

Arguments are passed according to normal [[Ownership]] rules. Passing a non-`Copy` owned value moves it unless the function accepts a reference. API design therefore depends heavily on [[Borrowing]].

## Example
```rust
fn area((width, height): (u32, u32)) -> u32 {
    width * height
}

fn describe_area(label: &str, size: (u32, u32)) {
    println!("{label}: {}", area(size));
}

fn main() {
    let size = (4, 5);
    describe_area("rectangle", size);
    assert_eq!(area(size), 20);
}
```

## Common errors
A stray semicolon after the intended return value changes it to `()`:

```rust
fn plus_one(n: i32) -> i32 {
    // n + 1;
    n + 1
}
```

Typical diagnostic when the semicolon is present:

```text
error[E0308]: mismatched types
expected `i32`, found `()`
```

## Best practice
- ✅ Put types in function signatures where callers and compiler diagnostics benefit most.
- ✅ Return the tail expression for straightforward results; use `return` for early exits when it improves clarity.
- ✅ Prefer borrowing parameters (`&T`, `&str`, `&[T]`) when the function does not need ownership.
- ✅ Document public functions with [[Documentation Comments]] and examples.

## Pitfalls
- ⚠️ Adding a semicolon to a return expression changes the value to `()`.
- ⚠️ Taking `String` or `Vec<T>` by value when `&str` or `&[T]` is enough forces unnecessary ownership transfer.
- ⚠️ Hiding too much behavior in a large function makes ownership and control flow harder to reason about.
- ⚠️ Assuming parameter types can be inferred in signatures; Rust requires them.

## See also
[[Statements vs Expressions]] · [[Ownership]] · [[Borrowing]] · [[Tuples]] · [[Documentation Comments]] · [[Result]] · [[Type Inference]] · [[Readable Generic APIs]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.3 "Functions" — [[the-book]], https://doc.rust-lang.org/book/ch03-03-how-functions-work.html
- The Rust Reference, "Functions" — [[the-reference]], https://doc.rust-lang.org/reference/items/functions.html
