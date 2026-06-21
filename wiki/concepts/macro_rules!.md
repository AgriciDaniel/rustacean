---
type: concept
title: "macro_rules!"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, macro-rules, declarative-macros]
domain: "Macros"
difficulty: intermediate
related: ["[[Declarative Macros]]", "[[Macro Fragment Specifiers]]", "[[Macro Repetitions]]", "[[Macro Hygiene]]", "[[Exporting macro_rules Macros]]", "[[Ambiguous macro_rules Matchers]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/macros-by-example.html"]
rust_version: "edition 2024 / 1.85+"
---

# macro_rules!

`macro_rules!` is the built-in construct for defining declarative macros from ordered matcher/transcriber rules.

## What it is
`macro_rules! name { ... }` defines a named macro. The name is written without `!` in the definition and with `!` at invocation sites.

Each arm describes one accepted token shape and the code emitted for that shape. The macro system binds metavariables in the matcher and substitutes them in the transcriber. This is why the system is often described as "macros by example": the left side is an example of accepted syntax, and the right side is the template for generated syntax.

The definition itself is an item-like construct with macro-specific scoping rules. By default it is textually scoped from the point of definition onward; it does not behave exactly like ordinary functions or modules.

## How it works
The matcher and transcriber must both be delimited. The outer delimiter in the matcher is flexible: a matcher written with `()` can match an invocation using `{}` or `[]` at that outer level. Inner delimiters still matter.

Common matcher pieces:

- Literal tokens, such as `=>`, `,`, or a keyword.
- Metavariables, such as `$name:ident`, `$value:expr`, and `$ty:ty`.
- Repetitions, such as `$( $value:expr ),*`.

Rules are tried in source order. Put special cases before general cases. If one arm matches but expands to invalid Rust, later arms are not considered.

Edition 2024 matters for `expr`: in macros defined in the 2024 edition, `expr` can match top-level underscore expressions and const block expressions. Use `expr_2021` only when you intentionally need the pre-2024 matcher behavior.

Edition is attached to the macro definition, not the call site. A 2024 crate defining `macro_rules!` gets 2024 fragment behavior even when called by an older-edition dependent crate, and an older macro keeps its older fragment behavior until the defining crate migrates.

## Example
```rust
macro_rules! hashmap {
    ($( $key:expr => $value:expr ),* $(,)?) => {{
        let mut map = ::std::collections::HashMap::new();
        $(
            map.insert($key, $value);
        )*
        map
    }};
}

fn main() {
    let numbers = hashmap! {
        "one" => 1,
        "two" => 2,
    };

    assert_eq!(numbers.get("two"), Some(&2));
}
```

## Worked example: mode-specific arms
```rust
macro_rules! ensure {
    ($condition:expr $(,)?) => {
        assert!($condition);
    };
    ($condition:expr, $message:literal $(, $arg:expr)* $(,)?) => {
        assert!($condition, $message $(, $arg)*);
    };
}

fn main() {
    let port = 8080;

    ensure!(port > 0);
    ensure!(port < 9000, "port out of test range: {port}");
}
```

Separate arms make the accepted forms explicit. The more structured arm with a literal message is placed after the simpler condition arm because the comma distinguishes the two forms.

## Common errors
Missing fragment specifiers are errors in current Rust:

```text
error: missing fragment specifier
```

Write `$name:ident`, `$value:expr`, `$ty:ty`, or another explicit fragment instead of plain `$name`. Another frequent message is:

```text
error: no rules expected this token in macro call
```

That usually means the invocation does not match any arm, a fragment cannot be followed by that punctuation, or an earlier arm consumed the input shape you intended for a later arm.

## Best practice
- ✅ Put the generated expression in an extra block (`{{ ... }}`) when you need local temporaries.
- ✅ Accept a trailing comma with `$(,)?` for list-like macros.
- ✅ Use absolute paths like `::std::collections::HashMap` in reusable macros so caller imports do not decide your helper names.
- ✅ Put narrow arms before catch-all arms.
- ✅ Treat the macro invocation syntax as an API; changing accepted tokens is a breaking change for downstream users.
- ✅ Choose fragment specifiers based on caller syntax, not generated code; `$path:path` and `$ty:ty` communicate different accepted input.
- ✅ Test macros through the same path users will call, especially when `#[macro_export]`, `$crate`, or re-exports are involved.

## Pitfalls
- ⚠️ Do not assume a macro can be called before its local `macro_rules!` definition; textual scope starts after the definition.
- ⚠️ Do not forward an `$x:expr` to another macro and expect the next macro to match literal tokens inside that expression; forwarded non-`tt` fragments are opaque.
- ⚠️ Do not depend on `local_inner_macros` in new code; prefer explicit `$crate::helper!()` as described in [[Exporting macro_rules Macros]].
- ⚠️ Avoid ambiguous repetition shapes such as `$($i:ident)* $j:ident`; see [[Ambiguous macro_rules Matchers]].
- ⚠️ Do not use `expr_2021` reflexively in new 2024 macros; it is for compatibility when the old matching behavior is required.
- ⚠️ Do not generate multiple statements without wrapping when the macro is intended to behave like one expression.

## See also
[[Macros]] · [[Declarative Macros]] · [[Macro Fragment Specifiers]] · [[Macro Repetitions]] · [[Macro Hygiene]] · [[Function-like Macros]] · [[Exporting macro_rules Macros]] · [[Ambiguous macro_rules Matchers]]

## Sources
- The Rust Programming Language, ch. 20.5 "Declarative Macros with macro_rules! for General Metaprogramming" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Macros by example" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html
