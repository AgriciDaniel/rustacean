---
type: concept
title: "Ownership"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, memory, core]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Borrowing]]", "[[References]]", "[[Lifetimes]]", "[[Move Semantics]]", "[[The Drop Trait]]", "[[Copy and Clone]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html"]
rust_version: "edition 2024 / 1.85+"
---

# Ownership

Ownership is Rust's compile-time discipline for managing memory: every value has exactly one
**owner**, and when the owner goes out of scope the value is dropped (freed). This gives memory
safety with no garbage collector and no manual `free`.

## What it is
The three rules ([the Book, ch. 4.1](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)):

1. Each value in Rust has an owner.
2. There can be only one owner at a time.
3. When the owner goes out of scope, the value is dropped.

The compiler enforces these statically, so use-after-free, double-free, and most leaks become
compile errors rather than runtime bugs.

Ownership is not only about heap memory.
It also describes who is allowed to use any value, including stack-only values, file handles, lock
guards, sockets, iterators, and user-defined structs.
The rule becomes most visible for heap-backed values because dropping the owner releases the heap
allocation, but the same move-and-drop model applies uniformly.

## How it works
Assigning or passing a non-`Copy` value **moves** it: ownership transfers and the source binding is
invalidated. Heap data (e.g. a `String`'s buffer) has a single owner responsible for freeing it via
the [[The Drop Trait]] when scope ends. Because only one owner exists, there is never ambiguity about
who frees the memory — and never two threads freeing it at once, which is also why ownership underpins
Rust's data-race freedom (see [[Concurrency]]).

To *use* a value without taking ownership, you **borrow** it with a reference — see [[Borrowing]] and
[[References]].

At runtime, a move of a type such as `String` is usually just a copy of its fixed-size handle
pointer, length, and capacity.
The important part is compile-time: the old binding is no longer considered initialized, so the
compiler will not generate another destructor call for it.
For a `Copy` type, the compiler instead permits both bindings to remain usable because duplicating
the bits cannot create two owners of the same cleanup obligation.

Ownership also composes through fields.
Moving a whole struct moves all of its fields; moving one non-`Copy` field out can make the original
struct only partially usable until the field is replaced.
That is why APIs often borrow fields for inspection but consume the whole value for transformation.

## Example
```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;            // move: s1's buffer is now owned by s2
    // println!("{s1}");    // ❌ compile error: borrow of moved value `s1`
    println!("{s2}");       // ✅ s2 owns it

    takes_ownership(s2);    // move into the function
    // s2 is no longer usable here

    let n = 5;
    makes_copy(n);          // i32 is Copy: n is copied, still usable
    println!("{n}");        // ✅
} // s2 was moved away; n (Copy) drops trivially

fn takes_ownership(s: String) { println!("{s}"); } // s dropped here
fn makes_copy(n: i32) { println!("{n}"); }
```

## Worked example
```rust
#[derive(Debug)]
struct Message {
    subject: String,
    body: String,
}

fn main() {
    let draft = Message {
        subject: String::from("Ownership"),
        body: String::from("moves make cleanup unambiguous"),
    };

    preview(&draft);
    let sent = send(draft);

    println!("{sent:?}");
}

fn preview(message: &Message) {
    println!("{}: {} bytes", message.subject, message.body.len());
}

fn send(message: Message) -> Message {
    // Taking ownership is appropriate here: sending consumes the draft state.
    message
}
```

## Common errors
The classic ownership diagnostic is using a moved value:

```text
error[E0382]: borrow of moved value: `s1`
```

Fix it by borrowing when the callee only needs access, returning the value to the caller, or cloning
deliberately when two independent owners are required.
For a function signature, that usually means changing `fn len(s: String)` to `fn len(s: &str)` or
`fn len(s: &String)` only when the concrete owner type matters.

## Best practice
- ✅ Prefer **borrowing** (`&T`/`&mut T`) over moving when a function only needs to read or mutate
  in place — pass `&str` not `String`, `&[T]` not `Vec<T>`. See [[Borrowing]].
- ✅ Let values drop naturally by scope; reach for explicit `drop(x)` only to release a lock or
  resource early ([[RAII and Drop Guards]]).
- ✅ Derive [[Copy and Clone]] for small, plain-data types so callers aren't forced to think about moves.
- ✅ Make ownership transfer visible in API names and signatures: `into_inner`, `into_bytes`, and
  `finish(self)` conventionally consume `self`, while `as_str` and `borrow` return views.
- ✅ Prefer a single clear owner for mutable state; add shared ownership (`Rc`, `Arc`) only when the
  domain really has multiple owners.

## Pitfalls
- ⚠️ **Cloning to silence the borrow checker.** Reaching for `.clone()` on every move error hides a
  design problem and costs allocations — see [[Needless Clone]].
- ⚠️ Returning references to locals (the value is dropped at function end) — that's a lifetime error;
  return the owned value or take the buffer as a parameter. See [[Lifetimes]].
- ⚠️ Moving one field out of a struct can leave the rest in a partially moved state; borrow the field
  or use `Option::take`/`mem::take` when you need to extract and keep using the container.
- ⚠️ Shared ownership is not shared mutation by itself; `Rc<T>`/`Arc<T>` share ownership, while
  mutation still needs interior mutability or synchronization.

## See also
[[Borrowing]] · [[References]] · [[Move Semantics]] · [[Lifetimes]] · [[The Drop Trait]] ·
[[Copy and Clone]] · [[Smart Pointers]] · [[Borrowed Parameter APIs]] · [[The Stack and the Heap]] · [[Ownership & Memory]] (MOC)

## Sources
- The Rust Programming Language, ch. 4.1 "What Is Ownership?" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- The Rust Reference, "Memory model / destructors" — [[the-reference]]
