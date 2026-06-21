---
type: concept
title: "Higher-Ranked Trait Bounds"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, lifetimes, hrtb, trait-bounds, type-system]
domain: "Advanced Type System"
difficulty: advanced
related: ["[[Lifetimes]]", "[[Trait Bounds]]", "[[Closures]]", "[[Fn, FnMut, FnOnce]]", "[[Generic Associated Types]]", "[[Variance]]", "[[Advanced Type System]]"]
sources: ["[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds", "https://doc.rust-lang.org/nomicon/hrtb.html"]
rust_version: "edition 2024 / 1.85+"
---

# Higher-Ranked Trait Bounds

A higher-ranked trait bound says a trait obligation must hold for every lifetime chosen by the caller or callee.
Reach for `for<'a>` when a callback, function pointer, or trait object must work with borrows that cannot be named ahead of time.

## What it is
Most lifetime parameters name one concrete lifetime per use of a generic item.
An HRTB quantifies over lifetimes with `for<'a>`, expressing a bound that is true for all possible `'a`.
The common form is `F: for<'a> Fn(&'a T)`.
That does not mean "some lifetime"; it means "any lifetime the function body needs to pass."
This matters when the borrow is created inside the function and is shorter than any lifetime parameter the caller could provide.
HRTBs appear in where clauses, trait object types, function pointer types, and bounds on associated types.
They are a core tool behind ergonomic callback APIs.
They also interact with [[Variance]] because higher-ranked function pointers and trait objects have their own subtyping behavior.

## How it works
The syntax can place `for<'a>` before the trait path or before the whole bound.
`where for<'a> F: Fn(&'a i32)` scopes `'a` over the full bound.
`where F: for<'a> Fn(&'a i32)` scopes `'a` over the following trait path.
For everyday callback bounds these forms are equivalent.
The callee may create a local value, borrow it for a short compiler-chosen lifetime, and call the callback.
Without `for<'a>`, the function would require the caller to choose a lifetime, which cannot name the callee's local stack frame.
HRTBs are especially useful for APIs that lend temporary references but do not let them escape.
When the reference must escape as an associated type, a [[Generic Associated Types]] design may be more appropriate.

## Example
```rust
fn with_temp<F, R>(f: F) -> R
where
    F: for<'a> Fn(&'a str) -> R,
{
    let value = String::from("temporary");
    f(value.as_str())
}

fn main() {
    let len = with_temp(|s| s.len());
    assert_eq!(len, 9);

    let upper = with_temp(|s| s.to_uppercase());
    assert_eq!(upper, "TEMPORARY");
}
```

## Edge cases
```rust
fn call_twice<F>(f: F)
where
    F: for<'a> Fn(&'a i32),
{
    let a = 1;
    let b = 2;
    f(&a);
    f(&b);
}

fn main() {
    call_twice(|n| assert!(*n == 1 || *n == 2));
}
```

## Best practice
- ✅ Use `for<'a>` when the callee creates the borrowed value and the callback must accept that borrow.
- ✅ Prefer HRTBs for callback APIs that consume borrows immediately and do not store them.
- ✅ Keep HRTB-heavy signatures in `where` clauses so the quantification is readable.
- ✅ Combine HRTBs with [[Fn, FnMut, FnOnce]] according to how the callback is invoked.
- ✅ Consider a named trait when repeated HRTB bounds make public signatures difficult to scan.
- ✅ Use [[Generic Associated Types]] when the API returns a value tied to the borrow rather than only calling a closure.

## Pitfalls
- ⚠️ Reading `for<'a>` as "there exists a lifetime"; it means "for all lifetimes."
- ⚠️ Trying to return the borrowed argument from an HRTB callback into a longer-lived place; the whole point is that the lifetime may be arbitrarily short.
- ⚠️ Adding a named lifetime parameter to the outer function when the needed lifetime is created inside the function.
- ⚠️ Combining HRTBs with trait objects without checking [[dyn Compatibility (Object Safety)]].
- ⚠️ Hiding a simple borrowed-parameter API behind HRTBs when ordinary [[Lifetime Elision]] would do.

## See also
[[Advanced Type System]]
[[Lifetimes]]
[[The 'static Lifetime]]
[[Trait Bounds]]
[[Where Clauses]]
[[Fn, FnMut, FnOnce]]
[[Closures]]
[[Variance]]
[[Generic Associated Types]]
[[Required Bounds on Generic Associated Types]]

## Sources
- The Rust Reference, "Higher-ranked trait bounds" — [[the-reference]],
  https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds
- The Rustonomicon, "Higher-Rank Trait Bounds" — [[rustonomicon]],
  https://doc.rust-lang.org/nomicon/hrtb.html
