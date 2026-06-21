---
type: concept
title: "Edition 2024"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, edition-2024, migration, compiler]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[Rust Editions]]", "[[Migrating Editions]]", "[[Lints and Lint Levels]]", "[[Conditional Compilation (cfg)]]", "[[The Never Type]]", "[[async and await]]"]
sources: ["[[edition-guide]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/edition-guide/rust-2024/index.html", "https://doc.rust-lang.org/rustc/lints/groups.html"]
rust_version: "edition 2024 / 1.85+"
---

# Edition 2024

Edition 2024 is the Rust edition stabilized in Rust 1.85.0; it tightens several unsafe and temporary-scope rules, reserves future syntax, updates macro matching, and changes a few standard-library and Cargo defaults.

## What it is
Rust 2024 is an opt-in edition selected with `edition = "2024"`.
It includes language, standard library, Cargo, rustdoc, and rustfmt changes.
The changes are edition-gated where compatibility requires it.
Many migrations are detected by the `rust-2024-compatibility` lint group and applied through [[Migrating Editions]].

Important language changes include RPIT lifetime capture rules, `if let` temporary rescoping, tail-expression temporary scope changes, match ergonomics reservations, required `unsafe extern` blocks, unsafe attributes, `unsafe_op_in_unsafe_fn` warning behavior, and stronger checks around `static mut` references.

## How it works
The edition changes the interpretation of source code, not the ABI of every dependency.
For example, a crate can move to 2024 while depending on crates written in earlier editions.

Rust 2024 also reserves `gen` as a keyword for future generator-block work.
The migration lint rewrites existing identifiers named `gen` to raw identifiers such as `r#gen`.

The standard prelude adds `Future` and `IntoFuture`, which can create ambiguous method calls.
Boxed slice `.into_iter()` method-call behavior changes in Rust 2024 to yield owned values instead of references.
Cargo also changes the implied resolver: `edition = "2024"` implies resolver version 3, which is Rust-version aware.

Several Rust 2024 changes are about making hidden obligations explicit.
`extern` blocks must be written as `unsafe extern`, the unsafe attributes `no_mangle`, `export_name`, and `link_section` must be wrapped as `#[unsafe(...)]`, and unsafe operations inside `unsafe fn` are linted unless they are inside an explicit `unsafe { ... }` block.
The compiler can add syntax during migration, but it cannot prove that an FFI signature, symbol export, or raw pointer operation is sound.

Temporary-scope changes are deliberately semantic.
In 2024, temporaries in an `if let` scrutinee are dropped before entering the `else` branch, and temporaries in tail expressions can be dropped before local variables at the end of the block.
The compatibility lints preserve older behavior where they can, but a human should decide whether the shorter lifetime is actually the desired behavior.

## Example
```rust
fn r#gen(limit: usize) -> Vec<usize> {
    (0..limit).collect()
}

fn main() {
    let values = r#gen(3);
    assert_eq!(values, vec![0, 1, 2]);
}
```

This example uses a raw identifier because `gen` is reserved in Edition 2024.
The same spelling is also compatible with earlier editions.

Another common migration area is FFI:

```rust
unsafe extern "C" {
    pub safe fn sqrt(x: f64) -> f64;
    pub unsafe fn strlen(ptr: *const std::ffi::c_char) -> usize;
}

fn main() {
    let root = sqrt(9.0);
    assert_eq!(root, 3.0);
}
```

The block is `unsafe` because the author must guarantee the declarations match the foreign library.
Individual items can be marked `safe` only when every call satisfying the Rust type signature is sound.

## Common errors
Using a newly reserved keyword as a normal identifier produces a parser error in Rust 2024:

```text
error: expected identifier, found reserved keyword `gen`
```

Fix it with `r#gen` for compatibility, or rename the item if the public API should avoid raw identifiers.

Old-style FFI declarations fail after the edition switch:

```text
error: extern blocks must be unsafe
```

Fix the syntax with `unsafe extern "C" { ... }`, then audit each signature and mark individual items `safe` only when the safety contract is truly call-site-free.

Taking a reference to mutable global state is denied by default:

```text
error: creating a shared reference to mutable static is discouraged
```

Prefer `static` plus `Atomic*`, `Mutex`, `RwLock`, `OnceLock`, or `LazyLock`.
If raw global access is unavoidable, use raw borrow operators such as `&raw const` or `&raw mut` and keep the unsafe region small.

## Best practice
- ✅ Run `cargo fix --edition` while still on the old edition, then review the diff before changing to `edition = "2024"`.
- ✅ Manually audit automatic unsafe migrations; adding `unsafe` syntax does not prove the FFI signature, attribute, or environment mutation is sound.
- ✅ Review temporary-scope migrations where `if let` became `match`, because the preserved old behavior may not be the behavior you actually want.
- ✅ Prefer explicit types when never-type fallback warnings show up; relying on fallback is fragile.
- ✅ Treat macro migrations as behavior reviews, especially when `expr` is rewritten to `expr_2021`.
- ✅ Review RPIT return types that gained or avoided lifetime capture through `use<...>` bounds.
- ✅ Check public APIs for raw identifiers introduced by migration, especially if docs or downstream callers would find them awkward.
- ✅ Run migration under important features and targets so cfg-gated unsafe, macro, and platform code is checked too.

## Pitfalls
- ⚠️ Assuming `cargo fix --edition` proves semantic equivalence; it aims to preserve compatibility but cannot audit intent.
- ⚠️ Leaving `r#gen` unexplained in public APIs; raw identifiers are compatible, but API naming may deserve a clearer alternative.
- ⚠️ Accepting `match` rewrites mechanically when the old longer temporary scope caused locks to stay held.
- ⚠️ Silencing `rust-2024-compatibility`; see [[Silencing Edition Migration Lints]].
- ⚠️ Treating the new prelude additions as harmless in every codebase; method-call ambiguity around `Future` or `IntoFuture` may need fully qualified syntax.
- ⚠️ Assuming `unsafe fn` bodies are automatically unsafe contexts; explicit unsafe blocks are now the reviewed boundary.
- ⚠️ Migrating only `src/lib.rs` and missing doctests, proc macro output, or build-script-generated Rust.

## See also
[[Rust Editions]] · [[Migrating Editions]] · [[Lints and Lint Levels]] · [[The rustc Compiler]] · [[The Never Type]] · [[Fully Qualified Syntax]] · [[Cargo.toml Manifest]] · [[Conditional Compilation (cfg)]] · [[Unsafe Rust]] · [[Foreign Function Interface (FFI)]] · [[Editions & Compiler]]

## Sources
- The Rust Edition Guide, "Rust 2024" — [[edition-guide]],
  https://doc.rust-lang.org/edition-guide/rust-2024/index.html
- The rustc book, "Lint Groups" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/lints/groups.html
