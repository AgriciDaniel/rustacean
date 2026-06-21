---
type: meta
title: "Coverage Backlog"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, backlog, meta]
---

# Coverage Backlog

What to add/expand after the current build (you asked me to note these down). Ordered by value.

## High value
- **std API deep-dive** — atomic notes for the most-used `std` modules (`std::collections`, `std::io`,
  `std::fmt`, `std::iter`, `std::sync`, `std::time`) from the (excluded) std API docs. See [[std]].
- **Expand short notes to ≥80 lines** — a Codex pass to deepen the ~thinner concept notes (current
  avg ~71 lines) with more worked examples and edge cases. Raises Brainstein C8.1 substance.
- **Rustlings exercises** — clone `rust-lang/rustlings` and add a `practice/` MOC mapping exercises to
  the concept notes that teach them.
- **Crate playbooks** — focused notes for the workhorse crates: [[tokio]], [[serde]], `clap`, `reqwest`,
  `rayon`, `tracing`, [[thiserror]]/[[anyhow]] (have notes; expand to full playbooks).

## Medium
- **Worked mini-projects** — end-to-end notes (CLI tool, web service, parser) wiring many concepts.
- **Compiler-error index** — notes for common `rustc` error codes (E0382 move, E0499 borrow, E0506…).
- **Design-patterns set** — port `rust-unofficial/patterns` (idioms, patterns, anti-patterns) and link in.
- **Cross-links to source** — link concept notes to the real implementation in `rust/library/`.

## Maintenance / freshness (the whole point: stay current)
- **6-week release refresh** — re-scrape books each Rust release; re-run the research workflow monthly.
  Provenance + due dates live in `references/source-ledger.json`.
- **Edition watch** — track post-2024 edition changes; update affected notes.
- **Security advisories** — periodic `cargo audit` / RustSec sweep feeding [[Dependency & Supply-Chain Security]].

## Optional (Brainstein product packaging — only if distributing the brain)
- Adapters/importers, deterministic sample-vault, `package_release.py`, CI, `CHANGELOG`, plugin manifest.
  Not needed for personal use; would make the brain a sellable Brainstein product.

See [[Rust Brain Home]] · [[overview]].
