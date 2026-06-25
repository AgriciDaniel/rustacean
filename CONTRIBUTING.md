# Contributing to Rustacean

Thanks for helping keep the Rust brain correct, idiomatic, and current. Rustacean is a curated Obsidian knowledge base: cross-linked atomic notes targeting Rust edition 2024 / stable 1.85+. Contributions that fit that mission are very welcome.

## Ways to contribute

- **Fix a note** that is wrong, unsound, or out of date (a stale version number, a deprecated idiom, a broken example).
- **Add a note** for a topic that is missing. Start from [`wiki/Coverage Backlog.md`](wiki/Coverage%20Backlog.md).
- **Improve links** by connecting related notes. Every note aims for at least six outbound `[[wikilinks]]`.
- **Report an issue** if you would rather flag than fix (see [Open an issue](#open-an-issue)).

## The authoring contract

Every note in `wiki/` follows one contract: **[`wiki/meta/CONVENTIONS.md`](wiki/meta/CONVENTIONS.md)**. Read it before writing. The gold-standard exemplar is [`wiki/concepts/Ownership.md`](wiki/concepts/Ownership.md). In short, a `concept`, `pattern`, or `antipattern` note needs:

- **Valid, flat frontmatter**: `type`, `title`, `status`, `created`, `updated`, `tags` (always include `rust`), and `domain`, plus `difficulty`, `related`, `sources`, `source_urls`, and `rust_version` for atomic notes.
- **An answer-first opening**: one or two sentences someone could quote, with no throat-clearing.
- **A minimal, compilable `rust` example** in a fenced ` ```rust ` block, idiomatic and current.
- **A ✅ Best practice list and a ⚠️ Pitfalls list**, with pitfalls linking to the relevant `[[antipattern]]`.
- **At least six `[[wikilinks]]`**, including a link up to the note's domain map (MOC).
- **Cited sources**: a `[[source note]]` plus the canonical `https://doc.rust-lang.org/...` URL.

### Currency

Notes target **edition 2024 / stable 1.85+**. Show the current idiom, not a deprecated one (for example `&raw const` / `&raw mut` rather than `&` on a `static mut`; `unsafe extern` blocks; const `Mutex::new`). If you are not sure a fact is current, mark the note `status: seed` and add a `> [!todo]` callout rather than guess. Never invent an API.

### Filenames and titles

Filenames are vault-unique and live directly under their category folder (`wiki/concepts/`, `wiki/patterns/`, `wiki/antipatterns/`, `wiki/mocs/`, `wiki/sources/`). A filename **cannot contain `/`**. If a title needs a slash (for example "Cancellation-Safe I/O"), use a slash-free filename (`Cancellation-Safe IO.md`) and add the slashed form as a frontmatter `aliases:` entry so existing `[[links]]` still resolve.

## Before you open a pull request

1. **Branch** off `main`, and keep each change scoped and reviewable.
2. **Run the link checker** and make sure it passes:

   ```bash
   python3 scripts/check-wikilinks.py wiki
   ```

   It must report `0 unresolved`. CI runs this on every pull request, alongside markdownlint on the authored docs.
3. **Fill in the pull request checklist.** It mirrors the authoring contract above.

Optional: open the repo as an Obsidian vault to preview the graph and confirm your links land where you expect.

## Open an issue

Prefer a form over freeform: choose **Note correction** (a note is wrong or stale) or **Coverage request** (a topic is missing) from the [issue templates](../../issues/new/choose). For questions, see [`SUPPORT.md`](SUPPORT.md). To report something privately (unsound `unsafe` guidance, a script vulnerability, an exposed secret), see [`SECURITY.md`](SECURITY.md).

## Conduct and licensing

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By contributing, you agree your work is released under the repository's [MIT License](LICENSE). When you quote third-party text, preserve its attribution (see [`NOTICE`](NOTICE)).
