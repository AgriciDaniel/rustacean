---
type: concept
title: "Declarative Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, declarative-macros, metaprogramming]
domain: "Macros"
difficulty: intermediate
related: ["[[macro_rules!]]", "[[Macro Fragment Specifiers]]", "[[Macro Repetitions]]", "[[Macro Hygiene]]", "[[Exporting macro_rules Macros]]", "[[Ambiguous macro_rules Matchers]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/macros-by-example.html"]
rust_version: "edition 2024 / 1.85+"
---

# Declarative Macros

Declarative macros are Rust's pattern-based syntax extensions: they match token structure at compile time and transcribe the match into Rust code.

## What it is
Declarative macros are also called macros by example or `macro_rules!` macros. They are the everyday macro system behind examples such as `vec!`, `println!`, and many small project-local syntax helpers.

Unlike a function, a declarative macro receives Rust tokens before type checking and can expand to expressions, statements, items, types, or patterns. That makes it useful when the input shape is not a fixed function signature: variable argument counts, repeated fields, generated impl blocks, or concise domain-specific syntax.

The key limitation is that a declarative macro does not run arbitrary Rust code over a parsed syntax tree. It matches with grammar fragments such as `expr`, `ident`, `ty`, and `tt`; for semantic parsing or complex validation, use [[Procedural Macros]] or ordinary functions.

## How it works
A declarative macro is a list of rules. Each rule has a matcher on the left and a transcriber on the right:

`(matcher) => { transcriber }`

At invocation time, the macro expander looks up the macro name and tries rules in order. The first rule whose matcher succeeds is transcribed. If that rule's transcription later produces an error, Rust does not backtrack to try later rules.

Matchers work on token trees, not runtime values. Literal tokens in the matcher must appear in the invocation; metavariables such as `$value:expr` capture fragments of Rust syntax; repetitions such as `$(...),*` capture variable-length lists.

Because expansion happens before type checking, a declarative macro can generate code that introduces items, impls, or patterns. It cannot inspect inferred types or ask whether a trait bound holds.

The macro parser does not parse the entire invocation with arbitrary lookahead. It consumes tokens according to the current matcher, fragment follow-set rules, and repetition boundaries. That is why separators are part of the macro's public grammar rather than cosmetic punctuation.

## Example
```rust
macro_rules! make_getter {
    ($field:ident, $ty:ty) => {
        fn $field(&self) -> &$ty {
            &self.$field
        }
    };
}

struct User {
    name: String,
}

impl User {
    make_getter!(name, String);
}

fn main() {
    let user = User {
        name: String::from("Ferris"),
    };

    assert_eq!(user.name(), "Ferris");
}
```

## Worked example: repeated item generation
```rust
macro_rules! define_flags {
    ($( $name:ident = $value:expr ),+ $(,)?) => {
        $(
            pub const $name: u32 = 1 << $value;
        )+
    };
}

mod permissions {
    define_flags! {
        READ = 0,
        WRITE = 1,
        EXECUTE = 2,
    }
}

fn main() {
    let mask = permissions::READ | permissions::WRITE;
    assert_eq!(mask, 0b011);
}
```

This is where a declarative macro is stronger than a function: the output is items (`pub const` declarations), not a runtime value. A function could compute a bitmask, but it could not introduce several named constants into the module.

## Common errors
The typical failure mode is a matcher that is too broad or too loose:

```text
error: no rules expected this token in macro call
```

Fix the macro by matching the delimiter or separator you actually require, or add a more specific arm before a catch-all `$( $tokens:tt )*` arm. If the compiler says `local ambiguity`, the fix is not a type annotation; it is a clearer token grammar, usually a comma, semicolon, keyword marker, or nested delimiter. See [[Ambiguous macro_rules Matchers]].

## Best practice
- ✅ Reach for declarative macros when the problem is token-shape repetition, not runtime behavior.
- ✅ Keep each macro arm small and make the accepted syntax obvious at the call site.
- ✅ Prefer typed functions after expansion has produced normal Rust values; macros should usually be a thin syntax layer.
- ✅ Use precise fragment specifiers from [[Macro Fragment Specifiers]] so callers get useful parse errors.
- ✅ Put exported macros behind stable paths using [[Exporting macro_rules Macros]] when they are part of a public API.
- ✅ Add doctests for public macros with representative invocations, including trailing commas and empty-list cases when those are supported.
- ✅ Keep macro-generated identifiers and helper paths deliberate; even declarative macros have only mixed-site hygiene.

## Pitfalls
- ⚠️ Do not use a macro where a generic function, trait method, or iterator adapter is clearer; macro errors are harder to read than normal type errors.
- ⚠️ Rule order matters: a broad `$($tokens:tt)*` arm before a specific arm can swallow all invocations.
- ⚠️ Local names and helper paths have special lookup rules; see [[Macro Hygiene]] before exporting macros.
- ⚠️ Ambiguous matchers fail during parsing even if a human can tell what was intended; see [[Ambiguous macro_rules Matchers]].
- ⚠️ Do not expect a macro to know the type of `$value:expr`; expansion happens before type checking.
- ⚠️ Do not depend on exact expansion text as a public guarantee unless you document it; downstream code should rely on the macro's accepted syntax and semantic output.

## See also
[[Macros]] · [[macro_rules!]] · [[Macro Fragment Specifiers]] · [[Macro Repetitions]] · [[Macro Hygiene]] · [[Procedural Macros]] · [[Function-like Macros]] · [[Exporting macro_rules Macros]] · [[Ambiguous macro_rules Matchers]]

## Sources
- The Rust Programming Language, ch. 20.5 "Macros" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Macros by example" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html
