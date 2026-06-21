---
type: pattern
title: "Type-State Pattern"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, typestate, generics, api-design]
domain: "Idioms & API Design"
difficulty: advanced
related: ["[[Making Invalid States Unrepresentable]]", "[[Builder Pattern]]", "[[Zero-Cost Abstractions]]", "[[Generic Parameters]]", "[[Sealed Traits]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/items/generics.html", "https://doc.rust-lang.org/std/marker/struct.PhantomData.html", "https://doc.rust-lang.org/book/ch10-01-syntax.html"]
rust_version: "edition 2024 / 1.85+"
---

# Type-State Pattern

The type-state pattern encodes an object's state in its type so methods for the wrong state are compile errors.

## What it is
Some APIs are protocols: configure before build, connect before send, close after flushing, authenticate before accessing protected data.
The type-state pattern represents each phase with a distinct type parameter or marker type.

Instead of storing `is_open: bool` and checking it at runtime, expose `Connection<Closed>` and `Connection<Open>`.
Only `Connection<Open>` implements `send`.
Only a transition method can move between states.

## How it works
State marker types are usually zero-sized structs.
The main type stores its real data plus `PhantomData<State>` so the state participates in the type system without runtime storage.
Methods are implemented on specific state instantiations.

This is a stronger form of [[Making Invalid States Unrepresentable]].
It can make APIs safer, but it also increases generic surface area, so reserve it for state mistakes that matter.

`PhantomData<State>` tells the compiler that `Connection<State>` logically carries `State` even though no value of that type is stored.
That affects type identity, variance, auto traits, and drop checking without increasing runtime size.
The marker structs are often private so callers cannot name arbitrary states unless the crate intentionally exposes the protocol.

Transition methods usually take `self` by value.
That consumes the old state and returns the next state, making it impossible to keep using the old phase accidentally.
Borrowing transitions are possible, but they are harder to reason about because the old value remains alive.

## Example
```rust
use std::marker::PhantomData;

struct Closed;
struct Open;

struct Connection<State> {
    address: String,
    _state: PhantomData<State>,
}

impl Connection<Closed> {
    fn new(address: impl Into<String>) -> Self {
        Self { address: address.into(), _state: PhantomData }
    }

    fn connect(self) -> Connection<Open> {
        Connection { address: self.address, _state: PhantomData }
    }
}

impl Connection<Open> {
    fn send(&self, message: &str) -> String {
        format!("{} -> {message}", self.address)
    }

    fn close(self) -> Connection<Closed> {
        Connection { address: self.address, _state: PhantomData }
    }
}

fn main() {
    let conn = Connection::<Closed>::new("localhost").connect();
    assert_eq!(conn.send("ping"), "localhost -> ping");
    let _closed = conn.close();
}
```

## Typestate builder example
For a small number of required fields, typestate can move missing-field errors from runtime to compile time.

```rust
use std::marker::PhantomData;

struct Missing;
struct Present;

struct RequestBuilder<Url> {
    url: Option<String>,
    method: String,
    _url: PhantomData<Url>,
}

impl RequestBuilder<Missing> {
    fn new() -> Self {
        Self { url: None, method: String::from("GET"), _url: PhantomData }
    }

    fn url(self, url: impl Into<String>) -> RequestBuilder<Present> {
        RequestBuilder { url: Some(url.into()), method: self.method, _url: PhantomData }
    }
}

impl<Url> RequestBuilder<Url> {
    fn method(mut self, method: impl Into<String>) -> Self {
        self.method = method.into();
        self
    }
}

impl RequestBuilder<Present> {
    fn build(self) -> (String, String) {
        (self.method, self.url.expect("url state is Present"))
    }
}

fn main() {
    let request = RequestBuilder::new().method("POST").url("/widgets").build();
    assert_eq!(request, (String::from("POST"), String::from("/widgets")));
}
```

## Common errors
Calling a method in the wrong state becomes a method-resolution error:

```text
error[E0599]: no method named `send` found for struct `Connection<Closed>`
```

The fix is to perform the required transition first (`connect()` before `send()`), or to simplify the API if the state distinction is not worth exposing.
Do not add the method to every state unless it is genuinely valid in every state.

## Best practice
- ✅ Use typestate when a wrong call order would be a real bug and can be expressed simply.
- ✅ Keep marker types private if callers should not manufacture states.
- ✅ Prefer clear transition methods that consume `self` and return the next state.
- ✅ Consider typestate builders when missing required builder fields should be compile-time errors.
- ✅ Keep the number of states small and name them after domain phases, not implementation details.
- ✅ Hide `PhantomData` and marker fields; callers should use transitions, not construct states manually.

## Pitfalls
- ⚠️ Avoid typestate for trivial flows where a runtime check is clearer.
- ⚠️ Watch public generic types; every state parameter becomes part of the API.
- ⚠️ Do not leak marker implementation details if you need freedom to change the state machine later.
- ⚠️ Avoid combinatorial typestate explosions for many independent options; a runtime [[Builder Pattern]] may be clearer.
- ⚠️ Be careful with trait impls for all states; blanket impls can accidentally expose behavior in states that should not have it.

## See also
[[Making Invalid States Unrepresentable]] · [[Builder Pattern]] · [[Zero-Cost Abstractions]] · [[Generic Parameters]] · [[Sealed Traits]] · [[Constructor Naming]] · [[PhantomData]] · [[Move Semantics]] · [[Idioms & API Design]]

## Sources
- The Rust Reference, "Generic parameters" - [[the-reference]], https://doc.rust-lang.org/reference/items/generics.html
- `PhantomData` - https://doc.rust-lang.org/std/marker/struct.PhantomData.html
- The Rust Programming Language, "Generic Data Types" - [[the-book]], https://doc.rust-lang.org/book/ch10-01-syntax.html
