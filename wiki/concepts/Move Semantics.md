---
type: concept
title: "Move Semantics"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, moves, memory]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Borrowing]]", "[[Copy and Clone]]", "[[The Drop Trait]]", "[[The Stack and the Heap]]", "[[Needless Clone]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/reference/expressions.html#place-expressions-and-value-expressions"]
rust_version: "edition 2024 / 1.85+"
---

# Move Semantics

Move semantics are Rust's rule that assigning, passing, or returning a non-`Copy` value transfers ownership instead of duplicating the owned resource. After a move, the old binding is no longer usable.

## What it is
A move transfers [[Ownership]] of a value from one place to another.
For types such as `String`, `Vec<T>`, and most user-defined resource owners, Rust copies the small stack representation but invalidates the old binding.
It does not automatically deep-copy heap data.

This prevents double-free bugs.
If two `String` bindings both thought they owned the same heap allocation, both would try to free it when dropped.
By allowing only one owner after the assignment, Rust knows exactly which value will run [[The Drop Trait]] logic.

Moves happen in assignment, function arguments, return values, pattern matching, closure capture, and many other value-consuming contexts.

## How it works
When a non-`Copy` value is moved, the destination becomes the owner.
The source is treated as uninitialized for ordinary use.
The compiler rejects reads, borrows, or drops of the moved-from binding.

Returning a value moves it to the caller.
Passing a value by value moves it into the callee unless the type implements [[Copy and Clone]] through `Copy`.
Borrowing with `&T` or `&mut T` avoids moving when the callee only needs temporary access.

Assignment to an already-initialized variable first drops the old value, then stores the new value.
That immediate drop behavior matters for resources such as files, locks, buffers, and heap allocations.

Moves can be partial.
If you move one non-`Copy` field out of a struct, fields that were not moved may still be accessible,
but the whole struct cannot be used as a complete value until the missing field is replaced.
Pattern matching can also move fields unless you match by reference with `ref`, `ref mut`, or by
borrowing the scrutinee.

The compiler tracks initialization state to decide which destructors must run.
A moved-from place is not dropped; the new owner is.
This is why move semantics prevent double-free while still compiling down to simple operations for
many types.

## Example
```rust
fn main() {
    let title = String::from("Rust");
    let title = add_suffix(title);

    println!("{title}");
}

fn add_suffix(mut s: String) -> String {
    s.push_str(" notes");
    s
}
```

## Worked example
```rust
#[derive(Debug)]
struct Job {
    id: u64,
    payload: String,
}

fn main() {
    let job = Job {
        id: 7,
        payload: String::from("render"),
    };

    let payload = job.payload;
    println!("job {} payload: {payload}", job.id);
    // println!("{job:?}"); // job is partially moved: payload is gone.
}
```

## Common errors
Using a value after moving it gives:

```text
error[E0382]: use of moved value: `value`
```

When only inspection is needed, borrow instead of moving:

```rust
fn main() {
    let value = String::from("data");
    print_len(&value);
    println!("{value}");
}

fn print_len(value: &str) {
    println!("{}", value.len());
}
```

## Best practice
- ✅ Take ownership when a function consumes, stores, transforms, or returns the value as a new owner.
- ✅ Borrow instead when the function only needs to inspect or temporarily mutate a value.
- ✅ Use `clone` only when two independent owned values are actually required.
- ✅ Design ownership flow so a value has a clear final owner after construction or transformation.
- ✅ Use `Option<T>` fields plus `take()` for state machines that need to move a value out while
  leaving the parent object valid.
- ✅ Prefer by-value builders and transformation methods when consuming the old value communicates a
  real state transition.

## Pitfalls
- ⚠️ Do not assume assignment deep-copies heap data; Rust moves non-`Copy` owners by default.
- ⚠️ Do not scatter `.clone()` around move errors without understanding the ownership contract. See [[Needless Clone]].
- ⚠️ Do not expect a moved variable to be dropped at its old binding; the destination owner controls the drop.
- ⚠️ Do not move out of a value while references to it are still needed; restructure around [[Borrowing]] or smaller scopes.
- ⚠️ Do not destructure by value when you meant to inspect fields; match on `&value` or borrow fields
  explicitly to avoid accidental moves.

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[Copy and Clone]] · [[The Drop Trait]] · [[The Stack and the Heap]] · [[Needless Clone]] · [[Returning References to Locals]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.1 "Variables and Data Interacting with Move" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- The Rust Reference, "Place expressions and value expressions" — [[the-reference]],
  https://doc.rust-lang.org/reference/expressions.html#place-expressions-and-value-expressions
