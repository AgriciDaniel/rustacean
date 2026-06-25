## What this changes

<!-- One or two sentences. Link any issue it closes, e.g. Closes #12. -->

## Type

- [ ] Fix to an existing note (correction / currency)
- [ ] New note (from the Coverage Backlog or otherwise)
- [ ] Linking / structure / tooling
- [ ] Docs (README, contributing, meta)

## Authoring checklist

For any change under `wiki/`, confirm the note follows the authoring contract in
`wiki/meta/CONVENTIONS.md`:

- [ ] Frontmatter is valid and flat (`type`, `title`, `status`, `created`, `updated`, `tags`, `domain`, plus `difficulty` / `related` / `sources` / `source_urls` / `rust_version` for atomic notes).
- [ ] Opens answer-first (a quotable one or two sentences).
- [ ] Includes a minimal, idiomatic `rust` example, current to edition 2024 / 1.85+.
- [ ] Has a ✅ Best practice list and a ⚠️ Pitfalls list.
- [ ] Has at least six `[[wikilinks]]` and links up to the right MOC.
- [ ] Cites sources (a `[[source note]]` plus a canonical URL).
- [ ] No invented APIs; anything uncertain is marked `status: seed`.

## Verification

- [ ] `python3 scripts/check-wikilinks.py wiki` reports 0 unresolved.
- [ ] CI (wikilinks + markdownlint) is green.
