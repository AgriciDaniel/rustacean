---
type: pattern
title: "The State Pattern"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, oop, state-pattern, trait-objects]
domain: "OOP & Trait Objects"
difficulty: advanced
related: ["[[Trait Objects]]", "[[Type-State State Machines]]", "[[Encapsulation in Rust]]", "[[dyn Compatibility (Object Safety)]]", "[[Making Invalid States Unrepresentable]]", "[[Composition over Inheritance]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-03-oo-design-patterns.html", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility"]
rust_version: "edition 2024 / 1.85+"
---

# The State Pattern

The state pattern represents an object's internal states as separate values that implement a shared trait, letting state-specific behavior and transitions live with each state.

## What it is
The classic OOP state pattern is useful when one public type should keep a stable API while its behavior changes according to an internal state. In Rust, the traditional version usually stores a private `Option<Box<dyn State>>` and delegates transitions to the current state object.

This pattern is available in Rust, but it is not always the most Rust-like design. If invalid transitions can be made compile-time errors, [[Type-State State Machines]] often produce stronger guarantees.

## How it works
Each state is a zero-sized or small struct. A private trait defines transition methods. Those methods often take `self: Box<Self>` so a state can consume itself and return the next `Box<dyn State>`.

The outer type stores the state in an `Option` so it can temporarily move the boxed state out with `take`, call the consuming transition method, and then put the replacement state back. Keeping both the state field and concrete state types private preserves encapsulation: callers can request transitions but cannot forge states directly.

The trade-off is runtime indirection and some coupling between state implementations. Adding a new state may require changing the states that transition to it.

The `Option<Box<dyn State>>` field is a practical ownership workaround, not a semantic "state may be absent" claim. Rust does not allow moving a field out of `&mut self` while leaving the struct partially uninitialized, so `take` replaces `Some(state)` with `None` during the transition. The outer method must restore `Some(...)` before returning; keep that invariant local.

The transition methods use `self: Box<Self>` because the concrete state is owned behind a `Box<dyn State>`. This receiver form is dyn-compatible, so Rust can dispatch the call through the trait object and pass ownership of the box to the concrete state's implementation.

## Example
```rust
struct Post {
    state: Option<Box<dyn State>>,
}

impl Post {
    fn new() -> Self {
        Self {
            state: Some(Box::new(Draft)),
        }
    }

    fn request_review(&mut self) {
        if let Some(state) = self.state.take() {
            self.state = Some(state.request_review());
        }
    }

    fn status(&self) -> &'static str {
        self.state.as_ref().expect("state is always restored").status()
    }
}

trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn status(&self) -> &'static str;
}

struct Draft;
struct PendingReview;

impl State for Draft {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        Box::new(PendingReview)
    }

    fn status(&self) -> &'static str {
        "draft"
    }
}

impl State for PendingReview {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }

    fn status(&self) -> &'static str {
        "pending"
    }
}

fn main() {
    let mut post = Post::new();
    assert_eq!(post.status(), "draft");
    post.request_review();
    assert_eq!(post.status(), "pending");
}
```

## Worked example: rejection transition
```rust
struct Ticket {
    state: Option<Box<dyn TicketState>>,
}

impl Ticket {
    fn new() -> Self {
        Self {
            state: Some(Box::new(Open)),
        }
    }

    fn close(&mut self) {
        if let Some(state) = self.state.take() {
            self.state = Some(state.close());
        }
    }

    fn reopen(&mut self) {
        if let Some(state) = self.state.take() {
            self.state = Some(state.reopen());
        }
    }

    fn label(&self) -> &'static str {
        self.state.as_ref().expect("state is restored").label()
    }
}

trait TicketState {
    fn close(self: Box<Self>) -> Box<dyn TicketState>;
    fn reopen(self: Box<Self>) -> Box<dyn TicketState>;
    fn label(&self) -> &'static str;
}

struct Open;
struct Closed;

impl TicketState for Open {
    fn close(self: Box<Self>) -> Box<dyn TicketState> {
        Box::new(Closed)
    }

    fn reopen(self: Box<Self>) -> Box<dyn TicketState> {
        self
    }

    fn label(&self) -> &'static str {
        "open"
    }
}

impl TicketState for Closed {
    fn close(self: Box<Self>) -> Box<dyn TicketState> {
        self
    }

    fn reopen(self: Box<Self>) -> Box<dyn TicketState> {
        Box::new(Open)
    }

    fn label(&self) -> &'static str {
        "closed"
    }
}

fn main() {
    let mut ticket = Ticket::new();
    ticket.close();
    assert_eq!(ticket.label(), "closed");
    ticket.reopen();
    assert_eq!(ticket.label(), "open");
}
```

This keeps the public `Ticket` API stable while the state objects decide which transitions are no-ops and which produce a new concrete state.

## Common errors
```text
error[E0507]: cannot move out of `self.state` which is behind a mutable reference
```

Use `Option::take` or another replacement strategy when a transition must consume the boxed state. You need to leave the outer struct initialized while moving the old state out.

```text
error[E0038]: the trait `State` is not dyn compatible
```

State traits often become non-dyn-compatible when a default transition tries to return bare `Self` or when a transition is generic. Use `self: Box<Self> -> Box<dyn State>` for object-dispatched transitions, or switch to typestate if compile-time transitions are the goal.

## Best practice
- ✅ Use this pattern when the public type must hide state details and new states may be added behind that API.
- ✅ Keep the state trait and concrete state structs private unless external implementors are truly part of the design.
- ✅ Consider an enum first when the state set is small, closed, and naturally handled with exhaustive `match`.
- ✅ Prefer [[Type-State State Machines]] when callers should be prevented from invoking invalid operations at compile time.
- ✅ Keep the `None` period introduced by `Option::take` inside a tiny method so the invariant is easy to audit.
- ✅ Name no-op transitions intentionally in each state; they are business rules, not accidental fall-through.
- ✅ Add tests for invalid transition attempts because this runtime pattern intentionally allows the method call to exist.

## Pitfalls
- ⚠️ The `Option::take` dance is a sign you are moving an owned state out temporarily; keep the invariant local and restore the state before returning.
- ⚠️ Default transition methods returning `self` are limited by [[dyn Compatibility (Object Safety)]] because a trait object does not know the concrete `Self` type.
- ⚠️ Avoid scattering transition logic between the outer type and the state types; that loses the main benefit of the pattern.
- ⚠️ Do not expose the private state trait as an extension point unless you are ready to support downstream state implementations.
- ⚠️ Avoid this pattern for simple closed state machines where an enum is shorter, faster, and easier to exhaustively test.

## See also
[[OOP & Trait Objects]] · [[Trait Objects]] · [[dyn Compatibility (Object Safety)]] · [[Type-State State Machines]] · [[Encapsulation in Rust]] · [[Making Invalid States Unrepresentable]] · [[Composition over Inheritance]] · [[Enums]]
· [[Ownership]] · [[Move Semantics]] · [[Overusing Trait Objects]] · [[Non-dyn-Compatible Traits as Trait Objects]]

## Sources
- The Rust Programming Language, ch. 18.3 "Implementing an Object-Oriented Design Pattern" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-03-oo-design-patterns.html
- The Rust Programming Language, ch. 18.2 "Using Trait Objects to Abstract over Shared Behavior" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
- The Rust Reference, "Dyn compatibility" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility
