---
type: pattern
title: "Composition over Inheritance"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, oop, composition, api-design]
domain: "OOP & Trait Objects"
difficulty: intermediate
related: ["[[Object-Oriented Rust]]", "[[Encapsulation in Rust]]", "[[Trait Objects]]", "[[Default Implementations]]", "[[Newtype Pattern]]", "[[The State Pattern]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-01-what-is-oo.html", "https://doc.rust-lang.org/book/ch18-02-trait-objects.html", "https://doc.rust-lang.org/reference/items/traits.html"]
rust_version: "edition 2024 / 1.85+"
---

# Composition over Inheritance

Composition over inheritance means building Rust types out of owned fields and trait-based behavior instead of trying to model parent-child class hierarchies.

## What it is
Rust has no built-in struct inheritance. A type cannot inherit fields or inherent methods from another struct. Instead, Rust code usually composes values: one type owns another as a field, delegates selected behavior, and exposes only the API it wants to promise.

For shared behavior, use traits. For reusable default behavior, use default trait methods. For runtime substitution, use trait objects. For a closed set of variants, use enums. These tools cover the main reasons people reach for inheritance without creating fragile base classes.

## How it works
Composition makes ownership explicit. If `Toolbar` contains `Vec<Button>`, the toolbar owns buttons. If `Cached<T>` contains `T`, the wrapper can add caching behavior without pretending to be a subtype of `T`.

Delegation is explicit too. You choose which methods to forward, which to hide, and which invariants to enforce. This is more verbose than inheritance in some cases, but it prevents accidental API inheritance where a child type exposes methods that do not make sense.

Use trait objects only when substitutability must happen at runtime. If the set of cases is closed, an enum can be simpler and more exhaustive.

Composition also makes borrowing and lifetimes visible. A wrapper may own a collaborator (`N`), borrow one (`&'a dyn Notifier`), or share one (`Arc<dyn Notifier + Send + Sync>`). Those choices are design facts in Rust, not incidental implementation details hidden behind a base class pointer.

Default trait methods can share behavior, but they should express behavior that follows from the trait contract. If a default method depends on fields a trait cannot see, move that logic into a helper type or require a smaller primitive method that implementors provide.

## Example
```rust
trait Notifier {
    fn send(&self, message: &str);
}

struct ConsoleNotifier;

impl Notifier for ConsoleNotifier {
    fn send(&self, message: &str) {
        println!("notice: {message}");
    }
}

struct AuditLog<N> {
    notifier: N,
    entries: Vec<String>,
}

impl<N: Notifier> AuditLog<N> {
    fn new(notifier: N) -> Self {
        Self {
            notifier,
            entries: Vec::new(),
        }
    }

    fn record(&mut self, entry: impl Into<String>) {
        let entry = entry.into();
        self.notifier.send(&entry);
        self.entries.push(entry);
    }
}

fn main() {
    let mut log = AuditLog::new(ConsoleNotifier);
    log.record("user signed in");
    assert_eq!(log.entries.len(), 1);
}
```

## Worked example: delegate selectively
```rust
use std::time::{Duration, Instant};

trait Clock {
    fn now(&self) -> Instant;
}

struct SystemClock;

impl Clock for SystemClock {
    fn now(&self) -> Instant {
        Instant::now()
    }
}

struct RateLimiter<C> {
    clock: C,
    last_seen: Option<Instant>,
    minimum_gap: Duration,
}

impl<C: Clock> RateLimiter<C> {
    fn new(clock: C, minimum_gap: Duration) -> Self {
        Self {
            clock,
            last_seen: None,
            minimum_gap,
        }
    }

    fn allow(&mut self) -> bool {
        let now = self.clock.now();
        let allowed = self
            .last_seen
            .is_none_or(|then| now.duration_since(then) >= self.minimum_gap);
        if allowed {
            self.last_seen = Some(now);
        }
        allowed
    }
}

fn main() {
    let mut limiter = RateLimiter::new(SystemClock, Duration::from_secs(1));
    assert!(limiter.allow());
}
```

`RateLimiter` does not become a subtype of `SystemClock`. It owns a clock-like collaborator, delegates only `now`, and keeps rate-limiting state private.

## Common errors
```text
error[E0599]: no method named `send` found for struct `AuditLog`
```

Composition does not automatically inherit the inner value's methods. Add a forwarding method only if exposing that operation preserves the outer type's meaning and invariants.

```text
error[E0277]: the trait bound `MockClock: Clock` is not satisfied
```

Generic composition requires the collaborator to implement the bound. Implement the trait for the test double, or change the field to a concrete type if substitution is not intended.

## Best practice
- ✅ Store collaborators as fields and expose behavior through methods that preserve the owner type's invariants.
- ✅ Use trait bounds for compile-time substitution and [[Trait Objects]] for runtime substitution.
- ✅ Use [[Default Implementations]] for shared behavior that truly belongs to a trait contract.
- ✅ Use [[Newtype Pattern]] when wrapping a type should create a distinct API, not leak the wrapped type's full surface.
- ✅ Forward methods deliberately; each forwarded method becomes part of the wrapper's public contract.
- ✅ Prefer small collaborator traits in tests so production types do not need to expose broad internals.
- ✅ Use enums for closed behavioral families when exhaustive handling is clearer than object dispatch.

## Pitfalls
- ⚠️ Do not simulate inheritance by exposing every inner method; that recreates the coupling composition is meant to avoid.
- ⚠️ Avoid macro-generated fake inheritance unless you have a narrow, well-tested reason.
- ⚠️ Do not choose trait objects for closed alternatives that an enum and exhaustive `match` would model better.
- ⚠️ Do not put a mutable collaborator behind shared ownership merely to mimic a mutable base class; prefer normal ownership or explicit interior mutability only when needed.
- ⚠️ Do not use default trait methods as a hidden field-access mechanism. Traits describe behavior, not object layout.

## See also
[[OOP & Trait Objects]] · [[Object-Oriented Rust]] · [[Encapsulation in Rust]] · [[Trait Objects]] · [[Default Implementations]] · [[Newtype Pattern]] · [[The State Pattern]] · [[Type-State State Machines]]
· [[Static vs Dynamic Dispatch]] · [[Enums]] · [[Trait Bounds]] · [[Overusing Trait Objects]]

## Sources
- The Rust Programming Language, ch. 18.1 "Inheritance as a Type System and as Code Sharing" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-01-what-is-oo.html
- The Rust Programming Language, ch. 18.2 "Using Trait Objects to Abstract over Shared Behavior" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-02-trait-objects.html
- The Rust Reference, "Traits" — [[the-reference]],
  https://doc.rust-lang.org/reference/items/traits.html
