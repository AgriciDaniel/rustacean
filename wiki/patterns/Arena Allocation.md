---
type: pattern
title: "Arena Allocation"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, allocation, arenas]
domain: "Performance & Optimization"
difficulty: advanced
related: ["[[Reducing Heap Allocations]]", "[[SmallVec for Inline Storage]]", "[[Ownership]]", "[[Lifetimes]]", "[[Vec]]", "[[Avoiding Premature Optimization]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html", "https://doc.rust-lang.org/std/vec/struct.Vec.html"]
rust_version: "edition 2024 / 1.85+"
---

# Arena Allocation

Arena allocation groups many allocations under one shared lifetime, making allocation and teardown cheap when all values can be freed together.

## What it is
An arena is a region that owns many values and releases them as a group.
Instead of freeing each value independently, the program drops the whole arena at the end of a request, compiler pass, frame, or other phase.
This can reduce allocator overhead and simplify ownership graphs when many objects genuinely share the same lifetime.

Rust's ownership model makes arenas explicit.
Values stored in an arena must not outlive the arena.
References into the arena carry that lifetime, or the API uses handles such as indexes to avoid self-referential borrowing problems.
External crates such as bump allocators and typed arenas provide production arena implementations, but the design tradeoff is visible with standard library containers too.

## How it works
Arena allocation is a lifetime strategy more than a collection type.
It works best when allocation happens frequently, individual deallocation is unnecessary, and the whole group has a clear end point.
It works poorly when values need independent lifetimes, when memory must be released incrementally, or when long-lived arenas accidentally retain short-lived data.
The performance win usually comes from changing many allocator calls into cheaper append-like operations and one bulk teardown.
The ownership cost is that every arena-allocated value effectively shares the arena's lifetime.
That is excellent for a compiler pass or request context, and dangerous for a server-global arena that quietly keeps every request's data alive.

In safe Rust, a simple handle-based arena can be represented as `Vec<T>` plus indexes.
This avoids returning references tied to a mutable borrow of the arena.
Production bump arenas often return references and use carefully designed lifetime APIs to keep those references valid.
Handle-based arenas also make mutation easier because a `NodeId` does not borrow the arena.
The tradeoff is that handles need validation if stale or cross-arena IDs can be constructed.
Generational indexes, newtyped IDs, or private constructors can prevent accidental reuse bugs.
Reference-returning arenas give direct access but make APIs more lifetime-heavy and can make "allocate, then mutate the graph" workflows harder to express.

## Example
```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct NodeId(usize);

#[derive(Debug)]
struct Node {
    name: String,
    parent: Option<NodeId>,
}

#[derive(Default)]
struct Arena {
    nodes: Vec<Node>,
}

impl Arena {
    fn add(&mut self, name: impl Into<String>, parent: Option<NodeId>) -> NodeId {
        let id = NodeId(self.nodes.len());
        self.nodes.push(Node { name: name.into(), parent });
        id
    }

    fn get(&self, id: NodeId) -> &Node {
        &self.nodes[id.0]
    }
}

fn main() {
    let mut arena = Arena::default();
    let root = arena.add("root", None);
    let child = arena.add("child", Some(root));

    assert_eq!(arena.get(child).parent, Some(root));
    assert_eq!(arena.get(root).name.as_str(), "root");
}
```

This handle-based arena uses ordinary `Vec` allocation but demonstrates the core ownership shape.
All nodes live as long as the arena, and relationships use stable handles instead of borrowed references.

## Worked example: phase-scoped scratch arena
```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct TempId(usize);

#[derive(Default)]
struct TempArena {
    strings: Vec<String>,
}

impl TempArena {
    fn intern_temp(&mut self, value: &str) -> TempId {
        let id = TempId(self.strings.len());
        self.strings.push(value.to_owned());
        id
    }

    fn get(&self, id: TempId) -> Option<&str> {
        self.strings.get(id.0).map(String::as_str)
    }

    fn clear_phase(&mut self) {
        self.strings.clear();
    }
}

fn main() {
    let mut arena = TempArena::default();
    let name = arena.intern_temp("temporary");
    assert_eq!(arena.get(name), Some("temporary"));

    arena.clear_phase();
    assert_eq!(arena.get(name), None);
}
```

This is not a full generational arena: after `clear_phase`, old handles become invalid by convention and are checked with `Option`.
A production arena that exposes handles outside a phase should prevent stale access more strongly.
The example shows the key boundary: all temporary values are released together when the phase ends.

## Common errors
The classic failed arena attempt returns a reference while also needing later mutation:

```text
error[E0499]: cannot borrow `arena` as mutable more than once at a time
```

This happens when an API returns `&T` tied to a mutable borrow of the arena and the caller tries to allocate another value while keeping that reference alive.
Use handles, split immutable lookup from mutation, or choose an arena crate with an API designed for the borrowing pattern.

Another common error is trying to return an arena-owned reference after the arena is dropped:

```text
error[E0515]: cannot return value referencing local variable `arena`
```

Return an owned value, move the arena to the caller, or make the arena a caller-owned context parameter.

## Best practice
- ✅ Use arenas for phase-scoped data where many allocations share one obvious lifetime.
- ✅ Prefer handles or indexes when direct references would create awkward borrowing or self-reference problems.
- ✅ Drop the arena at a clear boundary so retained memory does not grow without limit.
- ✅ Benchmark against ordinary ownership before adopting an external arena crate.
- ✅ Document the lifetime boundary in the API name or owning type.
- ✅ Newtype arena handles (`NodeId`, `ExprId`) so indexes from different arenas are not casually mixed.
- ✅ Decide whether stale handles are impossible by construction, checked with `Option`, or considered a programmer error.
- ✅ Keep arena ownership above the objects that borrow from it; callers should see the phase boundary in the type flow.

## Pitfalls
- ⚠️ Using an arena for data with independent lifetimes can retain memory much longer than needed.
- ⚠️ Returning references into an arena from APIs without clear lifetimes can make callers fight the borrow checker.
- ⚠️ Assuming arenas automatically improve cache locality ignores object layout and traversal order.
- ⚠️ Mixing mutation and references into the same arena can run into borrowing restrictions; handles often compose better.
- ⚠️ Introducing an arena before profiling allocation cost is [[Avoiding Premature Optimization]].
- ⚠️ Clearing an arena while handles escape can create stale-handle bugs even in otherwise safe code.
- ⚠️ Using one arena for unrelated lifetimes couples memory growth and teardown across parts of the program.

## See also
[[Reducing Heap Allocations]] · [[SmallVec for Inline Storage]] · [[Ownership]] · [[Lifetimes]] · [[Borrowing]] · [[Vec]] · [[Capacity and Reallocation]] · [[Benchmarking with Criterion]] · [[Avoiding Premature Optimization]] · [[Performance & Optimization]]

## Sources
- The Rust Programming Language, ch. 4.1 "What Is Ownership?" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- The Rust Programming Language, ch. 10.3 "Validating References with Lifetimes" — [[the-book]],
  https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
- Rust standard library, `Vec` — [[the-book]],
  https://doc.rust-lang.org/std/vec/struct.Vec.html
