---
type: concept
title: "Practice: Traits"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, traits]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Traits]]", "[[Default Implementations]]", "[[Trait Bounds]]", "[[The Display Trait]]", "[[The Debug Trait]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Traits

The traits group teaches shared behavior as an interface that types can implement. The key idea is to name required behavior once, then accept any type that implements that behavior.

## What it is
These exercises cover trait definitions, implementing traits for structs, default method bodies, trait bounds, and using trait methods through generic functions.

## How it works
A trait declares method signatures and optional default implementations. An `impl Trait for Type` block supplies the behavior for one concrete type. Generic code can require `T: Trait` to call trait methods.

## Example
```rust
trait Summary {
    fn summarize(&self) -> String;
}

struct Article {
    title: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("Article: {}", self.title)
    }
}

fn print_summary(item: &impl Summary) {
    println!("{}", item.summarize());
}

fn main() {
    print_summary(&Article { title: String::from("Rust") });
}
```

## Best practice
- ✅ Keep traits focused on coherent behavior.
- ✅ Use default methods only when the default is correct for most implementors.
- ✅ Choose trait bounds when static dispatch and type preservation are useful.

## Pitfalls
- ⚠️ Do not confuse a trait definition with an implementation.
- ⚠️ Methods from traits must be in scope or otherwise resolvable.
- ⚠️ Do not put unrelated methods into one large trait just for convenience.

## See also
[[Practice (Rustlings)]] · [[Traits]] · [[Default Implementations]] · [[Trait Bounds]] · [[The Display Trait]] · [[The Debug Trait]] · [[Blanket Implementations]]

## Sources
- Rustlings `15_traits` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings

