---
type: concept
title: "Constants"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, constants, const, compile-time]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Variables and Mutability]]", "[[Shadowing]]", "[[Scalar Types]]", "[[Const Evaluation]]", "[[Static Items]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html#constants", "https://doc.rust-lang.org/reference/const_eval.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Const Evaluation"]
---

# Constants

A Rust `const` is a named compile-time value with an explicit type, available in its scope and never mutable.

## What it is
Constants bind a name to a value that must be computable as a constant expression. They are declared with `const`, require a type annotation, and cannot use `mut`.

Use a constant when a named value is part of the program's meaning: limits, protocol sizes, conversion factors, flags, and other values that should be written once and reused.

Rust convention names constants in uppercase with underscores, such as `MAX_RETRIES` or `SECONDS_PER_HOUR`.

## How it works
Unlike a normal `let` binding, a constant can be declared in many item scopes, including module scope. Its initializer must be accepted by Rust's const-evaluation rules; it cannot depend on a runtime result such as user input, heap allocation through ordinary runtime APIs, or a non-const function call.

Constants are not storage locations that can be mutated. Conceptually, each use is the named value. For address-stable global storage, see [[Static Items]] rather than using a constant.

The type annotation is mandatory because constants are item-like declarations and should expose a stable type at the declaration site.

## Example
```rust
const SECONDS_PER_HOUR: u32 = 60 * 60;
const WORKDAY_HOURS: u32 = 8;

fn main() {
    let workday_seconds = SECONDS_PER_HOUR * WORKDAY_HOURS;
    assert_eq!(workday_seconds, 28_800);
}
```

## Common errors
Constants require explicit types and const-evaluable initializers:

```rust
// const LIMIT = 10;

fn runtime_limit() -> u32 {
    10
}

// const LIMIT_FROM_FUNCTION: u32 = runtime_limit();
```

Typical diagnostics include:

```text
error: missing type for `const` item
error[E0015]: cannot call non-const function in constants
```

Fix by adding the type and moving runtime work into a `let`, `static` initializer that is const-safe,
or a lazy initialization pattern.

## Best practice
- ✅ Name domain values with `const` instead of repeating numeric or string literals.
- ✅ Keep constants typed as narrowly and accurately as the domain allows.
- ✅ Use readable constant expressions, such as `60 * 60 * 3`, when they explain the value better than the folded result.
- ✅ Reach for [[Static Items]] only when you need a single storage location or mutable global state under strict rules.
- ✅ Keep public constants semver-stable: changing their type or meaning can break downstream code.

## Pitfalls
- ⚠️ Do not try to initialize a constant with runtime data; use a `let` binding or lazy initialization patterns instead.
- ⚠️ Do not add `mut`; constants are always immutable.
- ⚠️ Avoid vague names such as `VALUE` or `LIMIT`; a constant should document why the value exists.
- ⚠️ Remember that type inference is not enough for `const`; write the type explicitly.

## See also
[[Variables and Mutability]] · [[Shadowing]] · [[Scalar Types]] · [[Const Evaluation]] · [[Static Items]] · [[Statements vs Expressions]] · [[Type Inference]] · [[Integer Overflow]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.1 "Declaring Constants" — [[the-book]], https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html#constants
- The Rust Reference, "Constant evaluation" — [[the-reference]], https://doc.rust-lang.org/reference/const_eval.html
