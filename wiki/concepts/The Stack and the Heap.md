---
type: concept
title: "The Stack and the Heap"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, memory, heap]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Move Semantics]]", "[[Copy and Clone]]", "[[The Drop Trait]]", "[[Vec]]", "[[String and str]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/reference/destructors.html"]
rust_version: "edition 2024 / 1.85+"
---

# The Stack and the Heap

The stack stores fixed-size values in last-in-first-out scope order, while the heap stores dynamically sized or growable data behind pointers. Rust's ownership rules make heap cleanup deterministic without a garbage collector.

## What it is
The stack is fast, structured memory used for local variables, function arguments, return addresses, and fixed-size values.
Pushing and popping stack frames is simple because the compiler knows each frame's shape.

The heap is allocator-managed memory used when data size is not known at compile time, may grow, or must outlive a single stack frame through ownership transfer.
A `String` value, for example, stores pointer, length, and capacity on the stack, while its text buffer lives on the heap.

Rust does not make programmers manually pair every allocation with a free.
Instead, the owner of heap-backed data runs [[The Drop Trait]] cleanup when it goes out of scope.

## How it works
Values stored entirely on the stack and implementing [[Copy and Clone]] through `Copy` can be duplicated cheaply.
Values that own heap allocations usually move instead.
Moving a `String` copies its stack metadata to a new owner and invalidates the old binding; it does not copy the heap buffer.

Heap allocation is powerful but has costs: allocator work, pointer indirection, possible cache misses, and capacity management.
Stack values are usually cheaper to create and access, but they must have a known size and cannot grow dynamically.

Collections such as `Vec<T>` and `String` bridge both worlds.
The handle is a fixed-size stack value; the elements or bytes are heap storage managed by the handle's owner.

The stack/heap distinction is about storage strategy, not value importance.
A `Vec<T>` variable on the stack can own a large heap allocation, while a large fixed-size array can
be stack allocated if its size is known and the stack can accommodate it.
Rust's type system tracks the owner of the value, and the standard library type decides whether it
uses the allocator internally.

Borrowing a heap-backed value does not move either the handle or the allocation.
A `&str` borrowed from a `String` points into the string's heap buffer; a `&[T]` borrowed from a
`Vec<T>` points into the vector's element allocation.
Those borrows are why the compiler prevents mutation that could reallocate while the view is still
used.

## Example
```rust
fn main() {
    let stack_number = 42;
    let heap_text = String::from("hello");

    let moved_text = heap_text;
    println!("{stack_number}");
    println!("{moved_text}");
}
```

## Worked example
```rust
fn main() {
    let mut names = Vec::with_capacity(2);
    names.push(String::from("Ada"));
    names.push(String::from("Grace"));

    print_all(&names);

    let moved_names = names;
    println!("{} names", moved_names.len());
}

fn print_all(names: &[String]) {
    for name in names {
        println!("{name}");
    }
}
```

## Common errors
The stack/heap split often appears as a move surprise:

```text
error[E0382]: borrow of moved value: `heap_text`
```

Moving the `String` handle transfers ownership of the heap buffer.
Borrow the text if the original owner should remain usable:

```rust
fn main() {
    let heap_text = String::from("hello");
    print_text(&heap_text);
    println!("{heap_text}");
}

fn print_text(text: &str) {
    println!("{text}");
}
```

## Best practice
- ✅ Use ordinary stack values for small fixed-size data and owned heap-backed types for growable data.
- ✅ Let `String`, `Vec<T>`, `Box<T>`, and other owners manage allocation and deallocation through [[Ownership]].
- ✅ Think about heap allocation when cloning, collecting, boxing, or building strings in hot paths.
- ✅ Prefer borrowing heap-backed data when a function only needs temporary access.
- ✅ Use capacity-aware APIs such as `Vec::with_capacity` or `String::with_capacity` when growth cost is
  predictable and significant.
- ✅ Use `Box<T>` for single heap-owned values when indirection, recursive types, or stable address
  semantics are the actual need.

## Pitfalls
- ⚠️ Do not assume moving a heap-backed owner copies the heap allocation; it transfers ownership of that allocation. See [[Move Semantics]].
- ⚠️ Do not clone large heap data casually; it can turn a cheap borrow into an allocation-heavy deep copy. See [[Needless Clone]].
- ⚠️ Do not store references into growable heap buffers across mutations that may reallocate. See [[Holding Collection Element References Across Mutation]].
- ⚠️ Do not reach for heap allocation just to satisfy the borrow checker; first try clearer ownership or smaller borrow scopes.
- ⚠️ Do not assume "stack is always better"; large stack values can overflow limited stacks, and heap
  allocation can be the right design for size, sharing, or recursion.

## See also
[[Ownership]] · [[Move Semantics]] · [[Copy and Clone]] · [[The Drop Trait]] · [[Vec]] · [[String and str]] · [[Borrowing]] · [[The Slice Type]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.1 "The Stack and the Heap" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- The Rust Reference, "Destructors" — [[the-reference]],
  https://doc.rust-lang.org/reference/destructors.html
