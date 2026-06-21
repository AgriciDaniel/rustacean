---
type: antipattern
title: "Deref Polymorphism Antipattern"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, deref, traits, composition, antipattern]
domain: "Anti-patterns & Footguns"
difficulty: advanced
related: ["[[The Deref Trait]]", "[[Traits]]", "[[Smart Pointers]]", "[[Newtype Pattern]]", "[[Composition over Inheritance]]", "[[Anti-patterns & Footguns]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch15-02-deref.html", "https://doc.rust-lang.org/std/ops/trait.Deref.html", "https://doc.rust-lang.org/reference/expressions/method-call-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Deref Polymorphism Antipattern

Deref polymorphism is implementing `Deref` so a wrapper "inherits" another type's methods; in Rust, `Deref` should be reserved for pointer-like access, not general delegation.

## The mistake
`Deref` lets smart pointers behave like references to their targets. `Box<T>`, `Rc<T>`, `Arc<T>`, and `String`/`Vec<T>`-like containers use this to expose the value they own or buffer.

The antipattern is implementing `Deref<Target = Inner>` for an ordinary domain wrapper just to call `inner` methods directly on the wrapper. That makes method lookup implicit and surprising, and it does not create real subtyping.

## Why it happens
Rust has traits and composition, not inheritance. Developers coming from inheritance-heavy languages sometimes look for a way to "extend" a concrete type. `Deref` appears to work because method call syntax automatically dereferences receivers during lookup.

The result is fragile API design. Methods may appear on the wrapper without being part of its intended interface. Trait implementations for the inner type do not automatically become trait implementations for the wrapper.

Method-call lookup tries receiver adjustments, including auto-reference and auto-deref. That is why `box_value.method()` can call methods on `T`: pointer-like wrappers are meant to participate in this machinery. For an ordinary domain wrapper, the same machinery hides delegation behind implicit coercion.

`DerefMut` is even riskier because it hands out mutable access to the inner value. If the wrapper exists to maintain invariants, mutable deref can let callers bypass validation with ordinary method calls or assignments.

## Example
```rust
struct Canvas {
    pixels: Vec<u8>,
}

impl Canvas {
    fn clear(&mut self) {
        self.pixels.fill(0);
    }
}

trait Drawable {
    fn clear(&mut self);
}

struct Window {
    canvas: Canvas,
    title: String,
}

impl Drawable for Window {
    fn clear(&mut self) {
        self.canvas.clear();
    }
}

fn reset(target: &mut impl Drawable) {
    target.clear();
}

fn main() {
    let mut window = Window {
        canvas: Canvas { pixels: vec![255; 4] },
        title: String::from("main"),
    };

    reset(&mut window);
    println!("{}: {:?}", window.title, window.canvas.pixels);
}
```

## Second example: preserve newtype boundaries
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct NonEmptyName(String);

impl NonEmptyName {
    fn new(value: impl Into<String>) -> Option<Self> {
        let value = value.into();
        (!value.trim().is_empty()).then_some(Self(value))
    }

    fn as_str(&self) -> &str {
        &self.0
    }
}

fn greet(name: &NonEmptyName) {
    println!("hello, {}", name.as_str());
}

fn main() {
    let name = NonEmptyName::new("Ferris").expect("literal is non-empty");
    greet(&name);
}
```

This wrapper should not deref to `String`: callers should not be able to call every mutating `String` method and accidentally create an empty name. A small explicit API keeps the invariant visible.

## Common errors
Assuming deref transfers traits:

```text
error[E0277]: the trait bound `Wrapper: SomeTrait` is not satisfied
```

Fix it by implementing the trait for the wrapper or by making the function accept the inner type explicitly. `Deref<Target = Inner>` does not make `Wrapper` a subtype of `Inner`.

Confusing method resolution:

```text
error[E0599]: no method named `method` found for struct `Wrapper`
```

The fix is usually an explicit forwarding method or a trait bound, not another `Deref` impl. If callers should rely on the behavior, name it in the wrapper's public API.

## Best practice
- ✅ Implement `Deref` only when the type is pointer-like and dereferencing is the central meaning of the type.
- ✅ Use traits for shared behavior that callers should rely on.
- ✅ Use explicit forwarding methods when the wrapper owns the public API.
- ✅ Use composition to keep invariants around the inner type under the wrapper's control.
- ✅ Use `AsRef`, `Borrow`, or named accessors when callers need a view into the inner value without pretending it is the inner type.
- ✅ Implement traits on the wrapper when the wrapper is meant to participate in generic code.

## Pitfalls
- ⚠️ Deref-based delegation exposes more surface area than intended.
- ⚠️ Auto-deref method lookup can make error messages mention inner types instead of the abstraction the reader sees.
- ⚠️ `DerefMut` can let callers mutate through your wrapper and bypass invariants.
- ⚠️ Newtypes lose their safety value if they silently behave like the raw inner type. See [[Stringly-Typed Code]].
- ⚠️ Public `Deref` impls become part of the API surface and are difficult to remove without breaking callers.
- ⚠️ Deref coercions can make simple-looking calls depend on import order and receiver type details.

## See also
[[The Deref Trait]] · [[Traits]] · [[Smart Pointers]] · [[Newtype Pattern]] · [[Composition over Inheritance]] · [[Stringly-Typed Code]] · [[Type Aliases]] · [[Rc RefCell Overuse]] · [[Anti-patterns & Footguns]]

## Sources
- The Rust Programming Language, ch. 15.2 "Treating Smart Pointers Like Regular References with Deref" — [[the-book]], https://doc.rust-lang.org/book/ch15-02-deref.html
- Standard library, `Deref` — [[the-reference]], https://doc.rust-lang.org/std/ops/trait.Deref.html
- The Rust Reference, method-call expressions — [[the-reference]], https://doc.rust-lang.org/reference/expressions/method-call-expr.html
