---
type: pattern
title: "Return Iterators Instead of Collecting"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, iterators, api-design, lazy]
domain: "Closures & Iterators"
difficulty: intermediate
related: ["[[Iterators]]", "[[Lazy Evaluation]]", "[[Iterator Adapters]]", "[[Consuming Adapters]]", "[[Unnecessary Collect]]", "[[Returning Closures]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch13-03-improving-our-io-project.html", "https://doc.rust-lang.org/std/iter/trait.Iterator.html"]
rust_version: "edition 2024 / 1.85+"
---

# Return Iterators Instead of Collecting

Return an iterator when callers can consume results progressively or compose more adapters, instead of forcing an immediate allocation with `collect`.

## What it is
This pattern turns functions that build `Vec<T>` results into functions that return
`impl Iterator<Item = T>` or `impl Iterator<Item = &'a T>`. The function becomes an adapter over
its input rather than an eager materialization step.

It is useful for search results, filtered views, parser tokens, generated ranges, and other data
that callers may only partially consume.

## How it works
The returned iterator keeps the input borrow or owned source alive according to normal ownership
and lifetime rules. When returning borrowed items, the signature must name the lifetime tying the
output items to the input.

Callers can still collect if they need a collection, but they are no longer forced to allocate
before they can inspect the first result.

`impl Iterator` in return position hides the concrete adapter type while preserving static
dispatch. It works when all return paths produce the same concrete iterator type; if branches need
different iterator types, use a small enum, restructure the chain, collect intentionally, or use a
boxed trait object after measuring the tradeoff.

## Example
```rust
fn matching_lines<'a>(query: &'a str, contents: &'a str) -> impl Iterator<Item = &'a str> {
    contents.lines().filter(move |line| line.contains(query))
}

fn main() {
    let text = "Rust\ntrust\nborrow\n";
    let found: Vec<&str> = matching_lines("rust", text).collect();
    assert_eq!(found, vec!["trust"]);

    assert_eq!(matching_lines("Rust", text).next(), Some("Rust"));
}
```

The `move` closure captures `query` by value; because `query` is a reference, the value moved is
the reference itself.

## Worked example
```rust
fn error_codes<'a>(log: &'a str) -> impl Iterator<Item = u16> + 'a {
    log.lines().filter_map(|line| {
        let code = line.strip_prefix("ERR ")?;
        code.parse::<u16>().ok()
    })
}

fn first_error(log: &str) -> Option<u16> {
    error_codes(log).next()
}

fn main() {
    let log = "INFO boot\nERR 404\nERR nope\nERR 500\n";
    assert_eq!(first_error(log), Some(404));
    assert_eq!(error_codes(log).collect::<Vec<_>>(), vec![404, 500]);
}
```

The caller that only needs the first code avoids building a vector; another caller can still
collect all codes.

## Common errors
```rust
// fn bad_words() -> impl Iterator<Item = &'static str> {
//     let words = vec!["rust", "borrow"];
//     words.iter().copied()
// }
```

Uncommenting this fails with a lifetime error such as
`error[E0515]: cannot return value referencing local variable words`. The iterator would borrow a
vector dropped at function exit. Return an owning
iterator such as `["rust", "borrow"].into_iter()`, take the collection as input, or collect into
an owned return type when ownership is the API contract.

## Best practice
- ✅ Return `impl Iterator` for simple, single concrete iterator pipelines.
- ✅ Let callers decide whether to `collect`, `count`, `find`, or stream through a `for` loop.
- ✅ Use clear lifetime names when borrowed output comes from borrowed input.
- ✅ Add `+ '_` or a named lifetime when the returned iterator borrows from parameters and the elided lifetime would be unclear.
- ✅ Keep public iterator-returning functions focused; complex branching may deserve a named iterator type or an eager result.

## Pitfalls
- ⚠️ Returning an iterator that borrows a local `String` or `Vec`; return owned data or take the source as input.
- ⚠️ Exposing a very complex concrete iterator type in a public signature; prefer `impl Iterator`.
- ⚠️ Collecting internally when the caller only needs the first match. See [[Unnecessary Collect]].
- ⚠️ Using `impl Iterator` when callers specifically need random access, length, or repeated traversal; a slice or collection may be the better API.
- ⚠️ Forgetting that different `if`/`match` arms must return the same hidden concrete type with `impl Iterator`.

## See also
[[Closures & Iterators]] · [[Iterators]] · [[Lazy Evaluation]] · [[Iterator Adapters]] · [[Consuming Adapters]] · [[Unnecessary Collect]] · [[Lifetimes]] · [[Returning Closures]] · [[The Iterator Trait]] · [[Zero-Cost Abstractions]]

## Sources
- The Rust Programming Language, ch. 13.3 "Improving Our I/O Project" - [[the-book]], https://doc.rust-lang.org/book/ch13-03-improving-our-io-project.html
- Rust standard library, `Iterator` trait - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html
