---
type: antipattern
title: "Moving Out of FnMut Closures"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, closures, fnmut, footgun]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Fn, FnMut, FnOnce]]", "[[Closures]]", "[[Capturing the Environment]]", "[[move Closures]]", "[[Iterator Adapters]]", "[[Needless Clone]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-01-closures.html", "https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by_key"]
rust_version: "edition 2024 / 1.85+"
---

# Moving Out of FnMut Closures

Moving a captured non-`Copy` value out of a closure makes that closure callable only once, so it cannot satisfy APIs that need `FnMut` or `Fn`.

## The mistake
The common error is passing a closure to a repeated-callback API and moving captured state out of
the closure body. `sort_by_key`, iterator adapters, and visitor-style APIs may call the closure
multiple times, so they generally need at least `FnMut`.

If the first call consumes a captured `String`, `Vec`, or other non-`Copy` value, a second call
would have nothing left to use.

## Why it happens
Closure capture and closure call traits are determined by the body. Moving a captured value out
means the closure only implements `FnOnce`. Mutating captured state, by contrast, can still allow
`FnMut` because the state remains available for later calls.

The correct alternative is usually to mutate a counter or buffer, borrow data, compute the key
from the item, or clone deliberately only when each call truly needs its own owned value.

This is different from using a `move` closure. `move` controls how the closure captures values.
The error comes from moving a captured value out during a call. A `move` closure that only reads
its owned capture can still be called repeatedly and satisfy `Fn` or `FnMut`.

## Example
```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let mut rectangles = [
        Rectangle { width: 10, height: 1 },
        Rectangle { width: 3, height: 5 },
        Rectangle { width: 7, height: 12 },
    ];

    let mut calls = 0;
    rectangles.sort_by_key(|rect| {
        calls += 1;
        rect.width
    });

    assert_eq!(rectangles[0].width, 3);
    assert!(calls > 0);
}
```

The closure mutates `calls` but does not move it out, so it can be called repeatedly.

## Worked example
```rust
fn main() {
    let suffix = String::from(".log");
    let names = ["app", "db", "cache"];

    let paths: Vec<String> = names
        .iter()
        .map(|name| format!("{name}{suffix}"))
        .collect();

    assert_eq!(paths, vec!["app.log", "db.log", "cache.log"]);
}
```

The `map` closure is called once per item, but it only borrows `suffix` for formatting. It does
not move the `String` out of the closure body.

## Common errors
```rust
fn main() {
    let suffix = String::from(".log");
    let names = ["app", "db"];

    // let paths: Vec<String> = names.iter().map(|name| {
    //     let owned_suffix = suffix;
    //     format!("{name}{owned_suffix}")
    // }).collect();
}
```

Uncommenting this gives `error[E0507]: cannot move out of suffix, a captured variable in an
FnMut closure`. Use `format!("{name}{suffix}")` to borrow, or `suffix.clone()` only if each
iteration genuinely needs an owned `String`.

## Best practice
- ✅ For repeated callbacks, mutate captured state in place instead of moving it out.
- ✅ Use `FnOnce` bounds only when your API really calls the closure at most once.
- ✅ Clone inside a closure only after deciding that repeated owned values are the right semantics.
- ✅ Borrow captured configuration (`&str`, `&Path`, `&Regex`) when each call only needs to read it.
- ✅ Move data out before building the repeated closure if ownership transfer is a one-time setup step.

## Pitfalls
- ⚠️ Moving a `String` or `Vec` into another collection from inside a `sort_by_key` closure.
- ⚠️ Reading the compiler's clone suggestion as the default fix; cloning may hide a design issue. See [[Needless Clone]].
- ⚠️ Assuming `move ||` necessarily means the closure is only `FnOnce`; moving out of the body is the deciding part.
- ⚠️ Capturing an `Option<T>` and calling `.unwrap()` inside a repeated closure; `unwrap` moves the `T` out.
- ⚠️ Using `sort_by_key` with expensive key construction; consider precomputing keys or `sort_by_cached_key` where appropriate.

## See also
[[Closures & Iterators]] · [[Fn, FnMut, FnOnce]] · [[Closures]] · [[Capturing the Environment]] · [[move Closures]] · [[Iterator Adapters]] · [[Needless Clone]] · [[Ownership]] · [[Move Semantics]] · [[Closure Type Inference]]

## Sources
- The Rust Programming Language, ch. 13.1 "Moving Captured Values Out of Closures" - [[the-book]], https://doc.rust-lang.org/book/ch13-01-closures.html
- Rust standard library, `slice::sort_by_key` - [[std]], https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by_key
