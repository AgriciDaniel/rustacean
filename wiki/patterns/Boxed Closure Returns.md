---
type: pattern
title: "Boxed Closure Returns"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, pattern, closures, trait-objects]
domain: "Advanced Types & Features"
difficulty: advanced
related: ["[[Returning Closures]]", "[[Function Pointers]]", "[[Dynamically Sized Types]]", "[[Type Aliases]]", "[[Trait Objects]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-04-advanced-functions-and-closures.html#returning-closures", "https://doc.rust-lang.org/reference/types/trait-object.html"]
rust_version: "edition 2024 / 1.85+"
---

# Boxed Closure Returns

Box a closure behind `dyn Fn`, `dyn FnMut`, or `dyn FnOnce` when different closure types must be returned or stored through one common type.

## What it is
`Box<dyn Fn(i32) -> i32>` is an owned trait object for callable values.
It erases the concrete closure type and gives callers one sized handle they can store, return, and place in collections.

This is the usual solution when multiple functions return closures with the same call signature but different captured environments.
It is also useful when branches of one function produce different closure literals.
Without boxing or another enum-like wrapper, each closure literal has a distinct anonymous type.

Use this pattern deliberately.
It buys uniformity at the cost of heap allocation and dynamic dispatch.

## How it works
`dyn Fn(...) -> ...` is dynamically sized, so it must be behind a pointer such as `Box`, `&`, `Arc`, or `Rc`.
`Box<dyn Fn(...) -> ...>` owns the closure and stores the closure environment on the heap.
Calling the boxed closure dispatches through the trait object.

Add `Send`, `Sync`, or `'static` bounds when the closure crosses threads or outlives the current stack frame.
For example, `Box<dyn Fn() + Send + 'static>` is a common callback shape for work queues.

The boxed value has one concrete outer type, even when the closures inside have different anonymous types.
That is what lets different branches return a shared type and lets collections store heterogeneous callables.
The inner closure environment is still strongly typed before erasure; the trait object only exposes the chosen call trait and auto-trait bounds.

Lifetimes are part of the trait object type.
`Box<dyn Fn()>` often means the captured references must live long enough for the box's use; APIs that store callbacks usually require `Box<dyn Fn() + 'static>` so the callback does not borrow a stack frame that has ended.

## Example
```rust
type Handler = Box<dyn Fn(i32) -> i32>;

fn make_handler(kind: &str) -> Handler {
    match kind {
        "double" => Box::new(|x| x * 2),
        "offset" => {
            let offset = 10;
            Box::new(move |x| x + offset)
        }
        _ => Box::new(|x| x),
    }
}

fn main() {
    let handlers = vec![make_handler("double"), make_handler("offset"), make_handler("id")];
    let outputs: Vec<i32> = handlers.iter().map(|handler| handler(5)).collect();

    assert_eq!(outputs, vec![10, 15, 5]);
}
```

## More realistic example
```rust
type Filter = Box<dyn Fn(&str) -> bool + Send + Sync + 'static>;

fn make_filter(kind: &str, needle: String) -> Filter {
    match kind {
        "prefix" => Box::new(move |value| value.starts_with(&needle)),
        "suffix" => Box::new(move |value| value.ends_with(&needle)),
        _ => Box::new(|_| true),
    }
}

fn accepted<'a>(values: &'a [&'a str], filter: &Filter) -> Vec<&'a str> {
    values.iter().copied().filter(|value| filter(*value)).collect()
}

fn main() {
    let values = ["api/users", "api/health", "admin/users"];
    let filter = make_filter("prefix", String::from("api/"));

    assert_eq!(accepted(&values, &filter), vec!["api/users", "api/health"]);
}
```

The owned `needle` moves into whichever closure needs it, and the boxed trait object gives every branch one return type.

## Common errors
```rust
fn choose(add: bool) -> impl Fn(i32) -> i32 {
    let amount = 2;
    if add {
        move |x| x + amount
    } else {
        // move |x| x * amount
        move |x| x + amount
    }
}
```

With genuinely different closure literals in the branches, the usual diagnostic is `error[E0308]: if and else have incompatible types`.
Fix it by returning `Box<dyn Fn(i32) -> i32>`:

```rust
fn choose(add: bool) -> Box<dyn Fn(i32) -> i32> {
    let amount = 2;
    if add {
        Box::new(move |x| x + amount)
    } else {
        Box::new(move |x| x * amount)
    }
}
```

Another common lifetime error:

```rust
fn bad<'a>(prefix: &'a str) -> Box<dyn Fn(&str) -> String + 'a> {
    Box::new(move |name| format!("{prefix}{name}"))
}
```

If an API instead requires `Box<dyn Fn(&str) -> String + 'static>`, this borrowed prefix will fail with a lifetime diagnostic.
Move an owned `String` into the closure, or make the returned trait object's lifetime explicit as shown.

## Best practice
- ✅ Prefer `impl Fn...` for one concrete closure return path; use boxing when you need type erasure.
- ✅ Add bounds such as `Send + Sync + 'static` only when the storage or thread model requires them.
- ✅ Use a [[Type Aliases]] name for long boxed callback types that repeat across an API.
- ✅ Consider an enum when the set of closure variants is small and performance-sensitive.
- ✅ Use `Box<dyn FnMut...>` for stateful callbacks that mutate captured state, and call them through a mutable binding.
- ✅ Keep lifetime bounds explicit in library APIs; defaulting to `'static` is common for stored callbacks but too restrictive for short-lived borrowed callbacks.

## Pitfalls
- ⚠️ Do not box closures reflexively; allocation and dynamic dispatch are real costs.
- ⚠️ Captured references can make boxed closures fail lifetime checks; use `move` and owned data when the closure must outlive the caller.
- ⚠️ A `Vec<impl Fn(...)>` is not a way to store heterogeneous closures; see [[Returning Closures]].
- ⚠️ Do not add `Send` or `Sync` after capturing `Rc`, `RefCell`, or other non-thread-safe values; choose `Arc`, `Mutex`, or a single-threaded API deliberately.
- ⚠️ `Box<dyn FnOnce()>` can be called only once; design queues and task runners around consumption.

## See also
[[Returning Closures]] · [[Function Pointers]] · [[Dynamically Sized Types]] · [[Type Aliases]] · [[Trait Objects]] · [[Iterator]] · [[Borrowing]] · [[Move Semantics]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.4 "Returning Closures" — [[the-book]], https://doc.rust-lang.org/book/ch20-04-advanced-functions-and-closures.html#returning-closures
- The Rust Reference, "Trait objects" — [[the-reference]], https://doc.rust-lang.org/reference/types/trait-object.html
