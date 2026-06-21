---
type: concept
title: "Tuples"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, tuples, compound-types, unit]
domain: "Basic Concepts & Syntax"
difficulty: basic
related: ["[[Arrays]]", "[[Statements vs Expressions]]", "[[Pattern Matching]]", "[[Functions]]", "[[Scalar Types]]", "[[Basic Concepts & Syntax]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch03-02-data-types.html#the-tuple-type", "https://doc.rust-lang.org/reference/types/tuple.html", "https://doc.rust-lang.org/reference/expressions/tuple-expr.html"]
rust_version: "edition 2024 / 1.85+"
---

# Tuples

A tuple groups a fixed number of values, possibly of different types, into one structural value accessed by destructuring or numeric fields.

## What it is
Tuples are primitive compound types for heterogeneous fixed-size data. The type `(i32, f64, u8)` has three fields with three different types.

Tuple fields are named by position: `.0`, `.1`, `.2`, and so on. Tuple indexing uses decimal field numbers, not square brackets.

The empty tuple `()` is the unit type and unit value. It appears whenever an expression or function has no meaningful value to return.

## How it works
Tuple types are structural: two tuple types are the same if they have the same arity and element types in the same order. `(i32, String)` and `(String, i32)` are different types.

A one-element tuple requires a trailing comma, such as `(i32,)`, because `(i32)` is just a parenthesized type. The same applies to values: `(value,)` is a one-element tuple, while `(value)` is just `value`.

Use pattern matching to destructure a tuple when names make later code clearer. Use `.0` style access when there are only a couple of obvious fields or when destructuring would be noisier.

## Example
```rust
fn main() {
    let measurement: (&str, f64, char) = ("height", 1.82, 'm');
    let (name, value, unit) = measurement;

    assert_eq!(name, "height");
    assert_eq!(measurement.1, value);
    assert_eq!(unit, 'm');

    let one_item = ("only",);
    assert_eq!(one_item.0, "only");
}
```

## Common errors
A one-element tuple needs a trailing comma:

```rust
fn main() {
    let not_a_tuple = ("only");
    // assert_eq!(not_a_tuple.0, "only");
}
```

Typical diagnostic:

```text
error[E0609]: no field `0` on type `&str`
```

Fix it with `let one_item = ("only",);`.

## Best practice
- ✅ Use tuples for small, local groupings where field names would add little.
- ✅ Destructure tuples at boundaries where positional meaning should become named local variables.
- ✅ Use `()` intentionally for "no value" return types and ignored results.
- ✅ Promote recurring tuple shapes to [[Structs]] when fields need names or domain meaning.

## Pitfalls
- ⚠️ Large tuples become unreadable because field meaning is only positional.
- ⚠️ Forgetting the comma in a one-element tuple changes the type entirely.
- ⚠️ Using tuple field numbers in public APIs can make callers memorize order; prefer [[Structs]].
- ⚠️ Confusing tuple indexing `.0` with array indexing `[0]`; see [[Arrays]].

## See also
[[Arrays]] · [[Pattern Matching]] · [[Statements vs Expressions]] · [[Functions]] · [[Structs]] · [[Scalar Types]] · [[Type Inference]] · [[Private Fields with Public Constructors]] · [[Basic Concepts & Syntax]]

## Sources
- The Rust Programming Language, ch. 3.2 "The Tuple Type" — [[the-book]], https://doc.rust-lang.org/book/ch03-02-data-types.html#the-tuple-type
- The Rust Reference, "Tuple types" — [[the-reference]], https://doc.rust-lang.org/reference/types/tuple.html
- The Rust Reference, "Tuple expressions" — [[the-reference]], https://doc.rust-lang.org/reference/expressions/tuple-expr.html
