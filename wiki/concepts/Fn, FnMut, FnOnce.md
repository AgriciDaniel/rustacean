---
type: concept
title: "Fn, FnMut, FnOnce"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, traits, callable]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Closures]]", "[[Capturing the Environment]]", "[[move Closures]]", "[[Iterator Adapters]]", "[[Function Pointers]]", "[[Moving Out of FnMut Closures]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-01-closures.html", "https://doc.rust-lang.org/std/ops/trait.Fn.html", "https://doc.rust-lang.org/std/ops/trait.FnMut.html", "https://doc.rust-lang.org/std/ops/trait.FnOnce.html"]
rust_version: "edition 2024 / 1.85+"
---

# Fn, FnMut, FnOnce

`Fn`, `FnMut`, and `FnOnce` are the call traits that describe whether a closure can be called immutably, mutably, or at least once by value.

## What it is
Closure-accepting APIs use these traits as bounds. The bound tells callers what the API may do
with the callback:

`FnOnce` can be called once. `FnMut` can be called repeatedly with mutable access to its captured
state. `Fn` can be called repeatedly without mutating captured state.

## How it works
The traits are additive in practice:

1. All closures implement `FnOnce`.
2. Closures that do not move captured values out of the body can also implement `FnMut`.
3. Closures that do not mutate or move out of captured values can also implement `Fn`.

Choose the weakest bound your API needs. If your function calls a callback once, accept `FnOnce`.
If it calls repeatedly and allows stateful mutation, accept `FnMut`. If it needs shared,
repeatable, nonmutating calls, accept `Fn`.

The receiver mode mirrors the trait name: `FnOnce` consumes the closure value, `FnMut` calls it
through `&mut self`, and `Fn` calls it through `&self`. Function items and function pointers can
implement all three because they have no captured state to consume or mutate.

## Example
```rust
fn call_once<F>(f: F) -> String
where
    F: FnOnce() -> String,
{
    f()
}

fn call_twice<F>(mut f: F) -> i32
where
    F: FnMut() -> i32,
{
    f() + f()
}

fn main() {
    let name = String::from("rust");
    assert_eq!(call_once(|| name), "rust");

    let mut n = 0;
    assert_eq!(call_twice(|| {
        n += 1;
        n
    }), 3);
}
```

The first closure moves `name` out and is only `FnOnce`. The second mutates captured state and
fits `FnMut`.

## Worked example
```rust
fn retry<T, E, F>(times: usize, mut operation: F) -> Result<T, E>
where
    F: FnMut() -> Result<T, E>,
{
    let mut last = None;
    for _ in 0..times {
        match operation() {
            Ok(value) => return Ok(value),
            Err(err) => last = Some(err),
        }
    }
    Err(last.expect("retry called with zero attempts"))
}

fn main() {
    let mut attempts = 0;
    let result = retry(3, || {
        attempts += 1;
        if attempts == 2 { Ok("ready") } else { Err("not yet") }
    });

    assert_eq!(result, Ok("ready"));
    assert_eq!(attempts, 2);
}
```

`retry` must accept `FnMut` because it calls the closure more than once and allows the closure to
update captured state between calls.

## Common errors
```rust
fn call_twice<F: FnMut()>(mut f: F) {
    f();
    f();
}

fn main() {
    let text = String::from("once");
    // call_twice(|| drop(text));
}
```

Uncommenting the call gives `error[E0507]: cannot move out of text, a captured variable in an
FnMut closure`. Fix it by changing the API to `FnOnce` if it calls once, borrowing `text`, or
cloning deliberately inside the closure when each call needs owned data.

## Best practice
- ✅ Accept `FnOnce` for lazy fallbacks that are called zero or one time, like `unwrap_or_else`.
- ✅ Accept `FnMut` for repeated callbacks such as sorting keys, visitors, or iterator-like loops.
- ✅ Accept `Fn` only when mutation is not needed or concurrent repeated calls matter.
- ✅ Use `mut f: F` in the parameter or local binding when calling an `FnMut` argument.
- ✅ Document whether your callback may be called zero times, once, many times, or after partial progress.

## Pitfalls
- ⚠️ Requiring `Fn` when `FnMut` would work; this rejects useful stateful closures.
- ⚠️ Requiring `FnMut` when the callback is called only once; this rejects move-out closures unnecessarily.
- ⚠️ Moving a captured value out inside a closure passed to a repeated-call API. See [[Moving Out of FnMut Closures]].
- ⚠️ Forgetting that `FnOnce` is the most permissive bound for callers but the least capable for callees.
- ⚠️ Boxing as `dyn Fn` when the closure mutates state; the trait object must match the needed call trait.

## See also
[[Closures & Iterators]] · [[Closures]] · [[Capturing the Environment]] · [[move Closures]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Function Pointers]] · [[Moving Out of FnMut Closures]] · [[Returning Closures]] · [[Boxed Closure Returns]]

## Sources
- The Rust Programming Language, ch. 13.1 "Moving Captured Values Out of Closures" - [[the-book]], https://doc.rust-lang.org/book/ch13-01-closures.html
- Rust standard library call traits - [[std]], https://doc.rust-lang.org/std/ops/trait.Fn.html, https://doc.rust-lang.org/std/ops/trait.FnMut.html, https://doc.rust-lang.org/std/ops/trait.FnOnce.html
