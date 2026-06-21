---
type: concept
title: "Mutable References"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, borrowing, mutation]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[Borrowing]]", "[[References]]", "[[Lifetimes]]", "[[Shared State with Mutex]]", "[[Holding Collection Element References Across Mutation]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[ownership-borrowing-lifetimes]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#borrow-operators", "https://doc.rust-lang.org/reference/expressions/field-expr.html#borrowing"]
rust_version: "edition 2024 / 1.85+"
---

# Mutable References

A mutable reference, `&mut T`, is an exclusive borrow that lets code mutate a value without taking ownership. Its exclusivity is the rule that lets Rust permit mutation while preventing data races in safe code.

## What it is
`&mut T` means "I have the only active ordinary access to this place for now."
The original owner remains the owner, but it cannot be used while the mutable borrow is active.

This is stricter than just saying the referent can change.
If a mutable reference exists, Rust prevents simultaneous shared references to the same place and prevents a second mutable reference to that same place.
That rule is the everyday form of "aliasing XOR mutability."

Mutable references are used for in-place updates: pushing onto a `String`, sorting a slice, filling a buffer, updating a struct field, or advancing an iterator-like state machine.

## How it works
Creating `&mut value` puts the borrowed place into a mutable borrowed state.
While that state lasts, the place cannot be read, written, moved, or borrowed again through another ordinary access path.
The borrow ends at the last use the compiler can see.

Rust can reason about disjoint fields of a struct.
You may mutably borrow one field and shared-borrow another field when the compiler can see the fields are separate.
For slices, use safe splitting APIs such as `split_at_mut` when you need two mutable references to non-overlapping parts.

The exclusivity rule is about the borrowed place, not about the spelling of the variable.
If `left` and `right` are proven non-overlapping slices, each can be mutated through its own
`&mut [T]`.
If two indexes into the same slice are just runtime integers, safe Rust will not manufacture two
`&mut T` values from indexing alone because it cannot prove the indexes differ.

`&mut T` also enables reborrowing.
Passing `&mut value` into a helper often creates a shorter mutable borrow derived from a longer one;
after the helper returns and the shorter borrow is no longer used, the original mutable reference can
be used again.
This is how methods can temporarily lend part of their exclusive access without giving it away
forever.

## Example
```rust
fn main() {
    let mut scores = [10, 20, 30, 40];

    let (left, right) = scores.split_at_mut(2);
    left[0] += 1;
    right[0] += 5;

    println!("{scores:?}");
}
```

## Worked example
```rust
#[derive(Debug)]
struct Cursor {
    bytes: Vec<u8>,
    position: usize,
}

fn main() {
    let mut cursor = Cursor {
        bytes: b"abc".to_vec(),
        position: 0,
    };

    advance(&mut cursor);
    cursor.bytes.push(b'd');

    println!("{cursor:?}");
}

fn advance(cursor: &mut Cursor) {
    if cursor.position < cursor.bytes.len() {
        cursor.bytes[cursor.position] = cursor.bytes[cursor.position].to_ascii_uppercase();
        cursor.position += 1;
    }
}
```

## Common errors
Two active mutable borrows of the same place are rejected:

```text
error[E0499]: cannot borrow `values` as mutable more than once at a time
```

For non-overlapping slice regions, use `split_at_mut`:

```rust
fn bump_edges(values: &mut [i32]) {
    if values.len() < 2 {
        return;
    }

    let last_index = values.len() - 1;
    let (first, rest) = values.split_at_mut(1);
    first[0] += 1;
    rest[last_index - 1] += 1;
}
```

## Best practice
- ✅ Take `&mut T` when a function mutates a caller-owned value in place and does not need to keep it afterward.
- ✅ Narrow the scope of mutable borrows by using smaller blocks, helper functions, or last-use ordering.
- ✅ Use `split_at_mut`, field borrowing, or dedicated APIs to prove disjointness to the compiler.
- ✅ Prefer one clear owner plus temporary `&mut` borrows before reaching for shared mutable ownership.
- ✅ Prefer methods that take `&mut self` when mutation is part of a type's invariant-preserving API.
- ✅ Use `Option::take`, `mem::take`, or `mem::replace` when you need to move a field out through a
  mutable reference and leave a valid replacement behind.

## Pitfalls
- ⚠️ Do not hold an immutable borrow and then call a method that needs `&mut self`; use the borrowed value first, then mutate. See [[Borrowing]].
- ⚠️ Do not create `Rc<RefCell<T>>` just to avoid restructuring a borrow; that moves checks from compile time to runtime. See [[Rc RefCell Overuse]].
- ⚠️ Do not keep references into a `Vec` across `push`, `insert`, or other possible reallocation. See [[Holding Collection Element References Across Mutation]].
- ⚠️ Do not hold locks or runtime mutable borrows longer than needed; this can block progress or panic. See [[Holding Locks Too Long]].
- ⚠️ Do not assume `mut` on a binding and `&mut` mean the same thing; `let mut x` permits changing
  the binding's value, while `&mut x` grants exclusive borrowed access.

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[Lifetimes]] · [[Shared State with Mutex]] · [[Rc RefCell Overuse]] · [[Holding Collection Element References Across Mutation]] · [[The Slice Type]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.2 "Mutable References" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- The Rust Reference, "Borrow operators" and field borrowing — [[the-reference]],
  https://doc.rust-lang.org/reference/expressions/operator-expr.html#borrow-operators
  https://doc.rust-lang.org/reference/expressions/field-expr.html#borrowing
