---
type: antipattern
title: "Unhygienic Procedural Macro Output"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, procedural-macros, hygiene, antipattern]
domain: "Macros"
difficulty: advanced
related: ["[[Procedural Macros]]", "[[Macro Hygiene]]", "[[Derive Macros]]", "[[Attribute Macros]]", "[[Function-like Macros]]", "[[Exporting macro_rules Macros]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/procedural-macros.html#procedural-macro-hygiene"]
rust_version: "edition 2024 / 1.85+"
---

# Unhygienic Procedural Macro Output

Unhygienic procedural macro output emits names as if the caller had written them inline, so unqualified paths and ordinary helper names can be captured or collide.

## The mistake
Procedural macro authors often generate code like `Option<T>`, `Result<T, E>`, `helper()`, or `mod generated` assuming those names mean what they meant in the macro crate. They do not.

Procedural macros operate on tokens and their output is resolved in the caller's context. If the caller has a local `Option`, a conflicting module, unusual imports, or an item with the same helper name, the expansion may fail or mean something else.

This is different from many people's intuition after using `macro_rules!`, where local variables and labels have mixed-site hygiene. Procedural macros require explicit defensive naming.

## Why it happens
The Reference describes procedural macros as unhygienic. The output token stream behaves as though it were written inline next to the invocation. That makes procedural macros flexible, but it means the macro author must manage names and paths carefully.

The correct alternative is to generate absolute paths for known library items, use the runtime crate's exported paths for runtime helpers, and avoid injecting generic helper names into caller modules. When helpers must be generated, choose names that are reserved by convention for the macro's expansion and scope them as tightly as possible.

When reporting errors, prefer output that points to caller spans and says what input is unsupported. Do not let a captured name produce a confusing downstream type error if you can detect the problem earlier.

## Example
```rust
mod generated_support {
    pub fn is_some<T>(value: &::std::option::Option<T>) -> bool {
        value.is_some()
    }
}

fn main() {
    struct Option;

    let value = ::std::option::Option::Some(42);
    assert!(generated_support::is_some(&value));

    let _local_name_that_would_confuse_unqualified_output = Option;
}
```

This ordinary Rust example shows the defensive style procedural macro output should use: absolute paths such as `::std::option::Option` do not depend on caller-local names.

## Counterexample: shadowed standard names
```rust
fn main() {
    struct Result;

    let ok: ::std::result::Result<i32, &'static str> = Ok(3);
    assert_eq!(ok.unwrap(), 3);

    let _shadow = Result;
}
```

If generated procedural macro output had emitted `Result<i32, E>` in this module, it would have resolved to the local unit struct name and failed. Emitting `::std::result::Result<i32, E>` or `::core::result::Result<i32, E>` avoids that capture.

## Common errors
Callers often see name-resolution or type errors far from the real macro bug:

```text
error[E0573]: expected type, found struct `Result`
error[E0425]: cannot find function `helper` in this scope
```

Fix the macro output, not the caller. Qualify standard-library names, route helper calls through public runtime-crate paths, and generate helper identifiers that cannot collide with ordinary user items.

## Best practice
- ✅ Generate absolute paths for standard library items, such as `::std::option::Option` or `::core::result::Result`.
- ✅ Route runtime helper calls through documented public paths in your runtime crate.
- ✅ Keep generated helper items private when possible and give unavoidable helpers collision-resistant names.
- ✅ Test macro expansions in modules with shadowing names like `Option`, `Result`, `Vec`, and `helper`.
- ✅ Emit `compile_error!` for unsupported input instead of relying on accidental name-resolution failures.
- ✅ Use spans deliberately: caller spans for user-caused errors, call-site or mixed-site-like spans for generated support tokens when available through helper crates.
- ✅ Prefer generating code inside the narrowest possible scope, such as a block or private const, when helper items do not need module-level visibility.

## Pitfalls
- ⚠️ Do not emit `use` statements that can conflict with caller imports unless that is part of the documented output.
- ⚠️ Do not assume the caller has imported your trait, helper module, or prelude.
- ⚠️ Do not inject common names like `helper`, `Generated`, or `output` into caller-visible scope.
- ⚠️ Do not confuse `$crate` with procedural macros; `$crate` is a `macro_rules!` facility, not a general proc-macro escape hatch.
- ⚠️ Do not assume prelude names are always available or unshadowed; generated code should be robust in modules that define their own `Option`, `Vec`, or `Result`.
- ⚠️ Do not let an internal parse failure become a panic backtrace when a targeted `compile_error!` can explain the unsupported input.

## See also
[[Macros]] · [[Procedural Macros]] · [[Macro Hygiene]] · [[Derive Macros]] · [[Attribute Macros]] · [[Function-like Macros]] · [[Exporting macro_rules Macros]] · [[Name Resolution]]

## Sources
- The Rust Reference, "Procedural macro hygiene" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html#procedural-macro-hygiene
