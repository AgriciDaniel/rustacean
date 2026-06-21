---
type: concept
title: "Iterator scan and peekable"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterator, adapter, scan, peekable]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator fold and reduce]]", "[[Iterator take skip and while bounds]]", "[[Iterator Adapters]]", "[[Option]]", "[[Mutable References]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.scan", "https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.peekable", "https://doc.rust-lang.org/std/iter/struct.Peekable.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterator scan and peekable

`scan` carries mutable state while yielding a new iterator, and `peekable` buffers one next item so code can inspect it without consuming it.

## What it is
`Iterator::scan` is a stateful adapter.
It is like `fold` because it owns an accumulator-like state.
It differs from `fold` because it yields zero or more output items instead of returning one final value.
The scan closure receives `&mut state` and an input item.
It returns `Some(output)` to yield a value or `None` to stop the scan.
`Iterator::peekable` wraps an iterator in `Peekable`.
`Peekable::peek` returns a shared reference to the next item without advancing past the buffered item.
`Peekable::peek_mut` can mutate the buffered next item before it is yielded.
Together these adapters cover parsers, running totals, prefix detection, and lookahead.
They are useful when plain `map` and `filter` do not have enough memory of previous or upcoming items.

## How it works
`scan(initial_state, closure)` stores `initial_state` inside the adapter.
Each `next` call pulls one upstream item, passes a mutable state reference to the closure, and handles the returned `Option`.
Returning `None` ends the scan.
The state remains private to the adapter.
This avoids external mutable variables in many pipelines.
`peekable()` stores an optional buffered item.
The first call to `peek` may call `next` on the underlying iterator to fill that buffer.
That means side effects of the underlying iterator's `next` can happen during `peek`.
Repeated `peek` calls return the same buffered item until `next` consumes it.
After the buffered item is consumed, the next `peek` can pull again.
Use `peekable` when one-item lookahead is enough.

## Example
```rust
fn main() {
    let running: Vec<i32> = [1, 2, 3, 4]
        .into_iter()
        .scan(0, |sum, n| {
            *sum += n;
            Some(*sum)
        })
        .collect();

    assert_eq!(running, [1, 3, 6, 10]);
}
```

## Edge cases
```rust
fn main() {
    let mut chars = "12+34".chars().peekable();

    let mut first_number = String::new();
    while let Some(next) = chars.peek() {
        if next.is_ascii_digit() {
            first_number.push(chars.next().unwrap());
        } else {
            break;
        }
    }

    assert_eq!(first_number, "12");
    assert_eq!(chars.next(), Some('+'));
}
```

## Best practice
- ✅ Use `scan` for running state that still needs to yield intermediate values.
- ✅ Use `fold` when only the final state is needed.
- ✅ Use `peekable` for one-token lookahead in small parsers.
- ✅ Remember that `peek` returns a reference to the next item.
- ✅ Use `peek_mut` sparingly and only when mutating the buffered item is clearer than mapping.
- ✅ Keep scan state small and local to the pipeline.
- ✅ Return `None` from `scan` to stop when a boundary is reached.
- ✅ Prefer explicit parser code when lookahead grows beyond one item.

## Pitfalls
- ⚠️ `peek` can advance the underlying iterator enough to fill the buffer.
- ⚠️ `peekable` provides one-item lookahead, not arbitrary backtracking.
- ⚠️ Returning `None` from `scan` ends the adapter.
- ⚠️ External mutable captures in `scan` can fight the clarity of the internal state.
- ⚠️ Calling `unwrap` after `peek` can still be fragile if control flow changes; see [[Unwrap and Expect Overuse]].
- ⚠️ Mutating with `peek_mut` can surprise readers if the later yielded value changes.
- ⚠️ Using `scan` for simple stateless transforms obscures intent compared with `map`.
- ⚠️ Infinite iterators remain infinite unless `scan` returns `None` or a later bound is applied.

## See also
[[std: Iterator Adapter Catalog]] · [[Iterator fold and reduce]] · [[Iterator take skip and while bounds]] · [[Iterator map and filter]] · [[Iterator predicate search adapters]] · [[Iterator Adapters]] · [[Lazy Evaluation]] · [[Option]] · [[Mutable References]] · [[Closures]] · [[Unwrap and Expect Overuse]]

## Sources
- Rust standard library, `Iterator::scan` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.scan
- Rust standard library, `Iterator::peekable` - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.peekable
- Rust standard library, `Peekable` - [[std]], https://doc.rust-lang.org/std/iter/struct.Peekable.html
