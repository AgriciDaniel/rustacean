---
type: pattern
title: "Type-State State Machines"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, typestate, state-machines, oop]
domain: "OOP & Trait Objects"
difficulty: intermediate
related: ["[[The State Pattern]]", "[[Making Invalid States Unrepresentable]]", "[[Ownership]]", "[[Move Semantics]]", "[[Encapsulation in Rust]]", "[[Type-State Pattern]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-03-oo-design-patterns.html"]
rust_version: "edition 2024 / 1.85+"
---

# Type-State State Machines

Type-state state machines encode workflow states as distinct Rust types, so invalid operations are missing from the type's API and fail at compile time.

## What it is
This is the Rust-flavored alternative the Book presents after the traditional OOP state pattern. Instead of one `Post` type with a hidden runtime state object, each state has its own type: `DraftPost`, `PendingReviewPost`, and `Post` for published content.

The transition methods consume `self` and return the next state type. Because only the published type has a `content` method, code cannot accidentally display draft content; that method simply does not exist for drafts.

## How it works
Ownership drives the state transition. A method such as `DraftPost::request_review(self)` takes ownership of the draft, moves its data into a `PendingReviewPost`, and prevents further use of the old draft binding. The caller usually shadows the variable name with the new state.

This design gives up some classic OOP encapsulation because callers can see state-specific types. In return, the compiler enforces the workflow. It is often a better trade-off for protocols, builders, setup sequences, authentication flows, and domain workflows where certain operations are valid only after earlier steps.

The mechanism is ordinary ownership plus method resolution. If a method is implemented only on `PendingReviewPost`, then `DraftPost` values simply do not have that method. If a transition takes `self`, the previous binding is moved and cannot be used unless the value is returned. That turns workflow rules into type-checking rules.

A common variant uses a generic wrapper plus zero-sized marker types: `Connection<Open>` and `Connection<Closed>`. This reduces duplicated fields while still giving each state a distinct method set. Use `PhantomData` only when the marker type is not stored as a real field.

## Example
```rust
struct Post {
    content: String,
}

struct DraftPost {
    content: String,
}

struct PendingReviewPost {
    content: String,
}

impl Post {
    fn new() -> DraftPost {
        DraftPost {
            content: String::new(),
        }
    }

    fn content(&self) -> &str {
        &self.content
    }
}

impl DraftPost {
    fn add_text(&mut self, text: &str) {
        self.content.push_str(text);
    }

    fn request_review(self) -> PendingReviewPost {
        PendingReviewPost {
            content: self.content,
        }
    }
}

impl PendingReviewPost {
    fn approve(self) -> Post {
        Post {
            content: self.content,
        }
    }
}

fn main() {
    let mut post = Post::new();
    post.add_text("Rust turns workflow rules into types.");
    let post = post.request_review();
    let post = post.approve();
    assert_eq!(post.content(), "Rust turns workflow rules into types.");
}
```

## Worked example: generic marker states
```rust
use std::marker::PhantomData;

struct Disconnected;
struct Connected;

struct Client<State> {
    address: String,
    state: PhantomData<State>,
}

impl Client<Disconnected> {
    fn new(address: impl Into<String>) -> Self {
        Self {
            address: address.into(),
            state: PhantomData,
        }
    }

    fn connect(self) -> Client<Connected> {
        Client {
            address: self.address,
            state: PhantomData,
        }
    }
}

impl Client<Connected> {
    fn send(&self, message: &str) -> String {
        format!("sent to {}: {message}", self.address)
    }

    fn disconnect(self) -> Client<Disconnected> {
        Client {
            address: self.address,
            state: PhantomData,
        }
    }
}

fn main() {
    let client = Client::<Disconnected>::new("localhost").connect();
    assert_eq!(client.send("ping"), "sent to localhost: ping");
    let _client = client.disconnect();
}
```

`send` is not implemented for `Client<Disconnected>`, so disconnected clients cannot accidentally send messages. The marker states exist for the type system; they do not add runtime data.

## Common errors
```text
error[E0599]: no method named `send` found for struct `Client<Disconnected>`
```

This is the intended failure mode: the operation is invalid in that state. Call the required transition first, or change the workflow if the operation should be valid earlier.

```text
error[E0382]: use of moved value: `post`
```

Transitions that take `self` consume the old state. Bind the returned state, often by shadowing the same variable name: `let post = post.request_review();`.

## Best practice
- ✅ Use state-specific types when invalid operations should be compile errors.
- ✅ Make transition methods consume `self` when the previous state must no longer be usable.
- ✅ Keep fields private so callers cannot construct later states without the required transitions.
- ✅ Use shadowing to keep workflow code readable as the value changes type.
- ✅ Use marker-type generics when several states share the same stored fields.
- ✅ Keep marker structs public only when callers need to name the state in their own signatures.
- ✅ Use trait bounds on marker states sparingly; explicit per-state `impl` blocks are often clearer.

## Pitfalls
- ⚠️ Do not use type-state when the state graph is highly dynamic and callers need to store many states together; [[The State Pattern]] or an enum may fit better.
- ⚠️ Avoid exposing constructors for privileged states unless external code is allowed to bypass the workflow.
- ⚠️ Do not hide every state behind `dyn Trait` if the point is compile-time enforcement.
- ⚠️ Do not make typestate APIs so granular that normal control flow becomes a maze of one-method types.
- ⚠️ Avoid public fields on state-specific types; callers could then fabricate states that were meant to require transitions.

## See also
[[OOP & Trait Objects]] · [[The State Pattern]] · [[Making Invalid States Unrepresentable]] · [[Ownership]] · [[Move Semantics]] · [[Encapsulation in Rust]] · [[Type-State Pattern]] · [[Builder Pattern]]
· [[Generics]] · [[PhantomData]] · [[Enums]] · [[Composition over Inheritance]]

## Sources
- The Rust Programming Language, ch. 18.3 "Encoding States and Behavior as Types" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-03-oo-design-patterns.html
