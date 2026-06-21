# Safety Gates — Rust Brain

This is a **read-only** knowledge brain.

- **No credentials** are stored, requested, or emitted by this brain.
- **Read-only:** the brain never mutates external repos, registries, or systems; it only reads docs and writes notes in this vault.
- **Rollback:** all notes are plain files under version-controllable folders; any change can be reverted from git history.
- **Source:** every non-obvious claim cites an official doc, RFC, or the Rust source.

## Refusal rules
- No language/stdlib behavior claim without an official doc, RFC, or source citation.
- No unsafe-code recommendation without an explicit soundness rationale and citation.
- No idiom presented as current if deprecated in edition 2024 / current stable.
