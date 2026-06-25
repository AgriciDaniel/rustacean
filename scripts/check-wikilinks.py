#!/usr/bin/env python3
"""Resolve every [[wikilink]] in the brain and fail if any target is missing.

Resolution mirrors Obsidian's shortest-unique-path linking:
a link ``[[Target]]`` resolves if ``Target`` matches a note's filename stem OR
any value in that note's frontmatter ``aliases:`` list. Link text inside fenced
``` ``` ``` blocks and inline ``code`` spans is ignored (it is documentation,
not a real link), and the ``Target|alias`` / ``Target#heading`` / ``Target^block``
forms are reduced to ``Target`` before lookup.

Usage:
    python3 scripts/check-wikilinks.py [VAULT_DIR]   # default: wiki/

Exit code 0 = all links resolve, 1 = unresolved links found.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_RE = re.compile(r"`[^`]*`")
ALIAS_RE = re.compile(r"^aliases:\s*\[(.*?)\]\s*$", re.MULTILINE)


def note_targets(md_files: list[Path]) -> set[str]:
    """All resolvable names: filename stems plus declared aliases."""
    targets: set[str] = set()
    for path in md_files:
        targets.add(path.stem)
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
        m = ALIAS_RE.search(head)
        if m:
            for alias in m.group(1).split(","):
                alias = alias.strip().strip('"').strip("'")
                if alias:
                    targets.add(alias)
    return targets


def link_target(raw: str) -> str:
    """Reduce ``Name|alias`` / ``Name#heading`` / ``Name^block`` to ``Name``."""
    return raw.split("|")[0].split("#")[0].split("^")[0].strip()


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "wiki")
    if not root.is_dir():
        print(f"error: vault directory not found: {root}", file=sys.stderr)
        return 2

    md_files = sorted(root.rglob("*.md"))
    resolvable = note_targets(md_files)

    total = 0
    unresolved: dict[str, list[str]] = {}
    for path in md_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        text = FENCE_RE.sub("", text)
        text = INLINE_RE.sub("", text)
        for lineno, line in enumerate(text.splitlines(), 1):
            for raw in LINK_RE.findall(line):
                target = link_target(raw)
                if not target:
                    continue
                total += 1
                if target not in resolvable:
                    unresolved.setdefault(target, []).append(f"{path}:{lineno}")

    print(f"notes scanned:        {len(md_files)}")
    print(f"resolvable names:     {len(resolvable)} (stems + aliases)")
    print(f"wikilinks checked:    {total}")
    print(f"unresolved targets:   {len(unresolved)}")

    if unresolved:
        print("\nUNRESOLVED LINKS:")
        for target, sites in sorted(unresolved.items()):
            print(f"  [[{target}]]  ({len(sites)}x)")
            for site in sites[:5]:
                print(f"      {site}")
        return 1

    print("\nOK: 100% of wikilinks resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
