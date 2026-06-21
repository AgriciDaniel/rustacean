---
type: concept
title: "Function Pointers"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, functions, closures, fn, pointers]
domain: "Advanced Types & Features"
difficulty: intermediate
related: ["[[Returning Closures]]", "[[Boxed Closure Returns]]", "[[Fully Qualified Syntax]]", "[[Iterator]]", "[[Trait Objects]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-04-advanced-functions-and-closures.html#function-pointers", "https://doc.rust-lang.org/reference/types/function-pointer.html"]
rust_version: "edition 2024 / 1.85+"
---

# Function Pointers

A function pointer, written with lowercase `fn`, is a value that points to a function item with a known signature and can be called like a function.

## What it is
Rust functions can be passed as values.
When a function item is used where a function pointer is expected, it coerces to the `fn(...) -> ...` function pointer type.

Do not confuse lowercase `fn` with the closure traits `Fn`, `FnMut`, and `FnOnce`.
`fn(i32) -> i32` is a concrete pointer type.
`F: Fn(i32) -> i32` is a generic bound for anything callable without mutation or consumption, including function pointers and many closures.

Function pointers implement all three closure traits.
That means an API that accepts `F: Fn(...)` can accept both named functions and non-capturing or capturing closures, while an API that accepts `fn(...)` excludes capturing closures.

## How it works
Use `fn` when the contract truly requires a plain function pointer, such as an FFI callback shape or a table of non-capturing function operations.
For most Rust APIs, prefer generic closure bounds because they accept more callers and still allow static dispatch.

Enum variant constructors can also act like function pointers.
For example, `Status::Value` can be passed to `Iterator::map` to convert integers into enum values.
Fully qualified syntax often appears with named methods such as `ToString::to_string` when there are several methods with the same name.

A named function expression first has a unique zero-sized function item type.
It coerces to a `fn(...) -> ...` pointer when a function pointer is expected, or when multiple function item types with the same signature must meet in one branch expression.
Non-capturing, non-async closures can also coerce to function pointers.
Capturing closures cannot, because a plain function pointer has nowhere to store captured environment.

ABI and safety are part of the type.
`fn(i32) -> i32`, `unsafe fn(i32) -> i32`, and `extern "C" fn(i32) -> i32` are distinct shapes and should be spelled explicitly in FFI-facing APIs.

## Example
```rust
fn add_one(value: i32) -> i32 {
    value + 1
}

fn do_twice(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value) + f(value)
}

fn do_twice_generic<F>(f: F, value: i32) -> i32
where
    F: Fn(i32) -> i32,
{
    f(value) + f(value)
}

fn main() {
    assert_eq!(do_twice(add_one, 5), 12);

    let bonus = 3;
    assert_eq!(do_twice_generic(|x| x + bonus, 5), 16);
}
```

## More realistic example
```rust
#[derive(Debug, Copy, Clone, PartialEq, Eq)]
enum Op {
    Trim,
    Upper,
}

fn trim(input: String) -> String {
    input.trim().to_owned()
}

fn upper(input: String) -> String {
    input.to_uppercase()
}

fn operation(op: Op) -> fn(String) -> String {
    match op {
        Op::Trim => trim,
        Op::Upper => upper,
    }
}

fn main() {
    let pipeline: [fn(String) -> String; 2] = [operation(Op::Trim), operation(Op::Upper)];
    let output = pipeline
        .into_iter()
        .fold(String::from(" ferris "), |value, step| step(value));

    assert_eq!(output, "FERRIS");
}
```

This is a good fit because the table contains named, non-capturing operations.
If a step needs configuration, use `impl Fn` or `Box<dyn Fn>` instead.

## Common errors
```rust
fn accepts_fn(f: fn(i32) -> i32) -> i32 {
    f(10)
}

fn main() {
    let offset = 5;
    // accepts_fn(|x| x + offset);
    // error[E0308]: mismatched types
    // note: closures can only be coerced to `fn` types if they do not capture any variables
}
```

Fix it by changing the API to a closure bound:

```rust
fn accepts_callable<F>(f: F) -> i32
where
    F: Fn(i32) -> i32,
{
    f(10)
}

fn main() {
    let offset = 5;
    assert_eq!(accepts_callable(|x| x + offset), 15);
}
```

Another common FFI mistake is forgetting that `extern "C" fn` is not the same type as Rust ABI `fn`.
Spell the ABI in the callback type and keep unsafe callbacks as `unsafe extern "C" fn(...)` when the callee contract requires it.

## Best practice
- ✅ Prefer `F: Fn(...)`, `F: FnMut(...)`, or `F: FnOnce(...)` for ordinary Rust callbacks.
- ✅ Use `fn(...) -> ...` when capturing closures must be rejected or an external ABI expects a function pointer.
- ✅ Use named functions in iterator adapters when they make intent clearer than an inline closure.
- ✅ Keep ABI-sensitive callbacks explicit; `extern "C" fn(...)` is a different function pointer type from Rust ABI `fn(...)`.
- ✅ Use function-pointer arrays for compact dispatch tables of stateless operations.
- ✅ Reach for [[Fully Qualified Syntax]] in adapters such as `.map(ToString::to_string)` when several same-named methods exist.

## Pitfalls
- ⚠️ A capturing closure cannot coerce to `fn`; use a closure trait bound or a trait object instead.
- ⚠️ Do not return `fn` if the implementation captures local state; see [[Returning Closures]] and [[Boxed Closure Returns]].
- ⚠️ Do not choose `fn` just because the syntax is shorter; it narrows the API.
- ⚠️ Do not erase safety or ABI details behind a vague alias in FFI code.
- ⚠️ Function pointer calls are indirect when the identity is not known; for hot generic Rust paths, a closure trait bound may optimize better.

## See also
[[Returning Closures]] · [[Boxed Closure Returns]] · [[Fully Qualified Syntax]] · [[Iterator]] · [[Trait Objects]] · [[Dynamically Sized Types]] · [[Type Aliases]] · [[FFI]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.4 "Function Pointers" — [[the-book]], https://doc.rust-lang.org/book/ch20-04-advanced-functions-and-closures.html#function-pointers
- The Rust Reference, "Function pointer types" — [[the-reference]], https://doc.rust-lang.org/reference/types/function-pointer.html
