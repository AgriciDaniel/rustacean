# Rustacean Corpus — Manifest

Captured **2026-06-21**. Phase 1 of building the Rust brain (raw corpus). Three workstreams:
official docs (Firecrawl) · source tree (`rust-lang/rust`) · verified deep research.

## A. Official docs — `sources/` (Firecrawl, one file per book via `print.html`)
Scraped from the books linked at https://rust-lang.org/learn/ . mdBook nav chrome stripped; each
file begins at its real H1. Total: **~833,000 words** across 10 books.

| File | Source | Words |
|---|---|---|
| `sources/the-book.md` | https://doc.rust-lang.org/book/ | 208,290 |
| `sources/the-reference.md` | https://doc.rust-lang.org/reference/ | 166,857 |
| `sources/cargo-book.md` | https://doc.rust-lang.org/cargo/ | 162,034 |
| `sources/rustc-book.md` | https://doc.rust-lang.org/rustc/ | 134,560 |
| `sources/rustonomicon.md` | https://doc.rust-lang.org/nomicon/ | 45,874 |
| `sources/embedded-book.md` | https://doc.rust-lang.org/embedded-book/ | 30,183 |
| `sources/rust-by-example.md` | https://doc.rust-lang.org/rust-by-example/ | 26,901 |
| `sources/edition-guide.md` | https://doc.rust-lang.org/edition-guide/ | 26,532 |
| `sources/rustdoc-book.md` | https://doc.rust-lang.org/rustdoc/ | 21,469 |
| `sources/command-line-book.md` | https://rust-cli.github.io/book/ | 11,118 |

Re-run with `./scrape-rust-docs.sh` (uses `FIRECRAWL_API_KEY` from `~/.env` or `$KEYS_ENV`).

## B. Source tree — `rust/` (shallow clone)
- Repo: https://github.com/rust-lang/rust
- Commit: `a7740170e5e2f733b32a8206d5bb439c8e8c2fce` (2026-06-21)
- Size: 448M · `--depth 1`, submodules **not** initialized.
- Key paths: `rust/library/` (std/core/alloc source), `rust/compiler/`, `rust/src/`.
- Deepen later: `git -C rust fetch --unshallow`.

## C. Deep research — `research/` (orchestrated, adversarially verified)
10 cited topic reports + cross-cutting synthesis. Run via Workflow `rust-deep-research`
(21 sub-agents: 10 research @ high effort → 10 adversarial verifiers → 1 synthesizer).
**177 unique sources** cited. Each report ends with a `## Verification notes` section from its
fact-checker. Verdicts: **3 solid, 7 minor-issues, 0 major-issues** (corrections noted in-file).

| Report | Citations | Verdict |
|---|---|---|
| `research/01-idiomatic-api-design.md` | 31 | minor-issues |
| `research/02-ownership-borrowing-lifetimes.md` | 15 | solid |
| `research/03-error-handling.md` | 11 | solid |
| `research/04-async-rust.md` | 16 | minor-issues |
| `research/05-anti-patterns-footguns.md` | 15 | minor-issues |
| `research/06-unsafe-and-ffi.md` | 25 | minor-issues |
| `research/07-performance-optimization.md` | 15 | solid |
| `research/08-concurrency.md` | 14 | minor-issues |
| `research/09-tooling-project-hygiene.md` | 21 | minor-issues |
| `research/10-dependency-supply-chain-security.md` | 16 | minor-issues |
| `research/99-rust-mastery-synthesis.md` | — | cross-cutting good-vs-mistakes synthesis |
| `research/00-INDEX.md` · `research/sources.md` | — | index · 177 deduped sources |

"minor-issues" = verifier found small version/citation slips (e.g. const `Mutex::new` is 1.63 not
1.62; clippy ships 800+ lints not 400) and documented the correction in each file's verification notes.

## Out of scope (by choice)
std API docs · Unstable Book · Rust Forge · Rustlings (exercise repo — clone separately if wanted).
