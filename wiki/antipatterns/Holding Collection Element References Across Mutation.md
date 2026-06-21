---
type: antipattern
title: "Holding Collection Element References Across Mutation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, collections, borrowing, footgun]
domain: "Collections & Strings"
difficulty: intermediate
related: ["[[Vec]]", "[[Capacity and Reallocation]]", "[[VecDeque]]", "[[Ownership]]", "[[Borrowing]]", "[[Index Panics vs get]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch08-01-vectors.html#reading-elements-of-vectors", "https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation", "https://doc.rust-lang.org/std/collections/struct.VecDeque.html", "https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html"]
rust_version: "edition 2024 / 1.85+"
---

# Holding Collection Element References Across Mutation

Holding a reference into a growable collection while mutating the collection is a footgun because growth, removal, or reordering can invalidate the reference.

## The mistake
The common version is to borrow an element, then append to the same vector, then use the old reference.
It feels harmless when the mutation is "only at the end," but the append may require reallocation.

Rust rejects this pattern in safe code.
The immutable element reference and the mutable collection operation cannot coexist when the reference is later used.

The same design issue appears with `VecDeque`, `String` slices, maps, and any collection whose structural mutation may move, remove, or replace stored data.

## Why it happens
Growable collections own allocations.
When capacity is insufficient, they may allocate new memory and move existing elements or bytes.
A reference into the old allocation would point at invalid memory if it survived the growth.

Even without reallocation, operations such as `remove`, `insert`, sorting, or map replacement can change which value lives at a logical position.
Borrowing rules prevent using stale references after such changes.

The fix is usually to shorten the borrow, copy a small value, store an index or key and look up again, or restructure the code so mutation happens before borrowing.

Non-lexical lifetimes make Rust more precise than "a borrow lasts until the end of the block."
If a reference is no longer used, the compiler can often end the borrow before the next statement.
The error appears when the reference will still be used after the structural mutation.

## Example
```rust
fn main() {
    let mut values = vec![10, 20, 30];

    let first_value = values[0];
    values.push(40);
    assert_eq!(first_value, 10);

    let first_ref = values.first().copied();
    values.push(50);
    assert_eq!(first_ref, Some(10));

    let last = values.last().expect("values is non-empty");
    assert_eq!(*last, 50);
}
```

## More realistic example
```rust
use std::collections::HashMap;

fn bump_or_insert(scores: &mut HashMap<String, i32>, name: &str) {
    if let Some(score) = scores.get_mut(name) {
        *score += 1;
        return;
    }

    scores.insert(name.to_owned(), 1);
}

fn append_after_reading_len(values: &mut Vec<String>) {
    let first_len = values.first().map(|s| s.len());
    values.push(String::from("new"));

    if let Some(len) = first_len {
        assert!(len > 0);
    }
}

fn main() {
    let mut scores = HashMap::from([(String::from("ada"), 1)]);
    bump_or_insert(&mut scores, "ada");
    bump_or_insert(&mut scores, "grace");

    let mut values = vec![String::from("old")];
    append_after_reading_len(&mut values);
}
```

The examples avoid holding references across later mutations.
The map function finishes using `get_mut` before insertion; the vector function stores a copied length, not `&String`.

## Common errors
```text
error[E0502]: cannot borrow `values` as mutable because it is also borrowed as immutable
```

This is the classic "borrow an element, push to the vector, then use the element reference" error.
End the borrow before the push, or save owned/copy data instead of a reference.

```text
error[E0499]: cannot borrow `map` as mutable more than once at a time
```

This appears when a mutable reference to one entry is still live and code tries to mutate the same map again.
Use a smaller scope, `entry`, or split the operation into phases.

## Best practice
- ✅ Keep references into collections in the smallest possible scope.
- ✅ Copy or clone only the needed element when it is small or ownership is required.
- ✅ Store an index or key, mutate the collection, then look up again and handle absence.
- ✅ Reserve capacity before taking references only when no later operation can exceed it, and still keep borrows clear.
- ✅ Prefer iterator transformations that do not structurally mutate the collection being iterated.
- ✅ Move mutation before borrowing when the mutation does not depend on the borrowed value.
- ✅ Use `split_at_mut` or other slice-splitting APIs when you need disjoint mutable access inside one collection.

## Pitfalls
- ⚠️ Do not try to outsmart the borrow checker with raw pointers for ordinary collection code.
- ⚠️ Do not assume `push` cannot affect references to earlier elements; it can reallocate.
- ⚠️ Do not mutate a map while holding a reference to one of its values.
- ⚠️ Do not hold a string slice and then mutate the owning `String` in a way that may reallocate or alter boundaries.
- ⚠️ Do not rely on stored indices after removal, sorting, or deduplication unless the algorithm explicitly updates them.
- ⚠️ Do not use `RefCell` only to bypass this design issue; runtime borrow panics are usually worse than restructuring.

## See also
[[Vec]] · [[Capacity and Reallocation]] · [[VecDeque]] · [[String and str]] · [[HashMap]] · [[Ownership]] · [[Borrowing]] · [[Iterating Collections]] · [[Stale Slice Indices]] · [[Collections & Strings]]

## Sources
- The Rust Programming Language, ch. 8.1 vector references and push — [[the-book]], https://doc.rust-lang.org/book/ch08-01-vectors.html#reading-elements-of-vectors
- Standard library `Vec<T>` capacity and reallocation docs — [[std]], https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation
- Standard library `VecDeque` docs — [[std]], https://doc.rust-lang.org/std/collections/struct.VecDeque.html
- The Rust Programming Language, ch. 4.2 references and borrowing — [[the-book]], https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
