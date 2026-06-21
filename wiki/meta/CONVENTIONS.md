---
type: meta
title: "Authoring Conventions — Rust Brain"
status: evergreen
created: 2026-06-21
updated: 2026-06-21
tags:
  - meta
  - conventions
aliases: ["CONVENTIONS"]
---

# Authoring Conventions — Rust Brain

The contract every note in `wiki/` follows. Writers (human or agent) MUST adhere to this.
Goal of the brain: **look something up and write correct, idiomatic, current Rust with confidence.**
Targets **Rust edition 2024 / stable 1.85+** unless a note says otherwise.

## Note types (`type:` frontmatter)
| type | folder | purpose |
|---|---|---|
| `concept` | `wiki/concepts/` | A Rust language/stdlib concept (ownership, lifetimes, traits, iterators, async, …). |
| `pattern` | `wiki/patterns/` | An idiom / best practice (newtype, builder, `thiserror` errors, RAII guards). |
| `antipattern` | `wiki/antipatterns/` | A footgun / mistake to avoid (`unwrap` everywhere, needless `clone`, `Rc<RefCell>` overuse). |
| `moc` | `wiki/mocs/` | Map of Content — a domain hub linking related notes. |
| `source` | `wiki/sources/` | One summary page per raw book in `.raw/books/`. |
| `meta` | `wiki/meta/` | Index, log, hot cache, conventions, dashboards. |

## Frontmatter (flat YAML — no nesting; Obsidian Properties requires flat)
Every note:
```yaml
---
type: concept            # concept|pattern|antipattern|moc|source|meta
title: "Human Title"     # matches the H1 and the filename
status: seed             # seed|developing|mature|evergreen
created: 2026-06-21
updated: 2026-06-21
tags: [rust, <topic>]    # always include 'rust' + topical tags
domain: "Ownership & Memory"   # the MOC/domain this belongs to
---
```
`concept` / `pattern` / `antipattern` add:
```yaml
difficulty: intermediate          # basic|intermediate|advanced
related: ["[[Borrowing]]", "[[Lifetimes]]"]
sources: ["[[the-book]]"]          # raw book source note(s)
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html"]
rust_version: "edition 2024 / 1.85+"
```

## Body structure
- **H1** = the title (exactly once, first line after frontmatter).
- **First line = answer-first**: a one–two sentence definition someone could quote. No throat-clearing.
- Then sections with `##` headings. For `concept`/`pattern`/`antipattern` use this skeleton:
  - `## What it is` (or `## The mistake` for antipatterns)
  - `## How it works` / `## Why it happens`
  - `## Example` — a **minimal, compilable** Rust snippet in a ```rust fence. Prefer real, idiomatic code.
  - `## Best practice` — ✅ bullets of what to do.
  - `## Pitfalls` — ⚠️ bullets of what to avoid; link to the relevant ``[[antipattern]]``.
  - `## See also` — ``[[wikilinks]]`` to related notes (aim for ≥4).
  - `## Sources` — cite the book/section + URL.

## Linking rules
- Link with ``[[Note Title]]`` (filename-based, globally unique — **no paths**, no extension).
- Link **liberally**: every note should have **≥6 outbound ``[[wikilinks]]``**. A ``[[Link]]`` whose target
  doesn't exist yet is fine — it marks a note to write.
- Concepts link to their patterns and antipatterns and vice-versa. Everything links up to its `moc`.
- Cite sources with both a ``[[source note]]`` and the canonical `https://doc.rust-lang.org/...` URL.

## Quality bar (what "good" means)
- **Correct & current**: matches edition 2024 / current stable. No deprecated idioms presented as current
  (e.g. use `&raw const`/`&raw mut` not `&` on `static mut`; `unsafe extern` blocks; const `Mutex::new`).
- **Substantive**: real explanation + working example, not a stub. Aim ≥40 lines of body.
- **Idiomatic**: examples pass `clippy` in spirit; show the idiomatic form first.
- **Self-contained**: a reader can act on the note without opening the source.
- **No invented facts**: if unsure, mark `status: seed` and add a `> [!todo]` note rather than guess.

## Filenames
`wiki/<folder>/<Title>.md` where `<Title>` matches `title:` (spaces allowed, must be vault-unique).
Example: `wiki/concepts/Ownership.md`, `wiki/patterns/Error Handling with thiserror.md`.

See [[Ownership]] for the gold-standard exemplar that matches this contract.
