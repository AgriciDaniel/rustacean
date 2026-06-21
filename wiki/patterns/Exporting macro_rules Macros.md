---
type: pattern
title: "Exporting macro_rules Macros"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, macro-rules, exports]
domain: "Macros"
difficulty: advanced
related: ["[[macro_rules!]]", "[[Declarative Macros]]", "[[Macro Hygiene]]", "[[Macro Fragment Specifiers]]", "[[Macro Repetitions]]", "[[Ambiguous macro_rules Matchers]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-05-macros.html", "https://doc.rust-lang.org/reference/macros-by-example.html#scoping-exporting-and-importing", "https://doc.rust-lang.org/reference/macros-by-example.html#the-macro_export-attribute"]
rust_version: "edition 2024 / 1.85+"
---

# Exporting macro_rules Macros

Export `macro_rules!` macros with path-based names and `$crate` helper paths so downstream callers can import one stable macro without importing its internals.

## What it is
Local `macro_rules!` macros use textual scope by default. That is fine inside one module, but public library macros need path-based resolution so callers can write `your_crate::some_macro!()` or `use your_crate::some_macro;`.

There are two common tools:

- `#[macro_export]` exports a `macro_rules!` macro from the crate root with public path-based visibility.
- `pub(crate) use m;` or `pub use m;` can re-export a macro from within its textual scope, giving it path-based scope from the chosen module.

For public cross-crate macros, `#[macro_export]` is the traditional mechanism. For crate-internal module APIs, a `pub(crate) use` re-export is often cleaner because it avoids placing the macro in the crate root.

## How it works
Exported macros often need helper macros or helper functions. A helper name like `helper!()` is looked up from the invocation context and may not be in scope for downstream users. Use `$crate::helper!()` for helper macros and `$crate::module::function()` for helper items.

`$crate` refers to the defining crate. It does not make private items public. Any non-macro item referenced through `$crate` must still be visible from the invocation site when invoked externally.

The old `#[macro_export(local_inner_macros)]` option automatically prefixes inner macro calls with `$crate::`, but the Reference discourages it for new code. Write `$crate::` explicitly.

Path-based macro imports are the normal Rust 2018+ style: users can write `use your_crate::macro_name;` and then invoke `macro_name!(...)`. Unqualified macro lookup still checks textual scope first, so qualified calls like `your_crate::macro_name!(...)` are the least ambiguous in examples and docs.

## Example
```rust
mod macros {
    macro_rules! trace_value {
        ($value:expr) => {{
            let value = $value;
            eprintln!("{} = {:?}", stringify!($value), value);
            value
        }};
    }

    pub(crate) use trace_value;
}

fn main() {
    let answer = macros::trace_value!(40 + 2);
    assert_eq!(answer, 42);
}
```

## Worked example: exported helper macro
```rust
#[macro_export]
macro_rules! __say_prefix {
    () => {
        "note"
    };
}

#[macro_export]
macro_rules! say_note {
    ($message:expr $(,)?) => {{
        format!("{}: {}", $crate::__say_prefix!(), $message)
    }};
}

fn main() {
    assert_eq!(say_note!("hello"), "note: hello");
}
```

The helper macro is intentionally named as an internal implementation detail and called through `$crate`. In a published crate, document only `say_note!` unless callers are meant to use the helper directly.

## Common errors
Without `$crate`, downstream users see helper lookup failures:

```text
error: cannot find macro `helper` in this scope
```

With `$crate` pointing at a private helper function, they instead see a privacy error. Fix macro helpers with `$crate::helper!()`; fix non-macro helpers by exposing a documented public path or avoiding the helper in cross-crate expansion.

## Best practice
- ✅ Prefer path-based imports in Rust 2018+ style: `use crate_name::macro_name; macro_name!(...)`.
- ✅ Use `$crate::` for helper macros and helper items referenced by exported macros.
- ✅ Keep helper macros private unless callers are meant to invoke them directly.
- ✅ Integration-test public macros from a downstream crate perspective.
- ✅ Use module re-exports for crate-local macro APIs when root export would be too broad.
- ✅ Name hidden exported helper macros with a clear internal prefix if `#[macro_export]` forces them into the crate root.
- ✅ Include doctests that call the macro through the public path, not only from the defining module.

## Pitfalls
- ⚠️ `#[macro_export]` exports the macro from the crate root, even if the definition appears in an inner module.
- ⚠️ `#[macro_use] extern crate ...` imports macros into a macro-use prelude and has conflict behavior you should not rely on for new code.
- ⚠️ `$crate` fixes lookup but not visibility; external expansions cannot call private helper functions.
- ⚠️ Textual macro definitions can shadow path-based macro imports; qualify macro paths when ambiguity matters.
- ⚠️ Re-exporting a crate-private macro as `pub use` outside the crate is rejected because non-`#[macro_export]` macros are implicitly `pub(crate)`.
- ⚠️ Changing the crate-root exported macro name is a public API break even if the macro was defined in a private module.

## See also
[[Macros]] · [[macro_rules!]] · [[Declarative Macros]] · [[Macro Hygiene]] · [[Macro Fragment Specifiers]] · [[Macro Repetitions]] · [[Ambiguous macro_rules Matchers]] · [[Modules]]

## Sources
- The Rust Programming Language, ch. 20.5 "Declarative Macros with macro_rules! for General Metaprogramming" — [[the-book]], https://doc.rust-lang.org/book/ch20-05-macros.html
- The Rust Reference, "Scoping, exporting, and importing" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html#scoping-exporting-and-importing
- The Rust Reference, "`macro_export` attribute" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html#the-macro_export-attribute
