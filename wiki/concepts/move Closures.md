---
type: concept
title: "move Closures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, move, ownership]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Closures]]", "[[Capturing the Environment]]", "[[Fn, FnMut, FnOnce]]", "[[Ownership]]", "[[Move Semantics]]", "[[Concurrency]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-01-closures.html", "https://doc.rust-lang.org/std/thread/fn.spawn.html"]
rust_version: "edition 2024 / 1.85+"
---

# move Closures

A `move` closure forces captured values to be captured by value, which is essential when the closure may outlive the current stack frame.

## What it is
The `move` keyword before a closure parameter list changes capture from "minimum needed by the
body" to "capture used environment values by value." The closure can still read those values
immutably inside its body; `move` describes how values enter the closure, not necessarily how they
are used later.

This is common for thread closures, stored callbacks, and returned closures where borrowing local
stack variables would be invalid.

## How it works
For non-`Copy` values, `move` transfers ownership into the closure. The original binding is then
usually unavailable. For `Copy` values, the closure captures a copy.

The closure's call trait still depends on what the body does. A `move` closure that only reads its
owned capture can implement `Fn`; a `move` closure that moves a captured value out of the body is
only `FnOnce`.

For references, `move` moves the reference value into the closure, not the referenced data. That
distinction matters when returning iterators: `move |line| line.contains(query)` may only move an
`&str` into the closure, while the actual text still must outlive the returned iterator.

## Example
```rust
use std::thread;

fn main() {
    let values = vec![1, 2, 3];

    let handle = thread::spawn(move || {
        values.iter().sum::<i32>()
    });

    assert_eq!(handle.join().unwrap(), 6);
}
```

The spawned thread needs ownership because it may run after the creating stack frame has moved on.

## Worked example
```rust
fn prefixed<'a>(prefix: &'a str, words: &'a [&'a str]) -> impl Iterator<Item = &'a str> {
    words
        .iter()
        .copied()
        .filter(move |word| word.starts_with(prefix))
}

fn main() {
    let words = ["rust", "ruby", "borrow"];
    let found: Vec<&str> = prefixed("ru", &words).collect();
    assert_eq!(found, vec!["rust", "ruby"]);
}
```

The returned `filter` iterator stores the closure. `move` ensures the closure owns its copy of the
`prefix` reference, avoiding a borrow of the local parameter slot while still tying the referenced
string to lifetime `'a`.

## Common errors
```rust
fn main() {
    let values = vec![1, 2, 3];
    let print = move || println!("{values:?}");
    // println!("{}", values.len());
    print();
}
```

Uncommenting the outer `println!` gives `error[E0382]: borrow of moved value: values`. Clone before
the `move` closure if both places need ownership, or remove `move` when the closure stays local
and borrowing is sufficient.

## Best practice
- ✅ Use `move` when sending closures to threads or storing them beyond the current scope.
- ✅ Remember that `move` does not mean `FnOnce` by itself; the closure body decides whether values are moved out.
- ✅ Clone explicitly before a `move` closure only when both the outer scope and the closure need owned data.
- ✅ For returned iterator pipelines, use `move` on closures that capture parameters by reference so the iterator owns the reference values.
- ✅ Keep the capture list small by moving only the values the closure actually uses.

## Pitfalls
- ⚠️ Adding `move` and then expecting to keep using a non-`Copy` captured value outside the closure.
- ⚠️ Using `move` as a substitute for understanding lifetimes; sometimes a borrow is the clearer local solution.
- ⚠️ Capturing a large owned value by move into a closure that is cloned or stored widely. See [[Needless Clone]] and [[Ownership]].
- ⚠️ Assuming `move` extends lifetimes. It moves ownership or references; it does not make borrowed data live longer.
- ⚠️ Moving `Rc`, `RefCell`, or other non-`Send` state into `thread::spawn` and expecting it to cross threads. See [[Concurrency]].

## See also
[[Closures & Iterators]] · [[Closures]] · [[Capturing the Environment]] · [[Fn, FnMut, FnOnce]] · [[Ownership]] · [[Move Semantics]] · [[Concurrency]] · [[Returning Closures]] · [[Lifetimes]] · [[Needless Clone]]

## Sources
- The Rust Programming Language, ch. 13.1 "Capturing References or Moving Ownership" - [[the-book]], https://doc.rust-lang.org/book/ch13-01-closures.html
- Rust standard library, `thread::spawn` - [[std]], https://doc.rust-lang.org/std/thread/fn.spawn.html
