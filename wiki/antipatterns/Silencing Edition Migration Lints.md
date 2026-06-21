---
type: antipattern
title: "Silencing Edition Migration Lints"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, editions, lints, migration]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Migrating Editions]]", "[[Edition 2024]]", "[[Lints and Lint Levels]]", "[[Rust Editions]]", "[[The rustc Compiler]]", "[[Unchecked cfg Names]]"]
sources: ["[[edition-guide]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html", "https://doc.rust-lang.org/rustc/lints/groups.html"]
rust_version: "edition 2024 / 1.85+"
---

# Silencing Edition Migration Lints

Silencing edition migration lints hides exactly the compiler feedback meant to preserve behavior across editions; fix, review, or locally justify the lint instead.

## The mistake
A tempting migration shortcut is to add `#![allow(rust_2024_compatibility)]`, `#![allow(warnings)]`, or a broad project lint override so `cargo fix --edition` stops reporting problems.
That removes the compiler's map of code that may parse differently, drop temporaries differently, call different traits, or require explicit unsafe review.

This is especially risky in Rust 2024 because several changes are semantic, not merely cosmetic.
Examples include `if let` temporary scope, tail expression temporary scope, boxed-slice `.into_iter()`, prelude collisions, never-type fallback, and unsafe API changes.

## Why it happens
Edition lints can be noisy in older codebases.
Some warnings require manual judgment.
Some automatic fixes are intentionally conservative and may preserve old behavior when the new behavior is better.
Suppressing the lint feels faster than deciding.

The problem is that edition migration is not just about making the crate compile.
It is about making the crate compile with reviewed behavior.
Broad suppression also blocks `cargo fix --edition` from seeing the code it is supposed to rewrite.
If a compatibility lint is allowed at the crate root, the migration tool may have no machine-applicable suggestion to apply, and the later manifest edit turns a reviewed warning into an avoidable hard error.

## Example
```rust
fn main() {
    #[expect(unused_variables)]
    let intentionally_unused = "documented local expectation";

    println!("migration lints should be handled, not hidden globally");
}
```

The corrected alternative is local, narrow, and documented.
Use `#[expect]` or a targeted `#[allow(..., reason = "...")]` only when the exact lint and reason are understood.

Avoid this crate-wide shortcut:

```rust
#![allow(rust_2024_compatibility)]

fn main() {
    println!("the build is quieter, but the migration map is gone");
}
```

Prefer enabling a specific lint while working through one class of issue:

```rust
#![warn(if_let_rescope)]
#![warn(missing_unsafe_on_extern)]

fn main() {
    println!("review migration warnings one behavior at a time");
}
```

## Common errors
After suppressing lints and changing the manifest, the compiler may report errors the migration would have prepared you for:

```text
error: extern blocks must be unsafe
```

Fix by restoring the old edition, removing the broad allow, running `cargo fix --edition`, and auditing the generated `unsafe extern` blocks.

Keyword reservations can appear as parse failures:

```text
error: expected identifier, found reserved keyword `gen`
```

Let the migration lint rewrite compatible names to `r#gen`, then decide whether a public API rename is better.

Unsafe migrations can also remain hidden until later:

```text
warning[E0133]: call to unsafe function is unsafe and requires unsafe block
```

Add the explicit unsafe block with a safety argument, or redesign the unsafe boundary.

## Best practice
- ✅ Run [[Migrating Editions]] with compatibility lints enabled.
- ✅ Review each automatic change and each warning that cannot be fixed automatically.
- ✅ Use narrow local lint attributes with `reason = "..."` when suppression is truly intentional.
- ✅ Keep unsafe migrations as audit tasks, not formatting chores.
- ✅ For hard cases, enable individual lints and migrate incrementally.
- ✅ Use `#[expect]` for temporary, intentional suppressions so stale suppressions warn later.
- ✅ Track unresolved migration warnings in issue links or comments instead of hiding the entire lint group.
- ✅ Re-run migration after feature, target, or dependency changes that expose more code.

## Pitfalls
- ⚠️ `#![allow(warnings)]` suppresses unrelated warnings and future-incompatibility signals.
- ⚠️ Allowing the whole compatibility group can leave code that fails after changing `edition = "2024"`.
- ⚠️ Automatic insertion of `unsafe` syntax does not validate safety.
- ⚠️ Leaving cfg-gated code unmigrated because only the host/default-feature build was checked.
- ⚠️ Accepting a clean build as proof of migration when `--cap-lints`, crate attributes, or workspace lint config muted the relevant diagnostics.
- ⚠️ Hiding a temporary-scope lint before checking whether the shorter Rust 2024 drop scope fixes a real lock or borrow problem.

## See also
[[Migrating Editions]] · [[Edition 2024]] · [[Lints and Lint Levels]] · [[Rust Editions]] · [[The rustc Compiler]] · [[Unchecked cfg Names]] · [[Conditional Compilation (cfg)]] · [[Inspecting rustc Configuration]] · [[Enforcing Expected cfgs]] · [[Editions & Compiler]]

## Sources
- The Rust Edition Guide, "Advanced migration strategies" — [[edition-guide]],
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- The rustc book, "Lint Groups" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/lints/groups.html
