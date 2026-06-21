---
type: concept
title: "Encapsulation in Rust"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, oop, encapsulation, api-design]
domain: "OOP & Trait Objects"
difficulty: basic
related: ["[[Object-Oriented Rust]]", "[[Composition over Inheritance]]", "[[Making Invalid States Unrepresentable]]", "[[Modules]]", "[[Visibility]]", "[[Newtype Pattern]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch18-01-what-is-oo.html", "https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html", "https://doc.rust-lang.org/reference/visibility-and-privacy.html"]
rust_version: "edition 2024 / 1.85+"
---

# Encapsulation in Rust

Encapsulation in Rust means exposing the operations a caller needs while keeping representation details private, so invariants can be maintained and internals can change without breaking users.

## What it is
Rust encapsulates with module privacy. Items and fields are private by default; `pub` opts them into a wider API. A public struct can still have private fields, which lets external code construct and use the type only through the methods you provide.

This is the Rust version of a classic OOP goal: users interact through a public interface, while the type protects its internal state. It is especially important when a field is a cache, index, count, state marker, or any derived value that must stay synchronized with other data.

## How it works
Visibility is checked at compile time. Code outside the defining module cannot read or mutate private fields directly. Public methods can validate input, update multiple fields together, preserve representation invariants, and return borrowed views instead of exposing ownership of internals.

The Book's `AveragedCollection` example uses this idea: the collection keeps a list and a cached average. If callers could mutate the list directly, the average could become stale. By keeping fields private, `add` and `remove` become the only mutation path, so the cache can be updated reliably.

Encapsulation is also what lets you switch from `Vec<T>` to another storage type later while keeping the same public method signatures.

Rust's privacy boundary is lexical and module-based. A parent module cannot freely inspect a child module's private items unless visibility allows it, and external crates cannot name or construct private fields. This matters for public structs: `pub struct User { id: UserId }` exposes the type name but not its representation, while `pub struct User { pub id: UserId }` commits to that field forever as part of the API.

Encapsulation does not require hiding all data behind trivial getters. A field can be public when it is plain data with no invariant and changing its representation would not be part of the compatibility promise. The sharper test is whether callers can put the value into a state your type would not create itself.

## Example
```rust
pub struct AveragedCollection {
    values: Vec<i32>,
    average: Option<f64>,
}

impl AveragedCollection {
    pub fn new() -> Self {
        Self {
            values: Vec::new(),
            average: None,
        }
    }

    pub fn add(&mut self, value: i32) {
        self.values.push(value);
        self.recalculate();
    }

    pub fn average(&self) -> Option<f64> {
        self.average
    }

    fn recalculate(&mut self) {
        let len = self.values.len();
        self.average = (len > 0).then(|| {
            let total: i32 = self.values.iter().sum();
            total as f64 / len as f64
        });
    }
}

fn main() {
    let mut scores = AveragedCollection::new();
    scores.add(10);
    scores.add(20);
    assert_eq!(scores.average(), Some(15.0));
}
```

## Worked example: validated construction
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Username(String);

impl Username {
    pub fn new(value: impl Into<String>) -> Result<Self, String> {
        let value = value.into();
        let valid = !value.is_empty()
            && value.len() <= 16
            && value.chars().all(|c| c.is_ascii_alphanumeric() || c == '_');

        if valid {
            Ok(Self(value))
        } else {
            Err(String::from("username must be 1-16 ASCII letters, digits, or '_'"))
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

fn main() {
    let username = Username::new("rust_2024").unwrap();
    assert_eq!(username.as_str(), "rust_2024");
    assert!(Username::new("not valid!").is_err());
}
```

The private tuple field prevents callers from writing `Username("not valid!".into())` outside the defining module. After construction succeeds, downstream functions can accept `Username` without revalidating the same rule.

## Common errors
```text
error[E0451]: field `values` of struct `AveragedCollection` is private
```

This is usually a successful encapsulation boundary, not a bug. Add or use a public method that preserves the invariant instead of making the field public by reflex.

```text
error[E0616]: field `0` of struct `Username` is private
```

For tuple newtypes, expose `as_str`, `into_inner`, or a domain-specific method when external code needs access. Use `into_inner` only when giving away the representation is an intentional API promise.

## Best practice
- ✅ Keep fields private when direct mutation could break an invariant.
- ✅ Expose narrow methods that say what the caller wants to do, not how the type is stored.
- ✅ Return borrowed views such as `&str`, `&[T]`, or iterators when callers only need observation.
- ✅ Combine encapsulation with [[Making Invalid States Unrepresentable]] when invalid states can be ruled out by type design.
- ✅ Use constructors that return `Result` when construction can fail; the type should not exist in an invalid form.
- ✅ Keep helper functions private when they are implementation details, even if tests exercise them through public behavior.
- ✅ Document public invariants near the constructor and methods that maintain them.

## Pitfalls
- ⚠️ Do not make fields public just to avoid writing constructors or accessors; that freezes your representation into the public API.
- ⚠️ Avoid Java-style getters for every field by reflex; expose behavior-oriented methods when they communicate intent better.
- ⚠️ Do not rely on documentation alone to protect invariants that privacy can enforce.
- ⚠️ Do not return `&mut` references to internal collections when arbitrary mutation can desynchronize caches, indexes, or counters.
- ⚠️ Avoid `pub(crate)` as a casual shortcut in large crates; it widens the invariant boundary to the whole crate.

## See also
[[OOP & Trait Objects]] · [[Object-Oriented Rust]] · [[Composition over Inheritance]] · [[Making Invalid States Unrepresentable]] · [[Newtype Pattern]] · [[Type-State State Machines]] · [[Traits]] · [[Modules]]
· [[Visibility]] · [[Builder Pattern]] · [[Type-State Pattern]] · [[The State Pattern]]

## Sources
- The Rust Programming Language, ch. 18.1 "Encapsulation That Hides Implementation Details" — [[the-book]],
  https://doc.rust-lang.org/book/ch18-01-what-is-oo.html
- The Rust Programming Language, ch. 7.3 "Paths for Referring to an Item in the Module Tree" — [[the-book]],
  https://doc.rust-lang.org/book/ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
- The Rust Reference, "Visibility and privacy" — [[the-reference]],
  https://doc.rust-lang.org/reference/visibility-and-privacy.html
