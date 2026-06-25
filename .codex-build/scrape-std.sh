#!/usr/bin/env bash
# Scrape key std API pages (structure-preserving) into .raw/std/ for the std deep-dive.
set -u
set -a; . "${KEYS_ENV:-$HOME/.env}"; set +a
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; OUT="$ROOT/.raw/std"; mkdir -p "$OUT"
clean(){ awk 'p{print} /^# /{if(!p){p=1;print}}' | sed -E 's/^(#{1,6}) \[([^]]*)\]\([^)]*\)[[:space:]]*$/\1 \2/'; }

PAGES=(
 "vec-Vec|https://doc.rust-lang.org/std/vec/struct.Vec.html"
 "option-Option|https://doc.rust-lang.org/std/option/enum.Option.html"
 "result-Result|https://doc.rust-lang.org/std/result/enum.Result.html"
 "iter-Iterator|https://doc.rust-lang.org/std/iter/trait.Iterator.html"
 "string-String|https://doc.rust-lang.org/std/string/struct.String.html"
 "primitive-slice|https://doc.rust-lang.org/std/primitive.slice.html"
 "primitive-str|https://doc.rust-lang.org/std/primitive.str.html"
 "collections-index|https://doc.rust-lang.org/std/collections/index.html"
 "collections-HashMap|https://doc.rust-lang.org/std/collections/struct.HashMap.html"
 "collections-BTreeMap|https://doc.rust-lang.org/std/collections/struct.BTreeMap.html"
 "boxed-Box|https://doc.rust-lang.org/std/boxed/struct.Box.html"
 "rc-Rc|https://doc.rust-lang.org/std/rc/struct.Rc.html"
 "sync-Arc|https://doc.rust-lang.org/std/sync/struct.Arc.html"
 "sync-Mutex|https://doc.rust-lang.org/std/sync/struct.Mutex.html"
 "cell-index|https://doc.rust-lang.org/std/cell/index.html"
 "io-index|https://doc.rust-lang.org/std/io/index.html"
 "fmt-index|https://doc.rust-lang.org/std/fmt/index.html"
 "error-Error|https://doc.rust-lang.org/std/error/trait.Error.html"
 "convert-From|https://doc.rust-lang.org/std/convert/trait.From.html"
 "clone-Clone|https://doc.rust-lang.org/std/clone/trait.Clone.html"
 "default-Default|https://doc.rust-lang.org/std/default/trait.Default.html"
 "cmp-Ord|https://doc.rust-lang.org/std/cmp/trait.Ord.html"
 "hash-Hash|https://doc.rust-lang.org/std/hash/trait.Hash.html"
 "ops-index|https://doc.rust-lang.org/std/ops/index.html"
)
fail=0
for e in "${PAGES[@]}"; do
  f="${e%%|*}"; u="${e##*|}"
  resp=$(curl -s --max-time 150 https://api.firecrawl.dev/v1/scrape \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" \
    -d "{\"url\":\"$u\",\"formats\":[\"markdown\"],\"onlyMainContent\":false,\"timeout\":120000}")
  if [ "$(printf '%s' "$resp" | jq -r '.success // false')" = "true" ]; then
    printf '%s' "$resp" | jq -r '.data.markdown // ""' | clean > "$OUT/$f.md"
    echo "ok $f ($(wc -c <"$OUT/$f.md")B)"
  else
    echo "FAIL $f: $(printf '%s' "$resp" | jq -r '.error // "?"')"; fail=1
  fi
  sleep 1
done
echo "=== std scrape done (fail=$fail) ==="
