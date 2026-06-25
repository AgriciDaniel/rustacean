# Security Policy

Rustacean is a documentation repository: a set of Markdown notes plus a few
helper scripts. It runs no service and ships no compiled artifact. "Security"
here covers three things.

## What to report

1. **Unsound technical guidance.** A note (especially in the unsafe, FFI, or
   concurrency domains) that, if followed, would cause undefined behavior, a
   data race, or a soundness hole. The correctness of `unsafe` advice is a
   safety issue, so please report it privately first.
2. **A vulnerability in a helper script.** The repo ships `scrape-rust-docs.sh`,
   `rust-secretary.sh`, `scripts/check-wikilinks.py`, and the generators under
   `.codex-build/`. Report anything that could execute untrusted code, leak
   credentials, or write outside the repository.
3. **An exposed secret.** If you find an API key, token, or other credential
   committed anywhere in the history, report it privately and do not open a
   public issue.

## How to report

Use **private reporting**, not a public issue:

- **Preferred:** open a private advisory under the repository's **Security** tab
  ("Report a vulnerability").
- Or contact the maintainer privately via
  [github.com/AgriciDaniel](https://github.com/AgriciDaniel).

Please include the file or note, the impact, and a minimal reproduction or a
corrected source. Expect an acknowledgement within a few days. Once a fix is
released, you are welcome to be credited.

## Supported versions

Fixes land on `main` and in the latest tagged release. Older tags are not
patched; pull the latest brain.
