---
type: pattern
title: "Testing Macros with trybuild"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, macros, testing, trybuild, diagnostics]
domain: "Macros"
difficulty: advanced
related: ["[[Macro Diagnostics]]", "[[Procedural Macros]]", "[[Procedural Macro Crate Structure]]", "[[syn and quote]]", "[[Integration Tests]]", "[[Test Harness and cargo test]]", "[[Derive Macros]]"]
sources: ["docs.rs trybuild 1.0.116", "[[the-reference]]"]
source_urls: ["https://docs.rs/trybuild/latest/trybuild/", "https://docs.rs/trybuild/latest/trybuild/struct.TestCases.html", "https://doc.rust-lang.org/reference/procedural-macros.html"]
rust_version: "edition 2024 / 1.85+"
---

# Testing Macros with trybuild

Use `trybuild` to compile small fixture crates and snapshot the pass or compile-fail behavior that ordinary unit tests cannot observe.

## What it is
`trybuild` is a test harness for invoking rustc on test-case files and asserting that compilation succeeds or fails with expected diagnostics.
It is especially useful for [[Procedural Macros]] because macro behavior often appears at compile time, not runtime.

Ordinary unit tests can test parsing helpers, expansion helpers, and runtime support code.
They cannot directly assert that a downstream caller sees a good compiler error for `#[derive(MyMacro)]` on an unsupported enum.
`trybuild` fills that gap by compiling files under `tests/ui/` as if they were small user crates.

As of 2026-06-21, docs.rs shows `trybuild` 1.0.116.
Verify the docs.rs latest page before changing dependency pins because `trybuild` is an ecosystem crate.

## How it works
Add `trybuild` as a dev-dependency in the macro crate or in a workspace test crate:

```toml
[dev-dependencies]
trybuild = "1.0"
```

Create an integration test harness:

```rust
#[test]
fn ui() {
    let t = trybuild::TestCases::new();
    t.pass("tests/ui/pass/*.rs");
    t.compile_fail("tests/ui/fail/*.rs");
}
```

`t.pass` expects every matching file to compile.
`t.compile_fail` expects every matching file to fail and compares stderr with an adjacent `.stderr` snapshot.
If a `.stderr` file is missing, `trybuild` writes the actual output under `wip/` so the author can review and accept it.

The fixture files should import the macro through its public path, not private modules.
That makes the test exercise [[Procedural Macro Crate Structure]] and public dependency wiring too.

## Example
```rust
#[test]
fn ui() {
    let cases = trybuild::TestCases::new();
    cases.pass("tests/ui/pass/*.rs");
    cases.compile_fail("tests/ui/fail/*.rs");
}
```

This is the minimal harness.
It compiles as an integration test when `trybuild` is listed under `[dev-dependencies]`.

## Fixture sketch
```rust
// tests/ui/pass/derive_struct.rs
use my_crate::Describe;

#[derive(Describe)]
struct User {
    name: String,
}

fn main() {
    let _ = User {
        name: String::from("Ada"),
    };
}
```

A failing fixture would live beside an expected `derive_enum.stderr` file and deliberately misuse the macro.
The `.stderr` snapshot is part of the macro's user-facing diagnostic contract.

## Best practice
- ✅ Test success cases and failure cases separately with `pass` and `compile_fail`.
- ✅ Keep fixtures tiny and focused on one macro behavior each.
- ✅ Review generated `wip/*.stderr` files before accepting them into `tests/ui/`.
- ✅ Import macros through the public crate path, as downstream users do.
- ✅ Cover derives, attributes, helper attributes, generics, visibility, and shadowed names as relevant.
- ✅ Pair `trybuild` with unit tests for parser and expansion helpers.
- ✅ Run the harness under `cargo test` in CI so diagnostic regressions are visible.

## Pitfalls
- ⚠️ Do not snapshot enormous stderr output that hides the one diagnostic you care about.
- ⚠️ Do not accept `wip` snapshots mechanically; bad diagnostics are still passing tests.
- ⚠️ Do not rely only on `pass` cases; macro APIs need compile-fail tests for [[Macro Diagnostics]].
- ⚠️ Do not put fixture code in places where it is also compiled by Cargo outside `trybuild`.
- ⚠️ Do not make fixture crates depend on private macro implementation modules.
- ⚠️ Do not overfit snapshots to line numbers if small formatting changes would create noisy churn.

## See also
[[Macros]] · [[Procedural Macros]] · [[Macro Diagnostics]] · [[Procedural Macro Crate Structure]] · [[syn and quote]] · [[Derive Macros]] · [[Attribute Macros]] · [[Integration Tests]] · [[Test Harness and cargo test]] · [[Test Organization]]

## Sources
- docs.rs, `trybuild` crate docs, latest verified 2026-06-21 as 1.0.116, https://docs.rs/trybuild/latest/trybuild/
- docs.rs, `trybuild::TestCases`, https://docs.rs/trybuild/latest/trybuild/struct.TestCases.html
- The Rust Reference, "Procedural macros" — [[the-reference]], https://doc.rust-lang.org/reference/procedural-macros.html
