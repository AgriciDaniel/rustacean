---
type: antipattern
title: "Ambiguous macro_rules Matchers"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, macro-rules, antipattern]
domain: "Macros"
difficulty: advanced
related: ["[[macro_rules!]]", "[[Declarative Macros]]", "[[Macro Fragment Specifiers]]", "[[Macro Repetitions]]", "[[Macro Hygiene]]", "[[Exporting macro_rules Macros]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/macros-by-example.html#transcribing", "https://doc.rust-lang.org/reference/macros-by-example.html#follow-set-ambiguity-restrictions"]
rust_version: "edition 2024 / 1.85+"
---

# Ambiguous macro_rules Matchers

Ambiguous `macro_rules!` matchers ask the macro parser to choose between token interpretations without lookahead or with illegal follow tokens; rewrite the grammar with separators, sentinels, or narrower arms.

## The mistake
A common macro footgun is writing a matcher that looks clear to a human but is ambiguous to Rust's macro parser. The parser does not freely look ahead to see which arm or metavariable would work best.

The classic shape is a repetition followed by another capture of the same kind, such as `$($i:ident)* $j:ident`. Given one identifier, the parser cannot decide whether it belongs to the repetition or to `$j`.

Another class is follow-set ambiguity: certain fragments may only be followed by tokens that Rust has committed to allowing after that fragment kind. For example, `expr` and `stmt` captures may be followed only by `=>`, `,`, or `;`.

## Why it happens
Macro matchers must remain stable as Rust syntax evolves. A token that cannot follow an expression today might become valid in a future edition or language version. Follow-set restrictions prevent macros from accepting syntax that would become ambiguous later.

The parser also matches one token at a time. It will not scan ahead arbitrarily to determine whether a later token disambiguates the grammar.

The correct alternative is to design macro input with explicit boundaries: commas, semicolons, keywords, arrows, or nested delimiters. If a part is optional, put a distinctive marker before it or split the macro into separate arms.

## Example
```rust
macro_rules! bind_last {
    (first $(, $middle:ident)* ; last $last:ident) => {{
        let mut names = Vec::new();
        names.push(stringify!(first));
        $(
            names.push(stringify!($middle));
        )*
        names.push(stringify!($last));
        names
    }};
}

fn main() {
    let names = bind_last!(first, second, third; last final_name);
    assert_eq!(names, ["first", "second", "third", "final_name"]);
}
```

The `; last` marker gives the parser a clear boundary between the repeated identifiers and the final identifier.

## Counterexample
```rust
macro_rules! labels {
    ($( $name:ident ),* ; $value:expr) => {
        ([$( stringify!($name) ),*], $value)
    };
}

fn main() {
    let (names, value) = labels!(alpha, beta; 42);
    assert_eq!(names, ["alpha", "beta"]);
    assert_eq!(value, 42);
}
```

The comma separates identifiers inside the repetition, and the semicolon separates the repeated region from the expression. This design gives every syntactic region a boundary the macro parser can recognize one token at a time.

## Common errors
The classic local ambiguity diagnostic looks like:

```text
error: local ambiguity when calling macro `ambiguity`: multiple parsing options
```

Follow-set violations often look like:

```text
error: `$e:expr` is followed by `[`, which is not allowed for `expr` fragments
```

Fix the first by adding a boundary token or splitting arms. Fix the second by using an allowed follow token (`=>`, `,`, or `;` for `expr`/`stmt`) or by making the uncertain syntax a delimited `tt` group that another arm parses explicitly.

## Best practice
- ✅ Put separators between repeated fragments and the next syntactic region.
- ✅ Use sentinel keywords like `where`, `as`, `=>`, or a domain-specific marker when two adjacent captures could overlap.
- ✅ Split truly different syntaxes into separate macro arms ordered from most specific to most general.
- ✅ Check the Reference follow-set rules before placing punctuation after `expr`, `stmt`, `pat`, `path`, `ty`, or `vis` captures.
- ✅ Prefer delimited subgroups for nested syntax, such as `fields { ... }` or `where { ... }`.
- ✅ Prefer `$( name: value ),*`-style paired repetition when two parallel lists would need equal lengths.
- ✅ Add negative compile-fail UI tests for public macro grammars if the macro accepts a nontrivial DSL.

## Pitfalls
- ⚠️ Do not write `$($i:ident)* $j:ident`; one identifier is enough to create local ambiguity.
- ⚠️ Do not place arbitrary tokens after `$e:expr`; use `,`, `;`, or `=>` unless the Reference says otherwise.
- ⚠️ Do not use `$($tokens:tt)*` to accept everything and then rely on generated Rust errors for validation.
- ⚠️ Do not expect later macro arms to rescue an arm that matched first and expanded badly.
- ⚠️ Optional regions are especially risky when both the optional region and the following region can start with the same fragment kind.
- ⚠️ Edition changes can widen fragments such as `expr` or `pat`; review macros during edition migration instead of accepting mechanical fixes blindly.

## See also
[[Macros]] · [[macro_rules!]] · [[Declarative Macros]] · [[Macro Fragment Specifiers]] · [[Macro Repetitions]] · [[Macro Hygiene]] · [[Exporting macro_rules Macros]] · [[Function-like Macros]]

## Sources
- The Rust Reference, "Macros by example / Transcribing" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html#transcribing
- The Rust Reference, "Follow-set ambiguity restrictions" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html#follow-set-ambiguity-restrictions
