---
type: concept
title: "rustfmt and Clippy"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rustfmt, clippy, tooling, lints]
domain: "Tooling & Getting Started"
difficulty: basic
related: ["[[Cargo Basics]]", "[[Cargo Build Run Check Test]]", "[[Lints and Lint Levels]]", "[[rustup and Installation]]", "[[Use cargo check While Editing]]", "[[Edition 2024]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/appendix-04-useful-development-tools.html"]
rust_version: "edition 2024 / 1.85+"
---

# rustfmt and Clippy

`rustfmt` standardizes Rust source layout, while Clippy adds extra lints that catch common mistakes and improve idiom beyond what the compiler must reject.

## What it is
`rustfmt` is the Rust formatting tool. It rewrites code according to the
community style so teams do not spend review time debating indentation, brace
placement, or line wrapping.

Clippy is a collection of lints. It analyzes compiling Rust code and reports
patterns that are legal but suspicious, unclear, inefficient, or less idiomatic
than a standard alternative.

Both are included with standard Rust installations. In Cargo projects, use
`cargo fmt` and `cargo clippy`; those commands understand package conventions.

## How it works
`cargo fmt` walks the current package or workspace and formats Rust source
files. Formatting should not change program semantics. It is usually run before
commits or enforced in CI with a check mode.

`cargo clippy` compiles enough of the package to run Clippy lints. The Book's
example shows Clippy catching an approximate value of pi and suggesting the
standard-library constant instead. Clippy is strongest when paired with the
normal workflow: `cargo check` for compiler feedback, `cargo fmt` for layout,
`cargo clippy` for idiom, and `cargo test` for behavior.

`cargo fmt` delegates to rustfmt using Cargo's package knowledge, including the
edition from `Cargo.toml`. Direct `rustfmt` is useful for individual files, but
Cargo mode is the normal project command. In CI, `cargo fmt --check` reports a
diff-worthy formatting mismatch without rewriting files.

Clippy lints have levels just like compiler lints: allow, warn, deny, and
forbid. Cargo can configure package lint policy in `[lints]`, and local code can
use attributes such as `#[expect(clippy::lint_name)]` when a warning is known,
documented, and intentionally accepted.

## Example
```rust
fn area(radius: f64) -> f64 {
    std::f64::consts::PI * radius * radius
}

fn main() {
    println!("{}", area(8.0));
}
```

## Worked example
Use formatting and linting as separate gates:

```text
$ cargo fmt --check
$ cargo clippy --all-targets --all-features -- -D warnings
$ cargo test
```

`--all-targets` checks bins, tests, examples, and benches where relevant.
`--all-features` is useful for libraries whose optional code should keep
compiling. `-- -D warnings` passes `-D warnings` to the compiler/Clippy after
Cargo has parsed its own flags.

Project lint policy can live in the manifest:

```toml
[lints.rust]
unsafe_code = "forbid"

[lints.clippy]
unwrap_used = "warn"
```

Use this for stable team policy. Avoid enabling broad experimental groups
without reviewing their false-positive and churn costs.

## Common errors
Formatting checks in CI fail without changing files:

```text
Diff in /path/src/main.rs
```

Run `cargo fmt` locally and commit the formatting result.

Clippy can report a deny-by-default lint:

```text
error: approximate value of `f{32, 64}::consts::PI` found
```

Use `std::f64::consts::PI` or `std::f32::consts::PI` rather than a hand-written
approximation.

If `cargo clippy` is unavailable, install the component:

```text
$ rustup component add clippy
```

## Best practice
- ✅ Run `cargo fmt` before review or commit; style should be automatic and
  uninteresting.
- ✅ Run `cargo clippy` once the code compiles, especially on beginner code that
  may be legal but non-idiomatic.
- ✅ Treat Clippy suggestions as review prompts. Apply them when they improve
  clarity, but understand what changed.
- ✅ Keep lint policy explicit in shared projects; see [[Lints and Lint Levels]].
- ✅ Use `cargo fmt --check` and `cargo clippy --all-targets` in CI so tests,
  examples, and binaries do not drift.
- ✅ Prefer `#[expect(...)]` over silent `#[allow(...)]` when suppressing a lint
  on modern stable Rust; it documents that the lint is expected.
- ✅ Keep rustfmt configuration minimal unless a team really needs a stable
  option; uncommon formatting knobs create needless diffs.

## Pitfalls
- ⚠️ Treating formatting as a substitute for correctness. `cargo fmt` can make
  wrong code tidy; it cannot prove behavior.
- ⚠️ Ignoring Clippy because the compiler accepts the code; many Clippy lints
  flag real maintainability or correctness risks.
- ⚠️ Applying suggestions mechanically across a large codebase without running
  [[Cargo Build Run Check Test]] afterward.
- ⚠️ Enabling entire Clippy `restriction` or `nursery` groups as policy; those
  groups are intentionally noisy or unstable and should be cherry-picked.
- ⚠️ Running direct `rustfmt` in scripts without considering edition/style
  settings that `cargo fmt` would infer from the package.

## See also
[[Cargo Basics]] · [[Cargo Build Run Check Test]] · [[Use cargo check While Editing]] · [[Lints and Lint Levels]] · [[Edition 2024]] · [[Naming Conventions (Rust API Guidelines)]] · [[MSRV Policy]] · [[Tooling & Getting Started]]

## Sources
- The Rust Programming Language, Appendix D "Useful Development Tools" — [[the-book]],
  https://doc.rust-lang.org/book/appendix-04-useful-development-tools.html
