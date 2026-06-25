# Changelog

All notable changes to Rustacean are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-06-25

### Added

- Initial release of the Rust brain: hundreds of atomic, cross-linked notes
  (concepts, patterns, anti-patterns) across 34 domain maps, targeting Rust
  edition 2024 / stable 1.85+, with 100% wikilink resolution.
- Corpus: the ten official Rust books captured to `sources/`, plus ten
  adversarially verified deep-research reports and a cross-cutting synthesis in
  `research/`.
- The Rust Secretary agent (`AGENTS.md`, `rust-secretary.sh`).
- Community-health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `SUPPORT.md`, and issue / pull-request templates.
- CI quality gates: wikilink resolution (`scripts/check-wikilinks.py`) and
  markdownlint on the authored docs.
- `NOTICE` recording per-source licenses for the redistributed documentation.
- Brand assets and a README cover image.

### Fixed

- Resolved the last dangling wikilinks by relocating two notes that a `/` in
  their title had mis-filed into phantom subdirectories, and by adding the
  missing frontmatter aliases. Resolution is now 100% (13,444 links).

[Unreleased]: https://github.com/AgriciDaniel/rustacean/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/AgriciDaniel/rustacean/releases/tag/v1.0.0
