---
type: concept
title: "The Never Type"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, types, never, control-flow]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[panic!]]", "[[The Question Mark Operator]]", "[[Result]]", "[[Option vs Result]]", "[[Unwrap and Expect Overuse]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-03-advanced-types.html#the-never-type-that-never-returns", "https://doc.rust-lang.org/reference/types/never.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["Never Type"]
---

# The Never Type

The never type, written `!`, is the type of computations that never produce a value, such as `panic!`, `continue`, `break` from a never-returning context, process exit, and endless loops without `break`.

## What it is
`!` is an uninhabited type: no value of type `!` can exist.
Functions returning `!` are called diverging functions because control never returns normally to the caller.

The practical reason `!` matters is type coercion.
An expression of type `!` can coerce to another type because it never actually has to provide a value of that type.
This is why a `match` arm that says `continue` can live beside another arm that returns a `u32`.

`panic!` also has type `!`.
That lets APIs such as `Option::unwrap` return `T`: the `Some(value)` branch yields `T`, and the `None` branch diverges.

## How it works
Rust requires expression branches to agree on a type.
When one branch diverges, the compiler can use the type of the branch that does return.
The diverging branch cannot violate the chosen type because execution never reaches a point where a value is needed.

Use `!` explicitly when a function is deliberately non-returning: a fatal error helper, a command that exits the process, or a loop that owns the thread forever.
For ordinary errors, prefer [[Result]] and [[The Question Mark Operator]].

The compiler treats `!` as an uninhabited type, so pattern matching on a value of type `!` would require no arms.
In stable Rust 1.85, explicit `!` is primarily written in function return positions; you usually encounter it through diverging expressions such as `panic!`, `return`, `break`, `continue`, and infinite loops.
That distinction matters when reading diagnostics: the compiler may infer a diverging expression in a larger expression even when you did not write `!` yourself.

The coercion is one-way.
An expression that actually produces a value cannot be treated as `!`; only an expression that never completes can stand in for another type.

## Example
```rust
fn parse_or_skip(input: &str) -> Option<u32> {
    loop {
        let number: u32 = match input.trim().parse() {
            Ok(value) => value,
            Err(_) => break None,
        };

        break Some(number);
    }
}

fn fatal(message: &str) -> ! {
    panic!("{message}");
}

fn main() {
    assert_eq!(parse_or_skip("42"), Some(42));
    assert_eq!(parse_or_skip("nope"), None);

    let enabled = true;
    let value: u32 = if enabled { 10 } else { fatal("disabled") };
    assert_eq!(value, 10);
}
```

## More realistic example
```rust
use std::process;

fn require_env(name: &str) -> String {
    match std::env::var(name) {
        Ok(value) => value,
        Err(error) => exit_with_message(&format!("{name} is required: {error}")),
    }
}

fn exit_with_message(message: &str) -> ! {
    eprintln!("{message}");
    process::exit(2);
}

fn main() {
    // The Err arm has type !, so the match expression still has type String.
    let _path = require_env("PATH");
}
```

This is appropriate in a binary boundary where the program really should terminate.
Inside a library, return `Result<String, VarError>` instead so the caller decides how to handle failure.

## Common errors
```rust
fn main() {
    let value = match "42".parse::<u32>() {
        Ok(number) => number,
        // Err(_) => "not a number",
        Err(_) => panic!("not a number"),
    };

    assert_eq!(value, 42);
}
```

If the commented string arm is used, the typical diagnostic is:
`error[E0308]: match arms have incompatible types`.
The fix is not always to `panic!`; usually choose one return type such as `Result<u32, ParseIntError>` or `Option<u32>`.
Use a diverging arm only when the branch should truly never continue.

Another common surprise is an accidental non-diverging loop:

```rust
fn forever() -> ! {
    loop {
        if false {
            break; // error[E0308]: mismatched types, expected `!`, found `()`
        }
    }
}
```

Remove the reachable `break`, return a value type such as `()`, or make the loop break with a value in a function whose return type matches that value.

## Best practice
- ✅ Use explicit `-> !` for functions whose whole contract is "does not return normally."
- ✅ Let diverging control flow simplify `match` and `if` expressions when rejecting, skipping, or exiting a branch.
- ✅ Use [[Result]] for recoverable failure; reserve `panic!` or process exit for unrecoverable states and binary entry points.
- ✅ Treat `loop { ... }` as `!` only when the loop truly cannot `break`.
- ✅ Prefer `return Err(...)` or `?` over a fatal helper when writing library code.
- ✅ Use `std::process::exit` only at the edge of a command-line program; it skips normal unwinding and does not run all destructors.

## Pitfalls
- ⚠️ Do not use `panic!` merely to satisfy a type checker; it turns a recoverable design question into runtime failure. See [[Unwrap and Expect Overuse]].
- ⚠️ Remember that `!` means no value is produced, not "unknown type" or "any value."
- ⚠️ A `loop` with a reachable `break value` has the type of that break value, not `!`.
- ⚠️ Avoid teaching `!` as a normal substitute for every type; the coercion works because there is no runtime value to inspect.
- ⚠️ Do not model business-state impossibility with `panic!`; use enums and exhaustive [[Pattern Matching]] where the state is part of normal control flow.

## See also
[[panic!]] · [[Result]] · [[The Question Mark Operator]] · [[Option vs Result]] · [[Unwrap and Expect Overuse]] · [[Recoverable vs Unrecoverable Errors]] · [[Pattern Matching]] · [[Control Flow]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.3 "The Never Type That Never Returns" — [[the-book]], https://doc.rust-lang.org/book/ch20-03-advanced-types.html#the-never-type-that-never-returns
- The Rust Reference, "Never type" — [[the-reference]], https://doc.rust-lang.org/reference/types/never.html
