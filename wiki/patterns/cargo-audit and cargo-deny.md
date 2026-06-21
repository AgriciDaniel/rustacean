---
type: pattern
title: "cargo-audit and cargo-deny"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, cargo, security, supply-chain]
domain: "Cargo & Dependencies"
difficulty: intermediate
related: ["[[Cargo.lock]]", "[[Dependencies and Version Requirements]]", "[[Minimizing Dependencies]]", "[[Build Scripts (build.rs)]]"]
sources: ["[[cargo-book]]", "[[dependency-supply-chain-security]]"]
source_urls: ["https://doc.rust-lang.org/cargo/reference/resolver.html", "https://doc.rust-lang.org/cargo/reference/source-replacement.html"]
rust_version: "edition 2024 / 1.85+"
---

# cargo-audit and cargo-deny

Run `cargo-audit` and `cargo-deny` as layered dependency gates: audit catches known RustSec advisories in the lockfile, while deny enforces policy for advisories, duplicate versions, licenses, bans, and sources.

## What it is
`cargo-audit` checks `Cargo.lock` against the RustSec advisory database. It answers "does the exact resolved graph contain known-vulnerable or otherwise advised crates?"

`cargo-deny` is a policy linter. It can check advisories, ban wildcard requirements or specific crates, flag duplicate versions, enforce license allowlists, and restrict unknown git or registry sources.

## How it works
Both tools operate on Cargo metadata and the resolved dependency graph. That makes [[Cargo.lock]] central: it records what is actually present, not just what ranges were allowed.

The tools are complementary. Audit is a negative known-bad check. Deny is an organization policy check. Neither proves a dependency is trustworthy, and neither prevents malicious build-time code by itself.

For supply-chain hygiene, run them on every PR and on a schedule. Scheduled runs matter because advisories can be published after a dependency version has already shipped into your lockfile.

`cargo audit` is usually fast because it checks resolved package IDs against advisory metadata. `cargo deny` is broader: it can fail on duplicate versions, banned crates, unknown sources, and license expressions even when there is no vulnerability advisory.

These tools work best as a review gate, not as a replacement for dependency judgment. A crate with no advisories can still be abandoned, overprivileged through `build.rs`, incompatible with your license policy, or simply too large for the value it adds.

## Example
```rust
fn dependency_gate_failed(advisories: usize, denied_sources: usize) -> bool {
    advisories > 0 || denied_sources > 0
}

fn main() {
    assert!(dependency_gate_failed(1, 0));
    assert!(!dependency_gate_failed(0, 0));
}
```

This compiles as Rust; in CI, the counts come from tools that inspect Cargo's dependency graph.

## CI example
```text
cargo audit --deny warnings
cargo deny check advisories bans licenses sources
```

Run the commands after dependency resolution and before merge. A scheduled workflow should run the same checks even when application code has not changed, because advisory databases and crate metadata change independently of your repository.

## Common errors
```text
error: Vulnerable crate found: ...
```

Fix: update the affected dependency if a patched version exists. If no patched version exists, remove or replace the dependency, or add a narrow documented ignore with an owner and review date.

```text
error: found duplicate versions for package `syn`
```

Fix: inspect `cargo tree -d` and see whether a dependency update can unify the graph. Some duplicates are temporarily acceptable, but public duplicate types and heavy proc-macro stacks deserve scrutiny.

```text
error: source is not allowed: git+https://...
```

Fix: either move to a registry release or explicitly allow the source after review. Unknown git sources should not enter the graph by accident.

## Best practice
- ✅ Run `cargo audit --deny warnings` or an equivalent strict advisory gate in CI.
- ✅ Configure `cargo-deny` to deny wildcard requirements and unknown git or registry sources.
- ✅ Treat license checks as part of supply-chain risk, not paperwork after the fact.
- ✅ Keep ignores narrow, documented, and time-limited.
- ✅ Review `build.rs` and proc-macro dependencies with extra care because they execute code during the build.
- ✅ Pin tool versions in CI or install them through a reproducible toolchain path so policy changes are intentional.

## Pitfalls
- ⚠️ Audit tools only catch disclosed problems; they do not detect a brand-new malicious crate.
- ⚠️ Running checks locally but not in CI lets vulnerable lockfile changes merge.
- ⚠️ Build scripts and proc macros still execute during builds; pair policy gates with review and sandboxing for untrusted code. See [[Build Scripts (build.rs)]].
- ⚠️ Blanket advisory ignores become permanent risk if they are not owned and revisited.
- ⚠️ License allowlists that ignore transitive dependencies can still ship incompatible obligations.

## See also
[[Cargo & Dependencies]] · [[Cargo.lock]] · [[Dependencies and Version Requirements]] · [[Minimizing Dependencies]] · [[Build Scripts (build.rs)]] · [[Publishing to crates.io]] · [[Overbroad Version Requirements]] · [[Feature Flags]] · [[Cargo Workspaces]]

## Sources
- The Cargo Book, "Dependency Resolution" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/resolver.html
- The Cargo Book, "Source Replacement" — [[cargo-book]], https://doc.rust-lang.org/cargo/reference/source-replacement.html
