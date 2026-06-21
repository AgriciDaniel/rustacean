---
type: concept
title: "Capturing the Environment"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, borrowing, ownership]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Closures]]", "[[move Closures]]", "[[Fn, FnMut, FnOnce]]", "[[Borrowing]]", "[[Ownership]]", "[[Move Semantics]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-01-closures.html", "https://doc.rust-lang.org/std/ops/trait.FnMut.html"]
rust_version: "edition 2024 / 1.85+"
---

# Capturing the Environment

Capturing the environment is how a closure uses variables from its surrounding scope by immutable borrow, mutable borrow, or ownership.

## What it is
Closures are not limited to their explicit parameters. A closure body can refer to a nearby
binding, and the compiler records the minimum access the closure needs for that binding.

This is the core difference between closures and ordinary function items: functions cannot
capture local variables, while closures can carry those variables with the callable value.

## How it works
The closure body determines the capture mode:

1. Reading a value can capture it by immutable reference.
2. Mutating a value captures it by mutable reference.
3. Moving a value into or out of the closure captures ownership.

These capture choices interact with [[Borrowing]] exactly like normal references. A closure that
holds a mutable borrow prevents other uses of that value until the borrow ends. A closure that
takes ownership may make the original binding unusable after the closure is created.

The compiler represents captured variables as fields in the closure value. Modern Rust captures
only the parts of a place that are needed when it can, so a closure may capture one field of a
struct instead of treating every use as a borrow of the whole struct. The same ownership rules
still apply: captured references must not outlive their referents, and captured owned values are
dropped when the closure value is dropped.

## Example
```rust
fn main() {
    let label = String::from("items");
    let print_len = |values: &[i32]| {
        println!("{label}: {}", values.len());
    };

    let mut numbers = vec![1, 2, 3];
    print_len(&numbers);

    let mut add = |n| numbers.push(n);
    add(4);
    add(5);

    assert_eq!(numbers, vec![1, 2, 3, 4, 5]);
}
```

`print_len` immutably borrows `label`. `add` mutably borrows `numbers` while it exists and is used.

## Worked example
```rust
struct Metrics {
    seen: usize,
    accepted: usize,
}

fn count_nonempty(lines: &[&str]) -> Metrics {
    let mut metrics = Metrics { seen: 0, accepted: 0 };

    let mut keep = |line: &&str| {
        metrics.seen += 1;
        let ok = !line.trim().is_empty();
        if ok {
            metrics.accepted += 1;
        }
        ok
    };

    let kept: Vec<&str> = lines.iter().copied().filter(&mut keep).collect();
    assert_eq!(kept, vec!["rust", "iterators"]);
    metrics
}

fn main() {
    let metrics = count_nonempty(&["rust", "", "iterators"]);
    assert_eq!((metrics.seen, metrics.accepted), (3, 2));
}
```

The closure mutably captures `metrics`, but it is consumed by the iterator chain before `metrics`
is returned. Passing `&mut keep` lets the adapter call the same stateful closure repeatedly.

## Common errors
```rust
fn main() {
    let mut values = vec![1, 2, 3];
    let mut push = || values.push(4);
    // println!("{values:?}");
    push();
}
```

Uncommenting the `println!` produces a borrow-checking error such as
`error[E0502]: cannot borrow values as immutable because it is also borrowed as mutable`.
Call the closure first, move it into a smaller scope, or drop it before reading `values`.

## Best practice
- ✅ Let closures borrow when the closure does not need to outlive the captured variables.
- ✅ Keep mutating closures close to where they are called so the mutable borrow's scope stays obvious.
- ✅ Use `move` deliberately when crossing thread or lifetime boundaries. See [[move Closures]].
- ✅ Prefer capturing a small reference or scalar over moving a large owned value when the closure stays local.
- ✅ Put mutating closure variables in their own block when you need to use the captured value again afterward.

## Pitfalls
- ⚠️ Defining a mutable-borrowing closure and then trying to read the captured value before the closure is called or dropped.
- ⚠️ Moving a captured value when a repeated-callback API expects `FnMut` or `Fn`. See [[Moving Out of FnMut Closures]].
- ⚠️ Cloning captured data just to appease an error without checking whether borrowing would work. See [[Needless Clone]].
- ⚠️ Assuming a closure's borrow begins only when it is called; the borrow can begin when the closure value is created.
- ⚠️ Returning or storing a borrowing closure past the lifetime of the captured stack data. See [[Lifetimes]].

## See also
[[Closures & Iterators]] · [[Closures]] · [[move Closures]] · [[Fn, FnMut, FnOnce]] · [[Borrowing]] · [[Ownership]] · [[Move Semantics]] · [[Needless Clone]] · [[Lifetimes]] · [[Returning Closures]]

## Sources
- The Rust Programming Language, ch. 13.1 "Capturing References or Moving Ownership" - [[the-book]], https://doc.rust-lang.org/book/ch13-01-closures.html
- Rust standard library, `FnMut` trait - [[std]], https://doc.rust-lang.org/std/ops/trait.FnMut.html
