---
type: moc
title: "std: Iterator Adapter Catalog"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, std, iterator, moc]
domain: "std: Iterator Adapter Catalog"
difficulty: intermediate
related: ["[[Iterator Adapters]]", "[[The Iterator Trait]]", "[[Iterators]]", "[[Consuming Adapters]]", "[[Lazy Evaluation]]"]
sources: ["[[std]]"]
source_urls: ["https://doc.rust-lang.org/std/iter/trait.Iterator.html"]
rust_version: "edition 2024 / 1.85+"
---

# std: Iterator Adapter Catalog

This MOC links the standard-library iterator method-family notes for choosing the right adapter or consuming operation in Rust edition 2024 / stable 1.85+.

## What it is
This catalog is a map for practical `Iterator` method selection.
It groups related methods by the job they do.
Each linked note is intentionally atomic at the method-family level.
The focus is the stable standard library.
Nightly-only methods mentioned in rustdoc are not presented as primary tools.
Use this MOC when you know what you want a pipeline to do but not which method name best expresses it.
Use [[Iterator Adapters]] for the broad concept of lazy iterator transformation.
Use [[Consuming Adapters]] for terminal methods that consume an iterator and return a non-iterator result.
Use [[The Iterator Trait]] when implementing custom iterators.
Use [[Iterators]] for the language-level iteration model.

## Method families
- [[Iterator map and filter]] - transform items, keep matching items, and combine both with `filter_map`.
- [[Iterator fold and reduce]] - consume many items into one accumulator result.
- [[Iterator flat_map and flatten]] - expand nested iterables and remove one nesting layer.
- [[Iterator zip and enumerate]] - pair streams together or attach indices.
- [[Iterator take skip and while bounds]] - keep or discard prefixes by count or predicate.
- [[Iterator chain cycle and step_by]] - concatenate, repeat, or sample traversal.
- [[Iterator collect and FromIterator]] - materialize iterators into destination types.
- [[Iterator scan and peekable]] - carry state or inspect one item of lookahead.
- [[Iterator partition and unzip]] - split one stream into two collections.
- [[Iterator sum product and count]] - compute common totals.
- [[Iterator predicate search adapters]] - short-circuit predicate questions and first-match searches.
- [[Iterator rev and last]] - reverse traversal or consume to the final yielded item.

## Choosing quickly
- Need one output for each input: [[Iterator map and filter]].
- Need to remove some items: [[Iterator map and filter]].
- Need zero or one output from fallible parsing: [[Iterator map and filter]].
- Need zero or more outputs per input: [[Iterator flat_map and flatten]].
- Need a running total while still yielding values: [[Iterator scan and peekable]].
- Need only a final total: [[Iterator fold and reduce]].
- Need ordinary addition or multiplication: [[Iterator sum product and count]].
- Need the number of yielded items: [[Iterator sum product and count]].
- Need first match or first matching index: [[Iterator predicate search adapters]].
- Need existence or validation: [[Iterator predicate search adapters]].
- Need to pair two streams: [[Iterator zip and enumerate]].
- Need to add current index: [[Iterator zip and enumerate]].
- Need a prefix or page: [[Iterator take skip and while bounds]].
- Need to concatenate two streams: [[Iterator chain cycle and step_by]].
- Need to repeat a pattern: [[Iterator chain cycle and step_by]].
- Need reverse traversal: [[Iterator rev and last]].
- Need owned storage at the end: [[Iterator collect and FromIterator]].

## Stable scope
The source rustdoc includes nightly-only methods such as `try_collect`, `collect_into`, `partition_in_place`, and `try_reduce`.
Those are deliberately not central notes in this catalog.
For stable Rust edition 2024 / 1.85+, prefer stable methods listed in the linked notes.
When a nightly method looks attractive, check whether stable `collect`, `Extend::extend`, `try_fold`, or an explicit loop expresses the same behavior.
For third-party iterator helpers, cite docs.rs and verify the latest version before adding a note.
This catalog currently uses only `std`.

## Common composition paths
- Parse text values: [[Iterator map and filter]] -> [[Iterator collect and FromIterator]].
- Validate all inputs: [[Iterator predicate search adapters]] -> [[Result]].
- Build a summary: [[Iterator fold and reduce]] or [[Iterator sum product and count]].
- Traverse nested data: [[Iterator flat_map and flatten]] -> [[Iterator map and filter]].
- Split data into groups: [[Iterator partition and unzip]].
- Attach row numbers: [[Iterator zip and enumerate]].
- Consume a header and keep parsing: [[Iterator take skip and while bounds]] with `by_ref`.
- Implement lightweight parser lookahead: [[Iterator scan and peekable]].
- Cap infinite streams: [[Iterator take skip and while bounds]] before [[Iterator collect and FromIterator]].
- Reverse a finite sequence: [[Iterator rev and last]].

## Pitfall index
- [[Unconsumed Iterator Adapters]] - lazy adapters do nothing until consumed.
- [[Unnecessary Collect]] - collecting too early wastes allocation and loses streaming.
- [[Needless Clone]] - cloning before filtering or taking can copy discarded data.
- [[Manual Index Loops for Speed]] - manual indexing is often less clear than `enumerate`.
- [[Unwrap and Expect Overuse]] - many search and reduction methods return `Option`.
- [[Integer Overflow]] - sums, products, counts, positions, and enumerate indices can overflow.
- [[Index Panics vs get]] - iterator traversal often avoids direct indexing panics.
- [[Returning References to Locals]] - iterator closures cannot return references to temporaries.

## See also
[[Iterator Adapters]] · [[Consuming Adapters]] · [[The Iterator Trait]] · [[Iterators]] · [[Lazy Evaluation]] · [[Closures]] · [[Fn, FnMut, FnOnce]] · [[Option]] · [[Result]] · [[Vec]] · [[String and str]] · [[Type Inference]]

## Sources
- Rust standard library, `Iterator` trait - [[std]], https://doc.rust-lang.org/std/iter/trait.Iterator.html
