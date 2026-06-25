#!/usr/bin/env python3
"""Compile-gate for the brain's `rust` examples (edition 2024).

Extracts every ```rust fenced block from wiki/, type-checks each with
`rustc --emit=metadata` (no codegen) against the crates built by
scripts/examples-check, and compares the result to an allowlist of
known-non-compiling blocks (intentional "common error" demos, project-structure
snippets, proc-macro / no_std / uncommon-crate examples).

Exit code:
  0  every block outside the allowlist compiles (gate passes)
  1  a block outside the allowlist failed to compile (regression / new bug)

Env:
  RUSTC_EXTRA_ARGS   extra rustc flags (the -L/--extern for the deps build)
  ALLOWLIST          path to the allowlist (default scripts/rust-examples-allow.txt)
  WRITE_ALLOW        if set, (re)write the allowlist from the current failures

Usage: python3 scripts/check-rust-examples.py [wiki_dir]
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from glob import glob

FENCE = re.compile(r"^```[ \t]*rust[^\n]*\n(.*?)^```", re.M | re.S)


def iter_blocks(root):
    for path in sorted(glob(os.path.join(root, "**", "*.md"), recursive=True)):
        text = open(path, encoding="utf-8", errors="replace").read()
        for idx, code in enumerate(FENCE.findall(text)):
            yield os.path.relpath(path, root), idx, code


def wrap(code):
    if re.search(r"\bfn\s+main\s*\(", code):
        return code
    return "fn main() {\n" + code + "\n}\n"


def first_error(err):
    for line in err.splitlines():
        s = line.strip()
        if s.startswith("error"):
            return s[:120]
    return "?"


def load_allow(path):
    # Each line is "<path>#<idx>" optionally followed by "  # comment". The path
    # can contain spaces and the key contains '#', so match up to the first
    # "#<digits>"; full-line comments start with '#'.
    keys = set()
    if os.path.exists(path):
        for raw in open(path, encoding="utf-8"):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^(.+?#\d+)\s*(?:#.*)?$", line)
            if m:
                keys.add(m.group(1).strip())
    return keys


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "wiki"
    rustc = os.path.expanduser("~/.cargo/bin/rustc")
    if not os.path.exists(rustc):
        rustc = "rustc"
    extra = os.environ.get("RUSTC_EXTRA_ARGS", "").split()
    allow_path = os.environ.get("ALLOWLIST", "scripts/rust-examples-allow.txt")
    allow = load_allow(allow_path)
    workdir = tempfile.mkdtemp(prefix="rustgate-")
    out = os.path.join(workdir, "out.rmeta")

    total = passed = 0
    failures = []  # (key, codes, first_error)
    for rel, idx, code in iter_blocks(root):
        total += 1
        fn = os.path.join(workdir, "snippet.rs")
        open(fn, "w", encoding="utf-8").write(wrap(code))
        try:
            r = subprocess.run(
                [rustc, "--edition", "2024", "--crate-type", "lib",
                 "--emit=metadata", "-o", out, *extra, fn],
                capture_output=True, text=True, timeout=60,
            )
            rc, err = r.returncode, r.stderr
        except subprocess.TimeoutExpired:
            rc, err = 1, "timeout"
        if rc == 0:
            passed += 1
        else:
            codes = ",".join(sorted(set(re.findall(r"error\[(E\d{4})\]", err)))) or "?"
            failures.append((f"{rel}#{idx}", codes, first_error(err)))
    shutil.rmtree(workdir, ignore_errors=True)

    fail_keys = {k for k, _, _ in failures}
    regressions = sorted(k for k in fail_keys if k not in allow)
    stale = sorted(k for k in allow if k not in fail_keys)

    if os.environ.get("WRITE_ALLOW"):
        with open(allow_path, "w", encoding="utf-8") as f:
            f.write("# Known-non-compiling `rust` examples (intentional error-demos,\n")
            f.write("# project-structure snippets, proc-macro/no_std/uncommon-crate).\n")
            f.write("# Regenerate: WRITE_ALLOW=1 scripts/run-rust-gate.sh\n")
            f.write(f"# {passed}/{total} blocks compile; {len(failures)} listed below.\n\n")
            for key, codes, fe in sorted(failures):
                f.write(f"{key}    # {codes}: {fe}\n")
        print(f"wrote {len(failures)} entries to {allow_path}")

    print(f"total {total} | compiled {passed} ({100*passed//total}%) | "
          f"failed {len(failures)} | allowlisted {len(allow)} | "
          f"regressions {len(regressions)} | stale {len(stale)}")
    if regressions:
        print("\nREGRESSIONS (compile these or add to the allowlist):")
        fmap = {k: (c, e) for k, c, e in failures}
        for k in regressions:
            print(f"  {k}  [{fmap[k][0]}] {fmap[k][1]}")
    if stale:
        print("\nstale allowlist entries (now compile, can be removed):")
        for k in stale:
            print(f"  {k}")
    return 1 if regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
