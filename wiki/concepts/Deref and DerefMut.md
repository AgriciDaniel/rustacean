---
type: concept
title: "Deref and DerefMut"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, deref, derefmut, smart-pointers]
domain: "Smart Pointers & Interior Mutability"
difficulty: intermediate
related: ["[[Box]]", "[[Rc]]", "[[RefCell]]", "[[Operator Overloading]]", "[[Deref Polymorphism Antipattern]]", "[[Smart Pointers & Interior Mutability]]"]
sources: ["[[the-book]]", "[[std]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-02-deref.html", "https://doc.rust-lang.org/std/ops/trait.Deref.html", "https://doc.rust-lang.org/std/ops/trait.DerefMut.html", "https://doc.rust-lang.org/reference/expressions/operator-expr.html#the-dereference-operator"]
rust_version: "edition 2024 / 1.85+"
aliases: ["The Deref Trait"]
---

# Deref and DerefMut

`Deref` and `DerefMut` define how pointer-like types produce shared or mutable references to their target, enabling `*value` and deref coercions.

## What it is
`Deref` is the trait behind immutable dereferencing.
Its `deref(&self)` method returns `&Self::Target`.
`DerefMut` extends that idea for mutable access with `deref_mut(&mut self)` returning `&mut Self::Target`.

These traits are central to smart pointers because they let `Box<T>`, `Rc<T>`, `Ref<T>`, `RefMut<T>`, `String`, and `Vec<T>` behave like references to their contents in the right contexts.

## How it works
When code writes `*x`, Rust can translate that into a call to `Deref::deref` followed by an ordinary reference dereference.
For function and method arguments, deref coercion can automatically convert `&T` to `&U` when `T: Deref<Target = U>`.
The compiler may repeat this process several times during method lookup and argument coercion, such as `&MyBox<String>` to `&String` to `&str`.
This is a compile-time convenience; it does not allocate and it does not move the target value.

Mutable coercion has stricter rules.
Rust can coerce `&mut T` to `&mut U` when `T: DerefMut<Target = U>`, and it can coerce `&mut T` to `&U`.
It cannot coerce `&T` to `&mut U`, because shared references do not prove unique access.
That one-way rule is why smart pointers such as `Rc<T>` implement `Deref` but not `DerefMut`: shared ownership cannot promise exclusive access to `T`.

Implement these traits only when dereferencing is the obvious meaning of the type.
For ordinary wrappers, explicit methods or traits are clearer and safer; see [[Deref Polymorphism Antipattern]].

## Example
```rust
use std::ops::{Deref, DerefMut};

struct MyBox<T>(T);

impl<T> Deref for MyBox<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<T> DerefMut for MyBox<T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

fn shout(name: &str) -> String {
    format!("HELLO, {}!", name.to_uppercase())
}

fn main() {
    let mut name = MyBox(String::from("rust"));
    name.push_str("acean");
    assert_eq!(shout(&name), "HELLO, RUSTACEAN!");
}
```

## Worked example: preserving wrapper invariants
```rust
use std::ops::Deref;

struct NonEmpty(String);

impl NonEmpty {
    fn new(value: String) -> Option<Self> {
        (!value.is_empty()).then_some(Self(value))
    }

    fn replace(&mut self, value: String) -> bool {
        if value.is_empty() {
            false
        } else {
            self.0 = value;
            true
        }
    }
}

impl Deref for NonEmpty {
    type Target = str;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

fn main() {
    let mut label = NonEmpty::new(String::from("crate")).unwrap();
    assert_eq!(label.len(), 5);
    assert!(!label.replace(String::new()));
    assert_eq!(&*label, "crate");
}
```

This wrapper deliberately implements `Deref<Target = str>` for read ergonomics but not `DerefMut`, because arbitrary `String` mutation could make the value empty and break the invariant.

## Common errors
`E0614` appears when a type is not dereferenceable:

```text
error[E0614]: type `MyBox<String>` cannot be dereferenced
```

The fix is to implement `Deref` with a borrowed target, or to use an explicit accessor when pointer semantics are not the right model.

`E0596` appears when code expects mutable deref through a non-mutable binding or a type that lacks `DerefMut`.
Make the binding `mut`, implement `DerefMut` only if it preserves invariants, or expose a named mutation method.

## Best practice
- ✅ Implement `Deref` for types that are genuinely pointer-like and have one natural target.
- ✅ Implement `DerefMut` only when callers may safely mutate the target without bypassing wrapper invariants.
- ✅ Rely on deref coercion for ergonomic calls, but keep public API signatures explicit.
- ✅ Prefer `AsRef`, `Borrow`, or named methods when the conversion is not pointer semantics.
- ✅ Keep `deref` cheap, deterministic, and unsurprising; callers do not expect allocation, locking, or fallible behavior from `*x`.
- ✅ Use associated `Target` to expose the most useful borrowed view, such as `str` for string-like wrappers.

## Pitfalls
- ⚠️ Do not use `Deref` as inheritance or method delegation; see [[Deref Polymorphism Antipattern]].
- ⚠️ `DerefMut` can expose mutation that invalidates a wrapper's invariants.
- ⚠️ Auto-deref in method lookup can make APIs feel magical if the wrapper has too many implicit targets.
- ⚠️ `Deref` returns a reference; returning an owned value would move out of `self` and would not match the trait.
- ⚠️ Avoid implementing `Deref` merely to save `.inner()` calls; it changes method lookup and can accidentally enlarge the public API.

## See also
[[Box]] · [[Rc]] · [[RefCell]] · [[Operator Overloading]] · [[Conversion Traits]] · [[Borrow for Equivalent Keys]] · [[Deref Polymorphism Antipattern]] · [[Smart Pointers & Interior Mutability]]

## Sources
- The Rust Programming Language, ch. 15.2 "Treating Smart Pointers Like Regular References with `Deref`" - [[the-book]],
  https://doc.rust-lang.org/book/ch15-02-deref.html
- Standard library, `std::ops::Deref` and `std::ops::DerefMut` - [[std]],
  https://doc.rust-lang.org/std/ops/trait.Deref.html
  https://doc.rust-lang.org/std/ops/trait.DerefMut.html
