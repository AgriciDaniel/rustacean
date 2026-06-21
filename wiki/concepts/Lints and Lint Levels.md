---
type: concept
title: "Lints and Lint Levels"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, lints, diagnostics, compiler]
domain: "Editions & Compiler"
difficulty: intermediate
related: ["[[The rustc Compiler]]", "[[Migrating Editions]]", "[[Edition 2024]]", "[[Enforcing Expected cfgs]]", "[[Silencing Edition Migration Lints]]", "[[Unchecked cfg Names]]"]
sources: ["[[rustc-book]]", "[[edition-guide]]"]
source_urls: ["https://doc.rust-lang.org/rustc/lints/index.html", "https://doc.rust-lang.org/rustc/lints/levels.html"]
rust_version: "edition 2024 / 1.85+"
---

# Lints and Lint Levels

Rust lints are compiler diagnostics that can be configured from silent to warning or error; they catch suspicious code, style issues, future incompatibilities, and edition migration hazards.

## What it is
`rustc` runs lints while compiling.
Some lints warn by default, some deny by default, and some are allowed until you opt in.
Lints are not all hard language errors: a lint's level controls whether a finding is ignored, warned, or treated as an error.

The six levels are `allow`, `expect`, `warn`, `force-warn`, `deny`, and `forbid`.
`expect` documents that a lint is intentionally expected at that location and warns if the lint stops firing.
`force-warn` and `forbid` are special because normal local overrides cannot lower them.

## How it works
You can configure lints through attributes or through compiler flags.
Attributes include `#![warn(missing_docs)]`, `#[allow(unused_variables)]`, and `#[expect(unused_variables)]`.
Compiler flags include `-A`, `-W`, `--force-warn`, `-D`, `-F`, and `--cap-lints`.

Priority matters.
`--force-warn` has very high priority.
`--cap-lints` caps lint severity and is used by Cargo when compiling dependencies so their warnings do not pollute your build.
Source attributes generally override command-line defaults inside the relevant scope, except where `forbid` or forced warnings prevent it.
Command-line lint flags are order-sensitive for ordinary lint levels, so a later `-A unused_variables` can lower an earlier `-D unused_variables`.
That does not work once a lint has been forced to warn or forbidden.
`#[expect]` is attribute-only and is designed for local suppressions that should be revisited automatically when the lint stops firing.

Edition migrations rely on lint groups such as `rust-2024-compatibility`.
`cargo fix --edition` enables the appropriate compatibility lints, applies machine-applicable suggestions, and reruns checks.

## Example
```rust
#![deny(unused_must_use)]

fn might_fail() -> Result<(), &'static str> {
    Ok(())
}

fn main() {
    might_fail().expect("demo should succeed");

    #[expect(unused_variables)]
    let intentionally_unused = 42;
}
```

Lint levels can also document platform-specific code:

```rust
use std::path::PathBuf;

fn tool_name() -> PathBuf {
    #[allow(unused_mut, reason = "Windows appends an .exe extension below")]
    let mut name = PathBuf::from("rustfmt");

    #[cfg(target_os = "windows")]
    name.set_extension("exe");

    name
}
```

Here the local `allow` is narrow and explains why the variable is only mutable on one target.

## Common errors
Denying a warning turns it into a build-stopping error:

```text
error: unused variable: `x`
  = note: `#[deny(unused_variables)]` on by default
```

Fix the code, lower the lint at the narrowest useful scope, or rename intentionally unused bindings to `_x` when that convention is enough.

An obsolete `#[expect]` produces a warning:

```text
warning: this lint expectation is unfulfilled
  = note: `#[warn(unfulfilled_lint_expectations)]` on by default
```

Remove the `#[expect(...)]` once the expected lint no longer fires.
That is the main advantage over `#[allow(...)]` for temporary suppressions.

Trying to override `forbid` locally fails:

```text
error[E0453]: allow(unused_variables) overruled by outer forbid(unused_variables)
```

Use `deny` for project policy unless you intentionally want to prevent every lower-scope override.

## Best practice
- ✅ Set important project lints at crate or workspace level instead of scattering one-off attributes.
- ✅ Use `#[expect(...)]` when suppressing a lint that should still be tracked.
- ✅ Add `reason = "..."` to local `allow`/`warn`/`deny` attributes when the motivation is not obvious.
- ✅ Use lint groups for migrations, then narrow to individual lints when debugging a difficult fix.
- ✅ Treat future-incompatible and edition compatibility lints as real maintenance work.
- ✅ Prefer `deny` in CI over `forbid` in library source unless preventing overrides is part of the contract.
- ✅ Keep command-line lint settings in one place, such as CI or workspace lint config, so precedence is easy to audit.

## Pitfalls
- ⚠️ Blanket `#![allow(warnings)]` hides compiler feedback that may become a future hard error.
- ⚠️ Assuming dependency warnings should fail your crate; Cargo intentionally caps dependency lints.
- ⚠️ Using `forbid` casually in libraries; downstream tools cannot lower it.
- ⚠️ Suppressing edition lints to get a clean build; see [[Silencing Edition Migration Lints]].
- ⚠️ Forgetting that `--cap-lints allow` can hide dependency warnings but does not override `force-warn`.
- ⚠️ Using `#[allow]` for a known temporary issue when `#[expect]` would catch the moment the issue disappears.

## See also
[[The rustc Compiler]] · [[Edition 2024]] · [[Migrating Editions]] · [[Enforcing Expected cfgs]] · [[Unchecked cfg Names]] · [[Silencing Edition Migration Lints]] · [[Conditional Compilation (cfg)]] · [[Inspecting rustc Configuration]] · [[panic!]] · [[Editions & Compiler]]

## Sources
- The rustc book, "Lints" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/lints/index.html
- The rustc book, "Lint Levels" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/lints/levels.html
