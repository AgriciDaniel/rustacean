---
type: pattern
title: "try_reserve and Fallible Allocation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, allocation, errors]
domain: "std: Collections Deep"
difficulty: intermediate
related: ["[[Capacity and Reallocation]]", "[[Recoverable vs Unrecoverable Errors]]", "[[Result]]", "[[The Question Mark Operator]]", "[[Vec]]", "[[HashMap]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/vec/struct.Vec.html#method.try_reserve", "https://doc.rust-lang.org/std/string/struct.String.html#method.try_reserve", "https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.try_reserve", "https://doc.rust-lang.org/std/collections/struct.TryReserveError.html", "https://doc.rust-lang.org/std/collections/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# try_reserve and Fallible Allocation

`try_reserve` turns collection growth into a recoverable `Result`, letting memory-sensitive code fail before doing expensive or partially useful work.

## What it is
Most growable standard collections allocate implicitly when they need more capacity.
Plain `reserve` and growth from `push`, `insert`, or `extend` may panic or abort on allocation failure depending on the allocator and target behavior.
`try_reserve` gives code a stable, explicit error path for capacity planning.

Use this pattern when allocation failure is part of the caller-visible contract:
servers accepting untrusted input sizes, parsers with memory budgets, embedded or constrained systems, batch jobs that should report failure, and APIs that already return [[Result]].

The standard error type is `std::collections::TryReserveError`.
It implements `Debug`, `Display`, and `std::error::Error`, so it composes with ordinary Rust error handling.

## How it works
`try_reserve(additional)` asks the collection to ensure room for at least `len + additional`.
Like `reserve`, it may reserve more than requested to avoid frequent reallocations.
On `Ok(())`, the requested additional capacity is available.
If the requested capacity overflows or the allocator reports failure, it returns `Err(TryReserveError)`.

`try_reserve_exact(additional)` asks for the minimum additional capacity, but the allocator may still provide more.
Prefer `try_reserve` when future insertions are likely.
Use `try_reserve_exact` only when minimizing speculative over-allocation matters more than amortized growth.

The `additional` parameter is additional capacity, not final capacity.
For `String`, it is counted in UTF-8 bytes.
For `Vec<T>`, `VecDeque<T>`, `HashMap<K, V>`, and `HashSet<T>`, it is counted in elements or entries.

The pattern is most useful before a loop:
reserve once, return early on failure, then perform the work under clearer assumptions.
It does not make every later allocation impossible, because formatting, hashing, cloning, or nested collections may allocate too.

## Example
```rust
use std::collections::{HashMap, TryReserveError};

fn count_words(text: &str) -> Result<HashMap<String, usize>, TryReserveError> {
    let estimate = text.split_whitespace().count();
    let mut counts: HashMap<String, usize> = HashMap::new();

    counts.try_reserve(estimate)?;

    for word in text.split_whitespace() {
        *counts.entry(word.to_owned()).or_insert(0) += 1;
    }

    Ok(counts)
}

fn main() -> Result<(), TryReserveError> {
    let counts = count_words("rust rust ownership")?;

    assert_eq!(counts.get("rust"), Some(&2));
    assert_eq!(counts.get("ownership"), Some(&1));

    Ok(())
}
```

## Worked example
A fallible builder can reserve bytes for the outer `String` before concatenation.
The estimate must be in bytes, not characters.

```rust
use std::collections::TryReserveError;

fn join_lines(lines: &[&str]) -> Result<String, TryReserveError> {
    let bytes = lines.iter().map(|line| line.len()).sum::<usize>()
        + lines.len().saturating_sub(1);
    let mut out = String::new();

    out.try_reserve(bytes)?;

    for (index, line) in lines.iter().enumerate() {
        if index > 0 {
            out.push('\n');
        }
        out.push_str(line);
    }

    Ok(out)
}

fn main() -> Result<(), TryReserveError> {
    let text = join_lines(&["alpha", "beta"])?;
    assert_eq!(text, "alpha\nbeta");
    Ok(())
}
```

This pattern handles the top-level allocation for `out`.
It does not cover allocations that happen before the call or inside values inserted into the collection.

## When to use it
Use `try_reserve` when a capacity request comes from input, protocol metadata, file size, request size, or a batch length that can be large.
Use it when an API wants to return an error instead of unexpectedly panicking during collection growth.
Use it when you can preflight allocation before mutating several related data structures.

Do not add it to every small local vector.
For ordinary application code where allocation failure is unrecoverable, `Vec::with_capacity` or normal growth is usually clearer.

## Best practice
- ✅ Reserve before a large build loop when the expected size is known.
- ✅ Propagate `TryReserveError` with `?` when the surrounding API is already fallible.
- ✅ Treat `additional` as extra capacity beyond current length.
- ✅ Count `String` capacity in bytes.
- ✅ Prefer `try_reserve` over `try_reserve_exact` for amortized growth.
- ✅ Keep the collection usable on error; return or recover rather than continuing under a false capacity assumption.
- ✅ Combine with input size validation when an attacker can request huge allocations.
- ✅ Use [[Capacity and Reallocation]] to decide whether preallocation is worth the complexity.

## Pitfalls
- ⚠️ Do not confuse final desired capacity with the `additional` argument.
- ⚠️ Do not assume `try_reserve_exact` gives exact capacity; allocators may return more.
- ⚠️ Do not assume successful reservation prevents all future allocation in the rest of the algorithm.
- ⚠️ Do not convert `TryReserveError` into a panic in code that promised recoverable allocation failure.
- ⚠️ Do not use unstable details such as `TryReserveError::kind` in stable 1.85+ notes.
- ⚠️ Do not reserve based on character count for `String`; UTF-8 bytes are the capacity unit.
- ⚠️ Do not hide unbounded input behind `usize` arithmetic; use checked or saturating estimates where appropriate.
- ⚠️ Do not call `shrink_to_fit` immediately after fallible preallocation unless returning memory is more important than reuse.

## See also
[[Capacity and Reallocation]] · [[Recoverable vs Unrecoverable Errors]] · [[Result]] ·
[[The Question Mark Operator]] · [[Vec]] · [[String and str]] · [[HashMap]] · [[HashSet]] ·
[[VecDeque]] · [[BinaryHeap Priority Queues]] · [[Choosing Standard Collections]] · [[std: Collections Deep]]

## Sources
- Rust standard library, `Vec::try_reserve` - [[std]],
  https://doc.rust-lang.org/std/vec/struct.Vec.html#method.try_reserve
- Rust standard library, `String::try_reserve` - [[std]],
  https://doc.rust-lang.org/std/string/struct.String.html#method.try_reserve
- Rust standard library, `HashMap::try_reserve` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.try_reserve
- Rust standard library, `TryReserveError` - [[std]],
  https://doc.rust-lang.org/std/collections/struct.TryReserveError.html
- Rust standard library, collections overview - [[std]],
  https://doc.rust-lang.org/std/collections/index.html
