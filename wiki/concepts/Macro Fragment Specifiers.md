---
type: concept
title: "Macro Fragment Specifiers"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, macro-rules, fragments]
domain: "Macros"
difficulty: intermediate
related: ["[[macro_rules!]]", "[[Declarative Macros]]", "[[Macro Repetitions]]", "[[Macro Hygiene]]", "[[Ambiguous macro_rules Matchers]]", "[[Function-like Macros]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/macros-by-example.html"]
rust_version: "edition 2024 / 1.85+"
---

# Macro Fragment Specifiers

Macro fragment specifiers tell `macro_rules!` which kind of Rust syntax a metavariable may capture, such as an expression, type, item, identifier, or token tree.

## What it is
In a matcher, `$name:fragment` binds a fragment of Rust syntax to `$name`. The fragment specifier is not a type annotation; it is a parser category used by the macro matcher.

Common fragment specifiers include `expr`, `ident`, `ty`, `path`, `item`, `pat`, `stmt`, `literal`, `meta`, `vis`, and `tt`. The choice controls both what the caller may write and what tokens may legally follow the capture.

`tt` is the most flexible fragment because it captures a single token tree: either one token or a delimited group. It is often used for forwarding input to another macro, but it gives up the parser guidance and diagnostics of a more specific fragment.

## How it works
The macro matcher parses one token at a time with no arbitrary lookahead. A fragment such as `$value:expr` consumes a full expression according to Rust's grammar, then the next token must be legal after an `expr` fragment. For example, `,`, `;`, and `=>` are valid follow tokens for `expr`.

Forwarding has an important rule: when a fragment other than `ident`, `lifetime`, or `tt` is passed to another `macro_rules!` macro, the receiving macro sees an opaque syntax fragment. It cannot match literal tokens inside that fragment. If you need the next macro to inspect token-by-token syntax, capture and forward `tt` instead.

Edition 2024 changed `expr` matching for macros defined in that edition. Top-level `_` and `const { ... }` expressions are included in `expr`; `expr_2021` exists for compatibility with the old behavior.

The edition that matters is the edition of the crate where the macro is defined. A downstream crate's edition does not change how that macro's `expr` or `pat` fragments are parsed.

## Example
```rust
macro_rules! newtype {
    ($(#[$meta:meta])* $vis:vis struct $name:ident($inner:ty);) => {
        $(#[$meta])*
        $vis struct $name($inner);

        impl $name {
            $vis fn new(value: $inner) -> Self {
                Self(value)
            }

            $vis fn get(&self) -> &$inner {
                &self.0
            }
        }
    };
}

newtype! {
    #[derive(Debug, PartialEq)]
    pub struct UserId(u64);
}

fn main() {
    let id = UserId::new(7);
    assert_eq!(*id.get(), 7);
}
```

## Worked example: choosing `pat` vs `pat_param`
```rust
macro_rules! match_any {
    ($value:expr, $( $pattern:pat_param )|+ => $body:expr, _ => $fallback:expr $(,)?) => {
        match $value {
            $( $pattern )|+ => $body,
            _ => $fallback,
        }
    };
}

fn main() {
    let value = 2;
    let label = match_any!(value, 1 | 2 | 3 => "small", _ => "other");
    assert_eq!(label, "small");
}
```

`pat_param` is useful when the macro grammar itself uses `|` as a separator between pattern captures. In a 2024 macro, plain `pat` can match a top-level or-pattern, so it cannot be followed by a literal `|` in the same way.

## Common errors
Using a metavariable without a fragment specifier is rejected:

```text
error: missing fragment specifier
```

Fix it by writing the fragment explicitly, such as `$name:ident` or `$input:tt`. For illegal follow tokens, the compiler reports that the fragment is followed by a token it does not allow; change the grammar to use a legal separator like `,`, `;`, or `=>`, or capture a delimited `tt` group and parse it in another arm.

## Best practice
- ✅ Use the narrowest fragment that describes the API: `ident` for names, `ty` for types, `expr` for expressions, `meta` for attribute contents.
- ✅ Use `tt` when forwarding to another macro that needs to match literal tokens inside the input.
- ✅ Remember that `vis` may match an empty visibility; design surrounding tokens so that empty visibility is unambiguous.
- ✅ Use `expr_2021` only for compatibility-sensitive macros that must preserve pre-2024 matching.
- ✅ Use `pat_param` when your macro grammar places a literal `|` after a pattern capture.
- ✅ Put a marker token after an optional `vis` capture, such as `$vis:vis struct $name:ident`, so empty visibility cannot blur into the next capture.

## Pitfalls
- ⚠️ Do not overuse `$($tokens:tt)*` as a parser substitute; it hides errors until the generated code is compiled.
- ⚠️ Do not expect `$e:expr` to be followed by arbitrary punctuation; follow-set restrictions reject future-ambiguous grammar.
- ⚠️ Do not forward `$e:expr` and then try to match `(3)` literally in the next macro; use `tt` forwarding for that case.
- ⚠️ Pattern fragments changed across editions; verify whether you need `pat` or `pat_param`.
- ⚠️ `literal` matches a literal expression, including an optional leading `-`; it is not a general constant-expression parser.
- ⚠️ `ident` can match keywords accepted by the grammar in identifier positions, but it does not match `_`.

## See also
[[Macros]] · [[macro_rules!]] · [[Declarative Macros]] · [[Macro Repetitions]] · [[Macro Hygiene]] · [[Function-like Macros]] · [[Ambiguous macro_rules Matchers]] · [[Newtype Pattern]]

## Sources
- The Rust Reference, "Macros by example / Metavariables" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html
