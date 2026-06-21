---
type: concept
title: "Scoped Threads"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, scoped-threads, threads]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Threads]]", "[[Move Closures with Threads]]", "[[Ownership]]", "[[Borrowing]]", "[[Arc]]", "[[Send and Sync]]"]
sources: ["[[std]]", "[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/std/thread/fn.scope.html", "https://doc.rust-lang.org/book/ch16-01-threads.html"]
rust_version: "edition 2024 / 1.85+"
---

# Scoped Threads

Scoped threads let worker threads borrow non-`'static` local data because `std::thread::scope` guarantees that all spawned scoped threads finish before the scope returns.

## What it is
`thread::scope` is the standard-library fork-join API for threads that must not outlive a lexical scope.
Inside the scope closure, you spawn threads on a `Scope`.
Those threads may borrow stack data from the surrounding function, including mutable slices split into disjoint parts.

This is different from `thread::spawn`.
Plain spawned threads can outlive the caller, so their closures must be `'static`.
Scoped threads cannot escape the scope, so borrowing local data is sound.

## How it works
`thread::scope(|s| { ... })` creates a scope and passes in a spawner.
Each `s.spawn(...)` creates a scoped thread.
If a scoped thread is not joined manually, it is automatically joined before `scope` returns.
If any automatically joined scoped thread panics, `scope` propagates the panic after joining the remaining threads; manual joins let you handle each result explicitly.

The compiler still enforces ordinary borrowing.
You cannot give two threads mutable access to the same element, but you can split a slice into disjoint regions and move those separate borrows into different workers.
The lifetime parameter on the scope ties all borrowed captures to the call to `thread::scope`; the scoped join guarantee is what makes non-`'static` borrows sound.

## Example
```rust
use std::thread;

fn main() {
    let mut data = [1, 2, 3, 4, 5, 6];

    thread::scope(|scope| {
        let (left, right) = data.split_at_mut(3);

        scope.spawn(move || {
            for value in left {
                *value *= 2;
            }
        });

        scope.spawn(move || {
            for value in right {
                *value += 10;
            }
        });
    });

    println!("{data:?}");
}
```

## Example: returning values while borrowing input
```rust
use std::thread;

fn main() {
    let text = String::from("alpha beta gamma");

    let (words, bytes) = thread::scope(|scope| {
        let words = scope.spawn(|| text.split_whitespace().count());
        let bytes = scope.spawn(|| text.len());

        (words.join().unwrap(), bytes.join().unwrap())
    });

    println!("{words} words, {bytes} bytes");
}
```

## Common errors
Using `thread::spawn` where `thread::scope` is needed produces the familiar borrowed-data error:

```text
error[E0373]: closure may outlive the current function, but it borrows `text`
```

The fix is to use `thread::scope` for fork-join borrowing, or move owned data into a plain spawned thread when the work may outlive the caller.
Scoped threads still require captured values to satisfy [[Send and Sync]] because the work runs on another OS thread.

## Best practice
- ✅ Use scoped threads for fork-join parallelism over borrowed local data.
- ✅ Split mutable slices or structures into disjoint parts before spawning workers.
- ✅ Prefer scoped borrows over [[Arc]] when sharing is temporary and lexical.
- ✅ Still join handles manually when you need return values or precise panic handling.
- ✅ Let the scope body be small and obvious; long scopes make it harder to see what may be borrowed by workers.

## Pitfalls
- ⚠️ Replacing every lifetime issue with [[Arc]] can hide a simpler scoped-thread design.
- ⚠️ Scoped threads do not remove the need for [[Send and Sync]]; captured values still cross thread boundaries.
- ⚠️ Holding locks across an entire scope can cause [[Holding Locks Too Long]].
- ⚠️ Assuming scoped threads are async tasks confuses OS threads with [[Tasks and spawn]].
- ⚠️ Capturing the same mutable slice twice is still rejected; split with APIs like `split_at_mut` to prove disjointness.

## See also
[[Concurrency]] · [[Threads]] · [[Move Closures with Threads]] · [[Ownership]] · [[Borrowing]] · [[Arc]] · [[Send and Sync]] · [[Tasks and spawn]]

## Sources
- Standard library, `std::thread::scope` — [[std]],
  https://doc.rust-lang.org/std/thread/fn.scope.html
- The Rust Programming Language, ch. 16.1 "Using Threads to Run Code Simultaneously" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-01-threads.html
