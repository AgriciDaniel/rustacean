---
type: concept
title: "Index and IndexMut Traits"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, traits, operators, index, indexing]
domain: "std: Core Trait Catalog"
difficulty: intermediate
related: ["[[Operator Overloading]]", "[[Index Panics vs get]]", "[[Arrays]]", "[[The Slice Type]]"]
sources: ["[[std]]", "[[the-reference]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/std/ops/trait.Index.html", "https://doc.rust-lang.org/std/ops/trait.IndexMut.html", "https://doc.rust-lang.org/std/ops/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Index and IndexMut Traits

`Index` and `IndexMut` power `container[index]` syntax, but they should be reserved for indexing operations where panic-on-invalid-index is acceptable and unsurprising.

## What it is
`Index<Idx>` backs immutable indexing.
`IndexMut<Idx>` backs mutable indexing.
Both live in `std::ops`.

The expression `container[index]` desugars through these traits.
For immutable contexts, the output is borrowed.
For mutable contexts, `IndexMut` allows assignment through the indexed place.

The most familiar implementors are arrays, slices, `Vec`, maps with key indexing, and string/slice ranges.
Indexing is concise because it is expected to be common and direct.

## How it works
`Index` has an associated `Output` type.
The method returns `&Self::Output`.
`IndexMut` returns `&mut Self::Output`.
Because the output is a reference, the indexed value must live inside or behind the container.

Invalid indexing conventionally panics.
Slices panic on out-of-bounds indexing.
`HashMap` indexing panics when a key is absent.
That is why fallible lookup APIs such as `get` and `get_mut` are often better at boundaries.

Do not use `Index` when lookup needs allocation, IO, parsing, or recoverable failure.
The syntax has no place to return `Result`.
If failure is expected, use a named method.

## Example
```rust
use std::ops::{Index, IndexMut};

#[derive(Debug, PartialEq, Eq)]
struct Board {
    cells: [char; 9],
}

impl Index<(usize, usize)> for Board {
    type Output = char;

    fn index(&self, index: (usize, usize)) -> &Self::Output {
        let (row, col) = index;
        &self.cells[row * 3 + col]
    }
}

impl IndexMut<(usize, usize)> for Board {
    fn index_mut(&mut self, index: (usize, usize)) -> &mut Self::Output {
        let (row, col) = index;
        &mut self.cells[row * 3 + col]
    }
}

fn main() {
    let mut board = Board { cells: ['.'; 9] };
    board[(1, 2)] = 'x';
    assert_eq!(board[(1, 2)], 'x');
}
```

## Best practice
- ✅ Implement `Index` when the operation is cheap, direct, and conventionally index-like.
- ✅ Provide `get` or `try_get` when absence or bounds failure is a normal outcome.
- ✅ Keep index calculations simple enough that panics are diagnosable.
- ✅ Implement `IndexMut` only when mutable access to the same conceptual element is sound.
- ✅ Document custom index coordinate systems such as `(row, col)`.

## Pitfalls
- ⚠️ Do not use indexing syntax for fallible lookup in library APIs; see [[Index Panics vs get]].
- ⚠️ Do not return references to temporary computed values.
- ⚠️ Do not hide expensive searches behind `[]`.
- ⚠️ Be explicit about row-major vs column-major indexing for grid-like types.

## See also
[[std: Core Trait Catalog]] · [[Operator Overloading]] · [[Arithmetic Operator Traits Add and Mul]] · [[Index Panics vs get]] · [[Arrays]] · [[The Slice Type]] · [[Vec]] · [[HashMap]] · [[String Byte Indexing]] · [[Stale Slice Indices]]

## Sources
- Rust standard library, `std::ops::Index` - [[std]], https://doc.rust-lang.org/std/ops/trait.Index.html
- Rust standard library, `std::ops::IndexMut` - [[std]], https://doc.rust-lang.org/std/ops/trait.IndexMut.html
- Rust standard library, `std::ops` - [[std]], https://doc.rust-lang.org/std/ops/index.html
