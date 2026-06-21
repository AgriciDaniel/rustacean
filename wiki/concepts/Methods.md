---
type: concept
title: "Methods"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, structs, methods, impl]
domain: "Structs"
difficulty: basic
related: ["[[Structs]]", "[[Named Field Structs]]", "[[Associated Functions]]", "[[Borrowing]]", "[[Ownership]]", "[[Visibility and Privacy]]", "[[Fully Qualified Syntax]]", "[[Traits]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-03-method-syntax.html", "https://doc.rust-lang.org/reference/expressions/method-call-expr.html", "https://doc.rust-lang.org/reference/items/associated-items.html"]
rust_version: "edition 2024 / 1.85+"
---

# Methods

Methods are associated functions whose first parameter is `self`, letting behavior be called with dot syntax on a struct instance.

## What it is
A method is a function defined inside an `impl Type` block and called as `value.method(args...)`.
For structs, methods keep behavior next to the data shape it belongs to.

The receiver determines what the method can do:
`&self` reads, `&mut self` mutates in place, and `self` consumes the value.
This receiver design makes [[Ownership]] visible in the API.

## How it works
Inside `impl Rectangle`, `Self` means `Rectangle`.
The shorthand `&self` means `self: &Self`; `&mut self` means `self: &mut Self`; and `self` means `self: Self`.
Rust automatically borrows, mutably borrows, or dereferences the receiver as needed for method calls, so callers write `rect.area()` rather than `(&rect).area()`.

Methods may take more parameters after `self`, and those parameters follow normal ownership and borrowing rules.
A method can have the same name as a field: `rect.width` accesses the field, while `rect.width()` calls the method.

Method-call syntax has special receiver adjustment.
The compiler builds candidate receiver types by dereferencing the receiver and then considering `T`, `&T`, and `&mut T`.
That is why `rect.area()`, `(&rect).area()`, and sometimes `boxed.area()` can all resolve to the same `fn area(&self)`.
This automatic borrowing applies to the receiver only; ordinary parameters still require explicit references when the signature asks for them.

## Example
```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn grow(&mut self, amount: u32) {
        self.width += amount;
        self.height += amount;
    }

    fn into_tuple(self) -> (u32, u32) {
        (self.width, self.height)
    }
}

fn main() {
    let mut rect = Rectangle { width: 3, height: 4 };
    println!("{}", rect.area());
    rect.grow(2);
    println!("{:?}", rect.into_tuple());
}
```

## Worked example
```rust
#[derive(Debug)]
struct Counter {
    value: u64,
}

impl Counter {
    fn value(&self) -> u64 {
        self.value
    }

    fn increment_by(&mut self, amount: u64) {
        self.value += amount;
    }

    fn into_inner(self) -> u64 {
        self.value
    }
}

fn main() {
    let mut counter = Counter { value: 10 };

    counter.increment_by(5);
    println!("current = {}", counter.value());

    let final_value = counter.into_inner();
    println!("final = {final_value}");
}
```

The three receivers communicate the ownership contract: read by shared borrow, mutate by exclusive borrow, and consume by value.

## Common errors
A consuming method moves the receiver, so the old value cannot be used afterward:

```rust
struct Token(String);

impl Token {
    fn into_string(self) -> String {
        self.0
    }
}

fn main() {
    let token = Token(String::from("abc"));
    let text = token.into_string();
    println!("{text}");
    println!("{}", token.0);
}
```

```console
error[E0382]: borrow of moved value: `token`
```

Fix it by using a borrowing method such as `as_str(&self) -> &str`, cloning intentionally, or accepting that the conversion consumes the value.

## Best practice
- ✅ Use `&self` for read-only methods and `&mut self` only when mutation is part of the operation.
- ✅ Use consuming `self` for conversions or builders that intentionally prevent reuse of the old value.
- ✅ Group inherent methods in `impl` blocks close to the struct definition when practical.
- ✅ Use methods to expose behavior while keeping fields private when designing library APIs.
- ✅ Name borrowing conversion methods with `as_`, mutating operations with verbs, and consuming conversions with `into_` when that matches Rust convention.
- ✅ Keep non-receiver parameters explicit about borrowing, such as `fn can_hold(&self, other: &Rectangle)`.

## Pitfalls
- ⚠️ Taking `self` by value accidentally can make callers lose ownership; prefer borrowing unless consumption is intentional.
- ⚠️ Getter methods that simply expose every private field may be a sign the abstraction is too thin.
- ⚠️ Method receiver auto-borrowing is ergonomic, but other parameters still need explicit borrows such as `rect.can_hold(&other)`.
- ⚠️ Inherent methods and trait methods can have the same name; use [[Fully Qualified Syntax]] when resolution is ambiguous.
- ⚠️ A method with `&self` cannot reassign fields unless the fields use an interior mutability type designed for that purpose.

## See also
[[Structs]] · [[Named Field Structs]] · [[Associated Functions]] · [[Borrowing]] · [[Ownership]] · [[Visibility and Privacy]] · [[Fully Qualified Syntax]] · [[The Drop Trait]] · [[Traits]] · [[Move Semantics]]

## Sources
- The Rust Programming Language, ch. 5.3 "Method Syntax" — [[the-book]], https://doc.rust-lang.org/book/ch05-03-method-syntax.html
- The Rust Reference, "Method-call expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/method-call-expr.html
- The Rust Reference, "Associated items" — [[the-reference]], https://doc.rust-lang.org/reference/items/associated-items.html
