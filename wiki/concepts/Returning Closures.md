---
type: concept
title: "Returning Closures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, impl-trait, trait-objects]
domain: "Advanced Types & Features"
difficulty: advanced
related: ["[[Function Pointers]]", "[[Boxed Closure Returns]]", "[[Dynamically Sized Types]]", "[[Trait Objects]]", "[[Type Aliases]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-04-advanced-functions-and-closures.html#returning-closures", "https://doc.rust-lang.org/reference/types/closure.html"]
rust_version: "edition 2024 / 1.85+"
---

# Returning Closures

Return a closure as `impl Fn...` when one concrete closure type is returned, or as `Box<dyn Fn...>` when multiple closure implementations must share one return type.

## What it is
Closures have compiler-generated concrete types that you cannot name directly.
They implement one or more of the closure traits: `Fn`, `FnMut`, and `FnOnce`.

Because closure traits are traits, a function cannot return plain `Fn(i32) -> i32` by value.
Use `impl Fn(i32) -> i32` to return one opaque concrete closure type from a function.
Use `Box<dyn Fn(i32) -> i32>` or another pointer to a trait object when different closure-producing functions or branches must be stored under one type.

## How it works
Each `impl Trait` return position creates a distinct opaque type.
Two functions that both return `impl Fn(i32) -> i32` may still return different hidden types.
You cannot put those returned values into one `Vec` unless you erase the concrete type with a trait object or wrap the choice in a single enum.

Capturing closures usually need `move` when returned because they must own captured values that would otherwise be borrowed from a stack frame that is about to end.

The closure trait depends on what the closure does with captured values, not merely on whether it is written with `move`.
A `move` closure that only reads its captured `String` can still implement `Fn`; a closure that mutates captured state implements `FnMut`; a closure that moves a captured value out of its body implements only `FnOnce`.
Choose the return trait from the call pattern you promise to callers.

Returning `impl Fn...` uses static dispatch and no heap allocation for the closure itself.
Returning `Box<dyn Fn...>` stores the closure environment behind a pointer and dispatches calls through a vtable.
That tradeoff is often correct for heterogeneous plugin lists and runtime-selected handlers, but not needed for a single closure shape.

## Example
```rust
fn add_one() -> impl Fn(i32) -> i32 {
    |x| x + 1
}

fn add_amount(amount: i32) -> impl Fn(i32) -> i32 {
    move |x| x + amount
}

fn boxed_add_amount(amount: i32) -> Box<dyn Fn(i32) -> i32> {
    Box::new(move |x| x + amount)
}

fn main() {
    let f = add_one();
    assert_eq!(f(10), 11);

    let g = add_amount(5);
    assert_eq!(g(10), 15);

    let handlers: Vec<Box<dyn Fn(i32) -> i32>> = vec![boxed_add_amount(1), boxed_add_amount(10)];
    assert_eq!(handlers.iter().map(|h| h(5)).collect::<Vec<_>>(), vec![6, 15]);
}
```

## More realistic example
```rust
fn prefixer(prefix: String) -> impl Fn(&str) -> String {
    move |name| format!("{prefix}{name}")
}

fn counter(start: usize) -> impl FnMut() -> usize {
    let mut next = start;
    move || {
        let current = next;
        next += 1;
        current
    }
}

fn consume_once(token: String) -> impl FnOnce() -> String {
    move || token
}

fn main() {
    let add_user = prefixer(String::from("user:"));
    assert_eq!(add_user("ferris"), "user:ferris");
    assert_eq!(add_user("rust"), "user:rust");

    let mut ids = counter(10);
    assert_eq!(ids(), 10);
    assert_eq!(ids(), 11);

    let take = consume_once(String::from("secret"));
    assert_eq!(take(), "secret");
}
```

This example separates `Fn`, `FnMut`, and `FnOnce` by actual behavior, which is the rule the compiler applies.

## Common errors
```rust
fn bad_prefixer(prefix: String) -> impl Fn(&str) -> String {
    // |name| format!("{prefix}{name}")
    move |name| format!("{prefix}{name}")
}
```

Without `move`, the typical diagnostic is `error[E0373]: closure may outlive the current function, but it borrows ...`.
The fix is to move owned captured data into the returned closure, or return a closure whose lifetime is explicitly tied to borrowed input.

```rust
fn choose(add: bool, amount: i32) -> impl Fn(i32) -> i32 {
    if add {
        move |x| x + amount
    } else {
        // move |x| x * amount
        move |x| x + amount
    }
}
```

If the two branches contain different closure literals, the usual diagnostic is `error[E0308]: if and else have incompatible types`.
Even identical-looking closure literals have distinct anonymous types.
Fix it by boxing (`Box<dyn Fn(i32) -> i32>`) or by returning one closure that contains the branch inside its body.

## Best practice
- ✅ Use `impl Fn...` for a single returned closure shape and static dispatch.
- ✅ Use [[Boxed Closure Returns]] when heterogeneous closures must be stored together or returned from different branches.
- ✅ Add `move` when the returned closure captures values from the function body.
- ✅ Pick the weakest closure trait that matches behavior: `Fn` for shared calls, `FnMut` for mutation, `FnOnce` for consumption.
- ✅ Keep borrowed-returning closure APIs explicit about lifetimes; prefer owned captures when the closure escapes the creating function.
- ✅ Consider a named struct implementing a method when the closure has many configuration fields or needs documentation.

## Pitfalls
- ⚠️ Do not assume two `impl Fn(...)` return types are interchangeable merely because their printed bounds match.
- ⚠️ Do not return `fn(...)` for a closure that captures state; [[Function Pointers]] cannot represent captured environment.
- ⚠️ Boxing a closure adds allocation and dynamic dispatch; use it for type erasure, not by default.
- ⚠️ Do not promise `Fn` if the closure mutates internal state; return `impl FnMut` and require callers to bind it as `mut`.
- ⚠️ Be careful with `impl FnOnce` in containers: calling it consumes the closure, so storage and iteration patterns differ from `Fn` and `FnMut`.

## See also
[[Function Pointers]] · [[Boxed Closure Returns]] · [[Dynamically Sized Types]] · [[Trait Objects]] · [[Type Aliases]] · [[Iterator]] · [[Borrowing]] · [[Move Semantics]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.4 "Returning Closures" — [[the-book]], https://doc.rust-lang.org/book/ch20-04-advanced-functions-and-closures.html#returning-closures
- The Rust Reference, "Closure types" — [[the-reference]], https://doc.rust-lang.org/reference/types/closure.html
