---
type: concept
title: "Macro Hygiene"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, hygiene, name-resolution]
domain: "Macros"
difficulty: advanced
related: ["[[Declarative Macros]]", "[[macro_rules!]]", "[[Procedural Macros]]", "[[Exporting macro_rules Macros]]", "[[Unhygienic Procedural Macro Output]]", "[[Ambiguous macro_rules Matchers]]"]
sources: ["[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/reference/macros-by-example.html#hygiene", "https://doc.rust-lang.org/reference/procedural-macros.html#procedural-macro-hygiene"]
rust_version: "edition 2024 / 1.85+"
---

# Macro Hygiene

Macro hygiene is Rust's name-resolution behavior for expanded code; `macro_rules!` has mixed-site hygiene, while procedural macros are effectively unhygienic.

## What it is
Hygiene answers the question "which binding does this name refer to after macro expansion?" It matters because macro output is inserted into the caller's code, where caller names, imports, labels, and generated helper names may collide.

For `macro_rules!`, Rust uses mixed-site hygiene. Local variables, loop labels, and block labels are resolved at the macro definition site. Most other symbols, such as functions, types, traits, and modules, are resolved at the invocation site.

For procedural macros, the Reference describes the output as unhygienic: it behaves much like tokens written inline at the invocation location. Authors must deliberately generate robust paths and names.

## How it works
In a declarative macro, local temporaries created by one expansion do not leak into another expansion. Likewise, a local variable captured from the definition site is not accidentally replaced by a caller variable with the same text.

Item paths are different. If a macro expands to `Option<T>`, the caller's imports and local definitions affect what `Option` means. Reusable macros should use absolute paths, such as `::std::option::Option`, or `$crate::path` for helpers defined by the exporting crate.

`$crate` is a special metavariable in `macro_rules!` that refers to the crate where the macro is defined. It helps exported macros call their own helper macros or items without requiring users to import those helpers.

Edition hygiene is related but separate: tokens produced by a macro carry the edition of the macro definition. This is why migrating a macro-defining crate can change how its own generated tokens parse, even when the call sites live in another edition.

## Example
```rust
fn main() {
    let x = 1;

    macro_rules! check_local_x {
        () => {
            assert_eq!(x, 1);
        };
    }

    {
        let x = 2;
        // The local `x` in the macro body is resolved where the macro was
        // defined, so this checks the outer `x`, not the inner one.
        check_local_x!();
        assert_eq!(x, 2);
    }
}
```

## Edge case: item lookup is invocation-site lookup
```rust
fn helper() -> &'static str {
    "outer"
}

macro_rules! call_helper {
    () => {
        helper()
    };
}

fn main() {
    fn helper() -> &'static str {
        "inner"
    }

    assert_eq!(call_helper!(), "inner");
}
```

The local variable example above resolves `x` at the definition site. This example resolves the function `helper` at the invocation site. That mixed behavior is why exported macros should not emit unqualified item paths unless they intentionally want caller lookup.

## Common errors
When an exported macro calls a helper macro by bare name, downstream users often see:

```text
error: cannot find macro `helper` in this scope
```

Fix it by writing `$crate::helper!()` inside the exported macro. For helper functions, use `$crate::module::function()` and make sure the function is visible enough for external expansions.

## Best practice
- ✅ Use `$crate::helper!()` or `$crate::module::item()` when an exported `macro_rules!` macro depends on helper code from its defining crate.
- ✅ Use absolute standard-library paths in generated code that should not depend on caller imports.
- ✅ Make generated public item names explicit and documented; make generated private helper names unlikely to collide.
- ✅ Test exported macros from a separate crate or integration test so `$crate` paths and visibility are exercised.
- ✅ For procedural macros, assume every unqualified name can be captured by the caller; see [[Unhygienic Procedural Macro Output]].
- ✅ Prefer passing caller identifiers as metavariables when the caller is meant to choose a binding name.
- ✅ Keep macro-generated locals inside an extra block so their definition-site hygiene and lifetime are easy to reason about.

## Pitfalls
- ⚠️ `$crate` does not bypass visibility; private helper items are still private to external callers.
- ⚠️ `local_inner_macros` is a migration aid for old exported macros, not the preferred style for new macros.
- ⚠️ Procedural macro output that emits `Option`, `Result`, or `Vec` unqualified can break under unusual caller scopes.
- ⚠️ Generated names like `helper` or `new` can collide with user code when emitted into the caller's module.
- ⚠️ Mixed-site hygiene does not mean every name is protected; item paths, types, traits, and modules are generally looked up where the macro is invoked.
- ⚠️ `$crate` can only appear in `macro_rules!` transcriptions; procedural macro authors need ordinary absolute paths or runtime-crate paths.

## See also
[[Macros]] · [[Declarative Macros]] · [[macro_rules!]] · [[Procedural Macros]] · [[Exporting macro_rules Macros]] · [[Unhygienic Procedural Macro Output]] · [[Name Resolution]] · [[Modules]]

## Sources
- The Rust Reference, "Macros by example / Hygiene" — [[the-reference]], https://doc.rust-lang.org/reference/macros-by-example.html#hygiene
- The Rust Reference, "Procedural macro hygiene" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html#procedural-macro-hygiene
