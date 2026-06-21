---
type: concept
title: "Macro Repetitions"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, macro-rules, repetitions]
domain: "Macros"
difficulty: intermediate
related: ["[[macro_rules!]]", "[[Declarative Macros]]", "[[Macro Fragment Specifiers]]", "[[Macro Hygiene]]", "[[Ambiguous macro_rules Matchers]]", "[[Function-like Macros]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/macros-by-example.html"]
rust_version: "edition 2024 / 1.85+"
---

# Macro Repetitions

Macro repetitions are `macro_rules!`'s variable-length matching form, written as `$(` tokens `)` plus `*`, `+`, or `?` and an optional separator.

## What it is
Repetitions let one macro arm accept lists, optional clauses, repeated fields, or repeated statements. The most common shape is `$( $x:expr ),*`, which means zero or more expressions separated by commas.

The repetition operators are:

- `*`: zero or more repetitions.
- `+`: one or more repetitions.
- `?`: zero or one repetition.

A separator token may appear between the repeated group and the operator, as in `),*` or `);+`. The separator is a single token other than a delimiter or repetition operator; `,` and `;` are the idiomatic choices. `?` cannot use a separator because it matches at most one occurrence.

## How it works
Metavariables captured inside a repetition become a sequence of matches. In the transcriber, the same repetition structure tells Rust how many times to emit the corresponding output.

The transcriber has strict shape rules. A metavariable must appear under the same number, kind, and nesting order of repetitions as it did in the matcher. Each transcriber repetition must contain at least one metavariable so the macro engine knows how many times to expand it.

When multiple metavariables appear in the same repetition layer, they must have the same length. This is useful for zipping two lists, but mismatched lengths become a macro error.

Repetition legality also interacts with follow-set rules. If `$( $e:expr )*` can repeat multiple times without a separator, then an expression would need to be able to follow another expression, which is not a legal macro grammar. Add a separator such as `,` or `;` unless the repeated fragment kind is allowed to self-follow.

## Example
```rust
macro_rules! count {
    () => {
        0usize
    };
    ($head:expr $(, $tail:expr)* $(,)?) => {
        1usize + count!($($tail),*)
    };
}

macro_rules! tuple_debug {
    ($( $value:expr ),+ $(,)?) => {{
        let mut out = String::new();
        $(
            if !out.is_empty() {
                out.push_str(", ");
            }
            out.push_str(&format!("{:?}", $value));
        )+
        out
    }};
}

fn main() {
    assert_eq!(count!(10, 20, 30), 3);
    assert_eq!(tuple_debug!("a", 3, true), "\"a\", 3, true");
}
```

## Worked example: zipping repeated captures
```rust
macro_rules! pairs {
    ($( $left:ident ),* ; $( $right:expr ),* $(,)?) => {
        [
            $(
                (stringify!($left), $right),
            )*
        ]
    };
}

fn main() {
    let values = pairs!(alpha, beta, gamma; 1, 2, 3);
    assert_eq!(values, [("alpha", 1), ("beta", 2), ("gamma", 3)]);
}
```

This macro relies on the rule that `$left` and `$right` have the same repetition length in the same transcription layer. If the caller supplies three identifiers and two expressions, the macro has no coherent way to zip them.

## Common errors
Two common diagnostics are:

```text
error: variable `x` is still repeating at this depth
error: meta-variable `left` repeats 3 times, but `right` repeats 2 times
```

The first means a repeated capture was used outside its repetition in the transcriber. Put it back under the matching `$()*`, or change the matcher to capture a single value. The second means same-layer metavariables have different lengths; redesign the input as paired groups like `$( $left:ident => $right:expr ),*` when unequal lists would be easy to write accidentally.

## Best practice
- ✅ Accept trailing commas with `$(,)?` for comma-separated lists.
- ✅ Use `+` when an empty invocation would be meaningless; use `*` only when zero inputs are valid.
- ✅ Keep nested repetitions shallow; complex nesting quickly becomes hard to debug.
- ✅ Put separators in the matcher, not inside the captured fragment, so errors point to the macro call syntax.
- ✅ Prefer helper arms for recursive cases when they make repetition expansion easier to reason about.
- ✅ Prefer paired repetitions (`$( key => value ),*`) over parallel lists when the items logically belong together.
- ✅ Ensure every transcriber repetition contains at least one metavariable so the macro engine can determine the expansion count.

## Pitfalls
- ⚠️ Do not move a repeated metavariable outside its repetition layer in the transcriber; that violates repetition shape rules.
- ⚠️ Do not put two metavariables in the same output repetition unless they were captured with matching lengths.
- ⚠️ Repetition follow-set rules still apply; a repeated `expr` must be separated or followed by tokens legal after an expression.
- ⚠️ Very broad repetition such as `$($t:tt)*` can hide malformed input until much later; see [[Ambiguous macro_rules Matchers]].
- ⚠️ `?` cannot have a separator because it matches at most one occurrence.
- ⚠️ Nested repetitions are legal, but errors become much harder to understand once two layers can both be empty.

## See also
[[Macros]] · [[macro_rules!]] · [[Declarative Macros]] · [[Macro Fragment Specifiers]] · [[Macro Hygiene]] · [[Function-like Macros]] · [[Ambiguous macro_rules Matchers]] · [[Iterator Adapters]]

## Sources
- The Rust Programming Language, ch. 20.5 "Declarative Macros with macro_rules! for General Metaprogramming" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Macros by example / Repetitions" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html
