---
type: pattern
title: "Iterating Collections"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, iterators, loops]
domain: "Collections & Strings"
difficulty: basic
related: ["[[Vec]]", "[[HashMap]]", "[[String and str]]", "[[BTreeMap and BTreeSet]]", "[[VecDeque]]", "[[Unnecessary Collect]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-01-vectors.html#iterating-over-the-values-in-a-vector", "https://doc.rust-lang.org/book/ch08-02-strings.html#iterating-over-strings", "https://doc.rust-lang.org/book/ch08-03-hash-maps.html#accessing-values-in-a-hash-map", "https://doc.rust-lang.org/std/iter/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Iterating Collections

Iterate collections by choosing the ownership mode explicitly: borrow with `&collection`, mutate with `&mut collection`, or consume with `collection`.

## What it is
Rust collection iteration is built around `IntoIterator`.
The expression in a `for` loop determines whether items are borrowed, mutably borrowed, or moved.

For `Vec<T>`, `for x in &v` yields `&T`, `for x in &mut v` yields `&mut T`, and `for x in v` yields owned `T`.
For maps, iterating by reference yields key-value references.

For strings, iteration must also specify the text unit: `.chars()` for Unicode scalar values or `.bytes()` for raw UTF-8 bytes.

## How it works
Borrowed iteration keeps the collection available after the loop.
Mutable borrowed iteration lets you change each element but prevents structural mutation while the loop's borrow is active.
Consuming iteration moves the collection and yields owned items.

Hash map iteration order is arbitrary.
B-tree map and set iteration order is sorted by key or value.
`Vec` and `VecDeque` iteration is logical sequence order.

Iterator adapters such as `map`, `filter`, `take`, and `fold` often avoid intermediate allocations.
Collect only when the next API truly needs an owned collection.

Most iterators are lazy.
Calling `map` or `filter` describes work; the work runs when the iterator is consumed by a `for` loop, `collect`, `sum`, `find`, `any`, `fold`, or another consuming method.
This is why iterator chains can be both expressive and allocation-free.

## Example
```rust
use std::collections::HashMap;

fn main() {
    let mut numbers = vec![1, 2, 3];

    for n in &mut numbers {
        *n *= 2;
    }
    assert_eq!(numbers, [2, 4, 6]);

    let total: i32 = numbers.iter().sum();
    assert_eq!(total, 12);

    let counts = HashMap::from([("red", 2), ("blue", 1)]);
    for (color, count) in &counts {
        println!("{color}: {count}");
    }

    let chars: Vec<char> = "Зд".chars().collect();
    assert_eq!(chars, ['З', 'д']);
}
```

## More realistic example
```rust
use std::collections::BTreeMap;

fn active_usernames<'a>(users: &BTreeMap<u64, (&'a str, bool)>) -> Vec<&'a str> {
    users
        .values()
        .filter_map(|(name, active)| active.then_some(*name))
        .collect()
}

fn drain_completed(tasks: Vec<(String, bool)>) -> Vec<String> {
    tasks
        .into_iter()
        .filter_map(|(name, done)| done.then_some(name))
        .collect()
}

fn main() {
    let users = BTreeMap::from([
        (2, ("grace", true)),
        (1, ("ada", false)),
        (3, ("linus", true)),
    ]);

    assert_eq!(active_usernames(&users), ["grace", "linus"]);

    let completed = drain_completed(vec![(String::from("parse"), true), (String::from("test"), false)]);
    assert_eq!(completed, vec![String::from("parse")]);
}
```

The first function borrows from an ordered map and returns borrowed names.
The second consumes the vector so it can return owned `String` values without cloning.

## Common errors
```text
error[E0382]: borrow of moved value
```

`for item in collection` consumes many collection types.
Use `for item in &collection` or `collection.iter()` if the collection must remain usable after the loop.

```text
error[E0502]: cannot borrow `items` as mutable because it is also borrowed as immutable
```

This appears when a loop is borrowing a collection while the body tries to insert, remove, or push into the same collection.
Collect changes separately, use indices carefully, or use methods such as `retain` when they match the operation.

## Best practice
- ✅ Use `for item in &collection` when reading values without consuming the collection.
- ✅ Use `for item in &mut collection` for in-place element updates.
- ✅ Use consuming iteration when you need owned elements and are done with the collection.
- ✅ For maps, make ordering requirements explicit by choosing `HashMap` or `BTreeMap`.
- ✅ For strings, name the unit with `.chars()` or `.bytes()` instead of pretending byte indices are characters.
- ✅ Use `enumerate` when the index is part of output or diagnostics; otherwise iterate values directly.
- ✅ Use `filter_map` for "maybe produce an item" instead of mapping to `Option` and flattening by hand.

## Pitfalls
- ⚠️ Do not insert into or remove from a collection while a `for item in &collection` loop is borrowing it.
- ⚠️ Do not `collect::<Vec<_>>()` just to immediately iterate again. See [[Unnecessary Collect]].
- ⚠️ Do not assert exact `HashMap` iteration order in tests.
- ⚠️ Do not use `.chars().nth(n)` repeatedly in a loop as if it were constant-time indexing; it scans from the start each time.
- ⚠️ Do not call `.iter().cloned().collect()` unless the next owner truly needs separate owned elements. See [[Needless Clone]].
- ⚠️ Do not expect iterator adapters to run unless the iterator is consumed.

## See also
[[Vec]] · [[HashMap]] · [[String and str]] · [[BTreeMap and BTreeSet]] · [[VecDeque]] · [[Unnecessary Collect]] · [[String Byte Indexing]] · [[Needless Clone]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.1 vector iteration — [[the-book]], https://doc.rust-lang.org/book/ch08-01-vectors.html#iterating-over-the-values-in-a-vector
- The Rust Programming Language, ch. 8.2 string iteration — [[the-book]], https://doc.rust-lang.org/book/ch08-02-strings.html#iterating-over-strings
- The Rust Programming Language, ch. 8.3 map iteration — [[the-book]], https://doc.rust-lang.org/book/ch08-03-hash-maps.html#accessing-values-in-a-hash-map
- Standard library iterator docs — [[std]], https://doc.rust-lang.org/std/iter/index.html
