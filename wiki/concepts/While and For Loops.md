---
type: concept
title: "While and For Loops"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, while, for, loops, iterators]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Loop Expressions]]", "[[Arrays]]", "[[If Expressions]]", "[[Iterators]]", "[[Slices]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-05-control-flow.html#conditional-loops-with-while", "https://doc.rust-lang.org/book/ch03-05-control-flow.html#looping-through-a-collection-with-for", "https://doc.rust-lang.org/reference/expressions/loop-expr.html#predicate-loops", "https://doc.rust-lang.org/reference/expressions/loop-expr.html#iterator-loops"]
rust_version: "edition 2024 / 1.85+"
---

# While and For Loops

`while` repeats while a boolean or conditional pattern succeeds, while `for` iterates over values from `IntoIterator` and is the usual choice for collections.

## What it is
`while condition { ... }` runs a block repeatedly as long as the condition remains true. It is best for state-driven loops where the condition is not simply "each item in this collection."

`for pattern in expression { ... }` loops over values produced by an iterator. It is Rust's idiomatic collection loop and avoids manual index bookkeeping.

Both forms evaluate to `()`; use [[Loop Expressions]] with `break value` when the loop itself must compute a non-unit result.

## How it works
A `while` condition must be `bool` or a conditional `let` match. After each successful body execution, the condition is evaluated again.

A `for` expression calls `IntoIterator::into_iter` on the loop expression, repeatedly calls `Iterator::next`, and binds each yielded value to the loop pattern. The Reference specifies this desugaring in terms of standard `IntoIterator`, `Iterator`, and `Option`.

For arrays, `for element in array` consumes or copies elements depending on the element type and context. Use `for element in &array` when you want references instead of moving values.

## Example
```rust
fn main() {
    let mut countdown = 3;
    while countdown > 0 {
        countdown -= 1;
    }
    assert_eq!(countdown, 0);

    let values = [10, 20, 30];
    let mut sum = 0;
    for value in values {
        sum += value;
    }
    assert_eq!(sum, 60);
}
```

## Common errors
Iterating by value can move a collection:

```rust
fn main() {
    let names = vec![String::from("Ferris")];
    for name in names {
        println!("{name}");
    }
    // println!("{}", names.len());
}
```

Typical diagnostic:

```text
error[E0382]: borrow of moved value: `names`
```

Fix with `for name in &names` when later code still needs the collection.

## Best practice
- ✅ Use `for` for arrays, slices, vectors, ranges, and other iterable values.
- ✅ Use `while` when the loop condition is external state or a repeated predicate.
- ✅ Prefer ranges such as `(1..4).rev()` over manual counter loops for fixed numeric repetition.
- ✅ Borrow collections in `for` loops when later code still needs ownership.

## Pitfalls
- ⚠️ Manual index loops can panic if the length or condition changes; see [[Arrays]].
- ⚠️ `while` conditions are not truthy; they must evaluate to `bool` unless using `while let`.
- ⚠️ A `for` loop may move the iterated value; use references if that is not intended.
- ⚠️ `break value` is for `loop`, not ordinary `while` or `for` loops.

## See also
[[Loop Expressions]] · [[Arrays]] · [[Slices]] · [[Vectors]] · [[Iterators]] · [[If Expressions]] · [[Iterator Method Trio]] · [[Ownership]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.5 "Conditional Loops with `while`" — [[the-book]], https://doc.rust-lang.org/book/ch03-05-control-flow.html#conditional-loops-with-while
- The Rust Programming Language, ch. 3.5 "Looping Through a Collection with `for`" — [[the-book]], https://doc.rust-lang.org/book/ch03-05-control-flow.html#looping-through-a-collection-with-for
- The Rust Reference, "Predicate loops" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/loop-expr.html#predicate-loops
- The Rust Reference, "Iterator loops" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/loop-expr.html#iterator-loops
