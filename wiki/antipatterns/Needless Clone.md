---
type: antipattern
title: "Needless Clone"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, clone, performance, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: intermediate
related: ["[[Ownership]]", "[[Borrowing]]", "[[References]]", "[[Copy and Clone]]", "[[Move Semantics]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/std/clone/trait.Clone.html", "https://doc.rust-lang.org/std/marker/trait.Copy.html"]
rust_version: "edition 2024 / 1.85+"
---

# Needless Clone

Needless clone is using `.clone()` to avoid an ownership error when a borrow, shorter scope, or ownership redesign would express the program more accurately and avoid extra work.

## The mistake
`Clone` is a real semantic operation: it creates another value that is logically independent according to that type's clone contract. For cheap `Copy` values this is trivial, but for `String`, `Vec<T>`, maps, reference-counted pointers, and many domain types it may allocate, increment counts, or copy substantial data.

The footgun is treating `.clone()` as a borrow-checker silencer. A clone that is not needed by the domain model usually hides the real question: should this function own the value, borrow the value, mutate it in place, or return a transformed value?

## Why it happens
Rust's move semantics are explicit. Passing a `String` to `fn greet(name: String)` transfers ownership, so the caller cannot use the same `String` afterward. Beginners often respond by cloning at the call site instead of changing the function to accept `&str`.

That fix compiles, but it spreads ownership costs through the program. If the callee only reads, it should not demand ownership. If it needs to store the data, taking ownership is appropriate and the call-site clone may be the honest cost.

Under the hood, `Clone::clone` is ordinary user-defined code. For `Vec<T>` and `String`, it allocates a fresh buffer and copies elements or bytes. For `Arc<T>` and `Rc<T>`, it increments a reference count and keeps the same allocation alive longer. For domain types, `clone` may be arbitrarily expensive or may deliberately preserve identity-like fields, so a clone is part of the API's semantics, not just syntax.

The borrow checker error is often pointing at a better shape: accept a borrowed view, split a mutation into a smaller scope, move the value once into its real owner, or return the owned value from a transformation.

## Example
```rust
struct User {
    name: String,
}

fn greeting_for(name: &str) -> String {
    format!("hello, {name}")
}

fn main() {
    let user = User {
        name: String::from("Ferris"),
    };

    // Mistake: greeting_for used to take String, so callers wrote:
    // let msg = greeting_for(user.name.clone());

    let msg = greeting_for(&user.name);
    println!("{msg}");
    println!("still have the user name: {}", user.name);
}
```

## Second example: clone caused by an oversized borrow
```rust
#[derive(Debug)]
struct Cart {
    owner: String,
    items: Vec<String>,
}

impl Cart {
    fn owner(&self) -> &str {
        &self.owner
    }

    fn add_item(&mut self, item: impl Into<String>) {
        self.items.push(item.into());
    }
}

fn main() {
    let mut cart = Cart {
        owner: String::from("Ferris"),
        items: Vec::new(),
    };

    {
        let owner = cart.owner();
        println!("building cart for {owner}");
    } // immutable borrow ends here

    cart.add_item("book");
    println!("{cart:?}");
}
```

The tempting workaround is `let owner = cart.owner().to_owned();`, but that allocates just to keep a label alive. A narrower scope expresses the real dependency and lets the later mutation proceed without cloning.

## Common errors
Typical move error:

```text
error[E0382]: borrow of moved value: `name`
```

Fix it by changing the callee from `fn f(name: String)` to `fn f(name: &str)` when it only reads, or by moving the value and not using it afterward when the callee really becomes the owner.

Typical borrow error that triggers defensive clones:

```text
error[E0502]: cannot borrow `cart` as mutable because it is also borrowed as immutable
```

Fix it by shortening the immutable borrow's scope, using `split_at_mut`/field borrowing when appropriate, or computing the owned result before the mutable operation only when ownership is truly needed.

## Best practice
- ✅ Prefer `&T`, `&mut T`, `&str`, and `&[T]` when a function only needs temporary access.
- ✅ Clone at ownership boundaries where a second owned value is genuinely required, such as storing data while the caller also keeps it.
- ✅ Narrow borrow scopes with blocks or helper functions before reaching for `.clone()`.
- ✅ Let `Copy` types be copied naturally; do not call `.clone()` just to make integer or boolean copies look explicit.
- ✅ Use `to_owned`/`to_string` at text boundaries deliberately; inside generic code prefer the type's actual `Clone` contract.
- ✅ Run Clippy and review `redundant_clone`/`clone_on_copy` warnings, but verify the ownership intent before applying suggestions mechanically.

## Pitfalls
- ⚠️ Cloning a `Vec<T>` to read one element usually points to a missing slice borrow.
- ⚠️ Cloning to satisfy an async `'static` bound can hide the need to move one owned request object into a task; see [[Premature Arc Mutex]] and [[Blocking in Async]].
- ⚠️ Cloning `Rc<T>` or `Arc<T>` is cheap for the pointed-to data but changes ownership topology; see [[Rc RefCell Overuse]].
- ⚠️ Cloning in hot loops can turn a linear pass into allocation-heavy code.
- ⚠️ A clone that crosses a thread or task boundary may be correct, but it should be visible in the design, not scattered at call sites.
- ⚠️ Cloning to work around lifetime errors can leave the API less useful than accepting borrowed inputs.

## See also
[[Ownership]] · [[Borrowing]] · [[References]] · [[Copy and Clone]] · [[Move Semantics]] · [[Unnecessary Collect]] · [[Rc RefCell Overuse]] · [[Stringly-Typed Code]] · [[Premature Arc Mutex]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 4.2 "References and Borrowing" — [[the-book]], https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- Standard library, `Clone` — [[the-reference]], https://doc.rust-lang.org/std/clone/trait.Clone.html
- Standard library, `Copy` — [[the-reference]], https://doc.rust-lang.org/std/marker/trait.Copy.html
