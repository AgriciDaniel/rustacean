---
type: concept
title: "Box"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, box, heap, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: basic
related: ["[[Ownership]]", "[[Deref and DerefMut]]", "[[The Drop Trait]]", "[[Dynamically Sized Types]]", "[[Trait Objects]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-01-box.html", "https://doc.rust-lang.org/std/boxed/struct.Box.html"]
rust_version: "edition 2024 / 1.85+"
---

# Box

`Box<T>` is an owning smart pointer that stores a `T` in a heap allocation while keeping a fixed-size pointer on the stack.

## What it is
`Box<T>` gives a value one clear owner, just like an ordinary local variable, but places the owned value behind a pointer.
When the `Box<T>` is dropped, Rust drops the contained value and deallocates the heap storage.

The Book highlights three common uses: making recursive types have known size, moving large owned values without copying their bytes on the stack, and owning values through trait objects such as `Box<dyn Trait>`.

## How it works
`Box::new(value)` allocates enough heap space for `value`, moves the value there, and returns a `Box<T>`.
The box itself is sized because a pointer has known size even when the pointee is large or recursively shaped.

`Box<T>` implements [[Deref and DerefMut]], so `*boxed` accesses the inner value and method calls usually work through deref coercion.
It also participates in [[The Drop Trait]], so cleanup is automatic when ownership leaves scope.
For `Box<dyn Trait>` and `Box<[T]>`, the box is a fat pointer: it carries the data address plus metadata such as a vtable pointer or slice length.
That is still a fixed-size handle on the stack, while the dynamically sized value lives behind it.

Moving a `Box<T>` moves only the pointer-sized handle, not the heap allocation.
This is useful for large values or self-referential ownership graphs, but it does not by itself pin the value forever; use `Box::pin` or `Pin<Box<T>>` when address stability is part of an unsafe or async invariant.

`Box<T>` does not add shared ownership or runtime borrow checking.
If multiple parts of one thread need ownership of the same allocation, consider [[Rc]].
If callers need shared mutation through an immutable outer value, consider [[RefCell]] only when runtime borrow checks are appropriate.

## Example
```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}

impl List {
    fn len(&self) -> usize {
        match self {
            List::Cons(_, tail) => 1 + tail.len(),
            List::Nil => 0,
        }
    }
}

fn main() {
    let list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
    assert_eq!(list.len(), 2);
}
```

## Worked example: owned trait objects
```rust
trait Render {
    fn render(&self) -> String;
}

struct Heading(String);
struct Rule;

impl Render for Heading {
    fn render(&self) -> String {
        format!("# {}", self.0)
    }
}

impl Render for Rule {
    fn render(&self) -> String {
        String::from("---")
    }
}

fn main() {
    let blocks: Vec<Box<dyn Render>> = vec![
        Box::new(Heading(String::from("Smart pointers"))),
        Box::new(Rule),
    ];

    let output: Vec<String> = blocks.iter().map(|block| block.render()).collect();
    assert_eq!(
        output,
        vec![String::from("# Smart pointers"), String::from("---")]
    );
}
```

## Common errors
`E0072` appears when a recursive type contains itself directly:

```text
error[E0072]: recursive type `List` has infinite size
help: insert some indirection (e.g., a `Box`, `Rc`, or `&`) to break the cycle
```

The fix is to put an owning pointer at the recursive edge, commonly `Box<List>` for a singly owned tree or list.

`E0382` still applies after boxing: moving a `Box<T>` transfers ownership of the allocation.
Use a borrow if a function only needs to inspect it, or use [[Rc]] when the design needs multiple owners.

## Best practice
- ✅ Use `Box<T>` when the indirection itself is the feature: recursive enums, trait objects, or stable heap addresses.
- ✅ Prefer `Box<dyn Trait>` when the caller must own a value whose concrete type is intentionally hidden.
- ✅ Keep ordinary small values on the stack unless boxing solves a concrete type-size or ownership problem.
- ✅ Let boxes drop naturally; explicit `drop(boxed)` is only needed to release the allocation before the end of a scope.
- ✅ Use `Box<[T]>` when a fixed-length owned slice is enough and `Vec<T>`'s capacity management is not needed.
- ✅ Treat `Box::into_raw`/`Box::from_raw` as an FFI or unsafe-boundary tool; every raw pointer produced this way needs exactly one owner restored or an intentional leak.

## Pitfalls
- ⚠️ Boxing a value does not make it shared; moving a `Box<T>` still transfers the single owner.
- ⚠️ Boxing small values only to "avoid stack use" often adds allocation cost without improving the design.
- ⚠️ A recursive type still needs indirection at every recursive field that would otherwise contain itself directly.
- ⚠️ `Box<T>` is not a substitute for [[Rc]], [[Arc]], [[RefCell]], or [[Shared State with Mutex]] when the problem is shared ownership or mutation.
- ⚠️ `Box::leak` intentionally gives up automatic deallocation; reserve it for rare process-lifetime data or carefully documented global setup.

## See also
[[Ownership]] · [[Deref and DerefMut]] · [[The Drop Trait]] · [[Dynamically Sized Types]] · [[Trait Objects]] · [[Rc]] · [[RefCell]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.1 "Using `Box<T>` to Point to Data on the Heap" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-01-box.html
- Standard library, `std::boxed::Box` - [[std]],
  https://doc.rust-lang.org/std/boxed/struct.Box.html
