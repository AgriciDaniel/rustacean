---
type: concept
title: "Dynamically Sized Types"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, types, dst, sized, pointers]
domain: "Advanced Types & Features"
difficulty: advanced
related: ["[[Borrowing]]", "[[References]]", "[[Smart Pointers]]", "[[Trait Objects]]", "[[Type Aliases]]", "[[Advanced Types & Features]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-03-advanced-types.html#dynamically-sized-types-and-the-sized-trait", "https://doc.rust-lang.org/reference/dynamically-sized-types.html"]
rust_version: "edition 2024 / 1.85+"
---

# Dynamically Sized Types

Dynamically sized types are types whose exact size is known only at runtime, so Rust uses them behind pointers that carry the needed metadata.

## What it is
A dynamically sized type, often abbreviated DST or called an unsized type, cannot usually be held directly in a local variable or passed by value.
The canonical examples are `str`, slices such as `[T]`, and trait objects such as `dyn Display`.

The value `str` itself is not `&str`.
`str` is the unsized text data; `&str` is a sized fat pointer containing an address and a length.
Likewise, `[T]` is unsized; `&[T]` is sized because it stores a pointer and a length.
Trait objects are used as `&dyn Trait`, `Box<dyn Trait>`, `Rc<dyn Trait>`, and similar pointer forms because the pointer stores enough metadata to dispatch calls.

## How it works
Rust normally requires every variable, argument, and return value to have a statically known size.
Generic type parameters also have an implicit `T: Sized` bound.
You can relax that bound with `T: ?Sized`, but then you must take the value behind a pointer such as `&T`.

`?Sized` means "may or may not be `Sized`."
This syntax is special to `Sized`; it is not a general way to make arbitrary trait bounds optional.

Use DSTs through references or owning pointers.
Choose `&str` and `&[T]` for borrowed views, `Box<str>` or `Box<[T]>` for owned unsized data, and `Box<dyn Trait>` when you need owned dynamic dispatch.

Pointers to DSTs are sized because the pointer stores metadata.
For `str` and `[T]`, the metadata is a length.
For `dyn Trait`, the metadata is a vtable pointer that tells runtime dispatch which implementation to call.
That is why `&u8` is a thin pointer, while `&str`, `&[u8]`, and `&dyn Display` are often called fat pointers.

Structs may contain a DST only as their final field, which makes the struct itself unsized.
Most application code does not define custom DST structs, but this rule explains standard-library shapes such as slices and why unsized coercions happen at pointer boundaries.

## Example
```rust
use std::fmt::Display;

fn print_debug_name<T: ?Sized + Display>(value: &T) {
    println!("{value}");
}

fn main() {
    let text: &str = "hello";
    let numbers: &[i32] = &[1, 2, 3];
    let owned: Box<str> = String::from("owned text").into_boxed_str();

    print_debug_name(text);
    print_debug_name(&*owned);

    assert_eq!(numbers.len(), 3);
}
```

## More realistic example
```rust
use std::fmt::Display;

struct LogLine {
    target: String,
    message: Box<dyn Display + Send + Sync>,
}

impl LogLine {
    fn render(&self) -> String {
        format!("{}: {}", self.target, self.message)
    }
}

fn boxed_slice(values: Vec<u16>) -> Box<[u16]> {
    values.into_boxed_slice()
}

fn main() {
    let line = LogLine {
        target: String::from("auth"),
        message: Box::new("login accepted"),
    };
    assert_eq!(line.render(), "auth: login accepted");

    let ids = boxed_slice(vec![10, 20, 30]);
    assert_eq!(&ids[..], &[10, 20, 30]);
}
```

`LogLine` owns a dynamically dispatched display value, while `Box<[u16]>` owns a fixed-length slice allocation without `Vec` capacity.

## Common errors
```rust
fn main() {
    // let text: str = *"hello";
    // error[E0277]: the size for values of type `str` cannot be known at compilation time

    let text: &str = "hello";
    assert_eq!(text.len(), 5);
}
```

The fix is to use a pointer form such as `&str`, `Box<str>`, `&[T]`, `Box<[T]>`, `&dyn Trait`, or `Box<dyn Trait>`.

```rust
fn print_value<T: std::fmt::Display>(value: &T) {
    println!("{value}");
}

fn main() {
    let text: &str = "hello";
    // print_value(text);
    // error[E0277]: the size for values of type `str` cannot be known at compilation time
}
```

Here `T` is inferred as `str`, and the implicit `T: Sized` bound rejects it.
Change the bound to `T: ?Sized + Display` when the parameter is already behind a reference.

## Best practice
- ✅ Accept borrowed DST forms, especially `&str` and `&[T]`, in APIs that only need to read data.
- ✅ Use `T: ?Sized` only when the generic function actually takes `T` behind a pointer.
- ✅ Reach for `Box<dyn Trait>` or `&dyn Trait` when heterogeneity and dynamic dispatch matter more than static dispatch.
- ✅ Keep ownership explicit: `String` owns growable text, `&str` borrows text, and `Box<str>` owns a fixed unsized string allocation.
- ✅ Prefer `AsRef<str>` or `AsRef<[T]>` only when accepting many owned/borrowed input forms is more important than the simplest signature.
- ✅ Use `size_of_val` when you need the runtime size of a DST value through a reference.

## Pitfalls
- ⚠️ Do not try to write local variables of type `str` or `[T]`; use pointer forms such as `&str`, `&[T]`, `Box<str>`, or `Box<[T]>`.
- ⚠️ Avoid adding `?Sized` to every generic parameter; it complicates signatures and disables by-value use of `T`.
- ⚠️ Remember that a trait name by itself is not a concrete value type for storage; use `dyn Trait` behind a pointer. See [[Trait Objects]].
- ⚠️ Do not hide dynamic dispatch behind an alias unless the API docs make the `dyn` cost and object-safety requirements clear.
- ⚠️ Custom DST structs are advanced and rarely needed; prefer standard pointers and containers unless you are designing a low-level abstraction.

## See also
[[Borrowing]] · [[References]] · [[Smart Pointers]] · [[Trait Objects]] · [[Type Aliases]] · [[Returning Closures]] · [[Boxed Closure Returns]] · [[Slices]] · [[Advanced Types & Features]]

## Sources
- The Rust Programming Language, ch. 20.3 "Dynamically Sized Types and the Sized Trait" — [[the-book]], https://doc.rust-lang.org/book/ch20-03-advanced-types.html#dynamically-sized-types-and-the-sized-trait
- The Rust Reference, "Dynamically sized types" — [[the-reference]], https://doc.rust-lang.org/reference/dynamically-sized-types.html
