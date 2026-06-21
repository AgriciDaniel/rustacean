---
type: concept
title: "Borrowing"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, borrowing, memory]
domain: "Ownership & Memory"
difficulty: basic
related: ["[[Ownership]]", "[[References]]", "[[Mutable References]]", "[[Lifetimes]]", "[[The Slice Type]]", "[[Borrowed Parameter APIs]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[ownership-borrowing-lifetimes]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#borrow-operators"]
rust_version: "edition 2024 / 1.85+"
---

# Borrowing

Borrowing lets code use a value through `&T` or `&mut T` without taking [[Ownership]] of it. A borrow is temporary access checked at compile time, so the owner remains responsible for dropping the value.

## What it is
Borrowing is the act of creating a [[References]] value with `&` or `&mut`.
The borrowed value still belongs to its owner; the borrower only receives access for a limited lifetime.

This is the normal way to let a function inspect or mutate data without forcing callers to give up ownership and receive it back.
It is why idiomatic Rust APIs often accept `&str`, `&[T]`, `&T`, or `&mut T` rather than owned `String`, `Vec<T>`, or `T`.

Borrowing is also the compiler-visible form of aliasing.
Rust allows many shared borrows for reading, or one mutable borrow for exclusive mutation, but not both at the same time.
Those rules connect this note to [[Lifetimes]], [[Mutable References]], and [[Send and Sync]].

## How it works
The `&` borrow operator creates a shared borrow.
During a shared borrow, the place may be read and shared again, but not mutated through ordinary safe access.
The `&mut` borrow operator creates a mutable borrow.
During a mutable borrow, the borrowed place cannot be accessed by other references until that borrow ends.

Modern Rust uses non-lexical lifetimes, so a borrow usually ends at its last use, not necessarily at the closing brace of the variable's lexical scope.
This lets you read through a borrow, finish using it, and then mutate the original value afterward.

Borrowing does not extend the lifetime of the owner.
If a function returns a reference, the returned reference must be tied to data that still exists after the function returns.
Trying to return a reference to a local value is the [[Returning References to Locals]] antipattern.

Borrowing is checked over places, not only over variable names.
The compiler can often prove that `person.name` and `person.age` are disjoint fields, so separate
borrows of those fields may coexist.
For slices and vectors, index expressions are less transparent to the borrow checker; use APIs such
as `split_at_mut` to prove that two mutable regions do not overlap.

The runtime representation of a shared reference is pointer-like, and a slice reference also carries
length metadata.
The safety comes from the compile-time restrictions around constructing and using those references,
not from a garbage collector or hidden reference-counting for ordinary borrows.

## Example
```rust
fn main() {
    let mut name = String::from("rust");

    let len = length(&name);
    println!("{name} has {len} bytes");

    uppercase_first(&mut name);
    println!("{name}");
}

fn length(s: &str) -> usize {
    s.len()
}

fn uppercase_first(s: &mut String) {
    if let Some(first) = s.get_mut(0..1) {
        first.make_ascii_uppercase();
    }
}
```

## Worked example
```rust
struct Account {
    owner: String,
    cents: i64,
}

fn main() {
    let mut account = Account {
        owner: String::from("Ada"),
        cents: 2_500,
    };

    print_owner(&account.owner);
    deposit(&mut account.cents, 750);

    println!("{} has {}", account.owner, dollars(account.cents));
}

fn print_owner(owner: &str) {
    println!("owner: {owner}");
}

fn deposit(balance: &mut i64, amount: i64) {
    *balance += amount;
}

fn dollars(cents: i64) -> String {
    format!("${:.2}", cents as f64 / 100.0)
}
```

## Common errors
Overlapping a shared borrow with a mutation commonly produces:

```text
error[E0502]: cannot borrow `items` as mutable because it is also borrowed as immutable
```

The usual fix is to use the shared borrow first so it ends, then mutate:

```rust
fn main() {
    let mut items = vec![1, 2, 3];
    let first = items[0];
    println!("{first}");
    items.push(4);
}
```

## Best practice
- ✅ Borrow when a function only needs to read or mutate a caller-owned value temporarily.
- ✅ Prefer borrowed parameter types such as `&str` and `&[T]` for flexible APIs; see [[Borrowed Parameter APIs]].
- ✅ Let borrows end before mutation by using values, then mutating afterward, instead of adding unnecessary `clone` calls.
- ✅ Borrow disjoint struct fields directly when the work truly touches separate fields; see [[Mutable References]].
- ✅ Use small helper functions to make borrow scopes obvious; parameters express exactly which fields
  or buffers are borrowed.
- ✅ Prefer `get`, iterator adapters, and slice methods when they express the borrow shape more clearly
  than manual indexing.

## Pitfalls
- ⚠️ Do not use `.clone()` just to silence a move or borrow error; first check whether borrowing expresses the real ownership contract. See [[Needless Clone]].
- ⚠️ Do not return references to locals; return an owned value or borrow from an input instead. See [[Returning References to Locals]].
- ⚠️ Do not hold a collection element borrow while mutating the collection; reallocation can invalidate the borrow. See [[Holding Collection Element References Across Mutation]].
- ⚠️ Do not replace ordinary borrowing with `Rc<RefCell<T>>` unless runtime-checked shared mutation is truly required. See [[Rc RefCell Overuse]].
- ⚠️ Do not assume a lifetime annotation will shorten or lengthen a borrow; lifetimes describe
  relationships the compiler must verify.

## See also
[[Ownership]] · [[References]] · [[Mutable References]] · [[Lifetimes]] · [[The Slice Type]] · [[Borrowed Parameter APIs]] · [[Needless Clone]] · [[Returning References to Locals]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.2 "References and Borrowing" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- The Rust Reference, "Borrow operators" — [[the-reference]],
  https://doc.rust-lang.org/reference/expressions/operator-expr.html#borrow-operators
