#!/usr/bin/env bash
# Build the example-check dependencies, wire them into rustc, and run the
# `rust` example compile gate. Used by CI (.github/workflows/quality.yml) and
# locally. Pass WRITE_ALLOW=1 to regenerate scripts/rust-examples-allow.txt.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.cargo/bin:$PATH"
DEPS_PROJ="$ROOT/scripts/examples-check"

echo ">> building example dependencies"
cargo build --manifest-path "$DEPS_PROJ/Cargo.toml" >/dev/null

DEPS="$DEPS_PROJ/target/debug/deps"
EXTERN="-L dependency=$DEPS"
for c in tokio tokio_stream futures serde serde_json anyhow thiserror clap \
         itertools rayon regex tracing smallvec quote syn; do
  rlib=$(ls -t "$DEPS"/lib${c}-*.rlib 2>/dev/null | head -1 || true)
  [ -n "${rlib:-}" ] && EXTERN="$EXTERN --extern $c=$rlib"
done

export RUSTC_EXTRA_ARGS="$EXTERN"
export ALLOWLIST="${ALLOWLIST:-$ROOT/scripts/rust-examples-allow.txt}"
echo ">> running compile gate"
exec python3 "$ROOT/scripts/check-rust-examples.py" "$ROOT/wiki"
