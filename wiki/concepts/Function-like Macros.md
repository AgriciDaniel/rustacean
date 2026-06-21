---
type: concept
title: "Function-like Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, function-like-macros, procedural-macros]
domain: "Macros"
difficulty: intermediate
related: ["[[Declarative Macros]]", "[[macro_rules!]]", "[[Procedural Macros]]", "[[Derive Macros]]", "[[Attribute Macros]]", "[[Macro Fragment Specifiers]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/macros.html", "https://doc.rust-lang.org/reference/procedural-macros.html#the-proc_macro-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Function-like Macros

Function-like macros are invoked with `name!(...)`, `name![...]`, or `name!{...}` and expand at compile time instead of being called at runtime.

## What it is
"Function-like" describes the call syntax, not one implementation mechanism. A function-like macro can be a `macro_rules!` macro, a built-in macro, or a function-like procedural macro defined with `#[proc_macro]`.

They differ from functions in three important ways:

- They receive tokens, not already-typed values.
- They may accept input shapes that are impossible for a Rust function signature.
- They may expand to items, patterns, types, statements, or expressions depending on where they are invoked.

This is why `println!` can accept a format string plus a variable number of arguments, and why a procedural `sql!` macro can parse a domain-specific language inside the invocation.

## How it works
A macro invocation has a path, `!`, and a delimited token tree. For item or statement positions, semicolon rules depend on the delimiter: `name!(...)` and `name![...]` usually need a semicolon when used as statements or items, while `name!{...}` is the item-like form without a required trailing semicolon.

For a function-like procedural macro, the compiler passes the tokens inside the delimiters as one `TokenStream` argument. The output `TokenStream` replaces the entire invocation.

For a `macro_rules!` function-like macro, the same invocation syntax is resolved through declarative macro lookup and matched against macro arms.

The macro's expansion kind must fit the syntactic position where it is invoked. A macro that expands to an expression can be used where an expression is allowed; a macro that expands to items belongs in item position; a pattern expansion belongs in pattern position.

## Example
```rust
macro_rules! max_value {
    ($single:expr) => {
        $single
    };
    ($first:expr, $($rest:expr),+ $(,)?) => {{
        let candidate = max_value!($($rest),+);
        if $first > candidate {
            $first
        } else {
            candidate
        }
    }};
}

fn main() {
    let largest = max_value!(3, 9, 4, 7);
    assert_eq!(largest, 9);
}
```

## Worked example: avoid duplicated evaluation
```rust
macro_rules! clamp_once {
    ($value:expr, $min:expr, $max:expr $(,)?) => {{
        let value = $value;
        let min = $min;
        let max = $max;

        if value < min {
            min
        } else if value > max {
            max
        } else {
            value
        }
    }};
}

fn main() {
    let mut calls = 0;
    let value = clamp_once!({
        calls += 1;
        10
    }, 0, 5);

    assert_eq!(value, 5);
    assert_eq!(calls, 1);
}
```

Function-like syntax can make a macro look like a function, but arguments are tokens. Binding `$value`, `$min`, and `$max` into locals ensures each expression is evaluated once.

## Common errors
When an expansion kind does not fit the call site, the compiler may report:

```text
error: macro expansion ignores token `{` and any following
```

or a parse error near the invocation. Fix it by documenting and enforcing the intended position, or by making the macro expand to a block expression when it is meant to be expression-like.

## Best practice
- ✅ Use function-like syntax when the macro acts like an expression-producing operation at the call site.
- ✅ Choose delimiters to match convention: `!()` for expression-like calls, `![]` for collection-like literals, and `!{}` for item-like expansions.
- ✅ Keep macro inputs readable; a macro that starts to need a large grammar may belong in [[Procedural Macros]].
- ✅ Prefer functions once the inputs are ordinary typed values.
- ✅ Document what syntactic positions the macro supports.
- ✅ Bind expression inputs to temporaries when the macro would otherwise evaluate them more than once.
- ✅ Use `stringify!`, `concat!`, and other built-in macros deliberately when compile-time token text is part of the API.

## Pitfalls
- ⚠️ Do not assume a function-like macro evaluates arguments like a function; it expands tokens and may duplicate expressions.
- ⚠️ A macro can accept syntax that is not valid as a Rust expression until after expansion, so diagnostics may point inside generated code.
- ⚠️ Function-like procedural macros are unhygienic like other procedural macros; see [[Unhygienic Procedural Macro Output]].
- ⚠️ Avoid surprising delimiter-sensitive semicolon behavior in item or statement position.
- ⚠️ Do not hide control-flow effects such as `return`, `break`, or `?` inside expression-looking macros unless the macro name and docs make that behavior explicit.
- ⚠️ Do not use a procedural function-like macro for simple repetition that `macro_rules!` can express more transparently.

## See also
[[Macros]] · [[Declarative Macros]] · [[macro_rules!]] · [[Procedural Macros]] · [[Derive Macros]] · [[Attribute Macros]] · [[Macro Repetitions]] · [[Macro Fragment Specifiers]]

## Sources
- The Rust Programming Language, ch. 20.5 "Function-like Macros" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Macro invocation" — [[the-reference]], https://doc.rust-lang.org/reference/macros.html
- The Rust Reference, "`proc_macro` attribute" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html#the-proc_macro-attribute
