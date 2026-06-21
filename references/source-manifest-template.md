# Source Manifest Template — Rust Brain

Template for registering a new source in `references/source-ledger.json`:

```json
{
  "id": "short-slug",
  "title": "Human Title",
  "url": "https://...",
  "source_type": "official | primary",
  "retrieved": "YYYY-MM-DD",
  "refresh_due": "YYYY-MM-DD",
  "confidence": "high | medium | low",
  "local_path": ".raw/..."
}
```
Refresh cadence: every 6-week Rust release; monthly for ecosystem & security.
