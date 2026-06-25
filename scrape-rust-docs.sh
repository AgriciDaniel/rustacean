#!/usr/bin/env bash
# Scrape the core Rust mdBooks to STRUCTURED markdown via Firecrawl (one file per book).
# Uses onlyMainContent:false to PRESERVE the heading hierarchy (print.html), then cleans:
#   - strips the mdBook nav preamble (everything before the first top-level "# ")
#   - converts linked headings "## [Title](url)" -> "## Title"
# Key loaded from ~/.env or $KEYS_ENV (never printed). Re-runnable.
set -u
set -a; . "${KEYS_ENV:-$HOME/.env}"; set +a

ROOT="$(cd "$(dirname "$0")" && pwd)"
DIR="$ROOT/sources"
RAW="$ROOT/.raw/books"
mkdir -p "$DIR" "$RAW"

BOOKS=(
  "the-book.md|https://doc.rust-lang.org/book/print.html"
  "rust-by-example.md|https://doc.rust-lang.org/rust-by-example/print.html"
  "the-reference.md|https://doc.rust-lang.org/reference/print.html"
  "rustonomicon.md|https://doc.rust-lang.org/nomicon/print.html"
  "edition-guide.md|https://doc.rust-lang.org/edition-guide/print.html"
  "cargo-book.md|https://doc.rust-lang.org/cargo/print.html"
  "rustdoc-book.md|https://doc.rust-lang.org/rustdoc/print.html"
  "rustc-book.md|https://doc.rust-lang.org/rustc/print.html"
  "command-line-book.md|https://rust-cli.github.io/book/print.html"
  "embedded-book.md|https://doc.rust-lang.org/embedded-book/print.html"
)

clean() { # stdin -> stdout : strip preamble, de-link headings
  awk 'p{print} /^# /{if(!p){p=1; print}}' \
  | sed -E 's/^(#{1,6}) \[([^]]*)\]\([^)]*\)[[:space:]]*$/\1 \2/'
}

fail=0
for entry in "${BOOKS[@]}"; do
  file="${entry%%|*}"; url="${entry##*|}"
  echo ">> $file  <-  $url"
  resp=$(curl -s --max-time 200 https://api.firecrawl.dev/v1/scrape \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"$url\",\"formats\":[\"markdown\"],\"onlyMainContent\":false,\"timeout\":180000}")
  ok=$(printf '%s' "$resp" | jq -r '.success // false')
  if [ "$ok" = "true" ]; then
    printf '%s' "$resp" | jq -r '.data.markdown // ""' | clean > "$DIR/$file"
    cp "$DIR/$file" "$RAW/$file"
    h2=$(grep -cE '^#{2,6} ' "$DIR/$file"); bytes=$(wc -c < "$DIR/$file")
    if [ "$h2" -lt 5 ]; then
      echo "   !! WARNING: $file has only $h2 sub-headings (${bytes}B) — structure may be missing"
      fail=1
    else
      echo "   ok: ${bytes}B, $h2 sub-headings"
    fi
  else
    echo "   !! FAILED: $(printf '%s' "$resp" | jq -r '.error // "unknown"')"
    fail=1
  fi
  sleep 2
done
echo "=== done (fail=$fail) ==="
exit $fail
